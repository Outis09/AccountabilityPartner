import os
import yaml
import hashlib
import secrets
import uuid
import re
from datetime import datetime
import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

def hash_password(password,salt=None):
    """Hashes a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    # combine password and salt then hash
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def is_valid_email(email):
    """Validates an email address."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def is_valid_password(password):
    """Checks if the password is strong."""
    # Password should be at least 8 characters long, contain uppercase, lowercase, digits, and special characters
    if (len(password) < 8 or
        not re.search(r'[A-Z]', password) or
        not re.search(r'[a-z]', password) or
        not re.search(r'[0-9]', password) or
        not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password)
        ):
        return False
    return True

# user registration
def register_user(email, username, firstname, lastname, password, repeat_password):
    """Registers users with preauthorization and saves to database."""
    # supabase client
    supabase = st.session_state.supabase
    # validate inputs
    if not all([email, username, firstname, lastname, password, repeat_password]):
        return False, "All fields are required."
    # validate email
    if not is_valid_email(email):
        return False, "Invalid email format."
    # password strength check
    if not is_valid_password(password):
        return False, "Password must be at least 8 characters long and contain uppercase, lowercase, digits, and special characters."
    # check if email is already registered
    response = supabase.table("users").select("email").eq("email", email).execute()
    if response.data:
        return False, "Email already registered. Please use a different email or login."
    # check if username is already taken
    response = supabase.table("users").select("username").eq("username", username).execute()
    if response.data:
        return False, "Username already taken."
    # check if email is preauthorized
    preauth_response = supabase.table("authorized_emails").select("*").eq("email", email).execute()
    if not preauth_response.data:
        return False, "Email not preauthorized."
    # check if passwords match
    if password != repeat_password:
        return False, "Passwords do not match."
    # hash password
    password_hash, salt = hash_password(password)
    # generate user_id
    user_id = str(uuid.uuid4())
    # create user record
    user_data = {
        "user_id": user_id,
        "email": email,
        "username": username.lower(),
        "first_name": firstname,
        "last_name": lastname,
        "password_hash": password_hash,
        "salt": salt
    }

    # get email as used in authorized emails table
    auth_email_id = preauth_response.data[0]['id']
    # insert into supabase and mark email as used
    try:
        # add user
        user_response = supabase.table("users").insert(user_data).execute()
        # mark email as used
        supabase.table("authorized_emails").update({
            "used": True,
            "used_at": datetime.now().isoformat()}).eq("id", auth_email_id).execute()
        return True, "User registered successfully. Please log in."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    
def login_user(username, password):
    """Log user in and check credentials."""
    # supabase client
    supabase = st.session_state.supabase
    # validate inputs
    if not all([username, password]):
        return False, None, "All fields are required."
    # get user from database
    user_response = supabase.table("users").select("*").eq("username", username.lower()).execute()
    if not user_response.data:
        return False, None, "Invalid username or password."
    user_data = user_response.data[0]
    # verify password
    password_hash, _ = hash_password(password, user_data['salt'])
    if password_hash != user_data['password_hash']:
        return False,None, "Invalid username or password."
    
    return True, user_data, None


def generate_temporary_password():
    """Generates a temporary password."""
    # generate a random password
    temp_password = secrets.token_urlsafe(12)
    # hash the temporary password
    hashed_temp_password, salt = hash_password(temp_password)
    return hashed_temp_password, salt

def send_temporary_password_email(email, temp_password):
    """Sends the temporary password to the user's email."""
    # load sendgrid API key from secrets
    sender_email = st.secrets['email']['sender']
    sender_password = st.secrets['email']['password']

    subject = "Your Temporary Password"
    body = f"""
Hello,
    
Your temporary password is: {temp_password}
Please use this password to log in and change your password immediately.
Thank you for using our service!

Regards,
Accountability Partner Team
"""
    message = MIMEText(body)
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject
    # message.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return True, f"Temporary password sent to {email}. Please check your inbox or spam."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}. Please contact support if the problem persists."


def forgot_password(email):
    """Handles forgot password functionality."""
    # supabase client
    supabase = st.session_state.supabase
    # validate email
    if not is_valid_email(email):
        return False, "Invalid email format."
    # check if email exists
    user_response = supabase.table("users").select("*").eq("email", email).execute()
    if not user_response.data:
        return False, "Email not registered."
    
    # generate temporary password
    temp_password, salt = generate_temporary_password()

    success, message = send_temporary_password_email(email, temp_password)
    if not success:
        support_url = "https://linkedin.com/in/samuel-ayer"
        return False, f"Failed to send email: {message}. Please contact support at {support_url}"
    
    # update user with temporary password
    user_data = {
        "password_hash": temp_password,
        "salt": salt
    }
    
    try:
        supabase.table("users").update(user_data).eq("email", email).execute()
        return True, "Temporary password sent successfully. Please check your email."
    except Exception as e:
        support_url = "https://linkedin.com/in/samuel-ayer"
        return False, f"Email sent but failed to update password: {str(e)}. Please contact support at {support_url}"
    

    

def forgot_username(email):
    """Handles forgot username functionality."""
    # supabase client
    supabase = st.session_state.supabase
    # validate email
    if not is_valid_email(email):
        return False, "Invalid email format."
    # check if email exists
    user_response = supabase.table("users").select("*").eq("email", email).execute()
    if not user_response.data:
        return False, "Email not registered."
    
    # get username
    username = user_response.data[0]['username']
    
    return True, username

def send_username_email(email, username):
    """Sends the username to the user's email."""
#     # get resend email credentials
#     api_key = st.secrets['API_KEY']
#     sender = st.secrets['RESEND_SENDER']
#     # email message
#     data = {
#         "from": f"Accountability Partner <accountabilitypartner@resend.dev>",
#         "to": "chiefacctpartner@gmail.com",
#         "subject": "Your Username",
#         "html": f"""
# <p>Hello</p>
# <p>Your username is: <strong>{username}</strong></p>
# <p>Please use this username to log in to your account.</p>
# <p>Regards,<br>Accountability Partner Team</p>
# """
#     }
#     try:
#         response = requests.post(
#             "https://api.resend.com/emails",
#             headers={"Authorization": f"Bearer {api_key}",
#                      "Content-Type": "application/json"},
#             json=data
#         )
#         if response.status_code == 200:
#             return True, f"Username sent to {email}. Please check your inbox or spam."
#         else:
#             return False, f"Failed to send email: {response.text}. Please contact support if the problem persists."
#     except Exception as e:
#         return False, f"An error occurred: {str(e)}. Please contact support if the problem persists."

    # load sendgrid API key from secrets
    sender_email = st.secrets['smtp_sender']
    sender_password = st.secrets['smtp_password']

    subject = "Your Username"
    body = f"""
Hello,

Your username is: {username}
Please use this username to log in to your account.

Regards,
Accountability Partner Team
"""
    message = MIMEText(body)
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject
    # message.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return True, f"Username sent to {email}. Please check your inbox or spam."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}. Please contact support if the problem persists."