import pyrebase
import os
from dotenv import load_dotenv
import pwinput

load_dotenv()
print("hi")

firebaseConfig = {
    'apiKey': os.getenv('API_KEY'),
    'authDomain': os.getenv('AUTH_DOMAIN'),
    'projectId': os.getenv('PROJECT_ID'),
    'storageBucket': os.getenv('STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('MESSAGING_SENDER_ID'),
    'appId': os.getenv('APP_ID'),
    'measurementId': os.getenv('MEASUREMENT_ID'),
    'databaseURL': os.getenv('DATABASE_URL')  # Include only if using Firebase Realtime Database
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def signup():
    email = input("Email: ")
    password = pwinput.pwinput(prompt="Password: ")
    
    try:
        
        user = auth.create_user_with_email_and_password(email, password)
        print("Account created successfully!")
    except Exception as e:
        if 'EMAIL_EXISTS' in str(e):
            print("User already exists with this email!")
        else:
            print("An error occurred while creating the user.")


signup()
