# App Publisher

A simple CLI tool to publish Python Streamlit or Flask applications to a remote server via SSH.

## Features

- Deploy Streamlit and Flask applications to remote servers
- Automatic dependency installation
- Systemd service creation and management
- Simple SSH-based file transfer
- Support for custom configuration files

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd app-publisher

# Install the package
pip install -e .

# Verify installation
app-publisher --version
```

## Quick Start

### 1. Setup Configuration (Recommended)

Use the helper script to create a secure configuration:

```bash
./scripts/setup_config.sh
```

This will guide you through creating a `deploy.local.yaml` file with proper security settings.

### 2. Test Your Connection

```bash
./scripts/test_connection.sh
```

### 3. Deploy Your App

```bash
app-publisher deploy /path/to/your/app --config deploy.local.yaml
```

## Usage

### Basic Deployment

```bash
app-publisher deploy /path/to/your/app user@server:/remote/path --app-type streamlit --port 8501
```

### Using Configuration File

Create a `deploy.yaml` file in your application directory:

```yaml
server:
  host: example.com
  user: myuser
  remote_path: /var/www/myapp

app:
  type: streamlit  # or flask
  port: 8501
  name: my-app

ssh:
  key_file: ~/.ssh/id_rsa  # optional
```

Then deploy:

```bash
app-publisher deploy /path/to/your/app --config deploy.yaml
```

### Commands

- `deploy` - Deploy an application to remote server
- `start` - Start the application service
- `stop` - Stop the application service
- `restart` - Restart the application service
- `status` - Check application status
- `logs` - View application logs

## Requirements

**Local Machine:**
- Python 3.7+
- SSH client

**Remote Server:**
- Linux with systemd
- Python 3.7+
- SSH access with key-based authentication (recommended)
- sudo privileges

## Security Best Practices

### 1. Use SSH Keys (Not Passwords)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
```

### 2. Keep Secrets Secure

**Never commit these files to git:**
- `*.local.yaml` - Local deployment configs
- `*.prod.yaml` - Production deployment configs
- `.env` - Environment variables
- SSH private keys

**Use the provided templates:**
- `.env.example` - Copy to `.env` with your values
- `deploy.example.yaml` - Copy to `deploy.local.yaml` with your values

### 3. File Permissions

```bash
# Secure your config files
chmod 600 deploy.local.yaml
chmod 600 ~/.ssh/id_rsa

# Verify
ls -la deploy.local.yaml
```

### 4. Environment Variables

Store sensitive data in environment variables:

```yaml
# In deploy.local.yaml
app:
  environment_vars:
    DATABASE_URL: "postgresql://..."
    API_KEY: "your-secret-key"
```

## Documentation

- **[LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)** - Complete guide for local setup and secrets management
- **[USAGE.md](USAGE.md)** - Detailed usage guide with advanced options
- **[examples/](examples/)** - Working example applications

## Example

```bash
# Deploy a Streamlit app
app-publisher deploy ./my_streamlit_app user@192.168.1.100:/opt/apps/streamlit-app \
  --app-type streamlit \
  --port 8501 \
  --name my-dashboard

# Check status
app-publisher status user@192.168.1.100 --name my-dashboard

# View logs
app-publisher logs user@192.168.1.100 --name my-dashboard
```

## Example Applications

The repository includes complete working examples:

### Streamlit Dashboard
```bash
cd examples/streamlit-app

# Test locally
pip install -r requirements.txt
streamlit run app.py

# Deploy
cp deploy.example.yaml deploy.local.yaml
# Edit deploy.local.yaml with your server details
app-publisher deploy . --config deploy.local.yaml
```

### Flask Web App
```bash
cd examples/flask-app

# Test locally
pip install -r requirements.txt
python app.py

# Deploy
cp deploy.example.yaml deploy.local.yaml
# Edit deploy.local.yaml with your server details
app-publisher deploy . --config deploy.local.yaml
```

## Helper Scripts

- `scripts/setup_config.sh` - Interactive configuration setup
- `scripts/test_connection.sh` - Test SSH connection and server requirements

## Troubleshooting

### SSH Connection Issues
```bash
# Test connection manually
ssh -i ~/.ssh/id_rsa user@server

# Run connection test script
./scripts/test_connection.sh
```

### Permission Denied
```bash
# Fix SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Fix config permissions
chmod 600 deploy.local.yaml
```

### Service Not Starting
```bash
# Check logs
app-publisher logs user@server --name myapp --lines 100

# Check service status
app-publisher status user@server --name myapp
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
