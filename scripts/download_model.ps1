$dest = Join-Path $PSScriptRoot "..\models" | Resolve-Path -ErrorAction SilentlyContinue
if (-not $dest) { New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot "..\models") | Out-Null; $dest = (Join-Path $PSScriptRoot "..\models") }
$stub = Join-Path $dest "model.stub"
"stub model content" | Out-File -FilePath $stub -Encoding utf8
Write-Output "Created stub model at $stub"
