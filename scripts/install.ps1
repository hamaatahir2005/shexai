$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
py -3.12 -m venv .venv
if ($LASTEXITCODE) { throw 'Python 3.12 is required' }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e '.[voice,automation,service,dev]'
if ($LASTEXITCODE) { throw 'Dependency installation failed' }
Write-Host 'Start with .\.venv\Scripts\hamamomin.exe'
