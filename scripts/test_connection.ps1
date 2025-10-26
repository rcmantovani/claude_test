# PowerShell script to test SSH connection before deployment

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SSH Connection Test" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$host_input = Read-Host "Server hostname or IP"
$user = Read-Host "SSH username"
$defaultKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
$keyFile = Read-Host "SSH key path [$defaultKeyPath]"
if ([string]::IsNullOrWhiteSpace($keyFile)) {
    $keyFile = $defaultKeyPath
}

if (-not (Test-Path $keyFile)) {
    Write-Host "Error: Key file $keyFile does not exist" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Testing connection to $user@$host_input..." -ForegroundColor Yellow
Write-Host ""

# Test basic SSH connection
Write-Host "1. Testing basic SSH connection..." -ForegroundColor Cyan
$result = ssh -i "$keyFile" -o ConnectTimeout=10 -o BatchMode=yes "$user@$host_input" "echo 'Connection successful!'" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ SSH connection failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "- Check that the server is reachable: Test-Connection $host_input"
    Write-Host "- Verify SSH key permissions"
    Write-Host "- Try manual connection: ssh -i `"$keyFile`" $user@$host_input"
    Write-Host "- On Windows, ensure OpenSSH client is installed:"
    Write-Host "  Settings > Apps > Optional Features > OpenSSH Client"
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host "   ✓ SSH connection works!" -ForegroundColor Green
    Write-Host "   Output: $result" -ForegroundColor Gray
}

Write-Host ""
Write-Host "2. Checking Python installation..." -ForegroundColor Cyan
$pythonVersion = ssh -i "$keyFile" "$user@$host_input" "python3 --version" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Python3 not found on remote server" -ForegroundColor Red
} else {
    Write-Host "   ✓ Python found: $pythonVersion" -ForegroundColor Green
}

Write-Host ""
Write-Host "3. Checking pip installation..." -ForegroundColor Cyan
$pipVersion = ssh -i "$keyFile" "$user@$host_input" "pip3 --version" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠ pip3 not found - will need to install" -ForegroundColor Yellow
} else {
    $pipShort = ($pipVersion -split '\n')[0]
    Write-Host "   ✓ pip found: $pipShort" -ForegroundColor Green
}

Write-Host ""
Write-Host "4. Checking systemd..." -ForegroundColor Cyan
$systemdVersion = ssh -i "$keyFile" "$user@$host_input" "systemctl --version" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ systemd not found - service management may not work" -ForegroundColor Red
} else {
    Write-Host "   ✓ systemd is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "5. Checking sudo access..." -ForegroundColor Cyan
ssh -i "$keyFile" "$user@$host_input" "sudo -n true" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠ sudo requires password - deployment will prompt for password" -ForegroundColor Yellow
} else {
    Write-Host "   ✓ Passwordless sudo is configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "✓ Connection test complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your server appears ready for deployment." -ForegroundColor Cyan
Write-Host "Run: app-publisher deploy <app-dir> --config <config-file>" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to continue"
