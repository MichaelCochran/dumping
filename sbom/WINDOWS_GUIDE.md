# Windows Quick Reference Guide

Quick reference for using the C++ SBOM Generator on Windows with PowerShell.

## Initial Setup

```powershell
# Navigate to the tool directory
cd c:\Users\e480545\sbom

# Install Python dependencies
pip install -r requirements.txt

# Run tests to verify installation
python test_tool.py
```

## Basic Usage Examples

### Generate SBOM for a Project

```powershell
# SPDX format (most common)
python sbom_generator.py "C:\Projects\MyApp" -o sbom.json -f spdx

# CycloneDX format (security focused)
python sbom_generator.py "C:\Projects\MyApp" -o sbom.json -f cyclonedx

# With verbose output
python sbom_generator.py "C:\Projects\MyApp" -o sbom.json -f spdx -v
```

### Using Configuration File

```powershell
# Copy example config
copy config.example.json config.json

# Edit config.json with your settings
notepad config.json

# Run with config
python sbom_generator.py "C:\Projects\MyApp" -o sbom.json -c config.json
```

### Multiple Outputs

```powershell
# Generate all three formats
python sbom_generator.py "C:\Projects\MyApp" -o output\sbom-spdx.json -f spdx
python sbom_generator.py "C:\Projects\MyApp" -o output\sbom-cdx.json -f cyclonedx
python sbom_generator.py "C:\Projects\MyApp" -o output\sbom-raw.json -f json
```

## Utility Commands

### Compare Two SBOMs

```powershell
python utils.py compare baseline-sbom.json current-sbom.json -o diff.json
```

### Validate SBOM

```powershell
python utils.py validate sbom.json
```

### Generate Summary Report

```powershell
python utils.py summary sbom.json -o report.txt
type report.txt
```

### Extract Licenses

```powershell
python utils.py licenses sbom.json
```

## Working with Different Project Structures

### CMake Project

```powershell
# Project with CMakeLists.txt
python sbom_generator.py "C:\Projects\cmake-project" -o sbom.json -f spdx
```

### Visual Studio Project

```powershell
# Projects using vcpkg
python sbom_generator.py "C:\Projects\vs-project" -o sbom.json -f spdx
```

### Makefile Project

```powershell
# Projects with Makefile
python sbom_generator.py "C:\Projects\make-project" -o sbom.json -f spdx
```

## Common Windows Paths

### System Include Paths

Add to config.json:
```json
{
  "system_include_paths": [
    "C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.30.30705/include",
    "C:/Program Files (x86)/Windows Kits/10/Include/10.0.19041.0/ucrt",
    "C:/vcpkg/installed/x64-windows/include"
  ]
}
```

### vcpkg Integration

```powershell
# If using vcpkg
$env:VCPKG_ROOT="C:\vcpkg"
python sbom_generator.py . -o sbom.json -f spdx
```

## CI/CD Integration

### GitHub Actions (Windows)

```yaml
- name: Install Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'

- name: Generate SBOM
  shell: pwsh
  run: |
    cd sbom
    pip install -r requirements.txt
    python sbom_generator.py ${{ github.workspace }} -o sbom.json -f spdx

- name: Upload SBOM
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom/sbom.json
```

### Azure Pipelines

```yaml
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.10'

- script: |
    cd sbom
    pip install -r requirements.txt
    python sbom_generator.py $(Build.SourcesDirectory) -o sbom.json -f spdx
  displayName: 'Generate SBOM'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'sbom/sbom.json'
    artifactName: 'sbom'
```

## Batch Processing

### Process Multiple Projects

```powershell
# Create a batch script: generate-all-sboms.ps1
$projects = @(
    "C:\Projects\Project1",
    "C:\Projects\Project2",
    "C:\Projects\Project3"
)

foreach ($project in $projects) {
    $projectName = Split-Path $project -Leaf
    $outputFile = "output\$projectName-sbom.json"
    
    Write-Host "Processing $projectName..."
    python sbom_generator.py $project -o $outputFile -f spdx
}

Write-Host "All SBOMs generated!"
```

Run it:
```powershell
.\generate-all-sboms.ps1
```

## Troubleshooting on Windows

### Python Not Found

```powershell
# Check Python installation
python --version

# If not found, install from Microsoft Store or python.org
# Then verify:
where python
```

### Path Issues

```powershell
# Use quotes for paths with spaces
python sbom_generator.py "C:\Program Files\MyProject" -o sbom.json -f spdx

# Or use short paths (if needed)
python sbom_generator.py C:\PROGRA~1\MyProject -o sbom.json -f spdx
```

### Permission Errors

```powershell
# Run PowerShell as Administrator
# Or ensure you have write permissions to output directory
mkdir output -ErrorAction SilentlyContinue
```

### Encoding Issues

Windows uses different line endings. If you see strange characters:

```powershell
# Convert line endings (if needed)
# Install dos2unix via Git Bash or Cygwin
dos2unix sbom_generator.py
```

## Performance Tips

### Large Projects

```powershell
# Limit directory depth
python sbom_generator.py "C:\LargeProject" -o sbom.json --max-depth 10

# Exclude build directories
# Add to config.json:
{
  "exclude_patterns": [
    "**/build/**",
    "**/Debug/**",
    "**/Release/**",
    "**/.git/**"
  ]
}
```

### Parallel Processing

```powershell
# Process multiple projects in parallel
$jobs = @()

$projects | ForEach-Object {
    $jobs += Start-Job -ScriptBlock {
        param($proj)
        python sbom_generator.py $proj -o "output\$(Split-Path $proj -Leaf)-sbom.json" -f spdx
    } -ArgumentList $_
}

$jobs | Wait-Job
$jobs | Receive-Job
```

## Output Locations

### Recommended Directory Structure

```
C:\Projects\MyApp\
├── src/
├── include/
├── CMakeLists.txt
├── docs/
│   └── sbom/           # Store SBOMs here
│       ├── sbom-latest.json
│       ├── sbom-v1.0.0.json
│       └── sbom-v1.1.0.json
└── build/
```

Generate to docs:
```powershell
python sbom_generator.py "C:\Projects\MyApp" -o "C:\Projects\MyApp\docs\sbom\sbom-latest.json" -f spdx
```

## IDE Integration

### Visual Studio Code

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate SBOM",
      "type": "shell",
      "command": "python",
      "args": [
        "c:/Users/e480545/sbom/sbom_generator.py",
        "${workspaceFolder}",
        "-o",
        "${workspaceFolder}/sbom.json",
        "-f",
        "spdx"
      ],
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

Run with: `Ctrl+Shift+P` → "Tasks: Run Task" → "Generate SBOM"

### Visual Studio

Add as External Tool:
- Tools → External Tools → Add
- Title: Generate SBOM
- Command: `python.exe`
- Arguments: `c:\Users\e480545\sbom\sbom_generator.py $(SolutionDir) -o $(SolutionDir)sbom.json -f spdx`

## Quick Examples

### Example 1: Quick SBOM for Current Directory

```powershell
python sbom_generator.py . -o sbom.json -f spdx
```

### Example 2: Detailed Output with All Formats

```powershell
# Create output directory
mkdir sbom-output -ErrorAction SilentlyContinue

# Generate all formats with verbose output
python sbom_generator.py . -o sbom-output\sbom-spdx.json -f spdx -v
python sbom_generator.py . -o sbom-output\sbom-cdx.json -f cyclonedx -v
python sbom_generator.py . -o sbom-output\sbom-raw.json -f json -v

# Generate summary
python utils.py summary sbom-output\sbom-raw.json -o sbom-output\summary.txt

# View summary
type sbom-output\summary.txt
```

### Example 3: Versioned SBOMs

```powershell
# Generate SBOM with version in filename
$version = "1.0.0"
python sbom_generator.py . -o "sbom-v$version.json" -f spdx --project-version $version
```

---

## Need Help?

```powershell
# Show help
python sbom_generator.py --help

# Run tests
python test_tool.py

# Verbose mode for debugging
python sbom_generator.py . -o sbom.json -f spdx -v
```

**Happy SBOM generating! 🚀**
