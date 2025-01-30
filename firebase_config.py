import pyrebase
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import inspect
from google.oauth2 import service_account
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Initialize Firebase Admin SDK
def initialize_firebase_admin():
  cred_path = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
  if not cred_path:
    print("Error: SERVICE_ACCOUNT_KEY_PATH environment variable not set")
    return None
  
  if not os.path.exists(cred_path):
      print(f"Error: Service account key file not found at: {cred_path}")
      return None

  try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    
    gc_cred = service_account.Credentials.from_service_account_file(cred_path)
    db = firestore.Client(credentials=gc_cred)
    return db
  except Exception as e:
    print(f"Error initializing Firebase Admin: {e}, type: {type(e)}, arguments: {e.args}")
    return None

# global variable for db client
_db = None

def get_firestore_client():
  global _db
  if _db is None:
    _db = initialize_firebase_admin()
  return _db