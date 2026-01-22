@echo off
REM Build distributable using PyInstaller (Windows)
pyinstaller --noconfirm --onedir --name rag_qa_app launcher.py
echo Built. See dist\rag_qa_app
pause
