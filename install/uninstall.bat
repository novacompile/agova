@echo off
REM ###############################################################################
REM # Agova AI Agent System - Uninstall Script (Windows)
REM ###############################################################################

echo.
echo ========================================
echo    Agova AI Agent System Uninstaller
echo ========================================
echo.

REM Get the agova directory
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%.."
set "AGOVA_DIR=%CD%"

echo WARNING: This will remove Agova from your system.
echo Agova directory: %AGOVA_DIR%
echo.

set /p CONFIRM="Are you sure you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

REM Remove from PATH
echo Removing from PATH...
set "NEW_PATH=%PATH:;%AGOVA_DIR%=%"
setx PATH "%NEW_PATH%" >nul 2>&1
echo [OK] Removed from PATH

REM Remove launcher files
if exist "%AGOVA_DIR%\agova.bat" del /f "%AGOVA_DIR%\agova.bat" >nul 2>&1
if exist "%AGOVA_DIR%\agova.cmd" del /f "%AGOVA_DIR%\agova.cmd" >nul 2>&1
echo [OK] Removed launcher files

REM Remove PowerShell alias
powershell -Command "
    if (Test-Path \$PROFILE) {
        \$content = Get-Content \$PROFILE -Raw
        \$content = \$content -replace '# Agova AI Agent System\r?\n?', ''
        \$content = \$content -replace 'function agova \{.*?\}\r?\n?', ''
        Set-Content \$PROFILE \$content
    }
" >nul 2>&1
echo [OK] Removed PowerShell alias

REM Ask about removing the directory
set /p REMOVE_DIR="Do you want to remove the Agova directory? (%AGOVA_DIR%) (y/N): "
if /i "%REMOVE_DIR%"=="y" (
    rmdir /s /q "%AGOVA_DIR%"
    echo [OK] Removed Agova directory
) else (
    echo [OK] Kept Agova directory
)

echo.
echo ========================================
echo    Uninstall Complete!
echo ========================================
echo.
echo Please restart your terminal for changes to take effect.
echo.
pause
