import click
from firebase_admin import firestore
from firebase_config import firebase
import firebase_admin
import sys
from firebase_admin import credentials

# cred = credentials.ertificate('path_to_service_account_key.json')
# firebase_admin.initialize_app(cred)
db = firestore.client()

def save_user_role(uid, role):
    """
    Save users role
    """
    if role not in ["mentor", "peer"]:
        click.echo("Invalid role. Please choose either 'mentor' or 'peer'.")
        sys.exit(1)
    
    try:
        user_ref = db.collection("users").document(uid)
        user_ref.set({
            "role": role
        })
        click.echo(f"Role '{role}' assigned to user")
        return
    except Exception as e:
        click.echo(f"Error saving user role: {e}")
        sys.exit(1)
        
def get_user_by_email(email):
    """
    Get user by email using firebase admin sdk
    """
    try:
      user = firebase_admin.auth.get_user_by_email(email)
      return user
    except Exception as e:
      click.echo(f"Error getting user by email: {e}")
      sys.exit(1)