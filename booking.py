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

    print(f"\n🔍 Checking availability for {mentor_email} on {date} from {start_time} for {duration} mins\n")
    print(f"📅 Found {len(events)} existing events:\n")
    for event in events:
        print(f"- {event['summary']} ({event['start']['dateTime']} to {event['end']['dateTime']})")

    return len(events) == 0


def get_bookings(user_email):
    """
    Retrieves a list of bookings for the given user.
    """
    all_bookings_ref = db.child("bookings").get()
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
            # Delete expired booking
            db.child("bookings").child(booking_id).remove()

    return valid_bookings


def book_session(mentor_email, role, session_type, date, start_time, duration):
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    if not check_availability(service, mentor_email, date, start_time, duration):
        print("❌ Mentor is not available at this time. Choose another time.")
        return

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
        "role": role,  # Store the role along with other details
        "date": date,
        "start_time": start_time,
        "duration": duration,
    })

    success = True
    event_link = created_event.get("htmlLink", "No link available")

    print(f"✅ Booking successful! Event created: {event_link}")
    return success, event_link


def cancel_booking(mentor_email, session_type, date, start_time):
    """
    Cancels a booking for the given user by email, session type, date, and start time.
    """
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
        if (
            event["start"]["dateTime"].startswith(date) and
            event["start"]["dateTime"].endswith(start_time)
        ):
            event_to_delete = event["id"]
            break

    if not event_to_delete:
        print("❌ Event not found in Google Calendar.")
        return False

    try:
        service.events().delete(calendarId="primary", eventId=event_to_delete).execute()
        print("✅ Booking successfully removed from Google Calendar!")
        return True
    except Exception as e:
        print(f"❌ Error removing booking from Google Calendar: {e}")
        return False


def delete_expired_bookings():
    """Remove expired bookings from the database."""
    all_bookings_ref = db.child("bookings").get()
    bookings = all_bookings_ref.val()

    if not bookings:
        return

    current_date = datetime.datetime.utcnow().date()

    for booking_id, booking in bookings.items():
        booking_date = datetime.datetime.strptime(booking["date"], "%Y-%m-%d").date()

        if booking_date < current_date:
            db.child("bookings").child(booking_id).remove()
            print(f"🗑️ Deleted expired booking: {booking}")

