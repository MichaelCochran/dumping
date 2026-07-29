#!/usr/bin/env python3
"""
Example usage of the C++ SBOM Generator as a library.
This demonstrates how to use the tool programmatically.
"""

from pathlib import Path
from sbom_generator import SBOMGenerator

def generate_sbom_example():
    """Example: Generate SBOM for a C++ project."""
    
    # Configuration
    project_path = Path("path/to/your/cpp/project")
    output_path = Path("output/sbom.json")
    
    config = {
        'project_name': 'MyAwesomeProject',
        'project_version': '2.1.0',
        'system_include_paths': [
            '/usr/include',
            '/usr/local/include'
        ]
    }
    
    # Create generator
    generator = SBOMGenerator(project_path, config)
    
    # Scan project
    print("Scanning project...")
    generator.scan_project()
    
    # Print summary
    generator.print_summary()
    
    # Generate different formats
    print("\nGenerating SBOMs...")
    
    # SPDX JSON
    generator.generate_sbom('spdx', output_path.parent / 'sbom-spdx.json')
    
    # CycloneDX JSON
    generator.generate_sbom('cyclonedx', output_path.parent / 'sbom-cdx.json')
    
    # Raw JSON
    generator.generate_sbom('json', output_path.parent / 'sbom-raw.json')
    
    print("\nSBOM generation complete!")
    
    # Access components programmatically
    print(f"\nFound {len(generator.components)} components:")
    for name, component in list(generator.components.items())[:5]:
        print(f"  - {name} ({component.version})")

def analyze_dependencies_only():
    """Example: Just analyze dependencies without full SBOM generation."""
    from parsers.cpp_parser import CppSourceParser
    
    parser = CppSourceParser()
    source_files = list(Path("path/to/project").rglob("*.cpp"))
    
    dependencies = parser.analyze_dependencies(source_files)
    
    print("Dependencies found:")
    for lib_name, lib_info in dependencies.items():
        print(f"\n{lib_name}:")
        print(f"  Used in {len(lib_info['used_in_files'])} files")
        print(f"  Includes: {', '.join(lib_info['includes'][:3])}")

def custom_component_enrichment():
    """Example: Add custom metadata to components."""
    
    project_path = Path("path/to/project")
    
    config = {
        'project_name': 'CustomProject',
        'project_version': '1.0.0'
    }
    
    generator = SBOMGenerator(project_path, config)
    generator.scan_project()
    
    # Add custom metadata to a specific component
    if 'boost' in generator.components:
        boost = generator.components['boost']
        boost.properties['build_type'] = 'static'
        boost.properties['compiler'] = 'gcc-11'
        boost.cpe = 'cpe:2.3:a:boost:boost:1.78.0:*:*:*:*:*:*:*'
    
    generator.generate_sbom('spdx', Path('sbom-custom.json'))

if __name__ == '__main__':
    print("C++ SBOM Generator - Example Usage\n")
    print("=" * 60)
    
    # Uncomment the example you want to run:
    # generate_sbom_example()
    # analyze_dependencies_only()
    # custom_component_enrichment()
    
    print("\nEdit example_usage.py to run specific examples.")
