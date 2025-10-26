"""Application deployment logic."""

import os
import logging
from typing import Optional
from .ssh_client import SSHClient
from .config import DeployConfig

logger = logging.getLogger(__name__)


class Deployer:
    """Handles application deployment to remote server."""

    def __init__(self, config: DeployConfig, local_path: str):
        """
        Initialize deployer.

        Args:
            config: Deployment configuration
            local_path: Path to local application directory
        """
        self.config = config
        self.local_path = local_path
        self.ssh_client: Optional[SSHClient] = None

    def deploy(self):
        """Execute full deployment process."""
        logger.info("Starting deployment...")

        # Connect to server
        self._connect()

        try:
            # Upload application files
            self._upload_files()

            # Setup Python environment
            self._setup_environment()

            # Install dependencies
            self._install_dependencies()

            # Create systemd service
            self._create_service()

            # Start service
            self._start_service()

            logger.info("Deployment completed successfully!")

        finally:
            self._disconnect()

    def start(self):
        """Start the application service."""
        self._connect()
        try:
            self._start_service()
        finally:
            self._disconnect()

    def stop(self):
        """Stop the application service."""
        self._connect()
        try:
            self._stop_service()
        finally:
            self._disconnect()

    def restart(self):
        """Restart the application service."""
        self._connect()
        try:
            self._restart_service()
        finally:
            self._disconnect()

    def status(self):
        """Check application status."""
        self._connect()
        try:
            service_name = f"{self.config.app.name}.service"
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"systemctl status {service_name}"
            )
            print(stdout)
            if stderr:
                print(f"Errors: {stderr}")
        finally:
            self._disconnect()

    def logs(self, lines: int = 50):
        """View application logs."""
        self._connect()
        try:
            service_name = f"{self.config.app.name}.service"
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"journalctl -u {service_name} -n {lines} --no-pager"
            )
            print(stdout)
            if stderr:
                print(f"Errors: {stderr}")
        finally:
            self._disconnect()

    def _connect(self):
        """Establish SSH connection."""
        self.ssh_client = SSHClient(
            hostname=self.config.server.host,
            username=self.config.server.user,
            port=self.config.server.port,
            key_filename=self.config.server.key_file,
            password=self.config.server.password
        )
        self.ssh_client.connect()

    def _disconnect(self):
        """Close SSH connection."""
        if self.ssh_client:
            self.ssh_client.disconnect()

    def _upload_files(self):
        """Upload application files to remote server."""
        logger.info(f"Uploading files from {self.local_path} to {self.config.server.remote_path}")

        exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            '.venv',
            'venv',
            'env',
            '.env',
            '*.egg-info',
            '.DS_Store'
        ]

        self.ssh_client.upload_directory(
            self.local_path,
            self.config.server.remote_path,
            exclude_patterns=exclude_patterns
        )

    def _setup_environment(self):
        """Setup Python virtual environment on remote server."""
        logger.info("Setting up Python environment...")

        remote_path = self.config.server.remote_path
        python_version = self.config.app.python_version

        # Check if venv exists, create if not
        commands = [
            f"cd {remote_path}",
            f"if [ ! -d venv ]; then {python_version} -m venv venv; fi"
        ]

        exit_code, stdout, stderr = self.ssh_client.execute_command(" && ".join(commands))

        if exit_code != 0:
            raise RuntimeError(f"Failed to setup environment: {stderr}")

    def _install_dependencies(self):
        """Install Python dependencies on remote server."""
        logger.info("Installing dependencies...")

        remote_path = self.config.server.remote_path
        requirements_file = self.config.app.requirements_file

        commands = [
            f"cd {remote_path}",
            "source venv/bin/activate",
            f"pip install --upgrade pip",
            f"pip install -r {requirements_file}"
        ]

        exit_code, stdout, stderr = self.ssh_client.execute_command(" && ".join(commands))

        if exit_code != 0:
            raise RuntimeError(f"Failed to install dependencies: {stderr}")

        logger.info("Dependencies installed successfully")

    def _create_service(self):
        """Create systemd service file."""
        logger.info("Creating systemd service...")

        service_content = self._generate_service_file()
        service_name = f"{self.config.app.name}.service"
        service_path = f"/tmp/{service_name}"

        # Create service file on remote server
        escaped_content = service_content.replace("'", "'\\''")
        self.ssh_client.execute_command(f"echo '{escaped_content}' > {service_path}")

        # Move to systemd directory (requires sudo)
        commands = [
            f"sudo mv {service_path} /etc/systemd/system/{service_name}",
            "sudo systemctl daemon-reload",
            f"sudo systemctl enable {service_name}"
        ]

        for cmd in commands:
            exit_code, stdout, stderr = self.ssh_client.execute_command(cmd)
            if exit_code != 0:
                logger.warning(f"Command '{cmd}' returned non-zero exit code: {stderr}")

        logger.info("Service created successfully")

    def _generate_service_file(self) -> str:
        """Generate systemd service file content."""
        app_type = self.config.app.type
        remote_path = self.config.server.remote_path
        port = self.config.app.port
        service_name = self.config.app.name

        # Build environment variables
        env_vars = []
        for key, value in self.config.app.environment_vars.items():
            env_vars.append(f'Environment="{key}={value}"')

        env_vars_str = "\n".join(env_vars) if env_vars else ""

        # Determine the command based on app type
        if app_type == "streamlit":
            exec_cmd = f"{remote_path}/venv/bin/streamlit run app.py --server.port={port} --server.address=0.0.0.0"
        elif app_type == "flask":
            exec_cmd = f"{remote_path}/venv/bin/flask run --host=0.0.0.0 --port={port}"
            env_vars_str += f'\nEnvironment="FLASK_APP=app.py"'
        else:
            raise ValueError(f"Unsupported app type: {app_type}")

        service_content = f"""[Unit]
Description={service_name} - Python {app_type.capitalize()} Application
After=network.target

[Service]
Type=simple
User={self.config.server.user}
WorkingDirectory={remote_path}
ExecStart={exec_cmd}
Restart=always
RestartSec=10
{env_vars_str}

[Install]
WantedBy=multi-user.target
"""
        return service_content

    def _start_service(self):
        """Start the application service."""
        logger.info("Starting service...")
        service_name = f"{self.config.app.name}.service"
        exit_code, stdout, stderr = self.ssh_client.execute_command(
            f"sudo systemctl start {service_name}"
        )
        if exit_code != 0:
            raise RuntimeError(f"Failed to start service: {stderr}")
        logger.info("Service started successfully")

    def _stop_service(self):
        """Stop the application service."""
        logger.info("Stopping service...")
        service_name = f"{self.config.app.name}.service"
        exit_code, stdout, stderr = self.ssh_client.execute_command(
            f"sudo systemctl stop {service_name}"
        )
        if exit_code != 0:
            raise RuntimeError(f"Failed to stop service: {stderr}")
        logger.info("Service stopped successfully")

    def _restart_service(self):
        """Restart the application service."""
        logger.info("Restarting service...")
        service_name = f"{self.config.app.name}.service"
        exit_code, stdout, stderr = self.ssh_client.execute_command(
            f"sudo systemctl restart {service_name}"
        )
        if exit_code != 0:
            raise RuntimeError(f"Failed to restart service: {stderr}")
        logger.info("Service restarted successfully")
