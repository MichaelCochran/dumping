# Embedded Systems Support

This document provides detailed information about the embedded systems support added to the C++ SBOM Generator.

## Overview

The SBOM generator now has comprehensive support for embedded and IoT C/C++ projects, including:
- **PlatformIO** projects
- **ESP-IDF** (Espressif IoT Development Framework) projects
- **RTOS** detection (FreeRTOS, Zephyr, ThreadX, Mbed OS)
- **Hardware Abstraction Layers** (STM32 HAL, CMSIS, Nordic SDK, etc.)
- **Embedded libraries** (lwIP, FatFs, TinyUSB, LVGL, etc.)

## Implementation

### New Files

**`parsers/embedded_parser.py`** - Contains four main parsers:

1. **PlatformIOParser**
   - Parses `platformio.ini` files
   - Extracts platforms, frameworks, boards, and library dependencies
   - Handles multiple dependency formats (owner/name@version, URLs, simple names)

2. **ESPIDFParser**
   - Detects ESP-IDF projects
   - Parses `idf_component.yml` for component dependencies
   - Scans `sdkconfig` for enabled components (WiFi, Bluetooth, lwIP, etc.)
   - Extracts component requirements from ESP-IDF CMakeLists.txt

3. **RTOSDetector**
   - Detects FreeRTOS (with version extraction from headers)
   - Detects Zephyr RTOS (via prj.conf, west.yml)
   - Detects Azure ThreadX (via tx_api.h)
   - Detects Mbed OS (via mbed_lib.json)

4. **EmbeddedLibraryDetector**
   - Scans source files for embedded library patterns
   - Detects 15+ common embedded libraries
   - Includes metadata (homepage, licenses, suppliers, descriptions)

### Modified Files

**`parsers/build_parser.py`**
- Integrated all four embedded parsers into `BuildSystemParser`
- Added logging for embedded component detection

**`parsers/cpp_parser.py`**
- Added 22 new library mappings for embedded systems:
  - CMSIS, STM32 HAL, Nordic SDK
  - lwIP, FatFs, TinyUSB, LVGL
  - Arduino, PicoSDK, ESP-IDF
  - FreeRTOS, ThreadX, Mbed OS
  - MCUboot, LittleFS, nanopb, SEGGER RTT

**`README.md`**
- Added "Embedded Systems Support" section
- Updated features list
- Added embedded library examples
- Updated project structure
- Added PlatformIO and ESP-IDF usage examples

## Supported Embedded Libraries

### RTOS
- **FreeRTOS** - Version detection, MIT license
- **Zephyr** - Apache-2.0 license
- **Azure ThreadX** - MIT license
- **Mbed OS** - Apache-2.0 license

### Hardware Abstraction
- **CMSIS** - ARM Cortex Microcontroller Software Interface Standard
- **STM32 HAL** - STMicroelectronics Hardware Abstraction Layer
- **Nordic SDK** - Nordic Semiconductor SDK for nRF series
- **Raspberry Pi Pico SDK** - BSD-3-Clause license

### Networking
- **lwIP** - Lightweight TCP/IP stack, BSD-3-Clause
- **ESP-IDF WiFi/Bluetooth** - Espressif components

### Filesystems
- **FatFs** - Generic FAT filesystem module
- **LittleFS** - Fail-safe filesystem for embedded, BSD-3-Clause
- **SPIFFS** - ESP-IDF component

### USB
- **TinyUSB** - Cross-platform USB stack, MIT license

### Graphics
- **LVGL** - Light and Versatile Graphics Library, MIT license

### Machine Learning
- **TensorFlow Lite Micro** - ML for microcontrollers, Apache-2.0

### Bootloaders
- **MCUboot** - Secure bootloader for MCUs, Apache-2.0

### Protocols
- **nanopb** - Protocol Buffers for embedded, Zlib license
- **MQTT** - ESP-IDF component

### Debugging
- **SEGGER RTT** - Real-Time Transfer for debugging

### Frameworks
- **Arduino** - LGPL-2.1 license
- **PlatformIO** - Universal IoT platform
- **ESP-IDF** - Espressif IoT Development Framework

## Usage Examples

### PlatformIO ESP32 Project

```powershell
python sbom_generator.py /path/to/platformio-project -o sbom.json -f spdx
```

**Sample platformio.ini:**
```ini
[env:esp32dev]
platform = espressif32@6.3.0
board = esp32dev
framework = arduino
lib_deps = 
    bblanchon/ArduinoJson@^6.19.4
    ESP Async WebServer
    lvgl/lvgl@^8.3.0
```

**Detected dependencies:**
- Platform: espressif32 v6.3.0
- Framework: arduino
- Board: esp32dev
- Libraries: ArduinoJson, ESP Async WebServer, LVGL

### ESP-IDF Project

```powershell
python sbom_generator.py /path/to/espidf-project -o sbom.json -f cyclonedx
```

**Detected dependencies:**
- ESP-IDF components (from CMakeLists.txt)
- Enabled features from sdkconfig (WiFi, Bluetooth, lwIP, mbedTLS)
- Component dependencies from idf_component.yml

### STM32 FreeRTOS Project

```powershell
python sbom_generator.py /path/to/stm32-project -o sbom.json -f spdx
```

**Detected dependencies:**
- STM32 HAL (from #include "stm32xxx.h")
- FreeRTOS (from FreeRTOSConfig.h, with version)
- CMSIS (from #include "cmsis" headers)
- Middleware: FatFs, TinyUSB, etc. (if present)

### Zephyr RTOS Project

```powershell
python sbom_generator.py /path/to/zephyr-project -o sbom.json -f spdx
```

**Detected dependencies:**
- Zephyr RTOS (from prj.conf or west.yml)
- Zephyr modules and libraries

## Testing

A comprehensive test suite is provided in `test_embedded_support.py`:

```powershell
python test_embedded_support.py
```

**Tests include:**
- PlatformIO library dependency parsing
- ESP-IDF parser initialization
- RTOS detection
- Embedded library pattern matching
- Integration with BuildSystemParser
- C++ parser embedded library mappings

## Detection Strategy

The embedded parsers use multiple strategies:

1. **File-based detection**
   - Look for specific files (platformio.ini, sdkconfig, FreeRTOSConfig.h, etc.)
   - Parse configuration and manifest files

2. **Source code scanning**
   - Pattern matching for #include directives
   - Detection of library-specific symbols and functions
   - Limited scanning (first 500 files, 10KB per file) for performance

3. **Build system integration**
   - Parse CMakeLists.txt for ESP-IDF component requirements
   - Extract dependencies from build configurations

4. **Metadata enrichment**
   - Built-in metadata for 15+ embedded libraries
   - Includes homepage, licenses, suppliers, descriptions

## Performance Considerations

- **File scanning limit**: First 500 source files (configurable)
- **Content limit**: First 10KB per file for pattern matching
- **Caching**: Include parsing results are cached
- **Parallel detection**: All parsers run concurrently

Typical performance for embedded project:
- **Small project** (50-100 files): ~2-3 seconds
- **Medium project** (500 files): ~5-8 seconds
- **Large project** (1000+ files): ~10-15 seconds

## Limitations

Current limitations:
- **Keil/IAR projects**: Not yet supported (proprietary formats)
- **MPLAB X**: Not yet supported
- **Arduino IDE projects**: Partial support (via PlatformIO or source detection)
- **Transitive dependencies**: Not resolved (shows direct dependencies only)
- **Version detection**: Best-effort, may return "unknown" for some libraries

## Future Enhancements

Potential additions:
- [ ] Keil µVision project support (.uvprojx)
- [ ] IAR Embedded Workbench support (.ewp)
- [ ] MPLAB X project support
- [ ] West manifest parsing for Zephyr
- [ ] Transitive dependency resolution
- [ ] Board pinout and configuration detection
- [ ] Toolchain and compiler detection
- [ ] Flash/RAM usage analysis

## Contributing

To add support for a new embedded library:

1. **Add detection pattern** in `EmbeddedLibraryDetector._get_library_patterns()`:
   ```python
   'MyLib': ['#include "mylib', 'MYLIB_', 'mylib_init']
   ```

2. **Add metadata** in `EmbeddedLibraryDetector._get_library_metadata()`:
   ```python
   'MyLib': {
       'version': 'unknown',
       'type': 'library',
       'source': 'source-detection',
       'description': 'My Library Description',
       'homepage': 'https://mylib.org',
       'licenses': ['MIT']
   }
   ```

3. **Add library mapping** in `parsers/cpp_parser.py`:
   ```python
   'mylib/': 'MyLib',
   'mylib.h': 'MyLib',
   ```

## License Information

The SBOM generator includes license information for detected libraries where known. Always verify licenses in your actual project dependencies.

## Support

For issues or questions about embedded systems support:
1. Check verbose output with `-v` flag
2. Review the parser logs
3. Verify your project structure matches expected formats
4. Test with the provided test suite

---

**Embedded systems support added**: 2026-07-29  
**Version**: 1.0.0 with embedded support
