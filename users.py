import click
# from firebase_admin import firestore
# from firebase_config import firebase
import firebase_admin
import sys
# from firebase_admin import credentials

# cred = credentials.ertificate('path_to_service_account_key.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

def save_user_role(uid,email,name, role, db):
    """
    Save users role
    """
    if role not in ["mentor", "peer"]:
        click.echo("Invalid role. Please choose either 'mentor' or 'peer'.")
        sys.exit(1)

    try:
        availability = {}
        for hour in range(7, 18):
            availability[f"{hour:02d}:00"] = True

        user_ref = db.collection("Users").document(uid)
        user_ref.set({
            "name": name,
            "email": email,
            "role": role,
            "availability": availability
        })
        click.echo(f"User details for '{email}' saved")

    except Exception as e:
        click.echo(f"Error saving user details: {e}")
        sys.exit(1)

def get_user_by_email(email):

    try:
        user = firebase_admin.auth.get_user_by_email(email)
        return user
    
    except Exception as e:
      click.echo(f"Error getting user by email: {e}")
      sys.exit(1)

def book_mentor(mentor_uid, peer_id, booking_time, db):
    #Book a mentor if they are available 

    try:
        mentor_ref = db.collection("Users").document(mentor_uid)
        mentor_doc = mentor_ref.get()
        if not mentor_doc.exists:
            click.echo(f"Mentor with UID {mentor_uid} not found")
            return False
        
        mentor_data = mentor_doc.to_dict()
        availability = mentor_data.get("availability")
        if not availability:
            click.echo
    except Exception as e:
        click.echo(f"An error occurred: {e}")
