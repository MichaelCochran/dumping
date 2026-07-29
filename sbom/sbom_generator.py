#!/usr/bin/env python3
"""
C++ SBOM Generator - A comprehensive tool for generating Software Bill of Materials
for C++ projects with fine-grained dependency analysis.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import hashlib

from parsers.cpp_parser import CppSourceParser
from parsers.build_parser import BuildSystemParser
from parsers.dependency_analyzer import DependencyAnalyzer
from exporters.spdx_exporter import SPDXExporter
from exporters.cyclonedx_exporter import CycloneDXExporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Component:
    """Represents a software component in the SBOM."""
    
    def __init__(self, name: str, version: str = "unknown", 
                 component_type: str = "library"):
        self.name = name
        self.version = version
        self.component_type = component_type
        self.licenses: Set[str] = set()
        self.supplier: Optional[str] = None
        self.description: Optional[str] = None
        self.homepage: Optional[str] = None
        self.checksums: Dict[str, str] = {}
        self.file_paths: Set[Path] = set()
        self.dependencies: Set[str] = set()
        self.cpe: Optional[str] = None
        self.purl: Optional[str] = None
        self.properties: Dict[str, str] = {}
    
    def to_dict(self) -> dict:
        """Convert component to dictionary representation."""
        return {
            'name': self.name,
            'version': self.version,
            'type': self.component_type,
            'licenses': list(self.licenses),
            'supplier': self.supplier,
            'description': self.description,
            'homepage': self.homepage,
            'checksums': self.checksums,
            'file_paths': [str(p) for p in self.file_paths],
            'dependencies': list(self.dependencies),
            'cpe': self.cpe,
            'purl': self.purl,
            'properties': self.properties
        }


class SBOMGenerator:
    """Main SBOM generator orchestrating parsing and export."""
    
    def __init__(self, project_path: Path, config: Optional[Dict] = None):
        self.project_path = project_path
        self.config = config or {}
        self.components: Dict[str, Component] = {}
        self.source_files: Set[Path] = set()
        self.metadata = {
            'project_name': self.config.get('project_name', project_path.name),
            'project_version': self.config.get('project_version', '1.0.0'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'tool': 'cpp-sbom-generator',
            'tool_version': '1.0.0'
        }
        
        self.cpp_parser = CppSourceParser()
        self.build_parser = BuildSystemParser(project_path)
        self.dep_analyzer = DependencyAnalyzer()
    
    def scan_project(self, max_depth: Optional[int] = None) -> None:
        """Scan the project directory for source files and dependencies."""
        logger.info(f"Scanning project at {self.project_path}")
        
        # Find all C++ source files
        patterns = ['*.cpp', '*.cc', '*.cxx', '*.c', '*.h', '*.hpp', '*.hxx']
        for pattern in patterns:
            if max_depth:
                files = list(self.project_path.rglob(pattern))[:max_depth]
            else:
                files = list(self.project_path.rglob(pattern))
            self.source_files.update(files)
        
        logger.info(f"Found {len(self.source_files)} source files")
        
        # Parse build system files
        build_deps = self.build_parser.parse()
        for dep_name, dep_info in build_deps.items():
            self._add_or_update_component(dep_name, dep_info)
        
        # Parse source files for includes
        include_map = {}
        for source_file in self.source_files:
            try:
                includes = self.cpp_parser.parse_file(source_file)
                include_map[source_file] = includes
                
                # Add file as a component
                file_component = Component(
                    name=source_file.name,
                    version=self.metadata['project_version'],
                    component_type='source-file'
                )
                file_component.file_paths.add(source_file)
                file_component.checksums = self._compute_checksums(source_file)
                self.components[str(source_file)] = file_component
                
            except Exception as e:
                logger.warning(f"Failed to parse {source_file}: {e}")
        
        # Analyze dependencies
        dep_details = self.dep_analyzer.analyze(
            include_map, 
            self.project_path,
            self.config.get('system_include_paths', [])
        )
        
        for dep_name, details in dep_details.items():
            self._add_or_update_component(dep_name, details)
    
    def _add_or_update_component(self, name: str, info: Dict) -> None:
        """Add a new component or update existing one."""
        if name in self.components:
            component = self.components[name]
        else:
            component = Component(
                name=name,
                version=info.get('version', 'unknown'),
                component_type=info.get('type', 'library')
            )
            self.components[name] = component
        
        # Update component details
        if 'version' in info and component.version == 'unknown':
            component.version = info['version']
        
        if 'licenses' in info:
            component.licenses.update(info['licenses'])
        
        if 'supplier' in info:
            component.supplier = info['supplier']
        
        if 'description' in info:
            component.description = info['description']
        
        if 'homepage' in info:
            component.homepage = info['homepage']
        
        if 'file_paths' in info:
            component.file_paths.update(info['file_paths'])
        
        if 'dependencies' in info:
            component.dependencies.update(info['dependencies'])
        
        if 'cpe' in info:
            component.cpe = info['cpe']
        
        if 'purl' in info:
            component.purl = info['purl']
        
        if 'properties' in info:
            component.properties.update(info['properties'])
    
    def _compute_checksums(self, file_path: Path) -> Dict[str, str]:
        """Compute various checksums for a file."""
        checksums = {}
        
        try:
            content = file_path.read_bytes()
            checksums['sha256'] = hashlib.sha256(content).hexdigest()
            checksums['sha1'] = hashlib.sha1(content).hexdigest()
            checksums['md5'] = hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute checksums for {file_path}: {e}")
        
        return checksums
    
    def generate_sbom(self, output_format: str, output_path: Path) -> None:
        """Generate SBOM in specified format."""
        logger.info(f"Generating {output_format} SBOM")
        
        if output_format.lower() == 'spdx':
            exporter = SPDXExporter(self.metadata)
            exporter.export(self.components, output_path)
        elif output_format.lower() == 'cyclonedx':
            exporter = CycloneDXExporter(self.metadata)
            exporter.export(self.components, output_path)
        elif output_format.lower() == 'json':
            self._export_json(output_path)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
        
        logger.info(f"SBOM written to {output_path}")
    
    def _export_json(self, output_path: Path) -> None:
        """Export SBOM as raw JSON."""
        sbom_data = {
            'metadata': self.metadata,
            'components': {name: comp.to_dict() 
                          for name, comp in self.components.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sbom_data, f, indent=2, ensure_ascii=False)
    
    def print_summary(self) -> None:
        """Print a summary of discovered components."""
        print("\n" + "="*80)
        print(f"SBOM Summary for {self.metadata['project_name']}")
        print("="*80)
        print(f"Total components: {len(self.components)}")
        
        by_type = {}
        for comp in self.components.values():
            by_type[comp.component_type] = by_type.get(comp.component_type, 0) + 1
        
        print("\nComponents by type:")
        for comp_type, count in sorted(by_type.items()):
            print(f"  {comp_type}: {count}")
        
        print(f"\nSource files analyzed: {len(self.source_files)}")
        print("="*80 + "\n")


def load_config(config_path: Optional[Path]) -> Dict:
    """Load configuration from file."""
    if not config_path or not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate detailed SBOM for C++ projects',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'project_path',
        type=Path,
        help='Path to C++ project directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output file path for SBOM'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['spdx', 'cyclonedx', 'json'],
        default='spdx',
        help='SBOM output format (default: spdx)'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Configuration file path (JSON)'
    )
    
    parser.add_argument(
        '--project-name',
        help='Project name (overrides config)'
    )
    
    parser.add_argument(
        '--project-version',
        help='Project version (overrides config)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        help='Maximum depth for directory traversal'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate project path
    if not args.project_path.exists():
        logger.error(f"Project path does not exist: {args.project_path}")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with CLI arguments
    if args.project_name:
        config['project_name'] = args.project_name
    if args.project_version:
        config['project_version'] = args.project_version
    
    try:
        # Create generator and scan project
        generator = SBOMGenerator(args.project_path, config)
        generator.scan_project(max_depth=args.max_depth)
        
        # Print summary
        generator.print_summary()
        
        # Generate SBOM
        generator.generate_sbom(args.format, args.output)
        
        logger.info("SBOM generation completed successfully")
        
    except Exception as e:
        logger.error(f"SBOM generation failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()
