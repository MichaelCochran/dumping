"""Parser for build system files (CMake, Makefile, etc.)."""

import re
import logging
import subprocess
from pathlib import Path
from typing import Dict, Set, List, Optional

from parsers.embedded_parser import (
    PlatformIOParser,
    ESPIDFParser,
    RTOSDetector,
    EmbeddedLibraryDetector
)

logger = logging.getLogger(__name__)


class BuildSystemParser:
    """Parse various build system files to extract dependencies."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.cmake_parser = CMakeParser(project_path)
        self.makefile_parser = MakefileParser(project_path)
        self.pkgconfig_parser = PkgConfigParser()
        self.conan_parser = ConanParser(project_path)
        self.vcpkg_parser = VcpkgParser(project_path)
        self.platformio_parser = PlatformIOParser(project_path)
        self.espidf_parser = ESPIDFParser(project_path)
        self.rtos_detector = RTOSDetector(project_path)
        self.embedded_lib_detector = EmbeddedLibraryDetector(project_path)
    
    def parse(self) -> Dict[str, Dict]:
        """Parse all available build system files."""
        dependencies = {}
        
        # Try CMake
        cmake_deps = self.cmake_parser.parse()
        dependencies.update(cmake_deps)
        
        # Try Makefile
        makefile_deps = self.makefile_parser.parse()
        dependencies.update(makefile_deps)
        
        # Try Conan
        conan_deps = self.conan_parser.parse()
        dependencies.update(conan_deps)
        
        # Try vcpkg
        vcpkg_deps = self.vcpkg_parser.parse()
        dependencies.update(vcpkg_deps)
        
        # Try PlatformIO
        platformio_deps = self.platformio_parser.parse()
        dependencies.update(platformio_deps)
        logger.info(f"PlatformIO: {len(platformio_deps)} dependencies")
        
        # Try ESP-IDF
        espidf_deps = self.espidf_parser.parse()
        dependencies.update(espidf_deps)
        logger.info(f"ESP-IDF: {len(espidf_deps)} dependencies")
        
        # Detect RTOS
        rtos_deps = self.rtos_detector.detect()
        dependencies.update(rtos_deps)
        logger.info(f"RTOS: {len(rtos_deps)} detected")
        
        # Detect embedded libraries
        embedded_libs = self.embedded_lib_detector.detect()
        dependencies.update(embedded_libs)
        logger.info(f"Embedded libs: {len(embedded_libs)} detected")
        
        # Enhance with pkg-config if available
        self._enhance_with_pkgconfig(dependencies)
        
        return dependencies
    
    def _enhance_with_pkgconfig(self, dependencies: Dict[str, Dict]) -> None:
        """Try to get additional info from pkg-config for known libraries."""
        for dep_name in list(dependencies.keys()):
            pkg_info = self.pkgconfig_parser.get_package_info(dep_name)
            if pkg_info:
                dependencies[dep_name].update(pkg_info)


class CMakeParser:
    """Parse CMakeLists.txt files."""
    
    FIND_PACKAGE_PATTERN = re.compile(
        r'find_package\s*\(\s*(\w+)(?:\s+([0-9.]+))?\s*(?:REQUIRED|QUIET|COMPONENTS)?\s*([^)]*)\)',
        re.IGNORECASE
    )
    
    PKG_CHECK_MODULES_PATTERN = re.compile(
        r'pkg_check_modules\s*\(\s*\w+\s+(?:REQUIRED\s+)?([^\)]+)\)',
        re.IGNORECASE
    )
    
    TARGET_LINK_PATTERN = re.compile(
        r'target_link_libraries\s*\([^)]+\s+([^)]+)\)',
        re.IGNORECASE
    )
    
    PROJECT_VERSION_PATTERN = re.compile(
        r'project\s*\([^)]*VERSION\s+([0-9.]+)',
        re.IGNORECASE
    )
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse CMakeLists.txt files in the project."""
        dependencies = {}
        
        # Find all CMakeLists.txt files
        cmake_files = list(self.project_path.rglob('CMakeLists.txt'))
        
        for cmake_file in cmake_files:
            try:
                with open(cmake_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract find_package calls
                for match in self.FIND_PACKAGE_PATTERN.finditer(content):
                    package_name = match.group(1)
                    version = match.group(2) if match.group(2) else 'unknown'
                    components = match.group(3).strip() if match.group(3) else ''
                    
                    if package_name not in dependencies:
                        dependencies[package_name] = {
                            'version': version,
                            'type': 'library',
                            'source': 'cmake',
                            'components': []
                        }
                    
                    if components:
                        comp_list = [c.strip() for c in components.split() 
                                   if c.strip() and c.strip() not in ['REQUIRED', 'QUIET', 'COMPONENTS']]
                        dependencies[package_name]['components'].extend(comp_list)
                
                # Extract pkg_check_modules calls
                for match in self.PKG_CHECK_MODULES_PATTERN.finditer(content):
                    packages = match.group(1).strip().split()
                    for pkg in packages:
                        # Parse package specifications like "libusb-1.0>=1.0.9"
                        pkg_match = re.match(r'([a-zA-Z0-9_-]+)([><=]+)?([0-9.]+)?', pkg)
                        if pkg_match:
                            pkg_name = pkg_match.group(1)
                            version = pkg_match.group(3) if pkg_match.group(3) else 'unknown'
                            
                            if pkg_name not in dependencies:
                                dependencies[pkg_name] = {
                                    'version': version,
                                    'type': 'library',
                                    'source': 'pkg-config'
                                }
                
                # Extract target_link_libraries
                for match in self.TARGET_LINK_PATTERN.finditer(content):
                    libs = match.group(1).strip().split()
                    for lib in libs:
                        lib = lib.strip()
                        # Filter out CMake keywords and variables
                        if lib and not lib.startswith('$') and lib not in ['PUBLIC', 'PRIVATE', 'INTERFACE']:
                            # Remove namespace prefixes like Qt5::
                            lib_name = lib.split('::')[-1] if '::' in lib else lib
                            
                            if lib_name not in dependencies:
                                dependencies[lib_name] = {
                                    'version': 'unknown',
                                    'type': 'library',
                                    'source': 'cmake-link'
                                }
            
            except Exception as e:
                logger.warning(f"Failed to parse {cmake_file}: {e}")
        
        return dependencies


class MakefileParser:
    """Parse Makefile to extract dependencies."""
    
    LDFLAGS_PATTERN = re.compile(r'LDFLAGS\s*[+:=]+\s*(.+?)(?:\n|$)')
    LIBS_PATTERN = re.compile(r'LIBS\s*[+:=]+\s*(.+?)(?:\n|$)')
    PKGCONFIG_PATTERN = re.compile(r'pkg-config\s+--[^\s]+\s+([^\)]+)')
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse Makefile for dependencies."""
        dependencies = {}
        
        # Find Makefiles
        makefiles = list(self.project_path.glob('Makefile*'))
        makefiles.extend(self.project_path.glob('makefile*'))
        
        for makefile in makefiles:
            try:
                with open(makefile, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract libraries from LDFLAGS
                for match in self.LDFLAGS_PATTERN.finditer(content):
                    flags = match.group(1)
                    libs = re.findall(r'-l(\w+)', flags)
                    for lib in libs:
                        if lib not in dependencies:
                            dependencies[lib] = {
                                'version': 'unknown',
                                'type': 'library',
                                'source': 'makefile-ldflags'
                            }
                
                # Extract from LIBS
                for match in self.LIBS_PATTERN.finditer(content):
                    libs_str = match.group(1)
                    libs = re.findall(r'-l(\w+)', libs_str)
                    for lib in libs:
                        if lib not in dependencies:
                            dependencies[lib] = {
                                'version': 'unknown',
                                'type': 'library',
                                'source': 'makefile-libs'
                            }
                
                # Extract pkg-config dependencies
                for match in self.PKGCONFIG_PATTERN.finditer(content):
                    packages = match.group(1).strip().split()
                    for pkg in packages:
                        pkg = pkg.strip('`\'"')
                        if pkg and not pkg.startswith('-'):
                            if pkg not in dependencies:
                                dependencies[pkg] = {
                                    'version': 'unknown',
                                    'type': 'library',
                                    'source': 'makefile-pkgconfig'
                                }
            
            except Exception as e:
                logger.warning(f"Failed to parse {makefile}: {e}")
        
        return dependencies


class PkgConfigParser:
    """Use pkg-config to get package information."""
    
    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Get package information using pkg-config."""
        try:
            # Check if package exists
            result = subprocess.run(
                ['pkg-config', '--exists', package_name],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            # Get version
            version_result = subprocess.run(
                ['pkg-config', '--modversion', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = version_result.stdout.strip() if version_result.returncode == 0 else 'unknown'
            
            # Get description
            desc_result = subprocess.run(
                ['pkg-config', '--variable=description', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            description = desc_result.stdout.strip() if desc_result.returncode == 0 else None
            
            return {
                'version': version,
                'description': description,
                'type': 'library',
                'source': 'pkg-config'
            }
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"pkg-config query failed for {package_name}: {e}")
            return None


class ConanParser:
    """Parse Conan dependency files."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse conanfile.txt or conanfile.py."""
        dependencies = {}
        
        # Try conanfile.txt
        conanfile_txt = self.project_path / 'conanfile.txt'
        if conanfile_txt.exists():
            dependencies.update(self._parse_conanfile_txt(conanfile_txt))
        
        # Try conanfile.py
        conanfile_py = self.project_path / 'conanfile.py'
        if conanfile_py.exists():
            dependencies.update(self._parse_conanfile_py(conanfile_py))
        
        return dependencies
    
    def _parse_conanfile_txt(self, conanfile: Path) -> Dict[str, Dict]:
        """Parse conanfile.txt format."""
        dependencies = {}
        
        try:
            with open(conanfile, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for [requires] section
            requires_match = re.search(r'\[requires\](.*?)(?:\[|$)', content, re.DOTALL)
            if requires_match:
                requires_section = requires_match.group(1)
                
                # Parse package specifications: package/version@user/channel
                for line in requires_section.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('/')
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1].split('@')[0]
                            
                            dependencies[name] = {
                                'version': version,
                                'type': 'library',
                                'source': 'conan'
                            }
        
        except Exception as e:
            logger.warning(f"Failed to parse {conanfile}: {e}")
        
        return dependencies
    
    def _parse_conanfile_py(self, conanfile: Path) -> Dict[str, Dict]:
        """Parse conanfile.py (basic extraction)."""
        dependencies = {}
        
        try:
            with open(conanfile, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for requires attribute
            requires_match = re.search(r'requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if requires_match:
                requires_str = requires_match.group(1)
                
                # Extract package strings
                packages = re.findall(r'["\']([^"\']+)["\']', requires_str)
                for pkg in packages:
                    parts = pkg.split('/')
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1].split('@')[0]
                        
                        dependencies[name] = {
                            'version': version,
                            'type': 'library',
                            'source': 'conan'
                        }
        
        except Exception as e:
            logger.warning(f"Failed to parse {conanfile}: {e}")
        
        return dependencies


class VcpkgParser:
    """Parse vcpkg manifest files."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse vcpkg.json manifest."""
        dependencies = {}
        
        vcpkg_json = self.project_path / 'vcpkg.json'
        if not vcpkg_json.exists():
            return dependencies
        
        try:
            import json
            
            with open(vcpkg_json, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Parse dependencies
            deps = manifest.get('dependencies', [])
            for dep in deps:
                if isinstance(dep, str):
                    # Simple dependency: "package-name"
                    dependencies[dep] = {
                        'version': 'unknown',
                        'type': 'library',
                        'source': 'vcpkg'
                    }
                elif isinstance(dep, dict):
                    # Complex dependency with version constraints
                    name = dep.get('name')
                    if name:
                        version = dep.get('version-string', dep.get('version', 'unknown'))
                        dependencies[name] = {
                            'version': version,
                            'type': 'library',
                            'source': 'vcpkg',
                            'features': dep.get('features', [])
                        }
        
        except Exception as e:
            logger.warning(f"Failed to parse {vcpkg_json}: {e}")
        
        return dependencies
