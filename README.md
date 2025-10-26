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
pip install -e .
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

- Python 3.7+
- SSH access to remote server
- Remote server with Python installed

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

## License

MIT
