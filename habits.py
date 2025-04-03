"""
Add new habit window

This module implements the functionality for adding a new habit to the user's list of daily habits.
"""

# import required libraries
import tkinter as tk
from tkinter import ttk,messagebox
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
        main_frame = tk.Frame(self.window)
        main_frame.pack(expand=True)

        # enter habit name button
        habit_prompt = tk.Label(main_frame, text="Enter Habit Name (eg. Read for 30 mins each day):")
        new_habit_entry = tk.Entry(main_frame)
        habit_prompt.pack(pady=10)
        new_habit_entry.pack(pady=10)

        # file to store habit categories
        category_file = "categories.json"
        # default categories
        default_categories = ["Health", "Productivity", "Finance", "Learning", "Other"]

        # function to load categories from file
        def load_categories():
            if os.path.exists(category_file):
                with open(category_file, 'r') as file:
                    saved = json.load(file)
                return list(set(default_categories + saved))
            else:
                return default_categories
            
        # function to save new category to file
        def save_custom_category(category_name):
            if category_name not in default_categories:
                current = []
                if os.path.exists(category_file):
                    with open(category_file, 'r') as file:
                        current = json.load(file)
                if category_name not in current:
                    current.append(category_name)
                    with open(category_file, 'w') as file:
                        json.dump(current, file)
        
        # function to present entry box if user selects "Other" category
        def on_category_select():
            if category.get() == "Other":
                cust_cat_frame.pack(after=radio_frame,before=buttons_frame, pady=5)
                custom_entry_label.pack(in_=cust_cat_frame,pady=5)
                custom_entry.pack(in_=cust_cat_frame,pady=5)
            else:
                custom_entry_label.pack_forget()
                custom_entry.pack_forget()



        # habit category
        category_prompt = tk.Label(main_frame, text="Select Habit Category:")
        category_prompt.pack(pady=10)
        # create variable to store selected category
        category = tk.StringVar()
        # categories
        categories = load_categories()
        # frame for radio buttons
        radio_frame = tk.Frame(main_frame)
        radio_frame.pack()
        # create radio buttons for each category
        for category_name in categories:
            ttk.Radiobutton(main_frame, 
                            text=category_name, 
                            variable=category, 
                            value=category_name, 
                            command=on_category_select).pack(anchor=tk.W)
        # frame to control where dynamic category entry field appears
        cust_cat_frame = tk.Frame(main_frame)
        # custom entry label and entry field
        custom_entry_label = tk.Label(cust_cat_frame, text="Enter custom category name:")
        custom_entry = tk.Entry(cust_cat_frame)


        # frame for final buttons
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        # button to go back to the main window
        tk.Button(buttons_frame, text="Back to Main Window", command=self.back_to_main_window).pack(pady=10)
    
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
