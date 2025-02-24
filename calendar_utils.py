import os
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Shows basic usage of the Google Calendar API.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error refreshing tokens: {e}")
                os.remove("token.json")
                return get_calendar_service()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'path/to/your/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building calendar service {e}")
        return None
def create_calendar_event(service, summary, start_time, end_time, attendees):
    """Creates a Google Calendar event."""
    try:
       event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Africa/Johannesburg',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Africa/Johannesburg',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
       event = service.events().insert(calendarId='primary', body=event).execute()
       logging.info(f"Event created: {event.get('htmlLink')}")
       return event

    except HttpError as error:
        logging.error(f"An error occurred: {error}")
        return None

def send_email(sender_email, sender_password, receiver_email, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
               server.starttls() 
               server.login(sender_email, sender_password)
               server.send_message(msg)
            logging.info(f"Email sent successfully to: {receiver_email}")

        except smtplib.SMTPAuthenticationError as auth_error:
            logging.error(f"SMTP Authentication Error: {auth_error}")
        except Exception as e:
             logging.error(f"Error sending email: {e}")


if __name__ == '__main__':
    service = get_calendar_service()
    if service:
       start_time = datetime.datetime.now() + datetime.timedelta(minutes=10)
       end_time = start_time + datetime.timedelta(minutes=60)
       attendees = [{"email": "nenngwekhuluanele@gmail.com"}, {"email": "nengi.khuluanele@gmail.com"}]
       event = create_calendar_event(service, "Test Calendar Event", start_time, end_time, attendees)
       if event:
          print("Event created successfully")
       else:
           print("Event could not be created")
    else:
        print("Could not get the calendar service.")