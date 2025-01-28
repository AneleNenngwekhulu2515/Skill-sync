import pyrebase
import os
from dotenv import load_dotenv
import firebase_admin
# from firebase_admin import credentials, firestore

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

def auth_service():
    return firebase.auth()

db = None

def initialize_firebase_admin():
  global db
  cred_path = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
  if cred_path:
      cred = firebase_admin.credentials.Certificate(cred_path)
      firebase_admin.initialize_app(cred)
      db = firebase_admin.firestore.client() # Initialize db here
  else:
    print("Error: SERVICE_ACCOUNT_KEY_PATH environment variable not set")


def get_firestore_client():
    if db is None:
      initialize_firebase_admin()
    return db if db else None