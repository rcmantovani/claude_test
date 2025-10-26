@echo off
REM Test SSH connection before deployment (Windows)

setlocal enabledelayedexpansion

echo ==================================
echo SSH Connection Test
echo ==================================
echo.

set /p HOST="Server hostname or IP: "
set /p USER="SSH username: "
set /p KEY_FILE="SSH key path [%USERPROFILE%\.ssh\id_rsa]: "
if "%KEY_FILE%"=="" set KEY_FILE=%USERPROFILE%\.ssh\id_rsa

if not exist "%KEY_FILE%" (
    echo Error: Key file %KEY_FILE% does not exist
    exit /b 1
)

echo.
echo Testing connection to %USER%@%HOST%...
echo.

REM Test basic SSH connection
echo 1. Testing basic SSH connection...
ssh -i "%KEY_FILE%" -o ConnectTimeout=10 -o BatchMode=yes "%USER%@%HOST%" "echo Connection successful!" 2>nul
if errorlevel 1 (
    echo    X SSH connection failed!
    echo.
    echo Troubleshooting:
    echo - Check that the server is reachable: ping %HOST%
    echo - Verify SSH key permissions
    echo - Try manual connection: ssh -i "%KEY_FILE%" %USER%@%HOST%
    echo - On Windows, ensure OpenSSH client is installed
    pause
    exit /b 1
) else (
    echo    * SSH connection works!
)

echo.
echo 2. Checking Python installation...
ssh -i "%KEY_FILE%" "%USER%@%HOST%" "python3 --version" 2>nul
if errorlevel 1 (
    echo    X Python3 not found on remote server
) else (
    echo    * Python found
)

echo.
echo 3. Checking pip installation...
ssh -i "%KEY_FILE%" "%USER%@%HOST%" "pip3 --version" 2>nul
if errorlevel 1 (
    echo    ! pip3 not found - will need to install
) else (
    echo    * pip found
)

echo.
echo 4. Checking systemd...
ssh -i "%KEY_FILE%" "%USER%@%HOST%" "systemctl --version" 2>nul
if errorlevel 1 (
    echo    X systemd not found - service management may not work
) else (
    echo    * systemd is available
)

echo.
echo 5. Checking sudo access...
ssh -i "%KEY_FILE%" "%USER%@%HOST%" "sudo -n true" 2>nul
if errorlevel 1 (
    echo    ! sudo requires password - deployment will prompt for password
) else (
    echo    * Passwordless sudo is configured
)

echo.
echo ==================================
echo Connection test complete!
echo ==================================
echo.
echo Your server appears ready for deployment.
echo Run: app-publisher deploy ^<app-dir^> --config ^<config-file^>
echo.

pause
