import click
import pwinput
from firebase_config import auth_service, get_firestore_client
from users import save_user_role
from verification import check_password_strength
from requests.exceptions import HTTPError


@click.command()
@click.argument('email')
def signup(email):
    """Signs up a new user."""
    password = pwinput.pwinput(prompt="Password: ")
    if not check_password_strength(password):
        click.echo("Password is weak. Try again with a stronger password.")
        return
    try:

        user = auth_service().create_user_with_email_and_password(email, password)
        uid = user['localId']
        role = click.prompt("Enter your role (mentor/peer)", type=str)
        save_user_role(uid, role, get_firestore_client())  # Pass Firestore client
        click.echo(f"Account created successfully with role: {role}")
    except HTTPError as e:
       error = e.args[1]
       if "EMAIL_EXISTS" in error:
            click.echo("An account with this email already exists. Please use a different email or log in.")
       else:
            click.echo(f"An error occurred: {error}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")


@click.command()
@click.argument('email')
def login(email):
    """Logs in an existing user."""
    password = pwinput.pwinput(prompt="Password: ")
    try:
        user = auth_service().sign_in_with_email_and_password(email, password)
        click.echo("Login successful!")
        # Store the UID for later use (if needed)
        uid = user['localId']
        click.echo(f"User UID: {uid}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")