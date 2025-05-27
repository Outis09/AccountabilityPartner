import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import yaml
from yaml.loader import SafeLoader
import os
from supabase import create_client, Client

# Set page configuration
st.set_page_config(page_title="Accountability Partner",
                   page_icon="📊",
                   layout="wide")

from habit_wizard import create_habit_wizard
from activity_wizard import create_activity_wizard
import analytics as an
from todo import show_unlogged_activities
from utils import supabase_client as sp
from app_streamlit import user_auth as auth


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
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'just_logged_in' not in st.session_state:
    st.session_state.just_logged_in = False
if 'active_view' not in st.session_state:
    st.session_state.active_view = "Analytics"
if 'view_radio' not in st.session_state:
    st.session_state.view_radio = "Analytics"
if 'sub_option' not in st.session_state:
    st.session_state.sub_option = "📊 Overview"
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'supabase' not in st.session_state:
    st.session_state.supabase = sp.init_supabase()


supabase = sp.init_supabase()


# function to change active view
def update_active_view():
    st.session_state.active_view = st.session_state.view_radio

# dialog for forgot password
@st.dialog("Forgot Password")
def forgot_password_dialog():
    st.write("Please enter your email address to receive a temporary password.")
    email = st.text_input("Email", key="forgot_password_email")
    if st.button("Send Temporary Password"):
        # success, message = auth.forgot_password(email)
        # if not success:
        #     st.error(message)
        #     return
        # if success:
        url = "https://www.linkedin.com/in/samuel-ayer/"
        st.info('This feature has not been implemented yet. Please contact the admin on LinkedIn: [Samuel Ayer](%s)' % url)
        

# dialog for forgot username
@st.dialog("Forgot Username")
def forgot_username_dialog():
    st.write("Please enter your email address to retrieve your username.")
    email = st.text_input("Email", key="forgot_username_email")
    if st.button("Retrieve Username"):
        success, message = auth.forgot_username(email)
        if not success:
            st.error(message)
            return
        if success:
            url = "https://www.linkedin.com/in/samuel-ayer/"
            st.info('This feature has not been implemented yet. Please contact the admin on LinkedIn: [Samuel Ayer](%s)' % url)

def show_home():
    """Display the home page with login, signup, and demo options."""
    
    left_column, centre_column, right_column = st.columns([1,3,1])
    with centre_column:
        st.title("Accountability Partner")
        st.write("Track your habits and activities with ease!")
        st.write("Log in to your account or sign up to get started.")
        st.write("Or try the demo to explore the app without creating an account.")
        st.info("Please note that the demo only shows the analytics features and does not allow you to create or track habits.")
        st.image("images/AppLogo.png", use_container_width=True)

        # create 4 columns for login, signup, demo and forgot password
        login_col, signup_col, demo_col = st.columns([1, 1, 1])
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
        

        # show login form if login button was clicked
        if st.session_state.show_login:
            with st.container(border=True):
                st.subheader("Login")
                st.write("Please enter your username and password to log in.")
                # show login form
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                col1, col2 = st.columns([1,3])
                with col1:
                    user_login_button = st.button("Login")
                if user_login_button:
                    success, user, error  = auth.login_user(username, password)

                    if success:
                        st.success("Login successful!")
                        time.sleep(1)
                        st.session_state.just_logged_in = True
                        st.session_state.current_page = "main"
                        st.session_state['authentication_status'] = True
                        st.session_state.username = user['username']
                        st.session_state.user_id = user['user_id']
                        st.rerun()
                    else:
                        st.error(error)
                # columns for forgot username and password
                forgot1, forgot2 = st.columns([1,1])
                with forgot1:
                    if st.button("Forgot Username"):
                        forgot_username_dialog()
                with forgot2:
                    if st.button("Forgot Password"):
                        forgot_password_dialog()


        # show signup form if signup button was clicked
        if st.session_state.show_signup:
            with st.container(border=True):
                st.subheader("Sign Up")
                st.write("Please enter your details to create an account.")
                # show signup form
                email = st.text_input("Email", key="email")
                username = st.text_input("Username", key="signup_username")
                firstname = st.text_input("First Name", key="firstname")
                lastname = st.text_input("Last Name", key="lastname")
                password = st.text_input("Password", type="password", key="signup_password")
                repeat_password = st.text_input("Repeat Password", type="password", key="repeat_password")
                col1, col2 = st.columns([1,3])
                with col1:
                    user_signup_button = st.button("Sign Up")
                if user_signup_button:
                    success, message = auth.register_user(email, username, firstname, lastname, password, repeat_password)
                    if success:
                        st.success(message)
                        time.sleep(3)
                        st.session_state.show_signup = False
                        st.session_state.show_login = True
                        st.session_state.forgot_password = False
                        st.rerun()
                    else:
                        st.error(message)
                        url = "https://www.linkedin.com/in/samuel-ayer/"
                        st.info('Please contact the admin on LinkedIn: [Samuel Ayer](%s)' % url)

        # # show forgot password form if forgot password button was clicked
        # if st.session_state.forgot_password:
        #     try:
        #         (username_of_forgotten_password,
        #         email_of_forgotten_password,
        #         new_random_password) = st.session_state.authenticator.forgot_password()
        #         if username_of_forgotten_password:
        #             st.success(f"New password **'{new_random_password}'** to be sent to user securely")
        #             with open('config.yaml', 'w') as file:
        #                 yaml.dump(st.session_state.authenticator.credentials, file,default_flow_style=False)
        #             #config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
        #          # Random password to be transferred to the user securely
        #         elif not username_of_forgotten_password:
        #             st.error('Username not found')
        #     except ForgotError as e:
        #         st.error(e)

def show_main_app():
    """Display the main application dashboard after login."""
    
    # st.title("Accountability Partner Dashboard")

    if st.session_state['authentication_status']:
        with st.sidebar:
            st.title("Accountability Partner")
            st.write("Track your habits and activities with ease!")
            st.logo("images/AppLogo.png", size="large")
        # st.session_state.username = st.session_state['username']
        # st.write(f"*{st.session_state.username}*, Welcome to your dashboard! Here you can log and track your habits and activities.")
        # st.info("Use the radio to navigate through different features.")
        # log out button
        # st.session_state.authenticator.logout()



        # main radio selections
        main_view = st.sidebar.radio("Main Menu",
                     ["Analytics","Unlogged Activities","Log Activity", "Create Habit" ],
                     key='view_radio',
                     on_change=update_active_view,
                     horizontal=False)
    
        # get user data
        habits_df, activities_df, merged_df = sp.get_data(st.session_state.user_id)


        
        if main_view == "Analytics" or st.session_state.just_logged_in:
            if len(merged_df) == 0:
                st.info("New user? Please create a habit and log some activities to unlock analytics.")
                # st.info("No data available for analytics. Please log some activities.")
            else:
                st.title("📈 Analytics Dashboard")
                if len(merged_df) < 10 or len(habits_df) < 5:
                    st.warning("Not enough data for comprehensive analytics.")
                    st.info("Please create more habits and log more activities.")
                an.show_analytics(merged_df)
            st.session_state.just_logged_in = False
        elif main_view == "Log Activity":
            if len(habits_df) == 0:
                st.warning("No habits available. Please create a habit first.")
            else:
                st.title("📅 Log Activity")
                create_activity_wizard()
        elif main_view == "Create Habit":
            st.title("📝 Create a New Habit")
            create_habit_wizard()

        elif main_view == "Unlogged Activities":
            if len(merged_df) == 0:
                st.warning("No activities logged. Please log some activities.")
            else:
                st.title("📋 Unlogged Activities")
                show_unlogged_activities(st.session_state.user_id)

        if st.sidebar.button("Logout"):
            st.session_state.current_page = "home"
            st.session_state.show_login = False
            st.session_state.show_signup = False
            st.session_state.forgot_password = False
            st.session_state.username=None
            st.rerun()


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
    # initialize_authenticator()
    # Show home page
    if st.session_state.current_page == "home":
        show_home()
    
    # Show main app page after login
    elif st.session_state.current_page == "main":
        show_main_app()

if __name__ == "__main__":
    main()