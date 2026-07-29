#!/usr/bin/env python3
"""
Test script to verify C++ SBOM Generator functionality.
Run this to ensure the tool is working correctly.
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from parsers.cpp_parser import CppSourceParser
        from parsers.build_parser import BuildSystemParser
        from parsers.dependency_analyzer import DependencyAnalyzer
        from exporters.spdx_exporter import SPDXExporter
        from exporters.cyclonedx_exporter import CycloneDXExporter
        from sbom_generator import SBOMGenerator
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_cpp_parser():
    """Test C++ source parser."""
    print("\nTesting C++ parser...")
    try:
        from parsers.cpp_parser import CppSourceParser
        
        parser = CppSourceParser()
        
        # Test include pattern
        test_code = """
        #include <iostream>
        #include <vector>
        #include "myheader.h"
        #include <boost/algorithm/string.hpp>
        
        using namespace std;
        using namespace boost;
        """
        
        # Create temp file
        temp_file = Path("temp_test.cpp")
        temp_file.write_text(test_code)
        
        result = parser.parse_file(temp_file)
        
        # Verify results
        includes = result.get('includes', set())
        libraries = result.get('libraries', set())
        
        assert 'iostream' in includes
        assert 'vector' in includes
        assert 'boost' in libraries
        
        temp_file.unlink()
        
        print("  ✓ C++ parser working correctly")
        return True
    except Exception as e:
        print(f"  ✗ C++ parser test failed: {e}")
        if temp_file.exists():
            temp_file.unlink()
        return False

def test_cmake_parser():
    """Test CMake parser."""
    print("\nTesting CMake parser...")
    try:
        from parsers.build_parser import CMakeParser
        
        # Create temp CMakeLists.txt
        cmake_content = """
        cmake_minimum_required(VERSION 3.10)
        project(TestProject VERSION 1.0.0)
        
        find_package(Boost 1.70 REQUIRED)
        find_package(OpenCV REQUIRED)
        
        target_link_libraries(myapp Boost::boost OpenCV::core)
        """
        
        temp_dir = Path("temp_cmake_test")
        temp_dir.mkdir(exist_ok=True)
        cmake_file = temp_dir / "CMakeLists.txt"
        cmake_file.write_text(cmake_content)
        
        parser = CMakeParser(temp_dir)
        dependencies = parser.parse()
        
        assert 'Boost' in dependencies
        assert 'OpenCV' in dependencies
        
        # Cleanup
        cmake_file.unlink()
        temp_dir.rmdir()
        
        print("  ✓ CMake parser working correctly")
        return True
    except Exception as e:
        print(f"  ✗ CMake parser test failed: {e}")
        return False

def test_spdx_export():
    """Test SPDX export."""
    print("\nTesting SPDX export...")
    try:
        from exporters.spdx_exporter import SPDXExporter
        from sbom_generator import Component
        
        metadata = {
            'project_name': 'TestProject',
            'project_version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z',
            'tool': 'test-tool',
            'tool_version': '1.0.0'
        }
        
        exporter = SPDXExporter(metadata)
        
        # Create test component
        component = Component('test-lib', '1.2.3', 'library')
        component.licenses.add('MIT')
        component.supplier = 'Test Supplier'
        
        components = {'test-lib': component}
        
        output_file = Path("test_sbom_spdx.json")
        exporter.export(components, output_file)
        
        # Verify output
        with open(output_file, 'r') as f:
            sbom = json.load(f)
        
        assert sbom['spdxVersion'] == 'SPDX-2.3'
        assert len(sbom['packages']) >= 1
        
        output_file.unlink()
        
        print("  ✓ SPDX export working correctly")
        return True
    except Exception as e:
        print(f"  ✗ SPDX export test failed: {e}")
        if output_file.exists():
            output_file.unlink()
        return False

def test_cyclonedx_export():
    """Test CycloneDX export."""
    print("\nTesting CycloneDX export...")
    try:
        from exporters.cyclonedx_exporter import CycloneDXExporter
        from sbom_generator import Component
        
        metadata = {
            'project_name': 'TestProject',
            'project_version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z',
            'tool': 'test-tool',
            'tool_version': '1.0.0'
        }
        
        exporter = CycloneDXExporter(metadata)
        
        # Create test component
        component = Component('test-lib', '1.2.3', 'library')
        component.licenses.add('MIT')
        
        components = {'test-lib': component}
        
        output_file = Path("test_sbom_cdx.json")
        exporter.export(components, output_file)
        
        # Verify output
        with open(output_file, 'r') as f:
            sbom = json.load(f)
        
        assert sbom['bomFormat'] == 'CycloneDX'
        assert sbom['specVersion'] == '1.4'
        assert len(sbom['components']) >= 1
        
        output_file.unlink()
        
        print("  ✓ CycloneDX export working correctly")
        return True
    except Exception as e:
        print(f"  ✗ CycloneDX export test failed: {e}")
        if output_file.exists():
            output_file.unlink()
        return False

def test_full_workflow():
    """Test complete workflow on test project."""
    print("\nTesting full workflow...")
    try:
        test_project = Path("test_project")
        if not test_project.exists():
            print("  ⚠ Test project not found, skipping workflow test")
            return True
        
        from sbom_generator import SBOMGenerator
        
        config = {
            'project_name': 'TestApp',
            'project_version': '1.0.0'
        }
        
        generator = SBOMGenerator(test_project, config)
        generator.scan_project()
        
        assert len(generator.components) > 0
        
        output_file = Path("test_full_sbom.json")
        generator.generate_sbom('json', output_file)
        
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            sbom = json.load(f)
        
        assert 'metadata' in sbom
        assert 'components' in sbom
        
        output_file.unlink()
        
        print("  ✓ Full workflow test passed")
        return True
    except Exception as e:
        print(f"  ✗ Full workflow test failed: {e}")
        if output_file.exists():
            output_file.unlink()
        return False

def test_utils():
    """Test utility functions."""
    print("\nTesting utilities...")
    try:
        from utils import validate_sbom, extract_licenses
        
        # Create a minimal valid SPDX SBOM
        test_sbom = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "Test SBOM",
            "documentNamespace": "https://example.com/test",
            "creationInfo": {
                "created": "2024-01-01T00:00:00Z",
                "creators": ["Tool: test"]
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-Package-1",
                    "name": "test-package",
                    "versionInfo": "1.0.0",
                    "downloadLocation": "NOASSERTION",
                    "licenseConcluded": "MIT",
                    "licenseDeclared": "MIT",
                    "copyrightText": "NOASSERTION"
                }
            ]
        }
        
        test_file = Path("test_validation.json")
        with open(test_file, 'w') as f:
            json.dump(test_sbom, f)
        
        is_valid, issues = validate_sbom(test_file)
        
        if not is_valid:
            print(f"  Issues found: {issues}")
        
        licenses = extract_licenses(test_file)
        assert 'MIT' in licenses
        
        test_file.unlink()
        
        print("  ✓ Utilities working correctly")
        return True
    except Exception as e:
        print(f"  ✗ Utilities test failed: {e}")
        if test_file.exists():
            test_file.unlink()
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("C++ SBOM Generator - Test Suite")
    print("=" * 70)
    
    tests = [
        ("Imports", test_imports),
        ("C++ Parser", test_cpp_parser),
        ("CMake Parser", test_cmake_parser),
        ("SPDX Export", test_spdx_export),
        ("CycloneDX Export", test_cyclonedx_export),
        ("Full Workflow", test_full_workflow),
        ("Utilities", test_utils),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} - {test_name}")
    
    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The tool is ready to use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
