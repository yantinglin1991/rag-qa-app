# Helper script to create/update the GitHub Actions workflow
# Run this to setup the correct workflow file for automatic Windows exe builds

param(
    [string]$WorkflowPath = '.\.github\workflows\windows-build.yml'
)

$workflowContent = @'
name: Build Windows exe with full dependencies

on:
  push:
    branches: [ main, master ]
  workflow_dispatch: {}

jobs:
  build:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.10']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install MSVC and CMake via Chocolatey
        shell: powershell
        run: |
          choco install visualstudio2022buildtools cmake ninja --no-progress -y 2>&1 | Out-Null
          Write-Host "Build tools installed"
      
      - name: Setup MSVC environment
        uses: ilammy/msvc-dev-cmd@v1
        with:
          arch: x64
      
      - name: Install Python dependencies (including native packages)
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
          pip install annoy llama-cpp-python
      
      - name: Create sample documents and build index
        run: |
          mkdir -p data/docs
          echo "Sample document about artificial intelligence and machine learning." > data/docs/sample1.txt
          echo "Document about Python programming and best practices." > data/docs/sample2.txt
          echo "Information about cloud computing and distributed systems." > data/docs/sample3.txt
          python scripts/build_embeddings.py
          python scripts/build_index.py
      
      - name: Build standalone exe with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --name rag_qa_app launcher.py
      
      - name: Copy required files to distribution
        shell: powershell
        run: |
          mkdir -p dist/rag_qa_app/data dist/rag_qa_app/models
          Copy-Item -Path "static" -Destination "dist/rag_qa_app/static" -Recurse -Force -ErrorAction SilentlyContinue
          Copy-Item -Path "data" -Destination "dist/rag_qa_app/data" -Recurse -Force -ErrorAction SilentlyContinue
          Copy-Item -Path ".env.example" -Destination "dist/rag_qa_app/.env.example" -Force -ErrorAction SilentlyContinue
      
      - name: Create README for distribution
        shell: powershell
        run: |
          $readme = @"
# RAG QA App - Windows Build

## Quick Start

1. Extract this folder to desired location
2. Optionally edit `.env.example` and save as `.env`
3. Run: `rag_qa_app.exe`
4. Open browser to http://127.0.0.1:8000

## Model Setup (Optional)

To use local Llama models with llama-cpp-python:
1. Download a GGML quantized 7B model (e.g., from Hugging Face)
2. Place it in the `models/` folder
3. Update `.env` with the model path

## Notes

- First run will initialize embeddings and index
- Requires 8GB+ RAM for optimal performance
"@
          $readme | Out-File -FilePath "dist/rag_qa_app/README.txt" -Encoding UTF8
      
      - name: Upload Windows executable artifact
        uses: actions/upload-artifact@v4
        with:
          name: rag_qa_app-windows-exe
          path: dist/rag_qa_app/
          retention-days: 30
      
      - name: Create GitHub Release (on tag)
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v1
        with:
          files: dist/rag_qa_app/**/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'@

# Create directory if it doesn't exist
$workflowDir = Split-Path -Parent $WorkflowPath
if (-not (Test-Path $workflowDir)) {
    New-Item -ItemType Directory -Path $workflowDir -Force | Out-Null
    Write-Host "Created directory: $workflowDir"
}

# Write the workflow file
$workflowContent | Set-Content -Path $WorkflowPath -Encoding UTF8 -Force
Write-Host "✓ Workflow file created/updated: $WorkflowPath" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. git add .github/workflows/windows-build.yml"
Write-Host "2. git commit -m 'Update GitHub Actions workflow for full Windows build'"
Write-Host "3. git push"
Write-Host ""
Write-Host "Then visit your GitHub Actions page to monitor the build!"
