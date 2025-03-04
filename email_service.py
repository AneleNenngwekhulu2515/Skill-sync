import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS") 
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_booking_email(mentor_email, student_name, session_type, date, start_time, duration):
    """
    Sends an email to the mentor notifying them of a new booking.
    """
    subject = "📅 New Skill Sync Booking Confirmation"
    
    message = f"""
    Hello {mentor_email},

    You have been booked for a {session_type} session.

    📌 **Booking Details**:
    - **Student:** {student_name}
    - **Date:** {date}
    - **Time:** {start_time}
    - **Duration:** {duration} minutes

    Please check your Google Calendar for details.

    Best,  
    Skill Sync Team
    """

    msg = MIMEText(message, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = mentor_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() 
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, mentor_email, msg.as_string())

        print(f"✅ Booking confirmation email sent to {mentor_email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# send_booking_email('nenngwekhuluanele@gmail.com', 'Khosi', 'one-one-one', '2025-02-26', '10:00', '20')
