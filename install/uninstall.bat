@echo off
REM ###############################################################################
REM # Agova AI Agent System - Uninstall Script (Windows)
REM ###############################################################################

echo.
echo ========================================
echo    Agova AI Agent System Uninstaller
echo ========================================
echo.

echo WARNING: This will remove Agova from your system.
echo This includes:
echo   - Application files in %USERPROFILE%\.agova
echo   - System command: agova
echo   - Configuration in %USERPROFILE%\.config\agova
echo.

set /p CONFIRM="Are you sure you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

REM Remove system command
echo Removing system command...
if exist "C:\Windows\System32\agova.bat" (
    del /f "C:\Windows\System32\agova.bat" >nul 2>&1
    echo [OK] Removed system command
)

REM Remove from PATH
echo Removing from PATH...
set "PATH_TO_REMOVE=%USERPROFILE%\.agova"
set "NEW_PATH=%PATH:;%PATH_TO_REMOVE%=%"
setx PATH "%NEW_PATH%" >nul 2>&1
echo [OK] Removed from PATH

REM Remove aliases
if exist "%USERPROFILE%\agova_aliases.bat" (
    del /f "%USERPROFILE%\agova_aliases.bat" >nul 2>&1
    echo [OK] Removed aliases
)

REM Remove registry entry
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
echo [OK] Removed registry entry

REM Remove Start Menu shortcut
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Agova.lnk" (
    del /f "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Agova.lnk" >nul 2>&1
    echo [OK] Removed Start Menu shortcut
)

REM Backup and remove config
set "CONFIG_DIR=%USERPROFILE%\.config\agova"
if exist "%CONFIG_DIR%" (
    set /p BACKUP_CONFIG="Do you want to backup your configuration? (y/N): "
    if /i "!BACKUP_CONFIG!"=="y" (
        set "BACKUP_DIR=%USERPROFILE%\agova_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
        mkdir "!BACKUP_DIR!" 2>nul
        xcopy /E /I "%CONFIG_DIR%" "!BACKUP_DIR!\agova" >nul
        echo [OK] Configuration backed up to !BACKUP_DIR!
    )
    rmdir /s /q "%CONFIG_DIR%"
    echo [OK] Removed configuration
)

REM Remove installation directory
set "INSTALL_DIR=%USERPROFILE%\.agova"
if exist "%INSTALL_DIR%" (
    set /p KEEP_VENV="Do you want to keep the virtual environment? (y/N): "
    if /i not "!KEEP_VENV!"=="y" (
        rmdir /s /q "%INSTALL_DIR%"
        echo [OK] Removed installation directory
    ) else (
        echo [OK] Kept virtual environment
    )
)

REM Ask about workspace
set "WORKSPACE_DIR=%USERPROFILE%\agova_workspace"
if exist "%WORKSPACE_DIR%" (
    set /p REMOVE_WORKSPACE="Do you want to remove the workspace? This will delete all generated files! (y/N): "
    if /i "!REMOVE_WORKSPACE!"=="y" (
        rmdir /s /q "%WORKSPACE_DIR%"
        echo [OK] Removed workspace
    ) else (
        echo [OK] Kept workspace
    )
)

echo.
echo ========================================
echo    Uninstall Complete!
echo ========================================
echo.
echo Please restart your terminal for changes to take effect.
echo.
pause
