# Example Streamlit Application

This is a sample Streamlit dashboard application that demonstrates the app-publisher tool.

## Local Testing

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

### Option 1: Using configuration file

1. Edit `deploy.yaml` with your server details
2. Deploy:
```bash
app-publisher deploy . --config deploy.yaml
```

### Option 2: Using command-line arguments

```bash
app-publisher deploy . user@your-server.com:/opt/apps/streamlit-dashboard \
  --app-type streamlit \
  --port 8501 \
  --name streamlit-dashboard
```

## After Deployment

Check status:
```bash
app-publisher status user@your-server.com --name streamlit-dashboard
```

View logs:
```bash
app-publisher logs user@your-server.com --name streamlit-dashboard
```

Access your app at: `http://your-server.com:8501`
