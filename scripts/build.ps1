param([switch]$SkipTests, [switch]$Installer)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Build on Windows 10/11 x64. PyInstaller cannot cross-compile Windows applications.' }
Set-Location (Split-Path $PSScriptRoot -Parent)
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Program $($Arguments -join ' ')" }
}
if (-not (Test-Path $python)) {
    Invoke-Checked -Program 'py' -Arguments @('-3.12', '-m', 'venv', '.venv')
}
Invoke-Checked -Program $python -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip')
Invoke-Checked -Program $python -Arguments @('-m', 'pip', 'install', '-e', '.[voice,automation,service,dev]')
if (-not $SkipTests) {
    $previousQtPlatform = $env:QT_QPA_PLATFORM
    try {
        $env:QT_QPA_PLATFORM = 'offscreen'
        Invoke-Checked -Program $python -Arguments @('-m', 'pytest', '-q')
    } finally { $env:QT_QPA_PLATFORM = $previousQtPlatform }
}
Invoke-Checked -Program $python -Arguments @('scripts/make_icon.py')
Invoke-Checked -Program $python -Arguments @(
    '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed',
    '--name', 'SheikhHamamomin', '--icon', 'assets/icon.ico',
    '--paths', '.', '--add-data', 'assets;assets',
    '--collect-all', 'pyttsx3', '--collect-all', 'faster_whisper',
    '--collect-all', 'keyring', '--collect-all', 'sounddevice',
    '--recursive-copy-metadata', 'faster-whisper',
    '--hidden-import', 'keyring.backends.Windows',
    '--hidden-import', 'pyttsx3.drivers.sapi5', 'scripts/entry.py'
)
$binary = Join-Path (Get-Location) 'dist\SheikhHamamomin\SheikhHamamomin.exe'
if (-not (Test-Path $binary)) { throw 'Expected executable is missing.' }
$report = Join-Path (Get-Location) 'dist\windows-self-test.json'
$probe = Start-Process -FilePath $binary -ArgumentList @('--self-test') -PassThru -Wait -NoNewWindow
if (Test-Path $report) { Get-Content -Raw $report | Write-Host }
if ($probe.ExitCode -ne 0) { throw "Packaged application self-test failed. See $report" }
# A windowed executable has no console; the JSON report proves the probe ran.
if (-not (Test-Path $report)) { throw 'Packaged application did not produce its self-test report.' }
$check = Get-Content -Raw $report | ConvertFrom-Json
if ($check.status -ne 'ok') { throw "Packaged self-test reported failure: $($check.error)" }
Compress-Archive -Path 'dist\SheikhHamamomin' -DestinationPath 'dist\SheikhHamamomin-Windows-x64.zip' -Force
Get-FileHash 'dist\SheikhHamamomin-Windows-x64.zip' -Algorithm SHA256 | Format-List | Out-File 'dist\SHA256.txt'
if ($Installer) {
    $compiler = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
    if ($compiler) { $compilerPath = $compiler.Source }
    else { $compilerPath = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe' }
    if (-not (Test-Path $compilerPath)) { throw 'Install Inno Setup 6, then rerun with -Installer. The portable ZIP is already built.' }
    Invoke-Checked -Program $compilerPath -Arguments @('scripts\installer.iss')
}
Write-Host 'SUCCESS: dist\SheikhHamamomin-Windows-x64.zip'
Write-Host 'Extract the WHOLE folder, then double-click SheikhHamamomin.exe. Python is not required on the destination PC.'
