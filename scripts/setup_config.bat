@echo off
REM Helper script to create a secure deployment configuration for Windows
REM This script will prompt for values and create a properly secured config file

setlocal enabledelayedexpansion

echo ==================================
echo App Publisher - Configuration Setup
echo ==================================
echo.

REM Get application directory
set /p APP_DIR="Where is your application located? [%CD%]: "
if "%APP_DIR%"=="" set APP_DIR=%CD%

if not exist "%APP_DIR%" (
    echo Error: Directory %APP_DIR% does not exist
    exit /b 1
)

echo.
echo --- Server Configuration ---
set /p HOST="Server hostname or IP: "
set /p USER="SSH username: "
set /p REMOTE_PATH="Remote deployment path (e.g., /opt/apps/myapp): "
set /p SSH_PORT="SSH port [22]: "
if "%SSH_PORT%"=="" set SSH_PORT=22

echo.
echo --- SSH Authentication ---
echo 1) SSH key (recommended)
echo 2) Password (not recommended for production)
set /p AUTH_METHOD="Authentication method [1]: "
if "%AUTH_METHOD%"=="" set AUTH_METHOD=1

if "%AUTH_METHOD%"=="1" (
    set /p KEY_FILE="Path to SSH private key [%USERPROFILE%\.ssh\id_rsa]: "
    if "!KEY_FILE!"=="" set KEY_FILE=%USERPROFILE%\.ssh\id_rsa

    if not exist "!KEY_FILE!" (
        echo Warning: Key file !KEY_FILE! does not exist
        set /p CONTINUE="Continue anyway? [y/N]: "
        if /i not "!CONTINUE!"=="y" exit /b 1
    )
)

echo.
echo --- Application Configuration ---
echo 1) Streamlit
echo 2) Flask
set /p APP_TYPE_NUM="Application type [1]: "
if "%APP_TYPE_NUM%"=="" set APP_TYPE_NUM=1

if "%APP_TYPE_NUM%"=="1" (
    set APP_TYPE=streamlit
    set DEFAULT_PORT=8501
) else (
    set APP_TYPE=flask
    set DEFAULT_PORT=5000
)

set /p APP_PORT="Application port [%DEFAULT_PORT%]: "
if "%APP_PORT%"=="" set APP_PORT=%DEFAULT_PORT%

set /p APP_NAME="Application name (used for systemd service): "
if "%APP_NAME%"=="" (
    for %%I in ("%APP_DIR%") do set APP_NAME=%%~nxI
)

set /p PYTHON_VERSION="Python version on remote server [python3]: "
if "%PYTHON_VERSION%"=="" set PYTHON_VERSION=python3

echo.
echo --- Environment Variables (Optional) ---
set /p ADD_ENV_VARS="Add environment variables? [y/N]: "

echo.
echo --- Configuration Output ---
set /p CONFIG_FILE="Save as [deploy.local.yaml]: "
if "%CONFIG_FILE%"=="" set CONFIG_FILE=deploy.local.yaml

set CONFIG_PATH=%APP_DIR%\%CONFIG_FILE%

REM Create the configuration file
(
echo # Auto-generated deployment configuration
echo # Created: %DATE% %TIME%
echo # KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT
echo.
echo server:
echo   host: %HOST%
echo   user: %USER%
echo   remote_path: %REMOTE_PATH%
echo   port: %SSH_PORT%
) > "%CONFIG_PATH%"

if "%AUTH_METHOD%"=="1" (
    REM Convert Windows path to Unix-style for consistency
    set UNIX_KEY_FILE=!KEY_FILE:\=/!
    echo   key_file: !UNIX_KEY_FILE! >> "%CONFIG_PATH%"
) else (
    echo   # password: SET_YOUR_PASSWORD_HERE >> "%CONFIG_PATH%"
)

(
echo.
echo app:
echo   type: %APP_TYPE%
echo   port: %APP_PORT%
echo   name: %APP_NAME%
echo   python_version: %PYTHON_VERSION%
echo   requirements_file: requirements.txt
) >> "%CONFIG_PATH%"

if /i "%ADD_ENV_VARS%"=="y" (
    echo   environment_vars: >> "%CONFIG_PATH%"
    echo     # Add your environment variables here >> "%CONFIG_PATH%"
    echo     # DATABASE_URL: "postgresql://..." >> "%CONFIG_PATH%"
    echo     # API_KEY: "your-api-key" >> "%CONFIG_PATH%"
) else (
    echo   environment_vars: {} >> "%CONFIG_PATH%"
)

echo.
echo ==================================
echo Configuration created successfully!
echo ==================================
echo.
echo Config file: %CONFIG_PATH%
echo.
echo Next steps:
echo 1. Review the configuration: type %CONFIG_PATH%
echo 2. Edit if needed: notepad %CONFIG_PATH%
echo 3. Test SSH connection: scripts\test_connection.bat
echo 4. Deploy your app: app-publisher deploy %APP_DIR% --config %CONFIG_PATH%
echo.
echo IMPORTANT: This file contains secrets. Never commit it to git!
echo The file is already in .gitignore as: %CONFIG_FILE%
echo.

pause
