import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
from supabase import create_client, Client

# Set page configuration
st.set_page_config(page_title="Accountability Partner",
                   page_icon="📊",
                   layout="wide")

from habit_wizard import create_habit_wizard
from activity_wizard import create_activity_wizard
import analytics as an
from utils import supabase_client as sp


# Initialize session state variables if they don't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'forgot_password' not in st.session_state:
    st.session_state.forgot_password = False
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = None
if 'just_logged_in' not in st.session_state:
    st.session_state.just_logged_in = False
if 'active_view' not in st.session_state:
    st.session_state.active_view = "Create Habit"
if 'view_radio' not in st.session_state:
    st.session_state.view_radio = "Create Habit"
if 'sub_option' not in st.session_state:
    st.session_state.sub_option = "📊 Overview"
if 'username' not in st.session_state:
    st.session_state.username = None
if 'supabase' not in st.session_state:
    st.session_state.supabase = sp.init_supabase()

# # initialize supabase client
# @st.cache_resource
# def init_supabase():
#     url=st.secrets["SUPABASE_URL"]
#     key=st.secrets["SUPABASE_KEY"]
#     return create_client(url, key)

supabase = sp.init_supabase()


# function to change active view
def update_active_view():
    st.session_state.active_view = st.session_state.view_radio


def load_auth_config():
    """Load and return the authentication configuration file."""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.load(file, Loader=SafeLoader)
            return config
    except FileNotFoundError:
        st.error("Configuration file not found. Please make sure 'config.yaml' exists.")
        return None
    
def initialize_authenticator():
    """Initialize the Streamlit authenticator with the loaded configuration."""
    if st.session_state.authenticator is None:
        config = load_auth_config()
        if config:
            st.session_state.authenticator = stauth.Authenticate('config.yaml'
                # config['credentials'],
                # config['cookie']['name'],
                # config['cookie']['key'],
                # config['cookie']['expiry_days']
            )
            if 'authentication_status' not in st.session_state:
                st.session_state['authentication_status'] = None


def show_home():
    """Display the home page with login, signup, and demo options."""

    # load config file
    config = load_auth_config()
    
    left_column, centre_column, right_column = st.columns([1,3,1])
    with centre_column:
        st.title("Accountability Partner")
        st.write("Track your habits and activities with ease!")
        st.write("Log in to your account or sign up to get started.")
        st.write("Or try the demo to explore the app without creating an account.")
        st.info("Please note that the demo only shows the analytics features and does not allow you to create or track habits.")
        st.image("images/AppLogo.png", use_container_width=True)

        # create 4 columns for login, signup, demo and forgot password
        login_col, signup_col, demo_col, forgot_password_col = st.columns([1, 1, 1, 1])
        with login_col:
            if st.button("Login", use_container_width=True):
                st.session_state.show_login = True
                st.session_state.show_signup = False
                st.session_state.forgot_password = False
                st.rerun()

        with signup_col:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.session_state.show_login = False
                st.session_state.forgot_password = False
                st.rerun()
        
        with demo_col:
            if st.button("Demo", use_container_width=True):
                st.session_state.current_page = "demo"
                st.session_state.show_login = False
                st.session_state.show_signup = False
                st.session_state.forgot_password = False
                st.rerun()
        
        with forgot_password_col:
            if st.button("Forgot Password", use_container_width=True):
                st.session_state.forgot_password = True
                st.session_state.show_login = False
                st.session_state.show_signup = False
                st.rerun()

        # show login form if login button was clicked
        if st.session_state.show_login:
            st.session_state.authenticator.login()
            if st.session_state['authentication_status']:
                st.success('Logged in as: {}'.format(st.session_state['username']))
                time.sleep(1)
                st.session_state.just_logged_in = True
                st.session_state.current_page = "main"
                st.rerun()
            elif st.session_state["authentication_status"] is False:
                st.error('Username/password is incorrect')
            elif st.session_state["authentication_status"] is None:
                st.warning('Please enter your username and password')

        # show signup form if signup button was clicked
        if st.session_state.show_signup:
            try:
                (email_of_registered_user,
                username_of_registered_user,
                name_of_registered_user) = st.session_state.authenticator.register_user(pre_authorized=config['preauthorized']['emails'])
                if email_of_registered_user:
                    st.success('User registered successfully')
            except RegisterError as e:
                st.error(e)
                url = "https://www.linkedin.com/in/samuel-ayer/"
                st.info('Please contact the admin on LinkedIn: [Samuel Ayer](%s)' % url)

        # show forgot password form if forgot password button was clicked
        if st.session_state.forgot_password:
            try:
                (username_of_forgotten_password,
                email_of_forgotten_password,
                new_random_password) = st.session_state.authenticator.forgot_password()
                if username_of_forgotten_password:
                    st.success(f"New password **'{new_random_password}'** to be sent to user securely")
                    with open('config.yaml', 'w') as file:
                        yaml.dump(st.session_state.authenticator.credentials, file,default_flow_style=False)
                    #config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
                 # Random password to be transferred to the user securely
                elif not username_of_forgotten_password:
                    st.error('Username not found')
            except ForgotError as e:
                st.error(e)

def show_main_app():
    """Display the main application dashboard after login."""
    
    st.title("Accountability Partner Dashboard")

    if st.session_state.get('authentication_status'):
        st.session_state.username = st.session_state['username']
        st.write(f"*{st.session_state.username}*, Welcome to your dashboard! Here you can log and track your habits and activities.")
        st.info("Use the radio to navigate through different features.")
        # log out button
        st.session_state.authenticator.logout()


        # main radio selections
        main_view = st.radio("Select View",
                     ["Create Habit", "Log Activity", "Analytics"],
                     key='view_radio',
                     on_change=update_active_view,
                     horizontal=True,
                     label_visibility='collapsed')
    
        # get user data
        habits_df, activities_df, merged_df = sp.get_data(st.session_state.username)
        
        if main_view == "Create Habit" or st.session_state.just_logged_in:
            st.session_state.just_logged_in = False
            create_habit_wizard()
        elif main_view == "Log Activity":
            if len(habits_df) == 0:
                st.warning("No habits available. Please create a habit first.")
            else:
                create_activity_wizard()
        elif main_view == "Analytics":
            if len(merged_df) == 0:
                st.warning("No data available for analytics. Please log some activities.")
            else:
                an.show_analytics(merged_df)


    else:
        st.warning("You need to log in to access this page.")
        if st.button("Go to Login"):   
            st.session_state.current_page = "home"
            st.session_state.show_login = True
            st.session_state.show_signup = False
            st.session_state.forgot_password = False
            st.session_state.username=None
            st.rerun()



def main():
    """Main function to run the Streamlit app."""
    initialize_authenticator()
    # Show home page
    if st.session_state.current_page == "home":
        show_home()
    
    # Show main app page after login
    elif st.session_state.current_page == "main":
        show_main_app()

if __name__ == "__main__":
    main()