@echo off
REM ###############################################################################
REM # Agova AI Agent System - Simple Installation Script (Windows)
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
echo Installing Agova from: %AGOVA_DIR%
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
pip install -r requirements.txt >nul 2>&1
echo [OK] Dependencies installed

REM Create workspace directory
if not exist "workspace" mkdir workspace
echo [OK] Workspace directory created

REM Create launcher batch file
echo Creating launcher...
(
echo @echo off
echo set "AGOVA_DIR=%AGOVA_DIR%"
echo python "%%AGOVA_DIR%%\main.py" %%*
) > "%AGOVA_DIR%\agova.bat"
echo [OK] Launcher created

REM Add to system PATH
echo Adding to system PATH...
set "PATH_TO_ADD=%AGOVA_DIR%"
setx PATH "%PATH%;%PATH_TO_ADD%" >nul 2>&1
echo [OK] Added to PATH

REM Create PowerShell alias
echo Creating PowerShell alias...
powershell -Command "
    $profileDir = Split-Path $PROFILE -Parent
    if (!(Test-Path $profileDir)) {
        New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
    }
    $aliasLine = 'function agova { python \"%AGOVA_DIR%\main.py\" @args }'
    if (Test-Path $PROFILE) {
        $content = Get-Content $PROFILE -Raw
        if ($content -notmatch 'function agova') {
            Add-Content $PROFILE \"`n# Agova AI Agent System\"
            Add-Content $PROFILE $aliasLine
        }
    } else {
        \"# Agova AI Agent System\" | Out-File $PROFILE
        $aliasLine | Out-File $PROFILE -Append
    }
" >nul 2>&1
echo [OK] PowerShell alias created

REM Create Command Prompt doskey macro
(
echo @echo off
echo REM Agova AI Agent System
echo doskey agova=python "%AGOVA_DIR%\main.py" $*
) > "%USERPROFILE%\agova_aliases.bat"

REM Add to registry for Command Prompt auto-run
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%USERPROFILE%\agova_aliases.bat" /f >nul 2>&1
echo [OK] Command Prompt alias created

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
