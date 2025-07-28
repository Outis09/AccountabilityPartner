"""
Log Activity Module

This module implements the functionality for logging activity in the Streamlit web app.
"""

import streamlit as st
from datetime import date
import textwrap
import os
import sys
from app_streamlit.utils import supabase_client as supabase

username = st.session_state.get("username")
user_id = st.session_state.get("user_id")

def load_categories():
    """Load categories"""
    return supabase.get_categories(st.session_state.user_id)

def load_habits(selected_category):
    """Load habits for selected category"""
    return supabase.get_habits(st.session_state.user_id,selected_category)


# select Category and Habit
def step1_select_habit():
    """Asks user to select category and habit"""
    st.header("Step 1: Select Category and Habit")

    categories = load_categories()

    selected_cat = st.selectbox("Select a Category", categories)


    habits = []
    if selected_cat:
        habit_details = load_habits(selected_cat)
        habits = list(habit_details.keys())
        st.session_state.habit_details = habit_details 

    selected_habit = st.selectbox("Select a Habit", habits) if habits else None

    if st.button("Next ➡️", key="step1_next"):
        if not selected_cat or not selected_habit:
            st.warning("Please select both a category and a habit.")
            return
        st.session_state.activity_data = {
            "category": selected_cat,
            "habit": selected_habit,
            "habit_id": int(supabase.get_habit_id(st.session_state.user_id,selected_habit)),
            "tracking_type": st.session_state.habit_details.get(selected_habit)
        }
        st.session_state.activity_step = 2
        st.rerun()


# Log Activity Details
def step2_log_details():
    """Provides fields for logging activity details"""
    st.header("Step 2: Log Activity Details")

    data = st.session_state.activity_data
    today = date.today()

    activity_date = st.date_input("When did this activity take place?", max_value=today, 
                                  value=data.get('activity_date', today))

    tracking_input = None
    if data['tracking_type'] == "Yes/No (Completed or not)":
        tracking_input = st.radio("Did you complete this activity?", ["Yes", "No"],
                                  index=["Yes", "No"].index(data.get('tracking_input', 'Yes')))
    elif data['tracking_type'] == "Count (Number-based)":
        tracking_input = st.number_input("How many times did you do this?", min_value=0, step=1,
                                         value=int(data.get('tracking_input', 0)))
    elif data['tracking_type'] == "Duration (Minutes/hours)":
        tracking_input = st.number_input("How many minutes did you spend on this activity?", min_value=0, step=5,
                                         value=int(data.get('tracking_input', 0)))

    rating = int(st.number_input("Rate your productivity during this activity (1-5)", min_value=1, max_value=5, step=1,
                                 value=int(data.get('rating',1))))

    comments = st.text_area("Any comments?", height=100, placeholder="e.g., I felt great, I struggled with this, etc.",
                            value=data.get('comments', ''))

    if st.button("Next ➡️", key="step2_next"):
        if (data['tracking_type'] == "Yes/No (Completed or not)" and not tracking_input) or (data['tracking_type'] != "Yes/No (Completed or not)" and tracking_input == 0):
            st.warning("Please provide a valid tracking input.")
            return
        if not rating:
            st.warning("Please provide a rating between 1 and 5.")
            return
        
        # High value warnings
        if (data['tracking_type'] == "Duration (Minutes/hours)" and tracking_input >= 300 and not st.session_state.confirmed_save):
            if not st.session_state.get("duration_warning_accepted", False):
                st.warning("You entered a very high duration. Click next again to confirm if you are sure.")
                st.session_state.duration_warning_accepted = True
                return

        if (data['tracking_type'] == "Count (Number-based)" and tracking_input > 10 and not st.session_state.confirmed_save):
            if not st.session_state.get("count_warning_accepted", False):
                st.warning("You entered a very high count. Click next again to confirm if you are sure.")
                st.session_state.count_warning_accepted = True
                return

        st.session_state.activity_data.update({
            "activity_date": activity_date,
            "tracking_input": tracking_input,
            "rating": rating,
            "comments": textwrap.fill(comments, width=50)
        })
        st.session_state.activity_step = 3
        st.rerun()


# ask user to confirm or edit
def step3_confirm_and_save():
    """Asks user to confirm and save or to edit"""
    st.header("Step 3: Confirm Activity Details")

    data = st.session_state.activity_data

    st.markdown(f"**Category:** {data['category']}")
    st.markdown(f"**Habit:** {data['habit']}")
    st.markdown(f"**Activity Date:** {data['activity_date']}")
    st.markdown(f"**Tracking Input:** {data['tracking_input']}")
    st.markdown(f"**Rating:** {data['rating']}")
    st.markdown(f"**Comments:** {data['comments'] if data['comments'] else 'None'}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to Edit", key="step3_back"):
            st.session_state.activity_step = 2
            st.rerun()

    with col2:
        if st.button("✅ Confirm and Save", key="step3_confirm"):
            with st.spinner("Saving activity..."):
                success= supabase.insert_activity_log(
                    st.session_state.user_id,
                    data['habit_id'],
                    data['activity_date'],
                    data['tracking_input'],
                    data['rating'],
                    data['comments']
                )
            if success:
                st.success("Activity successfully logged!")
                st.session_state.activity_step = 4
                st.rerun()




# display success message
def step4_success():
    st.header("🎉 Activity Successfully Logged")

    if st.button("Log Another Activity"):
        for key in ["activity_step", "activity_data", "habit_details", "confirmed_save", "duration_warning_accepted", "count_warning_accepted"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.activity_step = 1
        st.rerun()


# Main App Logic
def create_activity_wizard():
    """Controls the log activity functionality"""
    # initialize session state at the start
    if "activity_step" not in st.session_state:
        st.session_state.activity_step = 1

    if "activity_data" not in st.session_state:
        st.session_state.activity_data = {}

    if "confirmed_save" not in st.session_state:
        st.session_state.confirmed_save = False

    if st.session_state.activity_step == 1:
        step1_select_habit()
    elif st.session_state.activity_step == 2:
        step2_log_details()
    elif st.session_state.activity_step == 3:
        step3_confirm_and_save()
    elif st.session_state.activity_step == 4:
        step4_success()


