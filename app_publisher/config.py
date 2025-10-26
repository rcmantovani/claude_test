"""Configuration management for app publisher."""

import os
import yaml
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str
    user: str
    remote_path: str
    port: int = 22
    key_file: Optional[str] = None
    password: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration."""
    type: str  # 'streamlit' or 'flask'
    port: int
    name: str
    python_version: str = "python3"
    environment_vars: Dict[str, str] = field(default_factory=dict)
    requirements_file: str = "requirements.txt"


@dataclass
class DeployConfig:
    """Complete deployment configuration."""
    server: ServerConfig
    app: AppConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeployConfig':
        """Create config from dictionary."""
        server_data = data.get('server', {})
        app_data = data.get('app', {})

        server = ServerConfig(
            host=server_data.get('host', ''),
            user=server_data.get('user', ''),
            remote_path=server_data.get('remote_path', ''),
            port=server_data.get('port', 22),
            key_file=server_data.get('key_file'),
            password=server_data.get('password')
        )

        app = AppConfig(
            type=app_data.get('type', 'streamlit'),
            port=app_data.get('port', 8501),
            name=app_data.get('name', 'myapp'),
            python_version=app_data.get('python_version', 'python3'),
            environment_vars=app_data.get('environment_vars', {}),
            requirements_file=app_data.get('requirements_file', 'requirements.txt')
        )

        return cls(server=server, app=app)

    @classmethod
    def from_yaml(cls, file_path: str) -> 'DeployConfig':
        """Load configuration from YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_cli_args(cls, host: str, user: str, remote_path: str,
                     app_type: str, port: int, name: str,
                     key_file: Optional[str] = None,
                     ssh_port: int = 22) -> 'DeployConfig':
        """Create config from CLI arguments."""
        server = ServerConfig(
            host=host,
            user=user,
            remote_path=remote_path,
            port=ssh_port,
            key_file=key_file
        )

        app = AppConfig(
            type=app_type,
            port=port,
            name=name
        )

        return cls(server=server, app=app)

    def to_yaml(self, file_path: str):
        """Save configuration to YAML file."""
        data = {
            'server': {
                'host': self.server.host,
                'user': self.server.user,
                'remote_path': self.server.remote_path,
                'port': self.server.port,
            },
            'app': {
                'type': self.app.type,
                'port': self.app.port,
                'name': self.app.name,
                'python_version': self.app.python_version,
                'environment_vars': self.app.environment_vars,
                'requirements_file': self.app.requirements_file,
            }
        }

        if self.server.key_file:
            data['server']['key_file'] = self.server.key_file

        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
