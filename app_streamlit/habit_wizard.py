"""
Create Habit Module

This module implements the functionality for adding a new habit to the user's list of activities in the Streamlit web app.
"""

import streamlit as st
from datetime import date
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from db.db_operations import safe_db_call, insert_habit
from app_streamlit.utils import supabase_client as supabase
import time

# setup session state 
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "form_data" not in st.session_state:
    st.session_state.form_data = {}

if "warning_confirm" not in st.session_state:
    st.session_state.warning_confirm = False


# load categories
def load_categories():
    """Loads default and any custom categories available
    
    Returns: list of categories available"""
    default_categories = ["Health", "Productivity", "Finance", "Learning"]
    category_file = "data/categories.json"
    if os.path.exists(category_file):
        with open(category_file, 'r') as f:
            saved = json.load(f)
        cats = list(set(default_categories + saved))
    else:
        cats = default_categories
    if "Other" not in cats:
        cats.append("Other")
    return cats

# save custom categories to file
def save_custom_category(category_name):
    """Saves a custom category to file"""
    default_categories = ["Health", "Productivity", "Finance", "Learning"]
    category_file = "categories.json"
    if category_name not in default_categories:
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                current = json.load(f)
        else:
            current = []
        if category_name not in current:
            current.append(category_name)
            with open(category_file, 'w') as f:
                json.dump(current, f)


# Habit Form
def step1_fill_form():
    """Creates the interface for creating new activities"""
    st.header("Step 1: Create New Habit")

    # retrieve stored data if it exists
    stored_data = st.session_state.form_data if 'form_data' in st.session_state else {}

    habit = st.text_input("Habit Name", 
                          value=stored_data.get('habit', ''),
                          placeholder="e.g., Read Atomic Habits", max_chars=50)
    start_date = st.date_input("Start Date", 
                               value=stored_data.get('start_date', date.today()),
                               min_value=date.today())
    frequency = st.radio("Frequency", ["Daily", "Weekly", "Monthly"],
                         index=["Daily", "Weekly", "Monthly"].index(stored_data.get('frequency', 'Daily')))

    tracking_options = ["Yes/No (Completed or not)", "Count (Number-based)", "Duration (Minutes/hours)"]
    tracking = st.radio("How to track this habit?", tracking_options, 
                        index=tracking_options.index(stored_data.get('tracking',"Yes/No (Completed or not)" )))

    goal = None
    goal_units = None

    if tracking == "Yes/No (Completed or not)":
        st.info("Goals with this type are automatically expected to be completed at least once per frequency.")
    elif tracking == "Count (Number-based)":
        goal = st.number_input("Number of times you want to do this", min_value=1, step=1, 
                               value=int(stored_data.get('goal', 1)))
        goal_units = st.text_input("Enter unit of measurement", placeholder="e.g., times, reps, sets",
                                   value=stored_data.get('goal_units', ''))
        # goal_units = "times"
    elif tracking == "Duration (Minutes/hours)":
        goal = st.number_input("Number of minutes you want to spend", min_value=1, step=5,
                               value=int(stored_data.get('goal', 5)))
        goal_units = "minutes"

    categories = load_categories()
    category_default = stored_data.get('category', categories[0] if categories else '')
    category = st.selectbox("Category", categories,
                            index=categories.index(category_default) if category_default in categories else 0)

    custom_category = None
    if category == "Other":
        custom_category = st.text_input("Enter custom category",
                                        value=stored_data.get('category', '') if category_default == "Other" else '')

    notes = st.text_area("Why is this habit important?", 
                         height=100, 
                         placeholder="e.g., To improve my health, to learn a new skill, etc.",
                         value=stored_data.get('notes', ''))

    end_date_status = st.radio("When do you want to end?", ["Indefinitely", "Specific Date"],
                               index=["Indefinitely", "Specific Date"].index(stored_data.get('end_date_status', 'Indefinitely')))
    end_date = None
    if end_date_status == "Specific Date":
        end_date = st.date_input("Select End Date", min_value=date.today(),
                                 value=stored_data.get('end_date', date.today()))

    if st.button("Next ➡️"):
        if not habit:
            st.warning("Habit name is required.")
            return
        if category == "Other" and not custom_category:
            st.warning("Please provide a custom category name.")
            return
        if end_date_status == "Specific Date":
            if end_date < start_date:
                st.error("End date cannot be before start date.")
                st.stop()

        # Save data into session
        st.session_state.form_data = {
            'habit': habit,
            'start_date': start_date,
            'frequency': frequency,
            'tracking': tracking,
            'goal': goal,
            'goal_units': goal_units,
            'category': custom_category if custom_category else category,
            'notes': notes,
            'end_date_status': end_date_status,
            'end_date': end_date
        }
        st.session_state.current_step = 2
        st.rerun()


# Confirmation window
def step2_confirm():
    """Asks user to confirm information and save or edit"""
    st.header("Step 2: Confirm Habit Details")

    data = st.session_state.form_data

    goal_text = "Complete once " + data['frequency'].lower() if data['tracking'] == "Yes/No (Completed or not)" else f"{data['goal']} {data['goal_units']} per {data['frequency'].lower()}"
    end_date_text = data['end_date'].strftime("%Y-%m-%d") if data['end_date_status'] == "Specific Date" else "Indefinitely"

    st.markdown(f"**Habit:** {data['habit']}")
    st.markdown(f"**Start Date:** {data['start_date'].strftime('%Y-%m-%d')}")
    st.markdown(f"**Frequency:** {data['frequency']}")
    st.markdown(f"**Tracking:** {data['tracking']}")
    st.markdown(f"**Goal:** {goal_text}")
    st.markdown(f"**Category:** {data['category']}")
    st.markdown(f"**Notes:** {data['notes'] if data['notes'] else 'None'}")
    st.markdown(f"**End Date:** {end_date_text}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to Edit"):
            st.session_state.current_step = 1
            st.rerun()

    with col2:
        if st.button("✅ Confirm and Save"):
            try:
                st.write("Attempting to save habit...")
                success = supabase.insert_habit(
                    st.session_state.user_id,
                    data['habit'],
                    data['start_date'].isoformat(),
                    data['frequency'],
                    data['tracking'],
                    data['goal'],
                    data['goal_units'],
                    data['category'],
                    data['notes'],
                    data['end_date'].isoformat() if data['end_date_status'] == "Specific Date" else None
                )
                if success:
                    if data['category'] not in load_categories():
                        save_custom_category(data['category'])
                    
                    st.success("✅ Habit saved successfully!")
                    # st.session_state.habit_saved = True
                    
                    time.sleep(0.2)
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.error("Failed to save habit.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try again or contact support if the problem persists")



# if habit save is successful
def step3_success():
    """Tells user that save is successful and asks if user wants to create another activity"""
    st.header("Step 3: Habit Created! 🎉")
    st.success("Your habit has been saved successfully!")

    if st.button("Create Another Habit"):
        # Reset everything
        st.session_state.current_step = 1
        st.session_state.form_data = {}
        st.rerun()


# Main App Logic
def create_habit_wizard():
    """Controls the flow of the create activity functionality"""
    # initialize all needed session states 
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}

    # control flow
    if st.session_state.current_step == 1:
        step1_fill_form()
    elif st.session_state.current_step == 2:
        step2_confirm()
    elif st.session_state.current_step == 3:
        step3_success()
