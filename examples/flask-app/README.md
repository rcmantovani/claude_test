# Example Flask Application

This is a sample Flask application that demonstrates the app-publisher tool.

## Local Testing

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

## Deployment

### Option 1: Using configuration file

1. Edit `deploy.yaml` with your server details
2. Deploy:
```bash
app-publisher deploy . --config deploy.yaml
```

### Option 2: Using command-line arguments

```bash
app-publisher deploy . user@your-server.com:/opt/apps/flask-app \
  --app-type flask \
  --port 5000 \
  --name flask-app
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/data` - Returns random JSON data
- `GET /health` - Health check endpoint

## After Deployment

Check status:
```bash
app-publisher status user@your-server.com --name flask-app
```

View logs:
```bash
app-publisher logs user@your-server.com --name flask-app
```

Restart the app:
```bash
app-publisher restart user@your-server.com --name flask-app
```

Access your app at: `http://your-server.com:5000`
