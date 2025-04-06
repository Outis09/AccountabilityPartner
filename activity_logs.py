# import modules
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import helper as hp
from db import db_operations as db

class Activity:
    def __init__(self, window, main_window=None):
        self.window = window
        self.main_window = main_window

        # set window properties
        self.window.title("Log Activity")
        self.window.geometry("400x300")

        # handle window close event
        self.window.protocol("WM_DELETE_WINDOW",lambda: hp.on_closing(self))

        # create scrollable frame
        self.scrollable = hp.ScrollableFrame(self.window)
        self.scrollable.pack(fill="both", expand=True)

        # get frame
        self.main_frame = self.scrollable.get_frame()

        # create widgets
        self.create_widgets()

        # create final buttons
        self.create_final_buttons()

    def create_widgets(self):
        """Create widgets for frame"""
        # show valid categories
        self.valid_categories = db.get_categories()
        # select category prompt
        category_prompt = tk.Label(self.main_frame, text="Select Category:")
        category_prompt.pack()
        # combobox widget for categories dropdown
        self.selected_cat = tk.StringVar()
        self.cat_dropdown = ttk.Combobox(self.main_frame, textvariable=self.selected_cat, width=30)
        self.cat_dropdown['values'] = self.valid_categories
        self.cat_dropdown.bind("<<ComboboxSelected>>", self.update_habits_dropdown)
        self.cat_dropdown.pack()

        # log activity prompt
        log_prompt = tk.Label(self.main_frame, text="Select Habit:")
        log_prompt.pack(pady=10)
        # habits based on categories
        self.selected_habit = tk.StringVar()
        self.habit_dropdown = ttk.Combobox(self.main_frame,textvariable=self.selected_habit, width=30)
        self.habit_dropdown.pack()


        # activity date
        activity_date_prompt = tk.Label(self.main_frame, text="When did this activity take place?")
        activity_date_prompt.pack(pady=10)
        # tomorrow's date to ensure activity date is not in the future
        today = date.today()
        # calendar
        self.calendar = DateEntry(self.main_frame,
                                  width=12,
                                  background='darkblue',
                                  foreground='white',
                                  borderwidth=2,
                                  maxdate=today,
                                  date_pattern="yyyy-mm-dd"
                                  )
        self.calendar.pack(pady=10)

        # add notes
        activity_notes = tk.Label(self.main_frame, text="Any comments?")
        activity_notes.pack(pady=5)
        self.activity_comments = tk.Text(self.main_frame, height=5, width=30)
        self.activity_comments.pack(pady=5)
    
    def update_habits_dropdown(self,event):
        """Update the habits dropdown when a category is selected"""
        selected_category = self.selected_cat.get()
        if selected_category:
            self.selected_habits = db.get_habits(selected_category)
            self.habit_dropdown['values'] = self.selected_habits
    
    def create_final_buttons(self):
        """Create final buttons for frame"""
                # frame for final buttons
        self.btns_frame = tk.Frame(self.main_frame)
        self.btns_frame.pack(pady=10)
        # save activity button
        tk.Button(self.btns_frame, text="Save Activity").pack()
        # back to main window button
        tk.Button(self.btns_frame, text="Back to Main Window", command=lambda: hp.back_to_main_window(self)).pack()





# run the main application loop
if __name__ == "__main__":
    root = tk.Tk()  # create the main application window
    app = Activity(root)  # create an instance of the AccountabilityPartner class
    root.mainloop()  # run the main application loop