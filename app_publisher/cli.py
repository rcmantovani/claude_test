"""Command-line interface for app publisher."""

import os
import sys
import logging
import click
from colorama import init, Fore, Style
from .config import DeployConfig
from .deployer import Deployer

# Initialize colorama
init()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def parse_server_string(server_str: str) -> tuple:
    """
    Parse server string in format 'user@host:/path'.

    Returns:
        tuple: (user, host, remote_path)
    """
    try:
        user_host, remote_path = server_str.split(':')
        user, host = user_host.split('@')
        return user, host, remote_path
    except ValueError:
        raise click.BadParameter(
            "Server string must be in format 'user@host:/remote/path'"
        )


@click.group()
@click.version_option(version='0.1.0')
def main():
    """App Publisher - Deploy Python web applications to remote servers via SSH."""
    pass


@main.command()
@click.argument('local_path', type=click.Path(exists=True))
@click.argument('server', required=False)
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--app-type', '-t', type=click.Choice(['streamlit', 'flask']),
              help='Application type (streamlit or flask)')
@click.option('--port', '-p', type=int,
              help='Port to run the application on')
@click.option('--name', '-n',
              help='Application name (used for service name)')
@click.option('--ssh-port', type=int, default=22,
              help='SSH port (default: 22)')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def deploy(local_path, server, config, app_type, port, name, ssh_port, key_file, verbose):
    """
    Deploy an application to a remote server.

    Examples:

    \b
    # Using command-line arguments
    app-publisher deploy ./myapp user@server:/opt/apps/myapp \\
        --app-type streamlit --port 8501 --name myapp

    \b
    # Using a configuration file
    app-publisher deploy ./myapp --config deploy.yaml
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Load or create configuration
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif server and app_type and port and name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host,
                user=user,
                remote_path=remote_path,
                app_type=app_type,
                port=port,
                name=name,
                key_file=key_file,
                ssh_port=ssh_port
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or all of (server, --app-type, --port, --name) must be provided{Style.RESET_ALL}")
            sys.exit(1)

        # Create deployer and deploy
        deployer = Deployer(deploy_config, local_path)

        click.echo(f"\n{Fore.GREEN}Starting deployment...{Style.RESET_ALL}")
        click.echo(f"Local path: {Fore.YELLOW}{local_path}{Style.RESET_ALL}")
        click.echo(f"Remote: {Fore.YELLOW}{deploy_config.server.user}@{deploy_config.server.host}:{deploy_config.server.remote_path}{Style.RESET_ALL}")
        click.echo(f"App type: {Fore.YELLOW}{deploy_config.app.type}{Style.RESET_ALL}")
        click.echo(f"Port: {Fore.YELLOW}{deploy_config.app.port}{Style.RESET_ALL}\n")

        deployer.deploy()

        click.echo(f"\n{Fore.GREEN}✓ Deployment completed successfully!{Style.RESET_ALL}")
        click.echo(f"Your application should be accessible at: {Fore.CYAN}http://{deploy_config.server.host}:{deploy_config.app.port}{Style.RESET_ALL}\n")

    except Exception as e:
        click.echo(f"\n{Fore.RED}✗ Deployment failed: {e}{Style.RESET_ALL}\n")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.argument('server')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--name', '-n',
              help='Application name')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
def start(server, config, name, key_file):
    """Start the application service."""
    try:
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host, user=user, remote_path=remote_path,
                app_type='streamlit', port=8501, name=name,
                key_file=key_file
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or --name must be provided{Style.RESET_ALL}")
            sys.exit(1)

        deployer = Deployer(deploy_config, ".")
        deployer.start()
        click.echo(f"{Fore.GREEN}✓ Service started successfully{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to start service: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.argument('server')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--name', '-n',
              help='Application name')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
def stop(server, config, name, key_file):
    """Stop the application service."""
    try:
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host, user=user, remote_path=remote_path,
                app_type='streamlit', port=8501, name=name,
                key_file=key_file
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or --name must be provided{Style.RESET_ALL}")
            sys.exit(1)

        deployer = Deployer(deploy_config, ".")
        deployer.stop()
        click.echo(f"{Fore.GREEN}✓ Service stopped successfully{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to stop service: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.argument('server')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--name', '-n',
              help='Application name')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
def restart(server, config, name, key_file):
    """Restart the application service."""
    try:
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host, user=user, remote_path=remote_path,
                app_type='streamlit', port=8501, name=name,
                key_file=key_file
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or --name must be provided{Style.RESET_ALL}")
            sys.exit(1)

        deployer = Deployer(deploy_config, ".")
        deployer.restart()
        click.echo(f"{Fore.GREEN}✓ Service restarted successfully{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to restart service: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.argument('server')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--name', '-n',
              help='Application name')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
def status(server, config, name, key_file):
    """Check application status."""
    try:
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host, user=user, remote_path=remote_path,
                app_type='streamlit', port=8501, name=name,
                key_file=key_file
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or --name must be provided{Style.RESET_ALL}")
            sys.exit(1)

        deployer = Deployer(deploy_config, ".")
        deployer.status()

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to get status: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.argument('server')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to deployment configuration file')
@click.option('--name', '-n',
              help='Application name')
@click.option('--lines', '-l', type=int, default=50,
              help='Number of log lines to display (default: 50)')
@click.option('--key-file', '-k', type=click.Path(exists=True),
              help='Path to SSH private key file')
def logs(server, config, name, lines, key_file):
    """View application logs."""
    try:
        if config:
            deploy_config = DeployConfig.from_yaml(config)
        elif name:
            user, host, remote_path = parse_server_string(server)
            deploy_config = DeployConfig.from_cli_args(
                host=host, user=user, remote_path=remote_path,
                app_type='streamlit', port=8501, name=name,
                key_file=key_file
            )
        else:
            click.echo(f"{Fore.RED}Error: Either --config or --name must be provided{Style.RESET_ALL}")
            sys.exit(1)

        deployer = Deployer(deploy_config, ".")
        deployer.logs(lines=lines)

    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to get logs: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
