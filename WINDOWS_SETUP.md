# Windows Setup Guide

Complete guide for setting up and using app-publisher on Windows.

## Prerequisites

### 1. Install Python

Download and install Python 3.7+ from [python.org](https://www.python.org/downloads/)

**Important:** Check "Add Python to PATH" during installation

Verify installation:
```cmd
python --version
pip --version
```

### 2. Install OpenSSH Client

**Windows 10/11:**

1. Open Settings → Apps → Optional Features
2. Click "Add a feature"
3. Search for "OpenSSH Client"
4. Click Install

**Verify installation:**
```cmd
ssh -V
```

If you see a version number, OpenSSH is installed correctly.

### 3. Install Git (Optional but Recommended)

Download from [git-scm.com](https://git-scm.com/download/win)

## Installation

### Option 1: Using Command Prompt

```cmd
REM Clone the repository
git clone <repository-url>
cd app-publisher

REM Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

REM Install app-publisher
pip install -e .

REM Verify installation
app-publisher --version
```

### Option 2: Using PowerShell

```powershell
# Clone the repository
git clone <repository-url>
cd app-publisher

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Note: If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install app-publisher
pip install -e .

# Verify installation
app-publisher --version
```

## SSH Key Setup on Windows

### Generate SSH Keys

**Using Command Prompt or PowerShell:**

```cmd
REM Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

REM Accept default location: C:\Users\YourName\.ssh\id_ed25519
REM Set a passphrase (recommended)
```

Your keys will be created in: `C:\Users\YourName\.ssh\`

### Copy Public Key to Server

**Method 1: Using ssh-copy-id (if available)**
```cmd
ssh-copy-id -i %USERPROFILE%\.ssh\id_ed25519.pub user@server
```

**Method 2: Manual Copy**
```cmd
REM Display your public key
type %USERPROFILE%\.ssh\id_ed25519.pub

REM Copy the output and paste it into the server's authorized_keys
ssh user@server "mkdir -p ~/.ssh && echo YOUR_PUBLIC_KEY >> ~/.ssh/authorized_keys"
```

**Method 3: Using PowerShell**
```powershell
# Read public key
$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"

# Copy to server
ssh user@server "mkdir -p ~/.ssh && echo $publicKey >> ~/.ssh/authorized_keys"
```

### Test SSH Connection

```cmd
ssh -i %USERPROFILE%\.ssh\id_ed25519 user@your-server.com
```

## Quick Start (Windows)

### Using Batch Files (Command Prompt)

```cmd
REM 1. Navigate to your app directory
cd C:\path\to\your\app

REM 2. Run the configuration wizard
..\app-publisher\scripts\setup_config.bat

REM 3. Test the connection
..\app-publisher\scripts\test_connection.bat

REM 4. Deploy
app-publisher deploy . --config deploy.local.yaml
```

### Using PowerShell Scripts (Recommended)

```powershell
# 1. Navigate to your app directory
cd C:\path\to\your\app

# 2. Run the configuration wizard
..\app-publisher\scripts\setup_config.ps1

# 3. Test the connection
..\app-publisher\scripts\test_connection.ps1

# 4. Deploy
app-publisher deploy . --config deploy.local.yaml
```

## Example: Deploy Streamlit App

### Command Prompt

```cmd
REM Navigate to example
cd app-publisher\examples\streamlit-app

REM Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM Test locally
streamlit run app.py
REM Press Ctrl+C to stop

REM Create deployment config
copy deploy.example.yaml deploy.local.yaml
notepad deploy.local.yaml

REM Edit the file with your server details:
REM   host: your-server.com
REM   user: ubuntu
REM   remote_path: /opt/apps/streamlit-app
REM   key_file: C:/Users/YourName/.ssh/id_ed25519

REM Deploy
app-publisher deploy . --config deploy.local.yaml
```

### PowerShell

```powershell
# Navigate to example
cd app-publisher\examples\streamlit-app

# Create virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Test locally
streamlit run app.py
# Press Ctrl+C to stop

# Create deployment config
Copy-Item deploy.example.yaml deploy.local.yaml
notepad deploy.local.yaml

# Edit the file with your server details

# Deploy
app-publisher deploy . --config deploy.local.yaml
```

## Path Handling on Windows

### SSH Key Paths

When specifying SSH key paths in `deploy.local.yaml`, use forward slashes:

```yaml
server:
  key_file: C:/Users/YourName/.ssh/id_rsa
  # or
  key_file: ~/.ssh/id_rsa  # This works too
```

**Both formats work:**
- `C:/Users/YourName/.ssh/id_rsa` (forward slashes)
- `C:\Users\YourName\.ssh\id_rsa` (backslashes)

The tool automatically converts paths as needed.

## Windows-Specific Tips

### 1. Virtual Environment Activation

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Execution Policy (PowerShell)

If you get an error about execution policy:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or temporarily bypass for one session
powershell -ExecutionPolicy Bypass -File .\scripts\setup_config.ps1
```

### 3. Using Windows Terminal

For the best experience, use [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701):
- Better color support
- Multiple tabs
- Better copy/paste
- Modern interface

### 4. Line Endings

If you're editing scripts, use an editor that preserves line endings:
- VS Code (recommended)
- Notepad++
- Sublime Text

**Avoid:** Windows Notepad (may cause issues with line endings)

## Troubleshooting Windows-Specific Issues

### Issue: "ssh: command not found"

**Solution:**
Install OpenSSH Client:
1. Settings → Apps → Optional Features
2. Add "OpenSSH Client"
3. Restart terminal

Or download from: https://github.com/PowerShell/Win32-OpenSSH/releases

### Issue: "python: command not found"

**Solution:**
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to PATH:
  1. System Properties → Environment Variables
  2. Add `C:\Python3X` and `C:\Python3X\Scripts` to PATH

### Issue: Permission errors with SSH keys

**Solution:**
```cmd
REM Windows doesn't have chmod, but you can set permissions via:
icacls %USERPROFILE%\.ssh\id_rsa /inheritance:r
icacls %USERPROFILE%\.ssh\id_rsa /grant:r "%USERNAME%:R"
```

### Issue: "app-publisher: command not found" after installation

**Solution:**
```cmd
REM Ensure Scripts directory is in PATH
REM Add to PATH: %USERPROFILE%\AppData\Local\Programs\Python\Python3X\Scripts

REM Or use full path:
python -m app_publisher.cli deploy ...

REM Or reinstall in virtual environment
python -m venv venv
venv\Scripts\activate
pip install -e .
```

### Issue: PowerShell script won't run

**Solution:**
```powershell
# Unblock the script
Unblock-File .\scripts\setup_config.ps1

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\scripts\setup_config.ps1
```

### Issue: Colors not showing in Command Prompt

**Solution:**
- Use Windows Terminal instead of Command Prompt
- Or use PowerShell
- Or install ConEmu/Cmder

## Configuration File Examples

### Windows-friendly deploy.local.yaml

```yaml
server:
  host: 192.168.1.100
  user: ubuntu
  remote_path: /opt/apps/myapp
  port: 22
  # Use forward slashes or let Windows handle it
  key_file: C:/Users/YourName/.ssh/id_rsa
  # or
  # key_file: ~/.ssh/id_rsa

app:
  type: streamlit
  port: 8501
  name: my-app
  python_version: python3
  requirements_file: requirements.txt
  environment_vars:
    DATABASE_URL: "postgresql://user:password@host/db"
    API_KEY: "your-secret-api-key"
```

## Useful Windows Commands

### Command Prompt
```cmd
REM Show environment variables
echo %USERPROFILE%
echo %PATH%

REM List SSH keys
dir %USERPROFILE%\.ssh

REM Display public key
type %USERPROFILE%\.ssh\id_ed25519.pub

REM Test SSH
ssh user@server

REM Check if port is open
telnet server-ip 22
```

### PowerShell
```powershell
# Show environment variables
$env:USERPROFILE
$env:PATH

# List SSH keys
Get-ChildItem $env:USERPROFILE\.ssh

# Display public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# Test SSH
ssh user@server

# Check if port is open
Test-NetConnection -ComputerName server-ip -Port 22
```

## Next Steps

1. **Test Examples**: Try deploying the example Streamlit or Flask app
2. **Read Documentation**:
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) - Security best practices
   - [USAGE.md](USAGE.md) - Advanced usage
3. **Deploy Your App**: Use the configuration wizard to deploy your own apps

## Additional Resources

- [Python on Windows](https://docs.python.org/3/using/windows.html)
- [OpenSSH on Windows](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [Windows Terminal](https://docs.microsoft.com/en-us/windows/terminal/)
- [WSL (Windows Subsystem for Linux)](https://docs.microsoft.com/en-us/windows/wsl/install) - Alternative approach

## WSL Alternative

If you prefer a Linux environment on Windows, consider using WSL:

```powershell
# Install WSL
wsl --install

# After restart, you can use Linux commands directly
wsl
cd /mnt/c/path/to/app-publisher
./scripts/setup_config.sh
```

This gives you the full Linux experience on Windows!
