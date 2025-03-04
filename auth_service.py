import os
import pyrebase
from dotenv import load_dotenv
from verification import check_password_strength

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID"),
    "measurementId": os.getenv("MEASUREMENT_ID"),
    "database_url": os.getenv("DATABASE_URL")
}

firebase = pyrebase.initialize_app(firebase_config)
auth_client = firebase.auth()
db = firebase.database()

def signup(name, email, password, role):
    if not check_password_strength(password):
        print("Password is weak. Try again with a stronger password.")
        return None
    try:
        user = auth_client.create_user_with_email_and_password(email, password)
        user = auth_client.sign_in_with_email_and_password(email, password)

        
        user_id = user["localId"]
        auth_token = user["idToken"] 
        db.child("users").child(user_id).set({"name": name, "email": email, "role": role}, auth_token)

        print(f'\n✅User created successfully: {user_id}✅\n')
        return user
    except Exception as e:
        print(f'Error creating user: {e}')
        return None

def login(email, password):
    try:
        user = firebase.auth().sign_in_with_email_and_password(email, password)

        user_data = db.child("users").child(user['localId']).get(user['idToken']).val()  # <---- idToken here

        if user_data and 'role' in user_data:
            user['role'] = user_data['role']
        else:
            user['role'] = 'Unknown'

        return user
    
    except Exception as e:
        print(f"\n❌ Error logging in: {e}\n")
        return None

def get_user_info(id_token): 
    try:
        user_info = auth_client.get_account_info(id_token)
        if "users" in user_info and len(user_info["users"]) > 0:
            user = user_info["users"][0]
            user_id = user["localId"]

            user_data = db.child("users").child(user_id).get(id_token).val()

            print('💻 User Information from Auth 💻:')
            print(f'🔑 Name: {user.get("displayName", "N/A")}')
            print(f'🔑 Email: {user.get("email")}')
            print(f'🔑 UID: {user.get("localId")}')



        return user_info
    except Exception as e:
        print(f'Error retrieving user info: {e}')
        return None
