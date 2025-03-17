import datetime as dt
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pyrebase
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
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


def load_credentials():
    creds = None
    token_path = "config/token.json"
    creds_path = "config/credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def check_availability(service, mentor_email, date, start_time, duration):
    start_datetime = dt.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + dt.timedelta(minutes=duration)

    events = service.events().list(
        calendarId="primary",
        timeMin=start_datetime.isoformat() + "Z",
        timeMax=end_datetime.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute().get("items", [])

    return len(events) == 0


def get_bookings(user_email):
    user = firebase.auth().current_user  
    if not user:
        raise Exception("User not authenticated!")

    all_bookings_ref = db.child("bookings").get(user["idToken"])
    bookings = all_bookings_ref.val()  

    if not bookings:
        return []

    valid_bookings = []
    current_date = datetime.datetime.utcnow().date()

    for booking_id, booking in bookings.items():
        booking_date = datetime.datetime.strptime(booking["date"], "%Y-%m-%d").date()

        if booking_date >= current_date:
            valid_bookings.append(booking)
        else:
            db.child("bookings").child(booking_id).remove()

    return valid_bookings


def book_session(mentor_email, role, session_type, date, start_time, duration):
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    if not check_availability(service, mentor_email, date, start_time, duration):
        click.echo("❌ No availability for this session time.")
        return False

    start_datetime = dt.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + dt.timedelta(minutes=duration)

    event = {
        "summary": f"{session_type.capitalize()} Session with {mentor_email}",
        "start": {"dateTime": start_datetime.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_datetime.isoformat(), "timeZone": "UTC"},
        "attendees": [{"email": mentor_email}],
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    event_id = created_event["id"]

    db.child("bookings").child(event_id).set({
        "mentor": mentor_email,
        "session_type": session_type,
        "role": role,
        "date": date,
        "start_time": start_time,
        "duration": duration,
    })

    return True


def cancel_booking(mentor_email, session_type, date, start_time):
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
        calendarId="primary",
        q=f"{session_type.capitalize()} Session with {mentor_email}",
        orderBy="startTime",
        singleEvents=True
    ).execute()

    events = events_result.get("items", [])
    event_to_delete = None

    for event in events:
        if event["start"]["dateTime"].startswith(date) and event["start"]["dateTime"].endswith(start_time):
            event_to_delete = event["id"]
            break

    if not event_to_delete:
        return False

    try:
        service.events().delete(calendarId="primary", eventId=event_to_delete).execute()
        return True
    except Exception:
        return False


def delete_expired_bookings(user):
    
    if not user or "email" not in user:
        raise ValueError("Invalid user data. User must be logged in and have an email.")

    all_bookings_ref = db.child("bookings").order_by_child("mentor").equal_to(user["email"]).get()

    bookings = all_bookings_ref.val()

    if not bookings:
        return

    current_date = datetime.datetime.utcnow().date()

    for booking_id, booking in bookings.items():
        booking_date = datetime.datetime.strptime(booking["date"], "%Y-%m-%d").date()

        if booking_date < current_date:
            db.child("bookings").child(booking_id).remove()
            print(f"🗑️ Deleted expired booking: {booking}")

