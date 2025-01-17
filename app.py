import click
from auth import signup, login
from firebase_config import firebase

@click.group()
def cli():
    """Main entry point for the CLI"""
    pass

cli.add_command(signup)
cli.add_command(login)

if __name__ == '__main__':
    cli()
