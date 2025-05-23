"""
Add new habit window

This module implements the functionality for adding a new habit to the user's list of daily habits.
"""

# import required libraries
import tkinter as tk
from tkinter import ttk,messagebox
from tkcalendar import DateEntry  # For date selection
from datetime import datetime, date
import json 
import os
import textwrap
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db_operations
import helper as hp

class Habits:
    def __init__(self,window,  main_window):
        self.window = window
        self.main_window = main_window

        # set window properties
        self.window.title("Create Habit")
        self.window.geometry("400x300")

        # handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # create scrollable frame
        self.scrollable = hp.ScrollableFrame(self.window)
        self.scrollable.pack(fill="both", expand=True)

        # get frame
        self.main_frame = self.scrollable.get_frame()

        # enter habit name button
        habit_prompt = tk.Label(self.main_frame, text="Enter Habit Name (eg. Read for 30 mins each day):")
        self.new_habit_entry = tk.Entry(self.main_frame, width=30)
        habit_prompt.pack(pady=10)
        self.new_habit_entry.pack(pady=10)

        # start date
        start_date_prompt = tk.Label(self.main_frame, text="When do you want to start?")
        start_date_prompt.pack(pady=10)
        # calendar
        self.cal = DateEntry(self.main_frame, 
                        width=12, 
                        background='darkblue', 
                        foreground='white', 
                        borderwidth=2, 
                        date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)
        # variable to hold selected date
        self.start_date = self.cal.get_date()

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
                            value=option).pack()
            
        # habit tracking
        tracking_prompt = tk.Label(self.main_frame,text="How do you want to track this habit?")
        tracking_prompt.pack()
        # tracking options
        self.tracking_options = ["Yes/No (Completed or not)",
                                 "Count (Number-based)",
                                 "Duration (Minutes/hours)"]
        # variable to hold tracking type
        self.tracking_type = tk.StringVar()
        # radio to display tracking options
        for option in self.tracking_options:
            ttk.Radiobutton(self.main_frame,
                            text=option,
                            variable=self.tracking_type,
                            value=option,
                            command=self.tracking_display).pack()
        # variable to hold goal
        self.habit_goal = tk.StringVar()       
        # frame to hold goals
        self.goal_frame = tk.Frame(self.main_frame)
        # set goals for yes/no habits
        self.yes_no_prompt = tk.Label(self.goal_frame, text="""
                                      Goals with this track type are automatically expected
                                      to be completed at least once
                                      per chosen frequency""")
        # set goals for counts
        self.count_goals = tk.Label(self.goal_frame, text="How many times do you want to do this?")
        # set goals for duration
        self.duration_goals = tk.Label(self.goal_frame, text="How many minutes do you want to spend on this?")
        # entry for goal
        self.goal = tk.Entry(self.goal_frame)
        
        
        # file to store habit categories
        self.category_file = "data/categories.json"
        # default categories
        self.default_categories = ["Health", "Productivity", "Finance", "Learning"]

 
        # create variable to store selected category
        self.category = tk.StringVar()
        # categories
        categories = self.load_categories()
        # frame for radio buttons
        self.category_frame = tk.Frame(self.main_frame)
        self.category_frame.pack()
        # habit category
        category_prompt = tk.Label(self.category_frame, text="Select Habit Category:")
        category_prompt.pack(pady=10)
        # create radio buttons for each category
        for category_name in categories:
            ttk.Radiobutton(self.main_frame, 
                            text=category_name, 
                            variable=self.category, 
                            value=category_name, 
                            command=self.on_category_select).pack()
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
        self.notes_entry = tk.Text(self.notes_frame, height=5, width=30)
        self.notes_entry.pack(pady=5)

        # end date frame
        self.end_date_frame  = tk.Frame(self.main_frame)
        self.end_date_frame.pack(pady=10)
        # add end date
        end_date_prompt = tk.Label(self.end_date_frame, text="When do you want to end?")
        end_date_prompt.pack(pady=10)

        # end date calendar frame
        self.end_date_cal_frame = tk.Frame(self.main_frame)
        # today
        today = date.today()
        # end date calendar
        self.end_date_cal = DateEntry(self.end_date_cal_frame, 
                        width=12, 
                        background='darkblue', 
                        foreground='white', 
                        borderwidth=2, 
                        mindate=today,
                        date_pattern="yyyy-mm-dd")
        # end date status
        self.end_date_status = tk.StringVar(value="Indefinitely")
        # end date options
        end_date_options = ["Indefinitely", "Specific Date"]
        for option in end_date_options:
            ttk.Radiobutton(self.main_frame,
                            text=option, 
                            variable=self.end_date_status, 
                            value=option,
                            command=self.on_end_date_toggle).pack()


        # frame for final buttons
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=10)
        # button to save habit
        tk.Button(self.buttons_frame, text="Save Habit", command=self.save_habit).pack()
        # button to go back to the main window
        tk.Button(self.buttons_frame, text="Back to Main Window", command=self.back_to_main_window).pack()

        # variable of if user has already tried submitting
        self.warning_confirm = False


    def on_mouse_wheel(self, event):
        "Handle mouse when scrolling"
        # if event.num == 4 or event.delta > 0:
        #     # scroll up
        #     self.canvas.yview_scroll(-1, "units")
        # elif event.num == 5 or event.delta < 0:
        #     # scroll down
        #     self.canvas.yview_scroll(1, "units")
        # else:
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def on_end_date_toggle(self):
        if self.end_date_status.get() == "Specific Date":
            self.end_date_cal_frame.pack(after=self.end_date_frame,before=self.buttons_frame, pady=5)
            self.end_date_cal.pack(in_=self.end_date_cal_frame,pady=5)
        else:
            self.end_date_cal_frame.pack_forget()
            # self.end_date_cal.pack_forget()
    
    # function to load categories from file
    def load_categories(self):
        if os.path.exists(self.category_file):
            with open(self.category_file, 'r') as file:
                saved = json.load(file)
            cats = list(set(self.default_categories + saved))
        else:
            cats = list(self.default_categories)
        if 'Other' not in cats:
            cats.append("Other")
        return cats
        
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
            self.cust_cat_frame.pack(after=self.category_frame,before=self.notes_frame, pady=5)
            self.custom_entry_label.pack(in_=self.cust_cat_frame,pady=5)
            self.custom_entry.pack(in_=self.cust_cat_frame,pady=5)
        else:
            # self.custom_entry_label.pack_forget()
            # self.custom_entry.pack_forget()
            self.cust_cat_frame.pack_forget()

    # on save habit button click
    def save_habit(self):
        habit = self.new_habit_entry.get()
        start_date = self.start_date
        frequency = self.frequency.get()
        tracking = self.tracking_type.get()
        if self.category.get() == "Other":
            category = self.custom_entry.get()
        else:
            category = self.category.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()
        wrapped_notes = textwrap.fill(notes, width=50)  # Wrap notes to 50 characters
        end_date_status = self.end_date_status.get()
        if end_date_status == "Specific Date":
            end_date = self.end_date_cal.get_date()
        else:
            end_date = None
        if tracking != "Yes/No (Completed or not)":
            goal = self.goal.get()
            if tracking == "Count (Number-based)":
                goal_units = "times"
            elif tracking == "Duration (Minutes/hours)":
                goal_units = "minutes"            
        else:
            goal = None
            goal_units = None

        # check if any mandatory field is empty
        mandatory_fields = [habit, start_date, frequency, tracking, category]
        # list to hold corresponding field names
        field_names = [
            (habit, "Habit"),
            (start_date, "Start Date"),
            (frequency, "Frequency"),
            (tracking, "Tracking Type"),
            (category, "Category")
        ]
        # missing fields
        missing_fields = [label for value, label in field_names if not value]
        # append goal label if tarcking type is not yes/no
        if self.tracking_type.get() != "Yes/No (Completed or not)" and not goal:
            missing_fields.append("Goal")
        # check if habit name is empty
        if missing_fields:
            messagebox.showerror("Error", f"{', '.join(missing_fields)} cannot be blank.")
            return
        
        # validate goal
        if goal:
            if not goal.isdigit():
                messagebox.showerror("Error", "Enter a valid goal")
                return
            elif float(goal) <= 0:
                messagebox.showerror("Error","Goal cannot be zero or negative")
                return
            elif tracking == "Count (Number-based)" and float(goal) > 10 and self.warning_confirm == False:
                warning = messagebox.askyesno("High Value Warning","The value you entered is unusually high. Are you sure you want to continue?")
                if warning:
                    self.warning_confirm = True
                return
            elif tracking == "Duration (Minutes/hours)" and float(goal) > 300 and self.warning_confirm == False:
                warning = messagebox.askyesno("High Value Warning","The goal value you entered is unusually high. Are you sure you want to continue?")
                if warning:
                    self.warning_confirm = True
                return
            
        
        # preview habit details
        habit_details = f"""
Habit: {habit}

Start Date: {start_date}

Frequency: {frequency}

Tracking Type: {tracking}

Goal: {goal} {goal_units} {frequency.lower()}

Category: {category}

Notes: {wrapped_notes if notes else "None"}

End Date: {end_date if end_date else "Indefinitely"}
        """
        
        # confirmation dialog
        if messagebox.askokcancel("Confirm Habit", habit_details):
            # save custom category if user entered one
            if self.custom_entry.get():
                self.save_custom_category(self.custom_entry.get())
            # save habit to database
            success = db_operations.safe_db_call(db_operations.insert_habit,habit, start_date, frequency,tracking,goal, goal_units, category, notes, end_date, success_message="Habit saved successfully!")
            if success:
                self.window.destroy()
                self.main_window.deiconify()

    def tracking_display(self):
        self.goal_frame.pack(before=self.category_frame)
        # display goal prompts when tracking is not yes/no
        if self.tracking_type.get() == "Yes/No (Completed or not)":
            self.goal.pack_forget()
            self.yes_no_prompt.pack()
            self.count_goals.pack_forget()
            self.duration_goals.pack_forget()
        elif self.tracking_type.get() == 'Count (Number-based)':
            self.goal.pack_forget()
            self.count_goals.pack()
            self.goal.pack()
            self.yes_no_prompt.pack_forget()
            self.duration_goals.pack_forget()
        elif self.tracking_type.get() == 'Duration (Minutes/hours)':
            self.goal.pack_forget()
            self.duration_goals.pack()
            self.goal.pack()
            self.count_goals.pack_forget()
            self.yes_no_prompt.pack_forget()

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
