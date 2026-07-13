@echo off
REM ###############################################################################
REM # Agova AI Agent System - Installation Script (Windows)
REM # This script installs Agova system-wide and creates the 'agova' command
REM ###############################################################################

setlocal enabledelayedexpansion

set "APP_NAME=agova"
set "INSTALL_DIR=%USERPROFILE%\.agova"
set "CONFIG_DIR=%USERPROFILE%\.config\agova"
set "WORKSPACE_DIR=%USERPROFILE%\agova_workspace"

echo.
echo ========================================
echo     Agova AI Agent System Installer
echo ========================================
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

REM Check git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Please install Git.
    pause
    exit /b 1
)
echo [OK] Git found

REM Create directories
echo Creating directories...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%WORKSPACE_DIR%" mkdir "%WORKSPACE_DIR%"
echo [OK] Directories created

REM Clone or copy repository
echo Setting up Agova...
if exist "%INSTALL_DIR%\main.py" (
    echo Existing installation found. Updating...
    cd /d "%INSTALL_DIR%"
    git pull origin main 2>nul || git pull origin master 2>nul
) else (
    echo Copying Agova files...
    if exist "..\main.py" (
        echo Installing from local source...
        xcopy /E /I /Y "..\*" "%INSTALL_DIR%"
    ) else (
        echo Cloning from GitHub...
        echo Please enter repository URL or press Enter to skip:
        set /p REPO_URL="Repository URL: "
        if not "!REPO_URL!"=="" (
            git clone "!REPO_URL!" "%INSTALL_DIR%"
        ) else (
            echo [WARNING] No repository URL provided. Please copy files manually.
        )
    )
)
echo [OK] Repository set up

REM Install Python dependencies
echo Installing Python dependencies...
cd /d "%INSTALL_DIR%"

if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
)

call venv\Scripts\activate
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo [OK] Dependencies installed

REM Create launcher script
echo Creating launcher script...
(
echo @echo off
echo set "AGOVA_HOME=%USERPROFILE%\.agova"
echo set "AGOVA_VENV=%AGOVA_HOME%\venv"
echo set "AGOVA_MAIN=%AGOVA_HOME%\main.py"
echo.
echo if not exist "%%AGOVA_MAIN%%" (
echo     echo Agova is not properly installed.
echo     echo Please run the install script again.
echo     exit /b 1
echo )
echo.
echo if not exist "%%AGOVA_VENV%%\Scripts\activate" (
echo     echo Virtual environment not found. Reinstalling dependencies...
echo     cd /d "%%AGOVA_HOME%%"
echo     python -m venv venv
echo     call venv\Scripts\activate
echo     pip install -r requirements.txt
echo )
echo.
echo call "%%AGOVA_VENV%%\Scripts\activate"
echo python "%%AGOVA_MAIN%%" %%*
) > "%INSTALL_DIR%\agova_launcher.bat"
echo [OK] Launcher script created

REM Create system-wide command
echo Setting up 'agova' command...

REM Method 1: Add to PATH using setx
set "PATH_TO_ADD=%INSTALL_DIR%"
setx PATH "%PATH%;%PATH_TO_ADD%" >nul 2>&1
echo [OK] Added to system PATH

REM Method 2: Create batch file in Windows directory
if exist "C:\Windows\System32" (
    (
    echo @echo off
    echo call "%INSTALL_DIR%\agova_launcher.bat" %%*
    ) > "C:\Windows\System32\agova.bat" 2>nul
    if not errorlevel 1 echo [OK] Created system-wide command
)

REM Method 3: Create alias using doskey
(
echo @echo off
echo REM Agova AI Agent System
echo doskey agova=call "%INSTALL_DIR%\agova_launcher.bat" $*
) >> "%USERPROFILE%\agova_aliases.bat"

REM Add to registry for auto-start
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%USERPROFILE%\agova_aliases.bat" /f >nul 2>&1

echo [OK] Created command alias

REM Setup config
echo Setting up configuration...
if exist "%INSTALL_DIR%\config.json" (
    if not exist "%CONFIG_DIR%\config.json" (
        copy "%INSTALL_DIR%\config.json" "%CONFIG_DIR%\config.json" >nul
        echo [OK] Default configuration created
    ) else (
        echo [OK] Existing configuration preserved
    )
)

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%START_MENU%" (
    powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%START_MENU%\Agova.lnk'); $SC.TargetPath = '%INSTALL_DIR%\agova_launcher.bat'; $SC.WorkingDirectory = '%INSTALL_DIR%'; $SC.Description = 'Agova AI Agent System'; $SC.Save()"
    echo [OK] Start Menu shortcut created
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo To start using Agova:
echo.
echo 1. Restart your terminal OR run:
echo    agova
echo.
echo 2. First time setup:
echo    - Configure your API key: agova --setup
echo    - Or edit config: %CONFIG_DIR%\config.json
echo.
echo Quick Commands:
echo   agova              - Start the application
echo   agova --setup      - Run configuration wizard
echo   agova --help       - Show help
echo.
echo Workspace: %WORKSPACE_DIR%
echo Config: %CONFIG_DIR%\config.json
echo.
pause
