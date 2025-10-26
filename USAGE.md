# Usage Guide

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd app-publisher
pip install -e .
```

### 2. Prepare Your Application

Your application should have:
- Main application file (e.g., `app.py`)
- `requirements.txt` file with dependencies
- For Streamlit: Entry point should be the file you want to run
- For Flask: Application variable should be named `app`

### 3. Deploy

#### Option A: Using Configuration File

Create `deploy.yaml`:

```yaml
server:
  host: 192.168.1.100
  user: ubuntu
  remote_path: /opt/apps/myapp
  port: 22
  key_file: ~/.ssh/id_rsa  # Optional

app:
  type: streamlit  # or flask
  port: 8501
  name: my-awesome-app
  python_version: python3
  requirements_file: requirements.txt
  environment_vars:
    MY_VAR: "value"
```

Deploy:
```bash
app-publisher deploy /path/to/your/app --config deploy.yaml
```

#### Option B: Using Command-Line Arguments

```bash
app-publisher deploy /path/to/your/app user@server:/remote/path \
  --app-type streamlit \
  --port 8501 \
  --name my-app
```

## Managing Your Deployment

### Check Status

```bash
app-publisher status user@server --name my-app
```

### View Logs

```bash
# Last 50 lines (default)
app-publisher logs user@server --name my-app

# Custom number of lines
app-publisher logs user@server --name my-app --lines 100
```

### Control Service

```bash
# Start
app-publisher start user@server --name my-app

# Stop
app-publisher stop user@server --name my-app

# Restart
app-publisher restart user@server --name my-app
```

## Advanced Usage

### Custom SSH Key

```bash
app-publisher deploy ./app user@server:/path \
  --app-type flask \
  --port 5000 \
  --name myapp \
  --key-file ~/.ssh/custom_key
```

### Environment Variables

In `deploy.yaml`:

```yaml
app:
  environment_vars:
    DATABASE_URL: "postgresql://..."
    API_KEY: "secret-key"
    DEBUG: "false"
```

### Different Python Version

```yaml
app:
  python_version: python3.11
```

## Troubleshooting

### Permission Issues

If you get permission errors during deployment, ensure:
1. SSH user has sudo privileges
2. Remote paths are writable
3. SSH key has correct permissions (600)

```bash
chmod 600 ~/.ssh/id_rsa
```

### Service Not Starting

Check logs:
```bash
app-publisher logs user@server --name myapp
```

Check systemd status directly:
```bash
ssh user@server "sudo systemctl status myapp.service"
```

### Port Already in Use

Change the port in your configuration:
```yaml
app:
  port: 8502  # Use a different port
```

### Dependencies Installation Fails

Ensure `requirements.txt` is in the application directory and properly formatted.

## Server Requirements

Your remote server needs:
- Python 3.7 or higher
- `systemd` (for service management)
- `pip` and `venv` module
- Sufficient disk space
- Open firewall for your application port

## Security Considerations

1. **Use SSH Keys**: Prefer key-based authentication over passwords
2. **Firewall**: Configure firewall to only allow necessary ports
3. **Environment Variables**: Store secrets in environment variables, not in code
4. **HTTPS**: Consider setting up a reverse proxy (nginx/Apache) with SSL
5. **User Permissions**: Run services as non-root users

## Example Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Tips

1. **Test Locally First**: Always test your application locally before deploying
2. **Version Control**: Keep your `deploy.yaml` in version control (without secrets)
3. **Backups**: Backup your remote application directory before updates
4. **Monitoring**: Set up monitoring for your application
5. **Updates**: To update, simply run deploy again - it will overwrite files and restart the service
