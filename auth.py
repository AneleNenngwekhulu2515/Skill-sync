import click
import pwinput
from firebase_config import get_firestore_client 
from users import save_user_role 
from verification import check_password_strength
from requests.exceptions import HTTPError


def signup(email, auth):  # Added auth argument
    """Signs up a new user."""
    password = pwinput.pwinput(prompt="Password: ")
    if not check_password_strength(password):
        click.echo("Password is weak. Try again with a stronger password.")
        return
    try:
        user = auth.create_user_with_email_and_password(email, password)  # Use auth directly
        uid = user['localId']
        name = click.prompt("Enter your name", type=str)

        while True:
            role = click.prompt("Enter your role (mentor/peer)", type=str)
            if role in ["mentor", "peer"]:
                break
            else:
                click.echo("Invalid role. Please enter 'mentor' or 'peer'.")
        db = get_firestore_client()
        if db:
            save_user_role(uid, email, name, role, db)
            click.echo(f"Account created successfully with role: {role}")
        else:
            click.echo("Failed to initialize Firestore client, cannot save the user details.")

    except HTTPError as e:
        error = e.args[1]
        if "EMAIL_EXISTS" in error:
            click.echo("An account with this email already exists. Please use a different email or log in.")
        else:
            click.echo(f"An error occurred: {error}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")


def login(email, auth): 
    """Logs in an existing user."""
    password = pwinput.pwinput(prompt="Password: ")
    try:
        user = auth.sign_in_with_email_and_password(email, password)  # Use auth directly
        click.echo("Login successful!")
        uid = user['localId']
        click.echo(f"User UID: {uid}")

        db = get_firestore_client()
        if db:
            user_doc = db.collection("Users").document(uid).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                role = user_data.get("role")
                click.echo(f"User Role: {role}")
            else:
                click.echo("User details not found in Firestore.")
        else:
            click.echo("Failed to initialize Firestore client, cannot retrieve users role")


    except Exception as e: 
        click.echo(f"An error occurred: {e}")       