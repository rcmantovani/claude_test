# Quick Start Guide

Get up and running with app-publisher in 5 minutes.

## Prerequisites

- Python 3.7+ on your local machine
- A remote Linux server with SSH access
- SSH key for authentication (or you can generate one)

## Step 1: Install (2 minutes)

```bash
# Clone and navigate to the project
git clone <repository-url>
cd app-publisher

# Install in development mode
pip install -e .

# Verify it works
app-publisher --version
```

## Step 2: Prepare SSH Access (3 minutes)

### If you already have SSH keys:

```bash
# Test your connection
ssh user@your-server.com

# If that works, you're ready!
```

### If you need to create SSH keys:

```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location (~/.ssh/id_ed25519)
# Set a passphrase (optional but recommended)

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server.com

# Test the connection
ssh -i ~/.ssh/id_ed25519 user@your-server.com
```

## Step 3: Try the Example Apps (5 minutes)

### Option A: Deploy Example Streamlit App

```bash
# Navigate to the example
cd examples/streamlit-app

# Test it locally first
pip install -r requirements.txt
streamlit run app.py
# Visit http://localhost:8501 - press Ctrl+C to stop

# Create your deployment config
cp deploy.example.yaml deploy.local.yaml

# Edit the config with your server details
nano deploy.local.yaml  # or use your favorite editor

# Edit these lines:
#   host: your-server.com (or IP like 192.168.1.100)
#   user: your-ssh-username (e.g., ubuntu)
#   remote_path: /opt/apps/streamlit-dashboard
#   key_file: ~/.ssh/id_ed25519 (or your key path)

# Deploy!
app-publisher deploy . --config deploy.local.yaml

# If successful, visit: http://your-server.com:8501
```

### Option B: Deploy Example Flask App

```bash
# Navigate to the example
cd examples/flask-app

# Test it locally first
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000 - press Ctrl+C to stop

# Create your deployment config
cp deploy.example.yaml deploy.local.yaml

# Edit the config with your server details
nano deploy.local.yaml

# Edit these lines:
#   host: your-server.com
#   user: your-ssh-username
#   remote_path: /opt/apps/flask-app
#   key_file: ~/.ssh/id_ed25519

# Deploy!
app-publisher deploy . --config deploy.local.yaml

# If successful, visit: http://your-server.com:5000
```

## Step 4: Deploy Your Own App

### For a Streamlit App:

```bash
# Go to your app directory
cd /path/to/your/streamlit/app

# Make sure you have requirements.txt
ls requirements.txt

# Make sure your main file is called app.py
ls app.py

# Use the interactive setup
../../scripts/setup_config.sh

# Deploy
app-publisher deploy . --config deploy.local.yaml
```

### For a Flask App:

```bash
# Go to your app directory
cd /path/to/your/flask/app

# Make sure you have requirements.txt
ls requirements.txt

# Make sure your app file is called app.py with a Flask 'app' variable
grep "app = Flask" app.py

# Use the interactive setup
../../scripts/setup_config.sh

# Deploy
app-publisher deploy . --config deploy.local.yaml
```

## Managing Your Deployed App

```bash
# Check if it's running
app-publisher status user@server --name your-app-name

# View logs
app-publisher logs user@server --name your-app-name

# Restart the app
app-publisher restart user@server --name your-app-name

# Stop the app
app-publisher stop user@server --name your-app-name
```

## Common Issues & Solutions

### Issue: "Permission denied (publickey)"

**Solution:**
```bash
# Make sure your SSH key has correct permissions
chmod 600 ~/.ssh/id_ed25519

# Test SSH connection manually
ssh -i ~/.ssh/id_ed25519 user@server

# If that doesn't work, copy your key again
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
```

### Issue: "Port already in use"

**Solution:**
```bash
# Change the port in deploy.local.yaml
# For Streamlit, try 8502, 8503, etc.
# For Flask, try 5001, 5002, etc.

app:
  port: 8502  # Change this
```

### Issue: "Cannot connect to deployed app"

**Solution:**
```bash
# Check if the service is running
app-publisher status user@server --name your-app

# Check the logs
app-publisher logs user@server --name your-app

# Check firewall on the server
ssh user@server "sudo ufw status"

# If firewall is blocking, allow the port
ssh user@server "sudo ufw allow 8501/tcp"
```

### Issue: "Module not found" in logs

**Solution:**
```bash
# Make sure all dependencies are in requirements.txt
pip freeze > requirements.txt

# Redeploy
app-publisher deploy . --config deploy.local.yaml
```

## Next Steps

- Read [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md) for security best practices
- Read [USAGE.md](USAGE.md) for advanced configuration options
- Set up a reverse proxy (nginx) for HTTPS
- Configure a domain name for your app
- Set up monitoring and backups

## Getting Help

- Check [USAGE.md](USAGE.md) for detailed documentation
- Run `app-publisher --help` for command reference
- Run `app-publisher deploy --help` for deployment options
- Check the logs: `app-publisher logs user@server --name app-name`

## Security Reminders

- ✓ Never commit `deploy.local.yaml` or `.env` files to git
- ✓ Use SSH keys, not passwords
- ✓ Keep your SSH keys secure with proper permissions (600)
- ✓ Use strong passwords/passphrases for SSH keys
- ✓ Store secrets in environment variables, not in code
- ✓ Set up HTTPS for production deployments

Happy deploying! 🚀
