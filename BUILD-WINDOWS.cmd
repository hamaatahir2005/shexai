@echo off
setlocal
cd /d "%~dp0"
echo SHEIKH HAMAMOMIN AI - Windows application builder
echo Requires Windows x64, Python 3.12, internet and free disk space.
echo This installs build dependencies in a local .venv and builds the portable app.
echo No administrator access is required. The first build can take several minutes.
echo.
choice /C YN /N /M "Download dependencies and build? [Y/N] "
if errorlevel 2 exit /b 0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build.ps1"
if errorlevel 1 (
    echo.
    echo BUILD FAILED. Read the error above. No successful build is claimed.
    pause
    exit /b 1
)
start "" explorer.exe "%~dp0dist"
echo.
echo Build complete. Your portable application ZIP is in dist.
pause
