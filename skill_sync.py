import click
import pwinput
import json
import inquirer
from auth_service import signup, login, get_user_info
from booking import book_session, get_bookings, cancel_booking, delete_expired_bookings
from email_service import send_booking_email
from workshops import list_workshops, get_available_mentors, get_available_peers

logged_in_user = None

@click.group()
def cli():
    pass

@cli.command()
def signup_cli():
    name = click.prompt('Enter your name')
    email = click.prompt('Enter your email')
    password = pwinput.pwinput(prompt='Enter your password: ')
    role = click.prompt('Are you signing up as a Mentor or Peer?', type=click.Choice(['Mentor', 'Peer'], case_sensitive=False))

    user = signup(name, email, password, role)
    if user:
        click.echo("✅ Signup successful!")
        get_user_info(user["idToken"])

@cli.command()
def login_cli():
    global logged_in_user
    email = click.prompt('Enter your email')
    password = pwinput.pwinput(prompt='Enter your password: ')

    user = login(email, password)
    if user:
        logged_in_user = user
        click.echo("✅ Login successful!")
        click.echo(f"\n💻 User Information from Auth 💻:\n")
        click.echo(f"🔑 Email: {user['email']}")
        click.echo(f"🔑 UID: {user['localId']}") 
        click.echo(f"🔑 Role: {user.get('role', 'Unknown')}")
        
        with open("logged_in_user.json", "w") as f:
            json.dump(user, f)

    else:
        click.echo("❌ Login failed.")

# @cli.command()
# def view_workshops():
#     workshops = list_workshops()
#     if not workshops:
#         click.echo("No workshops available.")
#     else:
#         for w in workshops:
#             click.echo(f"📅 {w['title']} - {w['date']} | Mentor: {w['mentor']}")

@cli.command()
def book_session_cmd():
    global logged_in_user

    if not logged_in_user:
        if not logged_in_user:
            try:
                with open("logged_in_user.json", "r") as f:
                    logged_in_user = json.load(f)
                    
                    if not isinstance(logged_in_user, dict) or 'idToken' not in logged_in_user:
                        click.echo("❌ Invalid user data. Please log in again.")
                        return
            except FileNotFoundError:
                click.echo("❌ You must log in first.")
                return


    role = click.prompt('Are you booking a session with a Mentor or Peer?', type=click.Choice(['Mentor', 'Peer'], case_sensitive=False))
    date = click.prompt('Enter date (YYYY-MM-DD)')
    start_time = click.prompt('Enter start time (HH:MM, 24-hour format)')
    duration = click.prompt('Enter session duration (minutes)', type=int)

    
    role = role.lower()

    if role == "mentor":
        available_options = get_available_mentors(date, start_time)  
    else:
        available_options = get_available_peers(date, start_time, logged_in_user)

    if not available_options:
        click.echo(f"No {role}s available for {date} at {start_time}. Try another date or time.")
        return

    mentor_list = [(f"{mentor['name']} ({mentor['email']})", mentor["email"]) for mentor in available_options]

    questions = [
        inquirer.List("mentor_email", message="Select a mentor/peer", choices=[m[0] for m in mentor_list])
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        click.echo("❌ No selection made.")
        return

    mentor_email = next(m[1] for m in mentor_list if m[0] == answers["mentor_email"])

    success = book_session(mentor_email, role, date, start_time, duration)
    if success:
        click.echo(f"✅ Booking successful with {mentor_email}")
        send_booking_email(mentor_email, logged_in_user["email"], role, date, start_time, duration)
        click.echo(f"✅ Booking confirmation email sent to {mentor_email}!")
    else:
        click.echo("❌ Booking failed. Please try again.")

# @cli.command()
# def view_bookings():
#     global logged_in_user
#     delete_expired_bookings(logged_in_user)

#     if not logged_in_user:
#         try:
#             with open("logged_in_user.json", "r") as f:
#                 logged_in_user = json.load(f)
#         except FileNotFoundError:
#             click.echo("❌ You must log in first.")
#             return

#     bookings = get_bookings(logged_in_user["email"])
#     if not bookings:
#         click.echo("No bookings found.")
#     else:
#         for b in bookings:
#             click.echo(f"📌 {b['session_type']} session on {b['date']} at {b['start_time']} with {b['mentor']}")

@cli.command()
def cancel_booking_cmd():
    global logged_in_user
    if not logged_in_user:
        try:
            with open("logged_in_user.json", "r") as f:
                logged_in_user = json.load(f)
        except FileNotFoundError:
            click.echo("❌ You must log in first.")
            return

    email = logged_in_user['email']
    click.echo(f"Logged in as: {email}")

    session_type = click.prompt('Enter the session type (group/one-on-one)')
    date = click.prompt('Enter the date of the session (YYYY-MM-DD)')
    start_time = click.prompt('Enter the start time (HH:MM, 24-hour format)')

    if session_type == "one on one":
        session_type = "one-on-one"

    bookings = get_bookings(email)
    booking_to_cancel = None
    for booking in bookings:
        if (booking["session_type"].lower() == session_type and 
            booking["date"] == date and 
            booking["start_time"] == start_time):
            booking_to_cancel = booking
            break
    
    if not booking_to_cancel:
        click.echo("❌ No matching booking found.")
        return
    
    success = cancel_booking(booking_to_cancel["mentor"], session_type, date, start_time)

    if success:
        click.echo("✅ Booking canceled successfully!")
    else:
        click.echo("❌ Failed to cancel booking. Please try again.")



if __name__ == '__main__':
    cli()
