# PowerShell script to create a secure deployment configuration
# This script will prompt for values and create a properly secured config file

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "App Publisher - Configuration Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Get application directory
$defaultDir = Get-Location
$appDir = Read-Host "Where is your application located? [$defaultDir]"
if ([string]::IsNullOrWhiteSpace($appDir)) {
    $appDir = $defaultDir
}

if (-not (Test-Path $appDir)) {
    Write-Host "Error: Directory $appDir does not exist" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "--- Server Configuration ---" -ForegroundColor Yellow
$host_input = Read-Host "Server hostname or IP"
$user = Read-Host "SSH username"
$remotePath = Read-Host "Remote deployment path (e.g., /opt/apps/myapp)"
$sshPort = Read-Host "SSH port [22]"
if ([string]::IsNullOrWhiteSpace($sshPort)) {
    $sshPort = "22"
}

Write-Host ""
Write-Host "--- SSH Authentication ---" -ForegroundColor Yellow
Write-Host "1) SSH key (recommended)"
Write-Host "2) Password (not recommended for production)"
$authMethod = Read-Host "Authentication method [1]"
if ([string]::IsNullOrWhiteSpace($authMethod)) {
    $authMethod = "1"
}

$keyFile = ""
if ($authMethod -eq "1") {
    $defaultKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
    $keyFile = Read-Host "Path to SSH private key [$defaultKeyPath]"
    if ([string]::IsNullOrWhiteSpace($keyFile)) {
        $keyFile = $defaultKeyPath
    }

    if (-not (Test-Path $keyFile)) {
        Write-Host "Warning: Key file $keyFile does not exist" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? [y/N]"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    } else {
        # Check file permissions (Windows ACL)
        Write-Host "Note: Ensure SSH key has proper permissions" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "--- Application Configuration ---" -ForegroundColor Yellow
Write-Host "1) Streamlit"
Write-Host "2) Flask"
$appTypeNum = Read-Host "Application type [1]"
if ([string]::IsNullOrWhiteSpace($appTypeNum)) {
    $appTypeNum = "1"
}

if ($appTypeNum -eq "1") {
    $appType = "streamlit"
    $defaultPort = "8501"
} else {
    $appType = "flask"
    $defaultPort = "5000"
}

$appPort = Read-Host "Application port [$defaultPort]"
if ([string]::IsNullOrWhiteSpace($appPort)) {
    $appPort = $defaultPort
}

$appName = Read-Host "Application name (used for systemd service)"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = Split-Path $appDir -Leaf
}

$pythonVersion = Read-Host "Python version on remote server [python3]"
if ([string]::IsNullOrWhiteSpace($pythonVersion)) {
    $pythonVersion = "python3"
}

Write-Host ""
Write-Host "--- Environment Variables (Optional) ---" -ForegroundColor Yellow
$addEnvVars = Read-Host "Add environment variables? [y/N]"

Write-Host ""
Write-Host "--- Configuration Output ---" -ForegroundColor Yellow
$configFile = Read-Host "Save as [deploy.local.yaml]"
if ([string]::IsNullOrWhiteSpace($configFile)) {
    $configFile = "deploy.local.yaml"
}

$configPath = Join-Path $appDir $configFile

# Create the configuration file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$content = @"
# Auto-generated deployment configuration
# Created: $timestamp
# KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

server:
  host: $host_input
  user: $user
  remote_path: $remotePath
  port: $sshPort
"@

if ($authMethod -eq "1") {
    # Convert Windows path to Unix-style for consistency
    $unixKeyFile = $keyFile -replace '\\', '/'
    $content += "`n  key_file: $unixKeyFile"
} else {
    $content += "`n  # password: SET_YOUR_PASSWORD_HERE"
}

$content += @"

app:
  type: $appType
  port: $appPort
  name: $appName
  python_version: $pythonVersion
  requirements_file: requirements.txt
"@

if ($addEnvVars -eq "y" -or $addEnvVars -eq "Y") {
    $content += @"

  environment_vars:
    # Add your environment variables here
    # DATABASE_URL: "postgresql://..."
    # API_KEY: "your-api-key"
"@
} else {
    $content += "`n  environment_vars: {}"
}

# Write the configuration file
$content | Out-File -FilePath $configPath -Encoding UTF8

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "✓ Configuration created successfully!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Config file: $configPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the configuration: Get-Content $configPath"
Write-Host "2. Edit if needed: notepad $configPath"
Write-Host "3. Test SSH connection: .\scripts\test_connection.ps1"
Write-Host "4. Deploy your app: app-publisher deploy $appDir --config $configPath"
Write-Host ""
Write-Host "⚠️  IMPORTANT: This file contains secrets. Never commit it to git!" -ForegroundColor Red
Write-Host "The file is already in .gitignore as: $configFile" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue"
