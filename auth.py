import click
import pwinput
from firebase_config import auth
from users import save_user_role
from verification import check_password_strength

def signup(email):
    """Signs up a new user."""
    password = pwinput.pwinput(prompt="Password: ")
    if not check_password_strength(password):
        click.echo("Password is weak. Try again with a stronger password.")
        return

    try:
        user = auth.create_user_with_email_and_password(email, password)
        uid = user['localId']
        role = click.prompt("Enter your role (mentor/peer)", type=str)
        save_user_role(uid, role)  # Save role to Firestore
        click.echo(f"Account created successfully with role: {role}")
    except Exception as e:
        click.echo(f"Error: {e}")

def login(email):
    """Logs in an existing user."""
    password = pwinput.pwinput(prompt="Password: ")
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        click.echo("Login successful!")
        # Store the UID for later use (if needed)
        uid = user['localId']
        click.echo(f"User UID: {uid}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
