import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID"),
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()  


def list_workshops():
    """Fetch upcoming workshops from the database or return mock data."""
    try:
        workshops_ref = db.child("workshops").get()
        workshops = workshops_ref.val()

        if not workshops:
            print("⚠️ No workshops found in the database.")
            return []

        workshops_list = []
        for workshop_id, workshop_data in workshops.items():
            if not all(k in workshop_data for k in ["title", "date", "mentor"]):
                print(f"⚠️ Skipping invalid workshop data: {workshop_data}")
                continue

            workshops_list.append({
                "title": workshop_data["title"],
                "date": workshop_data["date"],
                "mentor": workshop_data["mentor"],
            })

        return workshops_list

    except Exception as e:
        print("❌ Error fetching workshops:", e)
        return []
    
def get_available_mentors(date, logged_in_user):
    """Fetch available mentors for a given date."""
    users_ref = db.child("users").order_by_child("role").equal_to("mentor").get(logged_in_user['idToken'])
    available_mentors = []

    print(f"Searching for mentors available on: {date}") 
    for user in users_ref.each():
        mentor_data = user.val()
        print(f"Checking mentor: {mentor_data.get('name', 'N/A')}, Email: {mentor_data.get('email', 'N/A')}") 

        if "availability" in mentor_data:
            print(f"Mentor has availability data") 
            if date in mentor_data["availability"]:
                print(f"Mentor is available on {date}") 
                available_mentors.append({
                    "name": mentor_data["name"],
                    "email": mentor_data["email"],
                })
        else:
            print(f"Mentor has NO availability data") # Debugging

    print(f"Found available mentors: {available_mentors}")  # Debugging
    return available_mentors

def get_available_peers(date, logged_in_user):
    """Fetch available peers for a given date."""
    users_ref = db.child("users").order_by_child("role").equal_to("peer").get(logged_in_user['idToken'])
    
    available_peers = []
    for user in users_ref.each():
        peer_data = user.val()
        
        if "availability" in peer_data and date in peer_data["availability"]:
            available_peers.append({
                "name": peer_data["name"],
                "email": peer_data["email"],
            })

    return available_peers