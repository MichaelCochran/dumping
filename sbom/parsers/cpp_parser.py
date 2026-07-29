"""Parser for C++ source files to extract includes and dependencies."""

import re
import logging
from pathlib import Path
from typing import Set, List, Dict, Optional

logger = logging.getLogger(__name__)


class CppSourceParser:
    """Parse C++ source files for includes and dependencies."""
    
    # Patterns for different include styles
    INCLUDE_PATTERN = re.compile(
        r'^\s*#\s*include\s+[<"]([^>"]+)[>"]',
        re.MULTILINE
    )
    
    # Patterns for detecting library usage
    NAMESPACE_PATTERN = re.compile(r'using\s+namespace\s+(\w+)')
    USING_PATTERN = re.compile(r'using\s+([\w:]+)')
    
    # Common library prefixes and their library names
    LIBRARY_MAPPINGS = {
        'boost/': 'boost',
        'Qt': 'qt',
        'opencv2/': 'opencv',
        'eigen3/': 'eigen',
        'pcl/': 'pcl',
        'ros/': 'ros',
        'gtest/': 'gtest',
        'gmock/': 'gmock',
        'protobuf/': 'protobuf',
        'grpc/': 'grpc',
        'fmt/': 'fmt',
        'spdlog/': 'spdlog',
        'json/': 'jsoncpp',
        'nlohmann/': 'nlohmann-json',
        'curl/': 'curl',
        'openssl/': 'openssl',
        'zlib': 'zlib',
        'png': 'libpng',
        'jpeg': 'libjpeg',
        'tiff': 'libtiff',
        'sqlite3': 'sqlite',
        'mysql/': 'mysql',
        'pqxx/': 'postgresql',
        'zmq': 'zeromq',
        'msgpack': 'msgpack',
        'yaml-cpp/': 'yaml-cpp',
        'pugixml': 'pugixml',
        'tinyxml': 'tinyxml',
        'GL/': 'opengl',
        'GLFW/': 'glfw',
        'SDL': 'sdl',
        'vulkan/': 'vulkan',
        'thread': 'std-threads',
        'filesystem': 'std-filesystem',
        'regex': 'std-regex',
        'cmsis': 'CMSIS',
        'arm_math': 'CMSIS',
        'stm32': 'STM32_HAL',
        'nrf': 'Nordic_SDK',
        'lwip/': 'lwIP',
        'ff.h': 'FatFs',
        'fatfs': 'FatFs',
        'tusb': 'TinyUSB',
        'lvgl': 'LVGL',
        'tensorflow/lite/micro': 'TinyML',
        'Arduino.h': 'Arduino',
        'pico/': 'PicoSDK',
        'esp_': 'ESP-IDF',
        'freertos': 'FreeRTOS',
        'FreeRTOS': 'FreeRTOS',
        'tx_api': 'ThreadX',
        'mbed': 'Mbed-OS',
        'lfs.h': 'LittleFS',
        'pb_encode': 'nanopb',
        'pb_decode': 'nanopb',
        'SEGGER_RTT': 'Segger_RTT',
        'mcuboot': 'MCUboot',
    }
    
    def __init__(self):
        self.include_cache: Dict[Path, Set[str]] = {}
    
    def parse_file(self, file_path: Path) -> Dict[str, any]:
        """
        Parse a C++ source file and extract dependency information.
        
        Returns:
            Dictionary containing includes, namespaces, and inferred libraries
        """
        if file_path in self.include_cache:
            return self.include_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {}
        
        # Remove comments to avoid false positives
        content = self._remove_comments(content)
        
        # Extract includes
        includes = set()
        for match in self.INCLUDE_PATTERN.finditer(content):
            includes.add(match.group(1))
        
        # Extract namespaces
        namespaces = set()
        for match in self.NAMESPACE_PATTERN.finditer(content):
            namespaces.add(match.group(1))
        
        for match in self.USING_PATTERN.finditer(content):
            using_clause = match.group(1)
            if '::' in using_clause:
                namespace = using_clause.split('::')[0]
                namespaces.add(namespace)
        
        # Infer libraries from includes
        libraries = self._infer_libraries(includes)
        
        result = {
            'includes': includes,
            'namespaces': namespaces,
            'libraries': libraries,
            'system_includes': self._classify_includes(includes)
        }
        
        self.include_cache[file_path] = result
        return result
    
    def _remove_comments(self, content: str) -> str:
        """Remove C++ comments (both // and /* */ styles)."""
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _infer_libraries(self, includes: Set[str]) -> Set[str]:
        """Infer library names from include paths."""
        libraries = set()
        
        for include in includes:
            # Check against known library mappings
            for prefix, lib_name in self.LIBRARY_MAPPINGS.items():
                if include.startswith(prefix) or prefix in include:
                    libraries.add(lib_name)
                    break
            
            # Extract library name from first path component
            parts = include.split('/')
            if len(parts) > 1 and parts[0] not in ['std', 'bits']:
                # Potential library name
                potential_lib = parts[0]
                if not potential_lib.endswith('.h') and not potential_lib.endswith('.hpp'):
                    libraries.add(potential_lib)
        
        return libraries
    
    def _classify_includes(self, includes: Set[str]) -> Dict[str, List[str]]:
        """Classify includes into system vs local vs third-party."""
        classification = {
            'system': [],
            'local': [],
            'third_party': []
        }
        
        # Standard library headers
        std_headers = {
            'iostream', 'fstream', 'sstream', 'string', 'vector', 'map',
            'set', 'list', 'deque', 'queue', 'stack', 'algorithm',
            'functional', 'memory', 'utility', 'tuple', 'array',
            'unordered_map', 'unordered_set', 'thread', 'mutex',
            'condition_variable', 'atomic', 'chrono', 'regex',
            'filesystem', 'optional', 'variant', 'any', 'cstdio',
            'cstdlib', 'cstring', 'cmath', 'ctime', 'cassert',
            'stdexcept', 'exception', 'limits', 'numeric', 'iterator'
        }
        
        for include in includes:
            base_name = Path(include).stem
            
            # Check if it's a standard library header
            if base_name in std_headers or include.startswith('c') and len(include) < 15:
                classification['system'].append(include)
            # Check if it's a local include (no directory separator or starts with .)
            elif '/' not in include and '\\' not in include:
                classification['local'].append(include)
            else:
                classification['third_party'].append(include)
        
        return classification
    
    def analyze_dependencies(self, file_paths: List[Path]) -> Dict[str, Dict]:
        """
        Analyze multiple files and aggregate dependency information.
        
        Returns:
            Dictionary mapping library names to their usage information
        """
        all_libraries = {}
        
        for file_path in file_paths:
            try:
                parsed = self.parse_file(file_path)
                
                for lib in parsed.get('libraries', set()):
                    if lib not in all_libraries:
                        all_libraries[lib] = {
                            'name': lib,
                            'used_in_files': set(),
                            'includes': set(),
                            'namespaces': set()
                        }
                    
                    all_libraries[lib]['used_in_files'].add(file_path)
                    all_libraries[lib]['includes'].update(
                        inc for inc in parsed.get('includes', set())
                        if any(prefix in inc for prefix, name in self.LIBRARY_MAPPINGS.items() if name == lib)
                    )
                    
                    # Add relevant namespaces
                    for ns in parsed.get('namespaces', set()):
                        if lib.lower() in ns.lower() or ns.lower() in lib.lower():
                            all_libraries[lib]['namespaces'].add(ns)
            
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Convert sets to lists for JSON serialization
        for lib_info in all_libraries.values():
            lib_info['used_in_files'] = [str(p) for p in lib_info['used_in_files']]
            lib_info['includes'] = list(lib_info['includes'])
            lib_info['namespaces'] = list(lib_info['namespaces'])
        
        return all_libraries
