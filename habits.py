"""
Add new habit window

This module implements the functionality for adding a new habit to the user's list of daily habits.
"""

# import required libraries
import tkinter as tk
from tkinter import ttk,messagebox
from tkcalendar import DateEntry  # For date selection
import json 
import os

class Habits:
    def __init__(self, window, main_window):
        self.window = window
        self.main_window = main_window

        # set window properties
        self.window.title(" Create Habit")
        self.window.geometry("400x300")

        # handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # center window content
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(expand=True)

        # enter habit name button
        habit_prompt = tk.Label(self.main_frame, text="Enter Habit Name (eg. Read for 30 mins each day):")
        new_habit_entry = tk.Entry(self.main_frame)
        habit_prompt.pack(pady=10)
        new_habit_entry.pack(pady=10)

        # start date
        start_date_prompt = tk.Label(self.main_frame, text="When do you want to start?")
        start_date_prompt.pack(pady=10)
        # calendar
        cal = DateEntry(self.main_frame, 
                        width=12, 
                        background='darkblue', 
                        foreground='white', 
                        borderwidth=2, 
                        date_pattern="yyyy-mm-dd")
        cal.pack(pady=10)
        # variable to hold selected date
        self.start_date = cal.get_date()

        # habit frequency
        frequency_prompt = tk.Label(self.main_frame, text="How often do you want to do this?")
        frequency_prompt.pack(pady=10)
        # create variable to store selected frequency and set default value
        self.frequency = tk.StringVar(value="Daily")
        # frequency options
        frequency_options = ["Daily", "Weekly", "Monthly"]
        for option in frequency_options:
            ttk.Radiobutton(self.main_frame,
                            text=option, 
                            variable=self.frequency, 
                            value=option).pack(anchor=tk.W)
            

        # file to store habit categories
        self.category_file = "categories.json"
        # default categories
        self.default_categories = ["Health", "Productivity", "Finance", "Learning", "Other"]

        # habit category
        category_prompt = tk.Label(self.main_frame, text="Select Habit Category:")
        category_prompt.pack(pady=10)
        # create variable to store selected category
        self.category = tk.StringVar()
        # categories
        categories = self.load_categories()
        # frame for radio buttons
        self.radio_frame = tk.Frame(self.main_frame)
        self.radio_frame.pack()
        # create radio buttons for each category
        for category_name in categories:
            ttk.Radiobutton(self.main_frame, 
                            text=category_name, 
                            variable=self.category, 
                            value=category_name, 
                            command=self.on_category_select).pack(anchor=tk.W)
        # frame to control where dynamic category entry field appears
        self.cust_cat_frame = tk.Frame(self.main_frame)
        # custom entry label and entry field
        self.custom_entry_label = tk.Label(self.cust_cat_frame, text="Enter custom category name:")
        self.custom_entry = tk.Entry(self.cust_cat_frame)

        # frame to hold notes/motivation
        self.notes_frame = tk.Frame(self.main_frame)
        self.notes_frame.pack(pady=10)
        # notes label and entry field
        notes_label = tk.Label(self.notes_frame, text="Why is this habit important to you?:")
        notes_label.pack(pady=5)
        notes_entry = tk.Text(self.notes_frame, height=5, width=30)
        notes_entry.pack(pady=5)


        # frame for final buttons
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=10)
        # button to save habit
        tk.Button(self.buttons_frame, text="Save Habit").pack()
        # button to go back to the main window
        tk.Button(self.buttons_frame, text="Back to Main Window", command=self.back_to_main_window).pack()

    # function to load categories from file
    def load_categories(self):
        if os.path.exists(self.category_file):
            with open(self.category_file, 'r') as file:
                saved = json.load(file)
            return list(set(self.default_categories + saved))
        else:
            return self.default_categories
        
    # function to save new category to file
    def save_custom_category(self,category_name):
        if category_name not in self.default_categories:
            current = []
            if os.path.exists(self.category_file):
                with open(self.category_file, 'r') as file:
                    current = json.load(file)
            if category_name not in current:
                current.append(category_name)
                with open(self.category_file, 'w') as file:
                    json.dump(current, file)
    
    # function to present entry box if user selects "Other" category
    def on_category_select(self):
        if self.category.get() == "Other":
            self.cust_cat_frame.pack(after=self.radio_frame,before=self.notes_frame, pady=5)
            self.custom_entry_label.pack(in_=self.cust_cat_frame,pady=5)
            self.custom_entry.pack(in_=self.cust_cat_frame,pady=5)
        else:
            self.custom_entry_label.pack_forget()
            self.custom_entry.pack_forget()

    def back_to_main_window(self):
        """
        Close the current window and return to the main window.
        """
        self.window.destroy()
        self.main_window.deiconify()

    def on_closing(self):
        """
        Handle the window close event.
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()
            self.main_window.deiconify()
