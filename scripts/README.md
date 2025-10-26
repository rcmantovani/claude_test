# Helper Scripts

This directory contains helper scripts for setting up and testing app-publisher deployments.

## For Linux/macOS

### setup_config.sh
Interactive wizard to create a secure deployment configuration file.

**Usage:**
```bash
./scripts/setup_config.sh
```

### test_connection.sh
Test SSH connection and verify server requirements before deployment.

**Usage:**
```bash
./scripts/test_connection.sh
```

## For Windows

### PowerShell Scripts (Recommended)

#### setup_config.ps1
Interactive wizard to create a secure deployment configuration file.

**Usage:**
```powershell
.\scripts\setup_config.ps1
```

**If you get execution policy errors:**
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\scripts\setup_config.ps1
```

#### test_connection.ps1
Test SSH connection and verify server requirements before deployment.

**Usage:**
```powershell
.\scripts\test_connection.ps1
```

### Batch Scripts

#### setup_config.bat
Interactive wizard to create a secure deployment configuration file.

**Usage:**
```cmd
scripts\setup_config.bat
```

#### test_connection.bat
Test SSH connection and verify server requirements before deployment.

**Usage:**
```cmd
scripts\test_connection.bat
```

## What These Scripts Do

### Setup Config Scripts
1. Prompt for server details (hostname, username, remote path)
2. Ask for SSH authentication method (key or password)
3. Collect application details (type, port, name)
4. Optionally add environment variables
5. Create a `deploy.local.yaml` file with proper permissions
6. Provide next steps and warnings about secrets

### Test Connection Scripts
1. Test basic SSH connectivity
2. Check Python installation on remote server
3. Verify pip is installed
4. Check systemd availability
5. Test sudo access
6. Report overall readiness for deployment

## Security Notes

- All scripts help create `deploy.local.yaml` files which are in `.gitignore`
- Scripts remind users not to commit secrets to version control
- SSH key paths are normalized for cross-platform compatibility
- File permissions are set appropriately (Linux/macOS only)

## Troubleshooting

### Linux/macOS: Permission Denied

```bash
chmod +x scripts/setup_config.sh
chmod +x scripts/test_connection.sh
```

### Windows PowerShell: Execution Policy Error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows: "ssh: command not found"

Install OpenSSH Client:
1. Settings → Apps → Optional Features
2. Add "OpenSSH Client"
3. Restart your terminal

## See Also

- [WINDOWS_SETUP.md](../WINDOWS_SETUP.md) - Complete Windows setup guide
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide for all platforms
- [LOCAL_DEPLOYMENT.md](../LOCAL_DEPLOYMENT.md) - Security best practices
