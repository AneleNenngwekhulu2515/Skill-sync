import click
from firebase_config import get_firestore_client # Remove auth_service import
import sys
import logging
from google.cloud import firestore
from datetime import datetime, timedelta
from calendar_utils import get_calendar_service, create_calendar_event, send_email  # Import calendar functions
import os
from dotenv import load_dotenv

def save_user_role(uid, email, name, role, db):
    """Save users role"""
    if role not in ["mentor", "peer"]:
        click.echo("Invalid role. Please choose either 'mentor' or 'peer'.")
        sys.exit(1)

    try:
        availability = {}
        for hour in range(7, 18):
            availability[f"{hour:02d}:00"] = True

        user_ref = db.collection("Users").document(uid)
        user_ref.set({
            "name": name,
            "email": email,
            "role": role,
            "availability": availability
        })
        click.echo(f"User details for '{email}' saved")

    except Exception as e:
        click.echo(f"Error saving user details: {e}")
        sys.exit(1)

def get_user_by_email(email):
    try:
        db = get_firestore_client()
        if not db:
            logging.error("Firestore client is not initialized.")
            click.echo("Error: Firestore is not initialized")
            return None
    
        users_ref = db.collection("Users")
        query = users_ref.where("email", "==", email).limit(1)
        docs = query.get()

        if not docs:
             click.echo(f"Could not find user with email: {email}")
             return None

        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            return  type('User', (object,), user_data)()

    except Exception as e:
        click.echo(f"Error getting user by email: {e}")
        return None
    
def get_available_mentors(db):
    try:
        mentors_ref = db.collection("Users")
        query = mentors_ref.where("role", "==", "mentor")
        docs = query.get()

        if not docs:
            click.echo("No mentors available.")
            return []

        mentors = []
        for doc in docs:
           user_data = doc.to_dict()
           user_data["uid"] = doc.id
           mentors.append(type('User', (object,), user_data)())
        
        return mentors
    
    except Exception as e:
        logging.error(f"Error getting mentors: {e}")
        click.echo(f"Error getting mentors {e}")
        return []

def get_available_peers(db):
     try:
         peers_ref = db.collection("Users")
         query = peers_ref.where("role", "==", "peer")
         docs = query.get()

         if not docs:
             click.echo("No peers available")
             return []

         peers = []
         for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            peers.append(type('User', (object,), user_data)())
         return peers
     except Exception as e:
        logging.error(f"Error getting peers: {e}")
        click.echo(f"Error getting peers {e}")
        return []

def add_booking(booker_uid, booked_uid, booking_time, booked_date, db):
    #booking a mentor or a peer

    try:
        logging.info(f"Attempting to book {booked_uid} by {booker_uid} at {booking_time} on {booked_date}")

        booked_user_ref = db.collection("Users").document(booked_uid)
        booked_user_doc = booked_user_ref.get()
        if not booked_user_doc.exists:
            click.echo(f"User with UID {booked_uid} not found.")
            return False
        
        booked_user_data = booked_user_doc.to_dict()
        availabiity = booked_user_data.get("availability")

        if booking_time not in availabiity or not availabiity[booking_time]:
            click.echo(f"User with UID {booked_uid} is not abailable at {booking_time}")
            return False
        
        booking_ref = db.collection("Users").document(booked_uid).collection("bookings").document()
        booking_ref.set({
            "bookerId": booker_uid,
            "bookedId": booked_uid,
            "bookingTime": booking_time,
            "bookingDate": booked_date
        })

        #Update the availability
        booked_user_ref.update({
            f"availability.{booking_time}": False
        })
        logging.info(f"Mentor with UID {booked_uid} has been booked at time {booking_time} by {booker_uid}")
        return True

    except Exception as e:
      logging.error(f"Error booking: {e}")
      click.echo(f"Error booking: {e}")
      return False
def get_bookings(uid, db):
    """
    Retrieves all bookings for a specific user.
    """
    try:
        logging.info(f"Attempting to get bookings for user {uid}")
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
        click.echo(f"Error getting bookings: {e}")
        return []

def cancel_booking(booking_id, uid, db):
    """
    Cancels a booking by the booking ID.
    """
    try:
        logging.info(f"Attempting to cancel booking {booking_id} for user {uid}")
        booking_ref = db.collection("Users").document(uid).collection("bookings").document(booking_id)
        booking = booking_ref.get()

        if not booking.exists:
            click.echo(f"Booking with ID {booking_id} not found.")
            return False

        booking_data = booking.to_dict()
        booking_time = booking_data.get("bookingTime")
        booked_uid = booking_data.get("bookedId")

        # Update availability
        booked_user_ref = db.collection("Users").document(booked_uid)
        booked_user_ref.update({
            f"availability.{booking_time}": True
        })
        booking_ref.delete()
        click.echo(f"Booking with ID {booking_id} cancelled successfully.")
        return True
    except Exception as e:
        logging.error(f"Error canceling booking: {e}")
        click.echo(f"Error cancelling booking: {e}")
        return False