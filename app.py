import click
from auth import signup, login  
import logging
import os
from dotenv import load_dotenv
from calendar_utils import get_calendar_service, create_calendar_event, send_email
from users import add_booking, get_bookings, cancel_booking, get_user_by_email, get_available_mentors, get_available_peers, save_user_role # Import save_user_role
from firebase_config import get_firestore_client, firebaseConfig  # Import firebaseConfig only
from datetime import datetime, timedelta
import pyrebase 

load_dotenv()


try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()  # Get auth instance directly
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    auth = None 

@click.group()
def cli():
    """Main entry point for the CLI"""
    pass

@click.command()
@click.argument('email')
def signup_command(email):  
    """Signs up a new user."""
    signup(email, auth)  
cli.add_command(signup_command, name="signup") 

@click.command()
@click.argument('email')

def login_command(email):  
    """Logs in an existing user."""
    login(email, auth)  


cli.add_command(login_command, name="login") 

@click.command()
@click.argument('role', type=click.Choice(['mentor', 'peer']))
@click.argument('time')
@click.argument('date')

def book(role, time, date):
    try:
        logging.info(f"Attempting to book a {role}")
        db = get_firestore_client()
        if not db:
            click.echo("Error: Firestore client is not initialized.")
            return

        booker_email = click.prompt("Enter your email:", type=str)
        booker = get_user_by_email(booker_email)
        if not booker:
            click.echo(f"Could not find user with email: {booker_email}")
            return

        if role == "mentor":
            mentors = get_available_mentors(db)
            if not mentors:
                click.echo(f"No mentors are available")
                return
            click.echo("Available mentors: ")
            for i, mentor in enumerate(mentors):
                click.echo(f"{i + 1}. {mentor.name} ({mentor.email})")
            mentor_choice = click.prompt("Enter the number of the mentor to book: ", type=int)
            mentor_to_book = mentors[mentor_choice - 1]

            if add_booking(booker.uid, mentor_to_book.uid, time, datetime.fromisoformat(date), db):
                click.echo(f"Successfully booked mentor with email: {mentor_to_book.email} at {time}")
           
                service = get_calendar_service()
                if service:
                    start_time = datetime.fromisoformat(date).replace(hour=int(time.split(":")[0]), minute=int(time.split(":")[1]))
                    end_time = start_time + timedelta(hours=1)
                    attendees = [{"email": booker_email}, {"email": mentor_to_book.email}]
                    create_calendar_event(service, "Session with Mentor", start_time, end_time, attendees)

                email_address = os.getenv('EMAIL_ADDRESS')
                email_password = os.getenv('EMAIL_PASSWORD')

                send_email("your-email@gmail.com", "your-email-password", mentor_to_book.email, "New Session Booked", f"You have a new session booked by {booker_email} at {time} on {date}")
                send_email("your-email@gmail.com", "your-email-password", booker_email, "Session Booked Successfully", f"You have successfully booked a session with {mentor_to_book.email} at {time} on {date}")

            else:
                click.echo("Failed to book the mentor. Please try again.")

        elif role == "peer":
            peers = get_available_peers(db)
            if not peers:
                click.echo("No peers available")
                return
            click.echo("Available peers: ")
            for i, peer in enumerate(peers):
                click.echo(f"{i + 1}. {peer.name} ({peer.email})")
            peer_choice = click.prompt("Enter the number of the peer to book:", type=int)
            peer_to_book = peers[peer_choice - 1]

            # Book the peer
            if add_booking(booker.uid, peer_to_book.uid, time, datetime.fromisoformat(date), db):
                click.echo(f"Successfully booked peer with email: {peer_to_book.email} at {time}")

                # Create Calendar event
                service = get_calendar_service()
                if service:
                    start_time = datetime.fromisoformat(date).replace(hour=int(time.split(":")[0]), minute=int(time.split(":")[1]))
                    end_time = start_time + timedelta(hours=1)
                    attendees = [{"email": booker_email}, {"email": peer_to_book.email}]
                    create_calendar_event(service, "Session with Peer", start_time, end_time, attendees)

                # Send email notifications
                send_email("your-email@gmail.com", "your-email-password", peer_to_book.email, "New Session Booked", f"You have a new session booked by {booker_email} at {time} on {date}")
                send_email("your-email@gmail.com", "your-email-password", booker_email, "Session Booked Successfully", f"You have successfully booked a session with {peer_to_book.email} at {time} on {date}")

    except Exception as e:
        logging.error(f"An error occurred during booking: {e}")
        click.echo(f"An error occurred during booking: {e}")

@click.command()
def view_bookings():
    """View your bookings."""
    try:
        email = click.prompt("Enter your email:", type=str)
        logging.info(f"Attempting to view bookings for user with email: {email}")
        db = get_firestore_client()
        if not db:
            click.echo("Error: Firestore client is not initialized.")
            return

        user = get_user_by_email(email)
        if not user:
            click.echo(f"Could not find user with email: {email}")
            return

        bookings = get_bookings(user.uid, db)
        if bookings:
            if not bookings:
                click.echo("You do not have any bookings")
                return
            click.echo("Your bookings:")
            for booking in bookings:
                click.echo(f"  - Booking ID: {booking['id']}")
                click.echo(f"   - Booked ID: {booking['bookedId']}")
                click.echo(f"   - Booked time: {booking['bookingTime']}")
                click.echo(f"   - Booked date: {booking['bookingDate']}")
        else:
            click.echo("Could not fetch your bookings")
    except Exception as e:
        logging.error(f"An error occurred when viewing the bookings: {e}")
        click.echo(f"An error occurred: {e}")

@click.command()
@click.argument('booking_id')
def cancel(booking_id):
    """Cancel a booking."""
    try:
        email = click.prompt("Enter your email:", type=str)
        logging.info(f"Attempting to cancel booking for user with email: {email}")
        db = get_firestore_client()
        if not db:
            click.echo("Error: Firestore client is not initialized.")
            return

        user = get_user_by_email(email)
        if not user:
            click.echo(f"Could not find user with email: {email}")
            return

        if cancel_booking(booking_id, user.uid, db):
            click.echo(f"Booking {booking_id} has been successfully cancelled")
        else:
            click.echo(f"Failed to cancel booking {booking_id}")
    except Exception as e:
        logging.error(f"An error occurred when canceling the booking: {e}")
        click.echo(f"An error occurred: {e}")


cli.add_command(book)
cli.add_command(view_bookings)
cli.add_command(cancel)

if __name__ == '__main__':
    cli()