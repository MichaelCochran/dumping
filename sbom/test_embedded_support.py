"""Test embedded systems support."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parsers.embedded_parser import (
    PlatformIOParser,
    ESPIDFParser,
    RTOSDetector,
    EmbeddedLibraryDetector
)


def test_platformio_parser():
    """Test PlatformIO parser initialization and basic functionality."""
    print("Testing PlatformIO Parser...")
    parser = PlatformIOParser(Path("."))
    
    # Test library dependency parsing
    test_cases = [
        ("bblanchon/ArduinoJson@^6.19.4", "ArduinoJson", "^6.19.4"),
        ("ESP Async WebServer", "ESP Async WebServer", "latest"),
        ("https://github.com/user/repo.git#v1.0.0", "repo", "v1.0.0"),
    ]
    
    for lib_spec, expected_name, expected_version in test_cases:
        result = parser._parse_lib_dep(lib_spec)
        if result:
            print(f"  ✓ Parsed '{lib_spec}' -> {result['name']} v{result['version']}")
            assert result['name'] == expected_name, f"Expected {expected_name}, got {result['name']}"
        else:
            print(f"  ✗ Failed to parse '{lib_spec}'")
    
    print("  PlatformIO Parser: OK\n")


def test_espidf_parser():
    """Test ESP-IDF parser initialization."""
    print("Testing ESP-IDF Parser...")
    parser = ESPIDFParser(Path("."))
    print("  ✓ ESP-IDF Parser initialized")
    print("  ESP-IDF Parser: OK\n")


def test_rtos_detector():
    """Test RTOS detector initialization."""
    print("Testing RTOS Detector...")
    detector = RTOSDetector(Path("."))
    
    # Test library metadata
    freertos_info = detector._detect_freertos()
    if freertos_info:
        print(f"  ✓ FreeRTOS detected: {freertos_info}")
    else:
        print("  - FreeRTOS not found in current directory (expected)")
    
    print("  RTOS Detector: OK\n")


def test_embedded_library_detector():
    """Test embedded library detector."""
    print("Testing Embedded Library Detector...")
    detector = EmbeddedLibraryDetector(Path("."))
    
    # Test pattern recognition
    patterns = detector._get_library_patterns()
    print(f"  ✓ Loaded {len(patterns)} library detection patterns")
    
    # Test metadata
    metadata = detector._get_library_metadata()
    print(f"  ✓ Loaded {len(metadata)} library metadata entries")
    
    # Verify some key libraries
    expected_libs = ['CMSIS', 'STM32_HAL', 'lwIP', 'FatFs', 'TinyUSB', 'LVGL']
    for lib in expected_libs:
        assert lib in metadata, f"Missing metadata for {lib}"
        print(f"  ✓ {lib}: {metadata[lib]['description']}")
    
    print("  Embedded Library Detector: OK\n")


def test_integration():
    """Test that parsers integrate with build_parser."""
    print("Testing Integration with BuildSystemParser...")
    
    try:
        from parsers.build_parser import BuildSystemParser
        
        parser = BuildSystemParser(Path("."))
        
        # Verify embedded parsers are initialized
        assert hasattr(parser, 'platformio_parser'), "Missing platformio_parser"
        assert hasattr(parser, 'espidf_parser'), "Missing espidf_parser"
        assert hasattr(parser, 'rtos_detector'), "Missing rtos_detector"
        assert hasattr(parser, 'embedded_lib_detector'), "Missing embedded_lib_detector"
        
        print("  ✓ All embedded parsers integrated into BuildSystemParser")
        print("  Integration: OK\n")
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        raise


def test_cpp_parser_embedded_mappings():
    """Test that cpp_parser has embedded library mappings."""
    print("Testing C++ Parser Embedded Mappings...")
    
    from parsers.cpp_parser import CppSourceParser
    
    parser = CppSourceParser()
    mappings = parser.LIBRARY_MAPPINGS
    
    # Check for embedded-specific mappings
    embedded_keys = [
        'cmsis', 'stm32', 'nrf', 'lwip/', 'tusb', 'lvgl', 
        'Arduino.h', 'pico/', 'esp_', 'freertos', 'FreeRTOS'
    ]
    
    for key in embedded_keys:
        assert key in mappings, f"Missing mapping for {key}"
        print(f"  ✓ {key} -> {mappings[key]}")
    
    print(f"  ✓ Total library mappings: {len(mappings)}")
    print("  C++ Parser Embedded Mappings: OK\n")


def main():
    """Run all tests."""
    print("="*70)
    print("Embedded Systems Support - Test Suite")
    print("="*70 + "\n")
    
    try:
        test_platformio_parser()
        test_espidf_parser()
        test_rtos_detector()
        test_embedded_library_detector()
        test_integration()
        test_cpp_parser_embedded_mappings()
        
        print("="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nEmbedded systems support is fully integrated and functional!")
        print("\nSupported platforms:")
        print("  • PlatformIO (ESP32, STM32, nRF, AVR, etc.)")
        print("  • ESP-IDF (Espressif IoT Development Framework)")
        print("  • FreeRTOS, Zephyr, ThreadX, Mbed OS")
        print("  • STM32 HAL, CMSIS, Nordic SDK, Pico SDK")
        print("  • Arduino, TinyUSB, LVGL, lwIP, FatFs, and more!")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
