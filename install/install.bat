@echo off
REM ###############################################################################
REM # Agova AI Agent System - Installation Script (Windows)
REM ###############################################################################

setlocal enabledelayedexpansion

REM Get the directory where the install script is located
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%.."
set "AGOVA_DIR=%CD%"

echo.
echo ========================================
echo    Agova AI Agent System Installer
echo ========================================
echo.
echo Agova directory: %AGOVA_DIR%
echo.

REM Check Python
echo Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo [OK] Python found

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed. Please install pip.
    pause
    exit /b 1
)
echo [OK] pip found

REM Install dependencies
echo Installing dependencies...
cd /d "%AGOVA_DIR%"
pip install -r requirements.txt
echo [OK] Dependencies installed

REM Create workspace directory
if not exist "workspace" mkdir workspace
echo [OK] Workspace directory ready

REM Create launcher batch file
echo Creating launcher...
(
echo @echo off
echo python "%AGOVA_DIR%\main.py" %%*
) > "%AGOVA_DIR%\agova.bat"
echo [OK] Launcher created

REM Create wrapper for PowerShell
(
echo @echo off
echo python "%AGOVA_DIR%\main.py" %%*
) > "%AGOVA_DIR%\agova.cmd"

REM Add to system PATH
echo Adding to system PATH...
setx PATH "%PATH%;%AGOVA_DIR%" >nul 2>&1
echo [OK] Added to PATH

REM Create PowerShell profile alias
echo Creating PowerShell alias...
powershell -Command "
    \$agovaDir = '%AGOVA_DIR%'
    \$profileDir = Split-Path \$PROFILE -Parent
    if (!(Test-Path \$profileDir)) {
        New-Item -ItemType Directory -Force -Path \$profileDir | Out-Null
    }
    \$newAlias = \"function agova { python `\"\$agovaDir\main.py`\" @args }\"
    if (Test-Path \$PROFILE) {
        \$content = Get-Content \$PROFILE -Raw
        if (\$content -notmatch 'function agova') {
            Add-Content \$PROFILE \"\`n# Agova AI Agent System\"
            Add-Content \$PROFILE \$newAlias
        }
    } else {
        \"# Agova AI Agent System\" | Out-File \$PROFILE
        \$newAlias | Out-File \$PROFILE -Append
    }
" >nul 2>&1
echo [OK] PowerShell alias created

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Agova is now installed!
echo.
echo To start using Agova:
echo.
echo 1. Close and reopen your terminal
echo.
echo 2. Run: agova
echo.
echo Quick commands:
echo   agova              - Start the application
echo   agova --setup      - Run configuration wizard
echo.
echo Installation directory: %AGOVA_DIR%
echo Config file: %AGOVA_DIR%\config.json
echo.
pause
