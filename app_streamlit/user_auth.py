import os
import yaml
import hashlib
import secrets
import uuid
import re
from datetime import datetime
import streamlit as st

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
    if not all([email, username, firstname, lastname, password]):
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