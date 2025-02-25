import click
from auth_service import signup, login, get_user_info
from booking_service import book_session
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
    session_type = click.prompt('Session type (group/one-on-one)')
    date = click.prompt('Enter date (YYYY-MM-DD)')
    start_time = click.prompt('Enter start time (HH:MM, 24-hour format)')
    duration = click.prompt('Enter session duration (minutes)', type=int)

    book_session(mentor_email, session_type, date, start_time, duration)

if __name__ == '__main__':
    cli()
