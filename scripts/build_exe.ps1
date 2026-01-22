# Build a distributable folder using PyInstaller (Windows PowerShell)
# Requires pyinstaller installed in active Python environment

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

pyinstaller --noconfirm --onedir --name rag_qa_app launcher.py
Write-Output "Built with PyInstaller. Check dist\rag_qa_app"
