# Quick setup to push to GitHub and trigger Actions build
# Run this in PowerShell from the rag-qa-app directory

Write-Host "=== RAG QA App - GitHub Setup Helper ===" -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: RAG QA app with GitHub Actions"
} else {
    Write-Host "Git repository already initialized."
}

# Prompt for GitHub repo URL
$repoUrl = Read-Host "Enter your GitHub repository URL (https://github.com/username/repo.git)"

if ($repoUrl) {
    Write-Host "Adding remote: $repoUrl"
    git remote remove origin -ErrorAction SilentlyContinue
    git remote add origin $repoUrl
    
    Write-Host "Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    
    Write-Host "Setup complete! Check GitHub Actions at: $($repoUrl -replace '.git$', '/actions')" -ForegroundColor Green
} else {
    Write-Host "Setup skipped. Run this script again with your GitHub repo URL." -ForegroundColor Yellow
}
