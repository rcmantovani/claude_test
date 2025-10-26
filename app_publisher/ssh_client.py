"""SSH client for file transfer and remote command execution."""

import os
import paramiko
from scp import SCPClient
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SSHClient:
    """Handles SSH connections and operations."""

    def __init__(self, hostname: str, username: str, port: int = 22,
                 key_filename: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize SSH client.

        Args:
            hostname: Remote server hostname or IP
            username: SSH username
            port: SSH port (default: 22)
            key_filename: Path to SSH private key file
            password: SSH password (if not using key auth)
        """
        self.hostname = hostname
        self.username = username
        self.port = port
        self.key_filename = key_filename
        self.password = password
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self):
        """Establish SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs = {
                'hostname': self.hostname,
                'username': self.username,
                'port': self.port,
            }

            if self.key_filename:
                connect_kwargs['key_filename'] = self.key_filename
            elif self.password:
                connect_kwargs['password'] = self.password
            else:
                # Try to use SSH agent
                connect_kwargs['allow_agent'] = True

            self.client.connect(**connect_kwargs)
            logger.info(f"Connected to {self.username}@{self.hostname}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from server")

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on the remote server.

        Args:
            command: Command to execute

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            raise RuntimeError("Not connected to server")

        logger.debug(f"Executing: {command}")
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        stdout_str = stdout.read().decode('utf-8')
        stderr_str = stderr.read().decode('utf-8')

        if exit_code != 0:
            logger.warning(f"Command failed with exit code {exit_code}")
            logger.warning(f"stderr: {stderr_str}")

        return exit_code, stdout_str, stderr_str

    def upload_directory(self, local_path: str, remote_path: str,
                        exclude_patterns: Optional[List[str]] = None):
        """
        Upload a directory to the remote server.

        Args:
            local_path: Local directory path
            remote_path: Remote directory path
            exclude_patterns: List of patterns to exclude (e.g., ['__pycache__', '*.pyc'])
        """
        if not self.client:
            raise RuntimeError("Not connected to server")

        exclude_patterns = exclude_patterns or []

        # Create remote directory
        self.execute_command(f"mkdir -p {remote_path}")

        def should_exclude(path: str) -> bool:
            """Check if path matches any exclude pattern."""
            for pattern in exclude_patterns:
                if pattern in path or path.endswith(pattern.replace('*', '')):
                    return True
            return False

        with SCPClient(self.client.get_transport()) as scp:
            for root, dirs, files in os.walk(local_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(d)]

                # Calculate relative path
                rel_root = os.path.relpath(root, local_path)
                if rel_root == '.':
                    remote_root = remote_path
                else:
                    remote_root = os.path.join(remote_path, rel_root).replace('\\', '/')

                # Create remote directory structure
                if rel_root != '.':
                    self.execute_command(f"mkdir -p {remote_root}")

                # Upload files
                for file in files:
                    if should_exclude(file):
                        continue

                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(remote_root, file).replace('\\', '/')

                    logger.info(f"Uploading: {local_file} -> {remote_file}")
                    scp.put(local_file, remote_file)

        logger.info(f"Successfully uploaded {local_path} to {remote_path}")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
