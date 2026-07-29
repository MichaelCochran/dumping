"""Advanced dependency analyzer for version detection and metadata enrichment."""

import re
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Set, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
import time

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyze dependencies and enrich with version and metadata information."""
    
    # Known library metadata
    LIBRARY_METADATA = {
        'boost': {
            'homepage': 'https://www.boost.org',
            'description': 'Boost C++ Libraries',
            'supplier': 'Boost.org',
            'common_licenses': ['BSL-1.0']
        },
        'opencv': {
            'homepage': 'https://opencv.org',
            'description': 'Open Source Computer Vision Library',
            'supplier': 'OpenCV Team',
            'common_licenses': ['Apache-2.0']
        },
        'qt': {
            'homepage': 'https://www.qt.io',
            'description': 'Qt Framework',
            'supplier': 'The Qt Company',
            'common_licenses': ['LGPL-3.0', 'GPL-3.0']
        },
        'eigen': {
            'homepage': 'https://eigen.tuxfamily.org',
            'description': 'C++ template library for linear algebra',
            'supplier': 'Eigen Team',
            'common_licenses': ['MPL-2.0']
        },
        'openssl': {
            'homepage': 'https://www.openssl.org',
            'description': 'Cryptography and SSL/TLS Toolkit',
            'supplier': 'OpenSSL Software Foundation',
            'common_licenses': ['Apache-2.0']
        },
        'curl': {
            'homepage': 'https://curl.se',
            'description': 'Command line tool and library for transferring data',
            'supplier': 'curl',
            'common_licenses': ['curl']
        },
        'zlib': {
            'homepage': 'https://www.zlib.net',
            'description': 'Compression library',
            'supplier': 'zlib',
            'common_licenses': ['Zlib']
        },
        'gtest': {
            'homepage': 'https://github.com/google/googletest',
            'description': 'Google Testing Framework',
            'supplier': 'Google',
            'common_licenses': ['BSD-3-Clause']
        },
        'protobuf': {
            'homepage': 'https://protobuf.dev',
            'description': 'Protocol Buffers',
            'supplier': 'Google',
            'common_licenses': ['BSD-3-Clause']
        },
        'grpc': {
            'homepage': 'https://grpc.io',
            'description': 'High performance RPC framework',
            'supplier': 'Google',
            'common_licenses': ['Apache-2.0']
        },
        'fmt': {
            'homepage': 'https://fmt.dev',
            'description': 'Modern formatting library',
            'supplier': 'Victor Zverovich',
            'common_licenses': ['MIT']
        },
        'spdlog': {
            'homepage': 'https://github.com/gabime/spdlog',
            'description': 'Fast C++ logging library',
            'supplier': 'Gabi Melman',
            'common_licenses': ['MIT']
        },
        'nlohmann-json': {
            'homepage': 'https://json.nlohmann.me',
            'description': 'JSON for Modern C++',
            'supplier': 'Niels Lohmann',
            'common_licenses': ['MIT']
        },
        'sqlite': {
            'homepage': 'https://www.sqlite.org',
            'description': 'Embedded SQL database engine',
            'supplier': 'SQLite',
            'common_licenses': ['Public Domain']
        },
    }
    
    def __init__(self):
        self.version_cache: Dict[str, str] = {}
    
    def analyze(self, include_map: Dict[Path, Dict], 
                project_path: Path,
                system_include_paths: List[str] = None) -> Dict[str, Dict]:
        """
        Analyze dependencies from include map and enrich with metadata.
        
        Args:
            include_map: Mapping of source files to their parsed information
            project_path: Root path of the project
            system_include_paths: Additional system include paths to search
        
        Returns:
            Dictionary of enriched dependency information
        """
        dependencies = {}
        
        # Collect all libraries mentioned in source files
        all_libraries = set()
        for file_info in include_map.values():
            if isinstance(file_info, dict):
                all_libraries.update(file_info.get('libraries', set()))
        
        logger.info(f"Analyzing {len(all_libraries)} libraries")
        
        # Enrich each library with metadata
        for lib_name in all_libraries:
            dep_info = self._analyze_library(
                lib_name, 
                project_path,
                system_include_paths or []
            )
            if dep_info:
                dependencies[lib_name] = dep_info
        
        return dependencies
    
    def _analyze_library(self, lib_name: str, project_path: Path,
                        system_include_paths: List[str]) -> Optional[Dict]:
        """Analyze a single library and gather metadata."""
        info = {
            'version': 'unknown',
            'type': 'library',
            'file_paths': set()
        }
        
        # Add known metadata
        if lib_name.lower() in self.LIBRARY_METADATA:
            metadata = self.LIBRARY_METADATA[lib_name.lower()]
            info.update({
                'homepage': metadata.get('homepage'),
                'description': metadata.get('description'),
                'supplier': metadata.get('supplier'),
                'licenses': metadata.get('common_licenses', [])
            })
        
        # Try to detect version
        version = self._detect_version(lib_name, project_path, system_include_paths)
        if version and version != 'unknown':
            info['version'] = version
        
        # Try to find library files
        lib_files = self._find_library_files(lib_name, project_path)
        if lib_files:
            info['file_paths'] = lib_files
        
        # Generate package URL (purl) if possible
        purl = self._generate_purl(lib_name, info.get('version', 'unknown'))
        if purl:
            info['purl'] = purl
        
        return info
    
    def _detect_version(self, lib_name: str, project_path: Path,
                       system_include_paths: List[str]) -> str:
        """Try multiple methods to detect library version."""
        # Check cache first
        if lib_name in self.version_cache:
            return self.version_cache[lib_name]
        
        version = 'unknown'
        
        # Method 1: Check version header files
        version_from_header = self._check_version_header(
            lib_name, project_path, system_include_paths
        )
        if version_from_header:
            version = version_from_header
        
        # Method 2: Try pkg-config
        if version == 'unknown':
            version_from_pkg = self._check_pkgconfig_version(lib_name)
            if version_from_pkg:
                version = version_from_pkg
        
        # Method 3: Check CMake package config
        if version == 'unknown':
            version_from_cmake = self._check_cmake_version(lib_name, project_path)
            if version_from_cmake:
                version = version_from_cmake
        
        # Method 4: Check installed packages (system-specific)
        if version == 'unknown':
            version_from_system = self._check_system_package(lib_name)
            if version_from_system:
                version = version_from_system
        
        self.version_cache[lib_name] = version
        return version
    
    def _check_version_header(self, lib_name: str, project_path: Path,
                             system_include_paths: List[str]) -> Optional[str]:
        """Look for version information in header files."""
        # Common version header patterns
        version_headers = [
            f'{lib_name}/version.h',
            f'{lib_name}/version.hpp',
            f'{lib_name}/config.h',
            f'{lib_name.upper()}_VERSION.h',
            f'{lib_name}/core/version.hpp',
        ]
        
        # Common version macro patterns
        version_patterns = [
            re.compile(rf'{lib_name.upper()}_VERSION\s+"([^"]+)"', re.IGNORECASE),
            re.compile(rf'{lib_name.upper()}_VERSION_STRING\s+"([^"]+)"', re.IGNORECASE),
            re.compile(rf'#define\s+VERSION\s+"([^"]+)"'),
            re.compile(rf'{lib_name.upper()}_MAJOR_VERSION\s+(\d+).*{lib_name.upper()}_MINOR_VERSION\s+(\d+)', re.IGNORECASE | re.DOTALL),
        ]
        
        # Search in project includes
        include_dirs = [project_path / 'include', project_path / 'includes']
        include_dirs.extend([Path(p) for p in system_include_paths])
        
        for inc_dir in include_dirs:
            if not inc_dir.exists():
                continue
            
            for version_header in version_headers:
                header_path = inc_dir / version_header
                if header_path.exists():
                    try:
                        content = header_path.read_text(encoding='utf-8', errors='ignore')
                        
                        for pattern in version_patterns:
                            match = pattern.search(content)
                            if match:
                                if len(match.groups()) == 1:
                                    return match.group(1)
                                elif len(match.groups()) > 1:
                                    return '.'.join(match.groups())
                    except Exception as e:
                        logger.debug(f"Failed to read {header_path}: {e}")
        
        return None
    
    def _check_pkgconfig_version(self, lib_name: str) -> Optional[str]:
        """Try to get version from pkg-config."""
        try:
            result = subprocess.run(
                ['pkg-config', '--modversion', lib_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                if version:
                    return version
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"pkg-config failed for {lib_name}: {e}")
        
        return None
    
    def _check_cmake_version(self, lib_name: str, project_path: Path) -> Optional[str]:
        """Look for CMake package configuration files."""
        # Search for CMake config files
        cmake_patterns = [
            f'{lib_name}Config.cmake',
            f'{lib_name}-config.cmake',
            f'{lib_name.capitalize()}Config.cmake',
        ]
        
        search_paths = [
            project_path / 'cmake',
            project_path / 'CMake',
            project_path / 'lib' / 'cmake' / lib_name,
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            for pattern in cmake_patterns:
                cmake_file = search_path / pattern
                if cmake_file.exists():
                    try:
                        content = cmake_file.read_text(encoding='utf-8', errors='ignore')
                        
                        # Look for version in CMake config
                        version_match = re.search(
                            rf'set\s*\(\s*{lib_name.upper()}_VERSION\s+"([^"]+)"',
                            content,
                            re.IGNORECASE
                        )
                        if version_match:
                            return version_match.group(1)
                    except Exception as e:
                        logger.debug(f"Failed to read {cmake_file}: {e}")
        
        return None
    
    def _check_system_package(self, lib_name: str) -> Optional[str]:
        """Try to get version from system package manager."""
        # Try dpkg (Debian/Ubuntu)
        try:
            result = subprocess.run(
                ['dpkg', '-l', f'*{lib_name}*'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if lib_name in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        # Try rpm (RedHat/Fedora)
        try:
            result = subprocess.run(
                ['rpm', '-q', lib_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_match = re.search(r'-([0-9.]+)', result.stdout)
                if version_match:
                    return version_match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return None
    
    def _find_library_files(self, lib_name: str, project_path: Path) -> Set[Path]:
        """Find library files (.so, .a, .dll) for the library."""
        lib_files = set()
        
        # Common library file patterns
        patterns = [
            f'lib{lib_name}.so*',
            f'lib{lib_name}.a',
            f'{lib_name}.dll',
            f'{lib_name}.lib',
        ]
        
        # Search in common library directories
        search_dirs = [
            project_path / 'lib',
            project_path / 'libs',
            project_path / 'build' / 'lib',
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in patterns:
                    lib_files.update(search_dir.glob(pattern))
        
        return lib_files
    
    def _generate_purl(self, lib_name: str, version: str) -> Optional[str]:
        """Generate a package URL (purl) for the library."""
        # Basic purl generation for C++ libraries
        # Format: pkg:type/name@version
        
        # Try to determine the package type
        pkg_type = 'generic'
        
        # Check if it's a common package manager
        if lib_name in ['boost', 'qt', 'opencv']:
            pkg_type = 'conan'  # Could also be vcpkg
        
        if version and version != 'unknown':
            return f'pkg:{pkg_type}/{lib_name}@{version}'
        else:
            return f'pkg:{pkg_type}/{lib_name}'
