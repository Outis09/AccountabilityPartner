"""
To Do Module

This module implements the functionality for displaying habits that are due for the user in the Streamlit web app.
This module is responsible for displaying the list of habits that are due for the user, allowing them to select a habit and log their activity.
"""
import streamlit as st
from datetime import date
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_streamlit.utils import supabase_client as supabase

def show_unlogged_activities(user_id):
    """
    Display unlogged activities for the user.
    This function fetches the unlogged activities from the database and displays them in the Streamlit app.
    """
    st.header("Unlogged Activities")
    # get unlogged activities
    daily_unlogged,weekly_unlogged,monthly_unlogged = supabase.get_unlogged_activities(st.session_state.user_id)

    if not daily_unlogged and not weekly_unlogged and not monthly_unlogged:
        st.write("No unlogged activities for today.")
        # add motivational message
        st.write("Keep up the good work! You're doing great!")
        st.write("Stay consistent and keep tracking your progress.")
        return

    # add motivational message
    st.write("Stay consistent and keep tracking your progress.")
    st.write("Here are your unlogged activities for today:")
    # display daily unlogged activities if any
    if daily_unlogged:
        st.subheader("Daily Unlogged Activities")
        for activity in daily_unlogged:
            st.write(f"- {activity}")

    # display weekly unlogged activities if any
    if weekly_unlogged:
        st.subheader("Weekly Unlogged Activities")
        for activity in weekly_unlogged:
            st.write(f"- {activity}")

    # display monthly unlogged activities if any
    if monthly_unlogged:
        st.subheader("Monthly Unlogged Activities")
        for activity in monthly_unlogged:
            st.write(f"- {activity}")