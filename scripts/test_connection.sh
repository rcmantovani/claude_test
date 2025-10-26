#!/bin/bash
# Test SSH connection before deployment

set -e

echo "=================================="
echo "SSH Connection Test"
echo "=================================="
echo ""

read -p "Server hostname or IP: " HOST
read -p "SSH username: " USER
read -p "SSH key path [~/.ssh/id_rsa]: " KEY_FILE
KEY_FILE=${KEY_FILE:-~/.ssh/id_rsa}

# Expand tilde
KEY_FILE="${KEY_FILE/#\~/$HOME}"

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file $KEY_FILE does not exist"
    exit 1
fi

echo ""
echo "Testing connection to $USER@$HOST..."
echo ""

# Test basic SSH connection
echo "1. Testing basic SSH connection..."
if ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o BatchMode=yes "$USER@$HOST" "echo 'Connection successful!'" 2>/dev/null; then
    echo "   ✓ SSH connection works!"
else
    echo "   ✗ SSH connection failed!"
    echo ""
    echo "Troubleshooting:"
    echo "- Check that the server is reachable: ping $HOST"
    echo "- Verify SSH key: ssh-keygen -l -f $KEY_FILE"
    echo "- Check key permissions: ls -l $KEY_FILE"
    echo "- Try manual connection: ssh -i $KEY_FILE $USER@$HOST"
    exit 1
fi

echo ""
echo "2. Checking Python installation..."
if PYTHON_VERSION=$(ssh -i "$KEY_FILE" "$USER@$HOST" "python3 --version" 2>/dev/null); then
    echo "   ✓ Python found: $PYTHON_VERSION"
else
    echo "   ✗ Python3 not found on remote server"
    exit 1
fi

echo ""
echo "3. Checking pip installation..."
if PIP_VERSION=$(ssh -i "$KEY_FILE" "$USER@$HOST" "pip3 --version" 2>/dev/null); then
    echo "   ✓ pip found: $(echo $PIP_VERSION | cut -d' ' -f1-2)"
else
    echo "   ⚠ pip3 not found - will need to install"
fi

echo ""
echo "4. Checking systemd..."
if ssh -i "$KEY_FILE" "$USER@$HOST" "systemctl --version" &>/dev/null; then
    echo "   ✓ systemd is available"
else
    echo "   ✗ systemd not found - service management may not work"
fi

echo ""
echo "5. Checking sudo access..."
if ssh -i "$KEY_FILE" "$USER@$HOST" "sudo -n true" 2>/dev/null; then
    echo "   ✓ Passwordless sudo is configured"
else
    echo "   ⚠ sudo requires password - deployment will prompt for password"
fi

echo ""
echo "=================================="
echo "✓ Connection test complete!"
echo "=================================="
echo ""
echo "Your server appears ready for deployment."
echo "Run: app-publisher deploy <app-dir> --config <config-file>"
echo ""
