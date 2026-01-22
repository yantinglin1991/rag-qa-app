# rag-qa-app

Minimal RAG QA app skeleton.

Quickstart (Windows PowerShell):
1. Copy `.env.example` to `.env` and edit paths.
2. Create and activate a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. (Optional) create sample docs, build embeddings and index:

```powershell
mkdir data\docs
echo "Sample document" > data\docs\sample.txt
python scripts\build_embeddings.py
python scripts\build_index.py
```

5. Ensure you have a ggml model in `models/` (or run `scripts\download_model.ps1` to create a stub), then start the app:

```powershell
python launcher.py
```

Packaging (PyInstaller):

```powershell
pip install pyinstaller
pyinstaller --onedir --name rag_qa_app launcher.py
```

Note: do NOT embed large ggml model binaries into the exe. Place model files in a `models/` folder next to the exe before running.