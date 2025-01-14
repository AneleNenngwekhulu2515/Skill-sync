import pyrebase
import os
import click
from dotenv import load_dotenv
import pwinput

load_dotenv()


firebaseConfig = {
    'apiKey': os.getenv('API_KEY'),
    'authDomain': os.getenv('AUTH_DOMAIN'),
    'projectId': os.getenv('PROJECT_ID'),
    'storageBucket': os.getenv('STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('MESSAGING_SENDER_ID'),
    'appId': os.getenv('APP_ID'),
    'measurementId': os.getenv('MEASUREMENT_ID'),
    'databaseURL': os.getenv('DATABASE_URL')
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

@click.command()
@click.option('--email', prompt='Email', help='The email for the user')
def signup(email):
    """Signs up a new user."""
    password = pwinput.pwinput(prompt="Password: ")
    try:
        user = auth.create_user_with_email_and_password(email, password)
        click.echo("Account created successfully!")
    except Exception as e:
        if 'EMAIL_EXISTS' in str(e):
            click.echo("User already exists with this email!")
        elif 'WEAK_PASSWORD' in str(e):
            click.echo("The password is too weak. Please use a stronger password.")
        else:
            click.echo(f"An error occurred while creating the user: {e}")

@click.command()
@click.option('--email', prompt='Email', help='The email for the user')
def login(email):
    """Logs in an existing user."""
    password = pwinput.pwinput(prompt="Password: ")
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        click.echo("Login successful!")
    except Exception as e:
        if 'INVALID_PASSWORD' in str(e) or 'EMAIL_NOT_FOUND' in str(e):
            click.echo("Invalid email or password. Please check your credentials.")
        else:
            click.echo(f"An error occurred while logging in: {e}")
            

@click.group()
def cli():
    """A simple CLI for user authentication with Firebase."""
    pass

cli.add_command(signup)
cli.add_command(login)

if __name__ == '__main__':
    cli()