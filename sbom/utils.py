#!/usr/bin/env python3
"""
Utility functions for SBOM operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def compare_sboms(sbom1_path: Path, sbom2_path: Path) -> Dict:
    """
    Compare two SBOM files and report differences.
    
    Args:
        sbom1_path: Path to first SBOM (baseline)
        sbom2_path: Path to second SBOM (current)
    
    Returns:
        Dictionary containing added, removed, and changed components
    """
    with open(sbom1_path, 'r') as f:
        sbom1 = json.load(f)
    
    with open(sbom2_path, 'r') as f:
        sbom2 = json.load(f)
    
    # Handle different SBOM formats
    components1 = _extract_components(sbom1)
    components2 = _extract_components(sbom2)
    
    added = {}
    removed = {}
    changed = {}
    
    # Find added and changed
    for name, info2 in components2.items():
        if name not in components1:
            added[name] = info2
        elif components1[name] != info2:
            changed[name] = {
                'old': components1[name],
                'new': info2
            }
    
    # Find removed
    for name, info1 in components1.items():
        if name not in components2:
            removed[name] = info1
    
    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'summary': {
            'total_added': len(added),
            'total_removed': len(removed),
            'total_changed': len(changed)
        }
    }


def _extract_components(sbom: Dict) -> Dict:
    """Extract components from SBOM regardless of format."""
    components = {}
    
    # Raw JSON format
    if 'components' in sbom and isinstance(sbom['components'], dict):
        return sbom['components']
    
    # SPDX format
    if 'packages' in sbom:
        for pkg in sbom['packages']:
            name = pkg.get('name', 'unknown')
            components[name] = {
                'version': pkg.get('versionInfo', 'unknown'),
                'license': pkg.get('licenseConcluded', 'unknown')
            }
    
    # CycloneDX format
    elif 'components' in sbom and isinstance(sbom['components'], list):
        for comp in sbom['components']:
            name = comp.get('name', 'unknown')
            components[name] = {
                'version': comp.get('version', 'unknown'),
                'type': comp.get('type', 'library')
            }
    
    return components


def validate_sbom(sbom_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate SBOM file for completeness and correctness.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        with open(sbom_path, 'r') as f:
            sbom = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Failed to read file: {e}"]
    
    # Check SPDX format
    if 'spdxVersion' in sbom:
        if 'creationInfo' not in sbom:
            issues.append("Missing creationInfo")
        if 'packages' not in sbom:
            issues.append("Missing packages")
        
        # Validate packages
        for pkg in sbom.get('packages', []):
            if 'name' not in pkg:
                issues.append(f"Package missing name: {pkg.get('SPDXID', 'unknown')}")
            if 'downloadLocation' not in pkg:
                issues.append(f"Package {pkg.get('name', 'unknown')} missing downloadLocation")
    
    # Check CycloneDX format
    elif 'bomFormat' in sbom:
        if sbom.get('bomFormat') != 'CycloneDX':
            issues.append(f"Invalid bomFormat: {sbom.get('bomFormat')}")
        if 'components' not in sbom:
            issues.append("Missing components")
        
        # Validate components
        for comp in sbom.get('components', []):
            if 'name' not in comp:
                issues.append("Component missing name")
            if 'version' not in comp:
                issues.append(f"Component {comp.get('name', 'unknown')} missing version")
    
    # Check raw format
    elif 'metadata' in sbom and 'components' in sbom:
        if 'project_name' not in sbom.get('metadata', {}):
            issues.append("Missing project_name in metadata")
    
    else:
        issues.append("Unknown or invalid SBOM format")
    
    return len(issues) == 0, issues


def generate_summary_report(sbom_path: Path, output_path: Path = None) -> str:
    """
    Generate a human-readable summary report from SBOM.
    
    Args:
        sbom_path: Path to SBOM file
        output_path: Optional path to save report
    
    Returns:
        Summary report as string
    """
    with open(sbom_path, 'r') as f:
        sbom = json.load(f)
    
    components = _extract_components(sbom)
    
    # Generate report
    report_lines = [
        "=" * 80,
        "SBOM SUMMARY REPORT",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source: {sbom_path.name}",
        ""
    ]
    
    # Count by type
    by_type = {}
    by_license = {}
    versions = {}
    
    for name, info in components.items():
        comp_type = info.get('type', 'library')
        by_type[comp_type] = by_type.get(comp_type, 0) + 1
        
        version = info.get('version', 'unknown')
        if version != 'unknown':
            versions[name] = version
        
        license_info = info.get('license', info.get('licenses', 'unknown'))
        if isinstance(license_info, list):
            for lic in license_info:
                by_license[lic] = by_license.get(lic, 0) + 1
        elif license_info != 'unknown':
            by_license[license_info] = by_license.get(license_info, 0) + 1
    
    # Components summary
    report_lines.extend([
        f"Total Components: {len(components)}",
        "",
        "Components by Type:",
    ])
    
    for comp_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
        report_lines.append(f"  {comp_type:20s}: {count:3d}")
    
    # Version info
    report_lines.extend([
        "",
        f"Components with known versions: {len(versions)} / {len(components)}",
        f"Components with unknown versions: {len(components) - len(versions)}",
        ""
    ])
    
    # License info
    if by_license:
        report_lines.extend([
            "Licenses Detected:",
        ])
        for license_id, count in sorted(by_license.items(), key=lambda x: -x[1]):
            report_lines.append(f"  {license_id:30s}: {count:3d}")
    
    # Top components
    report_lines.extend([
        "",
        "Sample Components (first 10):",
    ])
    
    for idx, (name, info) in enumerate(list(components.items())[:10], 1):
        version = info.get('version', 'unknown')
        report_lines.append(f"  {idx:2d}. {name:40s} v{version}")
    
    report_lines.extend([
        "",
        "=" * 80
    ])
    
    report = "\n".join(report_lines)
    
    # Save to file if requested
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {output_path}")
    
    return report


def extract_licenses(sbom_path: Path) -> Set[str]:
    """Extract all unique licenses from SBOM."""
    with open(sbom_path, 'r') as f:
        sbom = json.load(f)
    
    licenses = set()
    
    if 'packages' in sbom:
        # SPDX format
        for pkg in sbom['packages']:
            lic = pkg.get('licenseConcluded', '')
            if lic and lic not in ['NOASSERTION', 'NONE']:
                # Split combined licenses
                for l in lic.split(' OR '):
                    licenses.add(l.strip())
    
    elif 'components' in sbom and isinstance(sbom['components'], list):
        # CycloneDX format
        for comp in sbom['components']:
            for lic_obj in comp.get('licenses', []):
                if 'license' in lic_obj and 'id' in lic_obj['license']:
                    licenses.add(lic_obj['license']['id'])
    
    return licenses


def main():
    """CLI for utility functions."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SBOM utility functions')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two SBOMs')
    compare_parser.add_argument('sbom1', type=Path, help='Baseline SBOM')
    compare_parser.add_argument('sbom2', type=Path, help='Current SBOM')
    compare_parser.add_argument('-o', '--output', type=Path, help='Output file for diff')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate SBOM')
    validate_parser.add_argument('sbom', type=Path, help='SBOM file to validate')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate summary report')
    summary_parser.add_argument('sbom', type=Path, help='SBOM file')
    summary_parser.add_argument('-o', '--output', type=Path, help='Output file for report')
    
    # Licenses command
    licenses_parser = subparsers.add_parser('licenses', help='Extract licenses')
    licenses_parser.add_argument('sbom', type=Path, help='SBOM file')
    
    args = parser.parse_args()
    
    if args.command == 'compare':
        diff = compare_sboms(args.sbom1, args.sbom2)
        
        print(f"\nSBOM Comparison: {args.sbom1.name} -> {args.sbom2.name}")
        print("=" * 60)
        print(f"Added: {diff['summary']['total_added']}")
        print(f"Removed: {diff['summary']['total_removed']}")
        print(f"Changed: {diff['summary']['total_changed']}")
        
        if diff['added']:
            print("\nAdded components:")
            for name in list(diff['added'].keys())[:10]:
                print(f"  + {name}")
        
        if diff['removed']:
            print("\nRemoved components:")
            for name in list(diff['removed'].keys())[:10]:
                print(f"  - {name}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(diff, f, indent=2)
            print(f"\nFull diff saved to {args.output}")
    
    elif args.command == 'validate':
        is_valid, issues = validate_sbom(args.sbom)
        
        print(f"\nValidating: {args.sbom}")
        print("=" * 60)
        
        if is_valid:
            print("✓ SBOM is valid")
        else:
            print("✗ SBOM has issues:")
            for issue in issues:
                print(f"  - {issue}")
    
    elif args.command == 'summary':
        report = generate_summary_report(args.sbom, args.output)
        print(report)
    
    elif args.command == 'licenses':
        licenses = extract_licenses(args.sbom)
        
        print(f"\nLicenses in {args.sbom.name}:")
        print("=" * 60)
        for lic in sorted(licenses):
            print(f"  - {lic}")
        print(f"\nTotal: {len(licenses)} unique licenses")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
