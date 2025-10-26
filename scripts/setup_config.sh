#!/bin/bash
# Helper script to create a secure deployment configuration
# This script will prompt for values and create a properly secured config file

set -e

echo "=================================="
echo "App Publisher - Configuration Setup"
echo "=================================="
echo ""

# Determine script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Prompt for deployment directory
echo "Where is your application located?"
read -p "Application directory [$(pwd)]: " APP_DIR
APP_DIR=${APP_DIR:-$(pwd)}

if [ ! -d "$APP_DIR" ]; then
    echo "Error: Directory $APP_DIR does not exist"
    exit 1
fi

echo ""
echo "--- Server Configuration ---"
read -p "Server hostname or IP: " HOST
read -p "SSH username: " USER
read -p "Remote deployment path (e.g., /opt/apps/myapp): " REMOTE_PATH
read -p "SSH port [22]: " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

echo ""
echo "--- SSH Authentication ---"
echo "1) SSH key (recommended)"
echo "2) Password (not recommended for production)"
read -p "Authentication method [1]: " AUTH_METHOD
AUTH_METHOD=${AUTH_METHOD:-1}

if [ "$AUTH_METHOD" = "1" ]; then
    read -p "Path to SSH private key [~/.ssh/id_rsa]: " KEY_FILE
    KEY_FILE=${KEY_FILE:-~/.ssh/id_rsa}

    # Expand tilde
    KEY_FILE="${KEY_FILE/#\~/$HOME}"

    if [ ! -f "$KEY_FILE" ]; then
        echo "Warning: Key file $KEY_FILE does not exist"
        read -p "Continue anyway? [y/N]: " CONTINUE
        if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
            exit 1
        fi
    fi

    # Check key permissions
    if [ -f "$KEY_FILE" ]; then
        PERMS=$(stat -c %a "$KEY_FILE" 2>/dev/null || stat -f %A "$KEY_FILE" 2>/dev/null || echo "000")
        if [ "$PERMS" != "600" ]; then
            echo "Warning: SSH key should have 600 permissions"
            read -p "Fix permissions now? [Y/n]: " FIX_PERMS
            if [ "$FIX_PERMS" != "n" ] && [ "$FIX_PERMS" != "N" ]; then
                chmod 600 "$KEY_FILE"
                echo "Permissions fixed: chmod 600 $KEY_FILE"
            fi
        fi
    fi
fi

echo ""
echo "--- Application Configuration ---"
echo "1) Streamlit"
echo "2) Flask"
read -p "Application type [1]: " APP_TYPE_NUM
APP_TYPE_NUM=${APP_TYPE_NUM:-1}

if [ "$APP_TYPE_NUM" = "1" ]; then
    APP_TYPE="streamlit"
    DEFAULT_PORT=8501
else
    APP_TYPE="flask"
    DEFAULT_PORT=5000
fi

read -p "Application port [$DEFAULT_PORT]: " APP_PORT
APP_PORT=${APP_PORT:-$DEFAULT_PORT}

read -p "Application name (used for systemd service): " APP_NAME
if [ -z "$APP_NAME" ]; then
    APP_NAME=$(basename "$APP_DIR")
fi

read -p "Python version on remote server [python3]: " PYTHON_VERSION
PYTHON_VERSION=${PYTHON_VERSION:-python3}

echo ""
echo "--- Environment Variables (Optional) ---"
echo "Add environment variables for your application? (e.g., API keys, database URLs)"
read -p "Add environment variables? [y/N]: " ADD_ENV_VARS

ENV_VARS=""
if [ "$ADD_ENV_VARS" = "y" ] || [ "$ADD_ENV_VARS" = "Y" ]; then
    echo "Enter environment variables (one per line, format: KEY=value)"
    echo "Press Ctrl+D when done"
    ENV_VARS_YAML="  environment_vars:"
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            KEY=$(echo "$line" | cut -d'=' -f1)
            VALUE=$(echo "$line" | cut -d'=' -f2-)
            ENV_VARS_YAML="$ENV_VARS_YAML"$'\n'"    $KEY: \"$VALUE\""
        fi
    done
    ENV_VARS=$ENV_VARS_YAML
else
    ENV_VARS="  environment_vars: {}"
fi

echo ""
echo "--- Configuration Output ---"
read -p "Save as [deploy.local.yaml]: " CONFIG_FILE
CONFIG_FILE=${CONFIG_FILE:-deploy.local.yaml}

CONFIG_PATH="$APP_DIR/$CONFIG_FILE"

# Create the configuration file
cat > "$CONFIG_PATH" << EOF
# Auto-generated deployment configuration
# Created: $(date)
# KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

server:
  host: $HOST
  user: $USER
  remote_path: $REMOTE_PATH
  port: $SSH_PORT
EOF

if [ "$AUTH_METHOD" = "1" ]; then
    echo "  key_file: $KEY_FILE" >> "$CONFIG_PATH"
else
    echo "  # password: SET_YOUR_PASSWORD_HERE" >> "$CONFIG_PATH"
fi

cat >> "$CONFIG_PATH" << EOF

app:
  type: $APP_TYPE
  port: $APP_PORT
  name: $APP_NAME
  python_version: $PYTHON_VERSION
  requirements_file: requirements.txt
EOF

if [ -n "$ENV_VARS" ]; then
    echo "$ENV_VARS" >> "$CONFIG_PATH"
fi

# Secure the configuration file
chmod 600 "$CONFIG_PATH"

echo ""
echo "=================================="
echo "✓ Configuration created successfully!"
echo "=================================="
echo ""
echo "Config file: $CONFIG_PATH"
echo "Permissions: $(ls -l "$CONFIG_PATH" | awk '{print $1}')"
echo ""
echo "Next steps:"
echo "1. Review the configuration: cat $CONFIG_PATH"
echo "2. Test SSH connection: ssh -i $KEY_FILE $USER@$HOST"
echo "3. Deploy your app: app-publisher deploy $APP_DIR --config $CONFIG_PATH"
echo ""
echo "⚠️  IMPORTANT: This file contains secrets. Never commit it to git!"
echo "The file is already in .gitignore as: $CONFIG_FILE"
echo ""
