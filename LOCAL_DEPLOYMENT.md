# Local Deployment & Secrets Management Guide

This guide explains how to set up app-publisher on your local machine and manage secrets securely.

## 1. Local Installation

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd app-publisher

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .

# Verify installation
app-publisher --version
```

### Step 2: Test the Installation

```bash
# View help
app-publisher --help

# Test with example app (dry run - don't actually deploy yet)
cd examples/streamlit-app
ls -la
```

## 2. Managing Secrets Securely

### Option A: SSH Key Authentication (Recommended)

**Best Practice**: Use SSH keys instead of passwords.

#### Generate SSH Key (if you don't have one)

```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Save to: ~/.ssh/id_ed25519 (or custom name like ~/.ssh/id_app_publisher)

# Set proper permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

#### Copy Public Key to Server

```bash
# Copy your public key to the server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server.com

# Test the connection
ssh -i ~/.ssh/id_ed25519 user@your-server.com
```

#### Use in Deployment

```bash
app-publisher deploy ./myapp user@server:/path \
  --app-type streamlit \
  --port 8501 \
  --name myapp \
  --key-file ~/.ssh/id_ed25519
```

### Option B: Environment Variables

Create a `.env` file (NEVER commit this to git):

```bash
# .env file (already in .gitignore)
DEPLOY_HOST=192.168.1.100
DEPLOY_USER=ubuntu
DEPLOY_REMOTE_PATH=/opt/apps/myapp
DEPLOY_SSH_KEY=/home/user/.ssh/id_rsa
DEPLOY_PORT=22

# Application settings
APP_TYPE=streamlit
APP_PORT=8501
APP_NAME=myapp

# Optional: Application secrets
DATABASE_URL=postgresql://user:password@host/db
API_KEY=your-secret-api-key
```

Load and use environment variables:

```bash
# Load environment variables
export $(cat .env | xargs)

# Deploy using environment variables
app-publisher deploy ./myapp $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_REMOTE_PATH \
  --app-type $APP_TYPE \
  --port $APP_PORT \
  --name $APP_NAME \
  --key-file $DEPLOY_SSH_KEY
```

### Option C: Secure Configuration Files

Create separate config files for different environments:

```bash
# Directory structure
myapp/
├── app.py
├── requirements.txt
├── deploy.yaml           # Template (commit to git)
├── deploy.local.yaml     # Local config (DON'T commit)
└── deploy.prod.yaml      # Production config (DON'T commit)
```

**deploy.yaml** (template - safe to commit):
```yaml
server:
  host: REPLACE_WITH_YOUR_HOST
  user: REPLACE_WITH_YOUR_USER
  remote_path: /opt/apps/myapp
  port: 22
  # key_file: ~/.ssh/id_rsa

app:
  type: streamlit
  port: 8501
  name: myapp
  python_version: python3
  requirements_file: requirements.txt
  environment_vars: {}
```

**deploy.local.yaml** (actual secrets - DON'T commit):
```yaml
server:
  host: 192.168.1.100
  user: ubuntu
  remote_path: /opt/apps/myapp
  port: 22
  key_file: /home/user/.ssh/id_rsa

app:
  type: streamlit
  port: 8501
  name: myapp
  python_version: python3
  requirements_file: requirements.txt
  environment_vars:
    DATABASE_URL: "postgresql://user:password@localhost/mydb"
    API_KEY: "your-secret-api-key"
    SECRET_TOKEN: "super-secret-token"
```

Deploy using:
```bash
app-publisher deploy ./myapp --config deploy.local.yaml
```

### Option D: System Keyring (Advanced)

For maximum security, use the system keyring:

```bash
# Install keyring
pip install keyring

# Store secrets
keyring set app-publisher ssh_password
# Enter password when prompted

# Or use a Python script
python3 << EOF
import keyring
keyring.set_password("app-publisher", "ssh_key_path", "/home/user/.ssh/id_rsa")
keyring.set_password("app-publisher", "server_host", "192.168.1.100")
EOF
```

## 3. Security Best Practices

### File Permissions

```bash
# Secure your config files
chmod 600 deploy.local.yaml
chmod 600 deploy.prod.yaml
chmod 600 .env

# SSH keys should be 600
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Git Configuration

Ensure `.gitignore` includes:
```
# Secrets and local configs
*.local.yaml
.env
.env.local
**/secrets/
**/*secret*
deploy.prod.yaml

# SSH keys
*.pem
*.key
id_rsa
id_ed25519
```

### Environment-Specific Configs

```bash
# Create a config generator script
cat > create_config.sh << 'EOF'
#!/bin/bash
echo "Creating deployment config..."
read -p "Server host: " HOST
read -p "Server user: " USER
read -p "Remote path: " REMOTE_PATH
read -p "SSH key path [~/.ssh/id_rsa]: " KEY_FILE
KEY_FILE=${KEY_FILE:-~/.ssh/id_rsa}

cat > deploy.local.yaml << YAML
server:
  host: $HOST
  user: $USER
  remote_path: $REMOTE_PATH
  port: 22
  key_file: $KEY_FILE

app:
  type: streamlit
  port: 8501
  name: myapp
  python_version: python3
  requirements_file: requirements.txt
  environment_vars: {}
YAML

chmod 600 deploy.local.yaml
echo "Config created: deploy.local.yaml"
EOF

chmod +x create_config.sh
```

## 4. Testing Locally Before Deployment

### Test Streamlit App Locally

```bash
cd examples/streamlit-app
pip install -r requirements.txt
streamlit run app.py
# Visit http://localhost:8501
```

### Test Flask App Locally

```bash
cd examples/flask-app
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

## 5. Deployment Workflow

### Safe Deployment Process

```bash
# 1. Test locally
cd myapp
pip install -r requirements.txt
streamlit run app.py  # or python app.py for Flask

# 2. Review what will be deployed
ls -la
cat requirements.txt

# 3. Check your deploy config (without showing secrets)
head -n 10 deploy.local.yaml

# 4. Deploy with verbose logging
app-publisher deploy . --config deploy.local.yaml --verbose

# 5. Check status
app-publisher status user@server --name myapp

# 6. View logs if there are issues
app-publisher logs user@server --name myapp --lines 100
```

## 6. Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection manually
ssh -i ~/.ssh/id_rsa user@server

# Debug SSH
ssh -vvv -i ~/.ssh/id_rsa user@server

# Check SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

### Permission Denied

```bash
# Ensure proper permissions
chmod 600 ~/.ssh/id_rsa
chmod 600 deploy.local.yaml

# Check server-side permissions
ssh user@server "ls -la /opt/apps"
```

### Secrets in Logs

If you see secrets in logs, ensure:
1. Use `--verbose` flag only during testing
2. Don't log deployment configs
3. Check systemd logs don't expose environment variables

## 7. Production Deployment Checklist

- [ ] SSH key authentication configured
- [ ] Secrets stored in separate config files (not in git)
- [ ] `.gitignore` properly configured
- [ ] File permissions set correctly (600 for configs/keys)
- [ ] Tested deployment in staging/local environment first
- [ ] Firewall rules configured on server
- [ ] Application port is accessible
- [ ] Backup of current deployment (if updating)
- [ ] Monitoring/alerting configured
- [ ] SSL/HTTPS configured (via reverse proxy)

## 8. Quick Reference

```bash
# Installation
pip install -e .

# Deploy with config file
app-publisher deploy ./myapp --config deploy.local.yaml

# Deploy with CLI args
app-publisher deploy ./myapp user@server:/path \
  --app-type streamlit --port 8501 --name myapp \
  --key-file ~/.ssh/id_rsa

# Management
app-publisher status user@server --name myapp
app-publisher logs user@server --name myapp
app-publisher restart user@server --name myapp

# Create secure config
chmod 600 deploy.local.yaml
```

## 9. Alternative: Using Docker (Bonus)

For even more isolation, you can run app-publisher in Docker:

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
ENTRYPOINT ["app-publisher"]
```

```bash
# Build and run
docker build -t app-publisher .
docker run -v ~/.ssh:/root/.ssh:ro -v $(pwd):/data app-publisher \
  deploy /data/myapp --config /data/deploy.yaml
```
