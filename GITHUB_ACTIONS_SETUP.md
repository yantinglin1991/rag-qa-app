# GitHub Actions 自動構建指南

## 使用 GitHub Actions 自動編譯與打包（Windows exe）

此指南說明如何設定 GitHub Actions，在 Windows runner 上自動：
1. 安裝 Visual C++ Build Tools + CMake
2. 安裝所有 Python 相依（包括 `annoy` 與 `llama-cpp-python`）
3. 用 PyInstaller 打包成單獨可執行檔案
4. 上傳 artifact 供下載

### 步驟 1：初始化 Git 倉庫（若尚未有）

```powershell
Set-Location 'D:\Personal\YT\個人專案\test\rag-qa-app'
git init
git add .
git commit -m "Initial commit: RAG QA app with GitHub Actions"
```

### 步驟 2：推上 GitHub

1. 在 GitHub 建立新倉庫（不初始化 README）
2. 在本機執行：

```powershell
git remote add origin https://github.com/YOUR_USERNAME/rag-qa-app.git
git branch -M main
git push -u origin main
```

### 步驟 3：更新工作流檔案

將 `.github/workflows/windows-build.yml` 內容替換為下方的完整內容（支援編譯原生套件）：

```yaml
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
      
      - name: Install MSVC & CMake via Chocolatey
        shell: powershell
        run: |
          choco install visualstudio2022buildtools cmake ninja --no-progress -y
      
      - name: Setup MSVC environment
        uses: ilammy/msvc-dev-cmd@v1
        with:
          arch: x64
      
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
      
      - name: Create sample data
        run: |
          mkdir -p data\docs
          echo "Sample document about AI and machine learning." > data\docs\sample1.txt
          echo "Another document about Python programming." > data\docs\sample2.txt
          python scripts\build_embeddings.py
          python scripts\build_index.py
      
      - name: Build exe with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --name rag_qa_app launcher.py
      
      - name: Copy static files and data
        shell: powershell
        run: |
          Copy-Item -Path "static" -Destination "dist\rag_qa_app\static" -Recurse -Force
          Copy-Item -Path "data" -Destination "dist\rag_qa_app\data" -Recurse -Force
          Copy-Item -Path "models" -Destination "dist\rag_qa_app\models" -Recurse -ErrorAction SilentlyContinue
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: rag_qa_app-windows-exe
          path: dist/rag_qa_app/
          retention-days: 30
```

### 步驟 4：提交並推送工作流

```powershell
git add .github\workflows\windows-build.yml
git commit -m "Add GitHub Actions workflow for Windows exe build"
git push
```

### 步驟 5：在 GitHub 檢查構建進度

1. 進入你的倉庫：https://github.com/YOUR_USERNAME/rag-qa-app
2. 點選「Actions」標籤
3. 查看「Build Windows exe with full dependencies」工作流的進度
4. 構建完成後，下載 artifact「rag_qa_app-windows-exe」

### 步驟 6：執行打包後的 exe

在本機下載 artifact 並解壓，執行：

```powershell
.\rag_qa_app.exe
```

伺服器會啟動在 `http://127.0.0.1:8000`。在瀏覽器開啟此地址即可使用 RAG QA 應用。

## 注意事項

- **模型檔**：若要使用本地 llama-cpp-python，將 ggml q4_0 模型放在 `dist\rag_qa_app\models\` 資料夾
- **環境變數**：複製 `.env.example` 到 `.env` 並修改 `MODEL_PATH` 與 `INDEX_PATH`
- **首次運行**：第一次執行時，embeddings 和 index 將自動建立

## 手動打包（在本機已安裝 MSVC + CMake 後）

若你已在本機安裝 Visual C++ Build Tools：

```powershell
Set-Location 'D:\Personal\YT\個人專案\test\rag-qa-app'
.venv\Scripts\pyinstaller --onedir --name rag_qa_app launcher.py
```

完成後在 `dist\rag_qa_app\` 找到可執行檔。
