# Quick Start Guide

Get started with the C++ SBOM Generator in minutes!

## 1. Installation

```powershell
# Navigate to the tool directory
cd c:\Users\e480545\sbom

# Install Python dependencies
pip install -r requirements.txt
```

## 2. Test the Tool

Try the tool on the included test project:

```powershell
python sbom_generator.py test_project -o test-sbom.json -f spdx -v
```

You should see output like:

```
INFO - Scanning project at test_project
INFO - Found 1 source files
INFO - Analyzing 3 libraries
...
================================================================================
SBOM Summary for test_project
================================================================================
Total components: 4
...
```

## 3. Use on Your Project

### Basic Command

```powershell
python sbom_generator.py C:\path\to\your\cpp\project -o sbom.json -f spdx
```

### With Configuration

1. Copy the example config:
   ```powershell
   copy config.example.json config.json
   ```

2. Edit `config.json` with your project details:
   ```json
   {
     "project_name": "YourProject",
     "project_version": "1.0.0"
   }
   ```

3. Run with config:
   ```powershell
   python sbom_generator.py C:\path\to\project -o sbom.json -c config.json
   ```

## 4. View the SBOM

The generated SBOM will contain:
- All detected dependencies
- Version information
- License data
- File checksums
- Package relationships

Open the JSON file in any text editor or JSON viewer.

## 5. Different Output Formats

### SPDX (Compliance focused)
```powershell
python sbom_generator.py your_project -o sbom-spdx.json -f spdx
```

### CycloneDX (Security focused)
```powershell
python sbom_generator.py your_project -o sbom-cdx.json -f cyclonedx
```

### Raw JSON (All data)
```powershell
python sbom_generator.py your_project -o sbom-raw.json -f json
```

## 6. Advanced Options

### Specify Project Metadata
```powershell
python sbom_generator.py your_project -o sbom.json ^
  --project-name "MyApp" ^
  --project-version "2.0.0"
```

### Limit Scan Depth
```powershell
python sbom_generator.py your_project -o sbom.json --max-depth 10
```

### Verbose Output
```powershell
python sbom_generator.py your_project -o sbom.json -v
```

## Common Use Cases

### 1. Compliance Reporting
Generate SPDX for license compliance:
```powershell
python sbom_generator.py . -o compliance-sbom.json -f spdx
```

### 2. Security Auditing
Generate CycloneDX for vulnerability tracking:
```powershell
python sbom_generator.py . -o security-sbom.json -f cyclonedx
```

### 3. Build Pipeline Integration
Add to your build script:
```powershell
# build.ps1
cmake --build build
python sbom\sbom_generator.py . -o build\sbom.json -f spdx
```

### 4. Release Documentation
Include SBOM with releases:
```powershell
python sbom_generator.py . -o release\sbom-v1.0.0.json -f cyclonedx ^
  --project-version "1.0.0"
```

## Troubleshooting

### Issue: No dependencies found
**Solution**: Ensure you have CMakeLists.txt, Makefile, or other build files in your project.

### Issue: Versions showing as "unknown"
**Solution**: 
- Check that header files with version info exist
- Install pkg-config if on Linux
- Add version info manually in config.json

### Issue: Tool runs slowly
**Solution**: Use `--max-depth` to limit directory traversal:
```powershell
python sbom_generator.py large_project -o sbom.json --max-depth 5
```

## Next Steps

1. **Customize**: Edit `config.json` for your project specifics
2. **Integrate**: Add to CI/CD pipeline
3. **Extend**: Modify parsers for custom build systems
4. **Automate**: Create scripts for regular SBOM generation

## Getting Help

1. Run with `-v` for verbose logging
2. Check the main README.md for detailed documentation
3. Review example_usage.py for programmatic usage
4. Examine the source code in parsers/ and exporters/

## Example Workflow

Complete workflow for a new C++ project:

```powershell
# 1. Navigate to project
cd C:\projects\my-cpp-app

# 2. Generate SBOM
python C:\Users\e480545\sbom\sbom_generator.py . ^
  -o sbom.json ^
  -f spdx ^
  --project-name "MyCppApp" ^
  --project-version "1.0.0" ^
  -v

# 3. Review the output
type sbom.json

# 4. Store with project
git add sbom.json
git commit -m "Add SBOM"
```

That's it! You now have a comprehensive SBOM for your C++ project.
