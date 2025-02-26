import click
from auth_service import signup, login, get_user_info
from booking import book_session
from email_service import send_booking_email
import pwinput

@click.group()
def cli():
    pass

@cli.command()
def signup_cli():
    name = click.prompt('Enter your name')
    email = click.prompt('Enter your email')
    password = pwinput.pwinput(prompt='Enter your password: ')

    user = signup(name, email, password)
    if user:
        get_user_info(user["idToken"])

@cli.command()
def login_cli():
    email = click.prompt('Enter your email')
    password = pwinput.pwinput(prompt='Enter your password: ')

    user = login(email, password)
    if user:
        get_user_info(user["idToken"])

def book_session_cli():
    mentor_email = click.prompt('Enter mentor email')
    student_name = click.prompt('Enter your name')
    session_type = click.prompt('Session type (group/one-on-one)')
    date = click.prompt('Enter date (YYYY-MM-DD)')
    start_time = click.prompt('Enter start time (HH:MM, 24-hour format)')
    duration = click.prompt('Enter session duration (minutes)', type=int)

    success = book_session(mentor_email, session_type, date, start_time, duration)

    if success:
        send_booking_email(
            to_email=mentor_email,
            subject="Skill Sync: You Have a New Booking!",
            message=f"Hello,\n\nYou have been booked for a {session_type} session on {date} at {start_time} for {duration} minutes.\n\nBest,\nSkill Sync Team"
        )
        click.echo(f"✅ Booking confirmation email sent to {mentor_email}!")
    else:
        click.echo("❌ Booking failed. Please try again.")

        
send_booking_email(
    to_email="recipient@example.com",
    subject="Test Email from Python",
    message="Hello, this is a test email sent using smtplib!"
)

@cli.command()
def book_session_cmd():
    book_session_cli()

if __name__ == '__main__':
    cli()
