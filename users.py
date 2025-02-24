import click
from firebase_config import get_firestore_client
import sys
import logging
from google.cloud import firestore
from datetime import datetime, timedelta

class User:
    def __init__(self, uid, email, name, role):
        self.uid = uid
        self.email = email
        self.name = name
        self.role = role

def save_user_role(uid, email, name, role, db):
    """Saves user role and initializes availability."""
    if role not in ["mentor", "peer"]:
        click.echo("Invalid role. Please choose either 'mentor' or 'peer'.")
        sys.exit(1)

    try:
        availability = {}
        for hour in range(7, 18):  # 7 AM to 5 PM
            availability[f"{hour:02d}:00"] = True  # Initialize to True (available)

        user_ref = db.collection("Users").document(uid)
        user_ref.set({
            "name": name,
            "email": email,
            "role": role,
            "availability": availability
        })
        click.echo(f"User details for '{email}' saved")

    except Exception as e:
        logging.error(f"Error saving user details: {e}")
        click.echo(f"Error saving user details")  # Don't expose internal error details to the user
        sys.exit(1)


def get_user_by_email(email):
    """Retrieves a user from Firestore by email."""
    try:
        db = get_firestore_client()
        if not db:
            logging.error("Firestore client is not initialized.")
            click.echo("Error: Firestore is not initialized")
            return None

        users_ref = db.collection("Users")
        query = users_ref.where(filter=firestore.FieldFilter("email", "==", email)).limit(1)  # Use filter keyword
        docs = query.get()

        if docs:
            for doc in docs:
                user_data = doc.to_dict()
                user_data["uid"] = doc.id
                return type('User', (object,), user_data)()
        else:
            click.echo(f"Could not find user with email: {email}")
            return None

    except Exception as e:
        logging.error(f"Error getting user by email: {e}")
        click.echo("Error getting user by email")  # More generic error message
        return None


def get_available_mentors(db):
    """Retrieves available mentors from Firestore."""
    try:
        mentors = []
        users_ref = db.collection("Users")
        query = users_ref.where(filter=firestore.FieldFilter("role", "==", "mentor"))  # Use filter keyword
        docs = query.get()

        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            mentors.append(type('User', (object,), user_data)())

        return mentors

    except Exception as e:
        logging.error(f"Error getting mentors: {e}")
        click.echo("Error getting mentors")  # More generic message
        return []


def get_available_peers(db):
    """Retrieves available peers from Firestore."""
    try:
        peers = []
        users_ref = db.collection("Users")
        query = users_ref.where(filter=firestore.FieldFilter("role", "==", "peer"))  # Use filter keyword
        docs = query.get()

        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            peers.append(type('User', (object,), user_data)())

        return peers

    except Exception as e:
        logging.error(f"Error getting peers: {e}")
        click.echo("Error getting peers")  # More generic message
        return []


def add_booking(booker_uid, booked_uid, booking_time, booked_date_str, db):
    """Adds a booking to Firestore, checking availability."""
    try:
        logging.debug(f"Attempting to book {booked_uid} by {booker_uid} at {booking_time} on {booked_date_str}")

        booked_user_ref = db.collection("Users").document(booked_uid)
        booked_user_doc = booked_user_ref.get()

        if not booked_user_doc.exists:
            click.echo(f"User with UID {booked_uid} not found.")
            return False

        booked_user_data = booked_user_doc.to_dict()
        availability = booked_user_data.get("availability", {})

        if not availability or booking_time not in availability or not availability[booking_time]:
            click.echo(f"User with UID {booked_uid} is not available at {booking_time}")
            return False

        booked_date = datetime.strptime(booked_date_str, "%Y-%m-%d").date()
        booking_ref = booked_user_ref.collection("bookings").document()  # Bookings subcollection
        booking_ref.set({
            "bookerId": booker_uid,
            "bookedId": booked_uid,
            "bookingTime": booking_time,
            "bookingDate": booked_date.isoformat()
        })

        # Atomic Availability Update (Important!)
        booked_user_ref.update({
            f"availability.{booking_time}": firestore.DELETE_FIELD  # More efficient
        })

        logging.info(f"User with UID {booked_uid} has been booked at time {booking_time} by {booker_uid}")
        click.echo("Booking successful!")  # User-facing message
        return True

    except ValueError:
        click.echo("Invalid date format. Please use YYYY-MM-DD.")
        return False
    except Exception as e:
        logging.error(f"Error booking: {e}")
        click.echo("Error booking")  # Generic error message
        return False


def get_bookings(uid, db):
    """Retrieves all bookings for a specific user."""
    try:
        logging.debug(f"Attempting to get bookings for user {uid}")
        bookings_ref = db.collection("Users").document(uid).collection("bookings")
        bookings = bookings_ref.get()
        booking_list = []

        for booking in bookings:
            booking_data = booking.to_dict()
            booking_data["id"] = booking.id
            booking_list.append(booking_data)

        logging.info(f"Successfully fetched bookings for user {uid}")
        return booking_list

    except Exception as e:
        logging.error(f"Error getting bookings: {e}")
        click.echo("Error getting bookings")  # Generic error message
        return []


def cancel_booking(booking_id, uid, db):
    """Cancels a booking by the booking ID."""
    try:
        logging.debug(f"Attempting to cancel booking {booking_id} for user {uid}")

        booking_ref = db.collection("Users").document(uid).collection("bookings").document(booking_id)
        booking = booking_ref.get()

        if not booking.exists:
            click.echo(f"Booking with ID {booking_id} not found.")
            return False

        booking_data = booking.to_dict()
        booking_time = booking_data.get("bookingTime")
        booked_uid = booking_data.get("bookedId")

        # Atomic Availability Update (Important!)
        booked_user_ref = db.collection("Users").document(booked_uid)
        booked_user_ref.update({
            f"availability.{booking_time}": True  # Set back to True
        })

        booking_ref.delete()
        click.echo(f"Booking with ID {booking_id} cancelled successfully.")
        return True

    except Exception as e:
        logging.error(f"Error canceling booking: {e}")
        click.echo("Error cancelling booking")  # Generic error message
        return False