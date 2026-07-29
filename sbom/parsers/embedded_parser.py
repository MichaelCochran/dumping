"""Parser for embedded system build files and dependencies."""

import re
import json
import logging
import configparser
from pathlib import Path
from typing import Dict, Set, List, Optional

logger = logging.getLogger(__name__)


class PlatformIOParser:
    """Parse PlatformIO project files."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse platformio.ini for dependencies and platform info."""
        dependencies = {}
        
        platformio_ini = self.project_path / 'platformio.ini'
        if not platformio_ini.exists():
            return dependencies
        
        try:
            config = configparser.ConfigParser()
            config.read(platformio_ini, encoding='utf-8')
            
            for section in config.sections():
                if section.startswith('env:'):
                    # Extract platform
                    if config.has_option(section, 'platform'):
                        platform = config.get(section, 'platform')
                        platform_name = platform.split('@')[0]
                        platform_version = platform.split('@')[1] if '@' in platform else 'latest'
                        
                        dependencies[f'platform-{platform_name}'] = {
                            'version': platform_version,
                            'type': 'platform',
                            'source': 'platformio',
                            'description': f'PlatformIO platform: {platform_name}'
                        }
                    
                    # Extract framework
                    if config.has_option(section, 'framework'):
                        framework = config.get(section, 'framework')
                        dependencies[f'framework-{framework}'] = {
                            'version': 'unknown',
                            'type': 'framework',
                            'source': 'platformio',
                            'description': f'Framework: {framework}'
                        }
                    
                    # Extract board
                    if config.has_option(section, 'board'):
                        board = config.get(section, 'board')
                        dependencies[f'board-{board}'] = {
                            'version': 'unknown',
                            'type': 'board',
                            'source': 'platformio',
                            'description': f'Target board: {board}'
                        }
                    
                    # Extract library dependencies
                    if config.has_option(section, 'lib_deps'):
                        lib_deps = config.get(section, 'lib_deps')
                        # Handle multi-line lib_deps
                        libs = [lib.strip() for lib in lib_deps.split('\n') if lib.strip()]
                        
                        for lib in libs:
                            lib_info = self._parse_lib_dep(lib)
                            if lib_info:
                                dependencies[lib_info['name']] = lib_info
            
            logger.info(f"Found {len(dependencies)} PlatformIO dependencies")
        
        except Exception as e:
            logger.warning(f"Failed to parse {platformio_ini}: {e}")
        
        return dependencies
    
    def _parse_lib_dep(self, lib_spec: str) -> Optional[Dict]:
        """Parse a PlatformIO library dependency specification."""
        # Format examples:
        # - "bblanchon/ArduinoJson@^6.19.4"
        # - "https://github.com/user/repo.git#v1.0.0"
        # - "ArduinoJson"
        # - "ESP Async WebServer"
        
        # Git URL
        if lib_spec.startswith('http'):
            match = re.match(r'(.+?)(?:#(.+))?$', lib_spec)
            if match:
                url = match.group(1)
                version = match.group(2) if match.group(2) else 'latest'
                name = url.split('/')[-1].replace('.git', '')
                return {
                    'name': name,
                    'version': version,
                    'type': 'library',
                    'source': 'platformio-git',
                    'homepage': url
                }
        
        # Registry format: owner/name@version or just name (with possible spaces)
        # Check if it has owner/ prefix
        if '/' in lib_spec and not lib_spec.startswith('http'):
            match = re.match(r'([^/]+)/([^@]+)(?:@(.+))?', lib_spec)
            if match:
                owner = match.group(1)
                name = match.group(2).strip()
                version = match.group(3).strip() if match.group(3) else 'latest'
                
                return {
                    'name': name,
                    'version': version,
                    'type': 'library',
                    'source': 'platformio',
                    'supplier': owner
                }
        else:
            # Simple library name (possibly with version)
            if '@' in lib_spec:
                parts = lib_spec.split('@')
                name = parts[0].strip()
                version = parts[1].strip()
            else:
                name = lib_spec.strip()
                version = 'latest'
            
            return {
                'name': name,
                'version': version,
                'type': 'library',
                'source': 'platformio',
                'supplier': None
            }
        
        return None


class ESPIDFParser:
    """Parse ESP-IDF component and project files."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def parse(self) -> Dict[str, Dict]:
        """Parse ESP-IDF project for components and dependencies."""
        dependencies = {}
        
        # Check for ESP-IDF project
        if not self._is_espidf_project():
            return dependencies
        
        # Parse idf_component.yml
        dependencies.update(self._parse_component_yml())
        
        # Parse sdkconfig for enabled components
        dependencies.update(self._parse_sdkconfig())
        
        # Detect ESP-IDF components from CMakeLists.txt
        dependencies.update(self._parse_espidf_cmake())
        
        return dependencies
    
    def _is_espidf_project(self) -> bool:
        """Check if this is an ESP-IDF project."""
        indicators = [
            self.project_path / 'sdkconfig',
            self.project_path / 'sdkconfig.defaults',
            self.project_path / 'CMakeLists.txt'
        ]
        return any(f.exists() for f in indicators)
    
    def _parse_component_yml(self) -> Dict[str, Dict]:
        """Parse idf_component.yml for component dependencies."""
        dependencies = {}
        
        yml_files = list(self.project_path.rglob('idf_component.yml'))
        
        for yml_file in yml_files:
            try:
                # Simple YAML parsing (avoiding pyyaml dependency)
                with open(yml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract dependencies section
                dep_match = re.search(r'dependencies:\s*\n((?:  .+\n)*)', content)
                if dep_match:
                    dep_section = dep_match.group(1)
                    
                    # Parse component: version format
                    for match in re.finditer(r'  (\S+):\s*["\']?([^"\'\n]+)["\']?', dep_section):
                        comp_name = match.group(1)
                        version = match.group(2).strip()
                        
                        dependencies[comp_name] = {
                            'version': version,
                            'type': 'component',
                            'source': 'esp-idf'
                        }
            
            except Exception as e:
                logger.warning(f"Failed to parse {yml_file}: {e}")
        
        return dependencies
    
    def _parse_sdkconfig(self) -> Dict[str, Dict]:
        """Parse sdkconfig for enabled ESP-IDF components."""
        dependencies = {}
        
        sdkconfig = self.project_path / 'sdkconfig'
        if not sdkconfig.exists():
            return dependencies
        
        try:
            with open(sdkconfig, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Common ESP-IDF components and their config options
            component_configs = {
                'CONFIG_BT_ENABLED': ('esp-bluetooth', 'ESP-IDF Bluetooth stack'),
                'CONFIG_ESP_WIFI_ENABLED': ('esp-wifi', 'ESP-IDF WiFi stack'),
                'CONFIG_LWIP_': ('lwip', 'LwIP TCP/IP stack'),
                'CONFIG_FREERTOS_': ('freertos', 'FreeRTOS'),
                'CONFIG_MBEDTLS_': ('mbedtls', 'Mbed TLS'),
                'CONFIG_FATFS_': ('fatfs', 'FAT filesystem'),
                'CONFIG_SPIFFS_': ('spiffs', 'SPIFFS filesystem'),
                'CONFIG_HTTPD_': ('esp-httpd', 'ESP HTTP server'),
                'CONFIG_MQTT_': ('esp-mqtt', 'ESP MQTT client'),
            }
            
            for config_key, (comp_name, description) in component_configs.items():
                if config_key in content and comp_name not in dependencies:
                    dependencies[comp_name] = {
                        'version': 'esp-idf',
                        'type': 'component',
                        'source': 'esp-idf',
                        'description': description
                    }
        
        except Exception as e:
            logger.warning(f"Failed to parse {sdkconfig}: {e}")
        
        return dependencies
    
    def _parse_espidf_cmake(self) -> Dict[str, Dict]:
        """Parse ESP-IDF CMakeLists.txt for component requirements."""
        dependencies = {}
        
        cmake_files = list(self.project_path.rglob('CMakeLists.txt'))
        
        for cmake_file in cmake_files:
            try:
                with open(cmake_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for idf_component_register with REQUIRES
                requires_match = re.search(
                    r'idf_component_register\s*\([^)]*REQUIRES\s+([^)]+)\)',
                    content,
                    re.DOTALL
                )
                
                if requires_match:
                    components = requires_match.group(1).split()
                    for comp in components:
                        comp = comp.strip()
                        if comp and not comp.startswith('#'):
                            dependencies[comp] = {
                                'version': 'esp-idf',
                                'type': 'component',
                                'source': 'esp-idf-cmake'
                            }
            
            except Exception as e:
                logger.warning(f"Failed to parse {cmake_file}: {e}")
        
        return dependencies


class RTOSDetector:
    """Detect RTOS and embedded operating systems."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def detect(self) -> Dict[str, Dict]:
        """Detect RTOS and related components."""
        dependencies = {}
        
        # Detect FreeRTOS
        freertos_info = self._detect_freertos()
        if freertos_info:
            dependencies['FreeRTOS'] = freertos_info
        
        # Detect Zephyr
        zephyr_info = self._detect_zephyr()
        if zephyr_info:
            dependencies['Zephyr'] = zephyr_info
        
        # Detect ThreadX
        threadx_info = self._detect_threadx()
        if threadx_info:
            dependencies['ThreadX'] = threadx_info
        
        # Detect Mbed OS
        mbed_info = self._detect_mbed()
        if mbed_info:
            dependencies['Mbed-OS'] = mbed_info
        
        return dependencies
    
    def _detect_freertos(self) -> Optional[Dict]:
        """Detect FreeRTOS configuration and version."""
        # Look for FreeRTOSConfig.h
        config_files = list(self.project_path.rglob('FreeRTOSConfig.h'))
        if not config_files:
            return None
        
        version = 'unknown'
        
        # Try to extract version from FreeRTOS.h
        freertos_headers = list(self.project_path.rglob('FreeRTOS.h'))
        for header in freertos_headers:
            try:
                with open(header, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for version defines
                version_match = re.search(r'#define\s+tskKERNEL_VERSION_NUMBER\s+"V(\d+\.\d+\.\d+)"', content)
                if version_match:
                    version = version_match.group(1)
                    break
            except Exception:
                pass
        
        return {
            'version': version,
            'type': 'rtos',
            'source': 'source-detection',
            'description': 'FreeRTOS Real-Time Operating System',
            'homepage': 'https://www.freertos.org',
            'licenses': ['MIT']
        }
    
    def _detect_zephyr(self) -> Optional[Dict]:
        """Detect Zephyr RTOS."""
        # Look for Zephyr project files
        indicators = [
            self.project_path / 'prj.conf',
            self.project_path / 'zephyr' / 'module.yml',
            self.project_path / 'west.yml'
        ]
        
        if not any(f.exists() for f in indicators):
            return None
        
        version = 'unknown'
        
        # Try to parse west.yml for version
        west_yml = self.project_path / 'west.yml'
        if west_yml.exists():
            try:
                with open(west_yml, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                version_match = re.search(r'revision:\s*v?(\d+\.\d+\.\d+)', content)
                if version_match:
                    version = version_match.group(1)
            except Exception:
                pass
        
        return {
            'version': version,
            'type': 'rtos',
            'source': 'source-detection',
            'description': 'Zephyr RTOS',
            'homepage': 'https://www.zephyrproject.org',
            'licenses': ['Apache-2.0']
        }
    
    def _detect_threadx(self) -> Optional[Dict]:
        """Detect Azure ThreadX."""
        threadx_files = list(self.project_path.rglob('tx_api.h'))
        if not threadx_files:
            return None
        
        return {
            'version': 'unknown',
            'type': 'rtos',
            'source': 'source-detection',
            'description': 'Azure ThreadX RTOS',
            'homepage': 'https://github.com/azure-rtos/threadx',
            'licenses': ['MIT']
        }
    
    def _detect_mbed(self) -> Optional[Dict]:
        """Detect Mbed OS."""
        mbed_lib = self.project_path / 'mbed_lib.json'
        if not mbed_lib.exists():
            return None
        
        version = 'unknown'
        
        try:
            with open(mbed_lib, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version', 'unknown')
        except Exception:
            pass
        
        return {
            'version': version,
            'type': 'framework',
            'source': 'mbed',
            'description': 'Arm Mbed OS',
            'homepage': 'https://os.mbed.com',
            'licenses': ['Apache-2.0']
        }


class EmbeddedLibraryDetector:
    """Detect common embedded libraries and HAL/BSP."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def detect(self) -> Dict[str, Dict]:
        """Detect embedded-specific libraries."""
        dependencies = {}
        
        # Search for common embedded library patterns
        source_files = []
        for ext in ['*.c', '*.cpp', '*.h', '*.hpp']:
            source_files.extend(list(self.project_path.rglob(ext)))
        
        detected_libs = set()
        
        for source_file in source_files[:500]:  # Limit to avoid excessive scanning
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)  # Read first 10KB
                
                # Check for library signatures
                for lib_name, patterns in self._get_library_patterns().items():
                    if lib_name not in detected_libs:
                        for pattern in patterns:
                            if pattern in content:
                                detected_libs.add(lib_name)
                                break
            
            except Exception:
                continue
        
        # Convert detected libraries to dependency format
        library_metadata = self._get_library_metadata()
        for lib_name in detected_libs:
            if lib_name in library_metadata:
                dependencies[lib_name] = library_metadata[lib_name]
        
        return dependencies
    
    def _get_library_patterns(self) -> Dict[str, List[str]]:
        """Get detection patterns for embedded libraries."""
        return {
            'CMSIS': ['#include "cmsis', 'CMSIS/Include', 'arm_math.h'],
            'STM32_HAL': ['stm32', 'HAL_', '#include "stm32'],
            'Nordic_SDK': ['#include "nrf', 'nrf_', 'NRF_'],
            'lwIP': ['#include "lwip/', 'LWIP_', 'lwip_init'],
            'FatFs': ['#include "ff.h"', 'f_mount', 'FATFS'],
            'TinyUSB': ['#include "tusb', 'tud_', 'TinyUSB'],
            'LVGL': ['#include "lvgl', 'lv_', 'LV_'],
            'TinyML': ['#include "tensorflow/lite/micro', 'TfLite'],
            'Newlib': ['#include <newlib.h>', '_NEWLIB_VERSION'],
            'PicoSDK': ['#include "pico/', 'pico_'],
            'Arduino': ['#include <Arduino.h>', 'pinMode', 'digitalWrite'],
            'MCUboot': ['#include "mcuboot', 'boot_'],
            'LittleFS': ['#include "lfs.h"', 'lfs_mount'],
            'nanopb': ['#include "pb', 'pb_encode', 'pb_decode'],
            'Segger_RTT': ['#include "SEGGER_RTT', 'SEGGER_RTT_'],
        }
    
    def _get_library_metadata(self) -> Dict[str, Dict]:
        """Get metadata for embedded libraries."""
        return {
            'CMSIS': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Cortex Microcontroller Software Interface Standard',
                'homepage': 'https://www.arm.com/technologies/cmsis',
                'supplier': 'ARM'
            },
            'STM32_HAL': {
                'version': 'unknown',
                'type': 'hal',
                'source': 'source-detection',
                'description': 'STM32 Hardware Abstraction Layer',
                'supplier': 'STMicroelectronics'
            },
            'Nordic_SDK': {
                'version': 'unknown',
                'type': 'sdk',
                'source': 'source-detection',
                'description': 'Nordic Semiconductor SDK',
                'supplier': 'Nordic Semiconductor'
            },
            'lwIP': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Lightweight TCP/IP stack',
                'homepage': 'https://savannah.nongnu.org/projects/lwip/',
                'licenses': ['BSD-3-Clause']
            },
            'FatFs': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Generic FAT filesystem module',
                'homepage': 'http://elm-chan.org/fsw/ff/',
                'supplier': 'ChaN'
            },
            'TinyUSB': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Cross-platform USB stack for embedded systems',
                'homepage': 'https://github.com/hathach/tinyusb',
                'licenses': ['MIT']
            },
            'LVGL': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Light and Versatile Graphics Library',
                'homepage': 'https://lvgl.io',
                'licenses': ['MIT']
            },
            'TinyML': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'TensorFlow Lite for Microcontrollers',
                'homepage': 'https://www.tensorflow.org/lite/microcontrollers',
                'licenses': ['Apache-2.0']
            },
            'Newlib': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'C standard library for embedded systems',
                'licenses': ['BSD']
            },
            'PicoSDK': {
                'version': 'unknown',
                'type': 'sdk',
                'source': 'source-detection',
                'description': 'Raspberry Pi Pico SDK',
                'homepage': 'https://github.com/raspberrypi/pico-sdk',
                'licenses': ['BSD-3-Clause']
            },
            'Arduino': {
                'version': 'unknown',
                'type': 'framework',
                'source': 'source-detection',
                'description': 'Arduino framework',
                'homepage': 'https://www.arduino.cc',
                'licenses': ['LGPL-2.1']
            },
            'MCUboot': {
                'version': 'unknown',
                'type': 'bootloader',
                'source': 'source-detection',
                'description': 'Secure bootloader for microcontrollers',
                'homepage': 'https://www.mcuboot.com',
                'licenses': ['Apache-2.0']
            },
            'LittleFS': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Little fail-safe filesystem for embedded systems',
                'homepage': 'https://github.com/littlefs-project/littlefs',
                'licenses': ['BSD-3-Clause']
            },
            'nanopb': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'Protocol Buffers for embedded systems',
                'homepage': 'https://jpa.kapsi.fi/nanopb/',
                'licenses': ['Zlib']
            },
            'Segger_RTT': {
                'version': 'unknown',
                'type': 'library',
                'source': 'source-detection',
                'description': 'SEGGER Real-Time Transfer',
                'homepage': 'https://www.segger.com/products/debug-probes/j-link/technology/about-real-time-transfer/',
                'supplier': 'SEGGER'
            },
        }
