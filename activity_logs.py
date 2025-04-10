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

        # variable for confirming save
        self.confirmed_save = False

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
        self.habit_dropdown.bind("<<ComboboxSelected>>", self.on_habit_select)


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

        # activity frame
        self.activity_frame = tk.Frame(self.main_frame)
        # activity prompts
        self.yes_no_prompts = tk.Label(self.activity_frame,text="Did you complete this activity?")
        self.duration_prompts = tk.Label(self.activity_frame,text="How many minutes did you spend on this activity?")
        self.count_prompt = tk.Label(self.activity_frame,text="How many times did you do this")
        # radio for yes/no habits
        self.activity = tk.StringVar()
        self.yes_radio = ttk.Radiobutton(self.activity_frame, text="Yes", variable=self.activity, value="yes")
        self.no_radio = ttk.Radiobutton(self.activity_frame, text="No", variable=self.activity,value="no")
        self.other_tracking_entry = tk.Entry(self.activity_frame)


        # rating frame
        self.rating_frame = tk.Frame(self.main_frame)
        self.rating_frame.pack()
        # rating prompt
        self.rating_prompt = tk.Label(self.rating_frame, text="On a scale of 1-5, How would you rate your productivity during this activity?")
        self.rating_prompt.pack()
        # rating entry
        self.rating_entry = tk.Entry(self.rating_frame)
        self.rating_entry.pack()

        # add notes
        self.notes_frame = tk.Frame(self.main_frame)
        self.notes_frame.pack()
        activity_notes = tk.Label(self.notes_frame, text="Any comments?")
        activity_notes.pack(pady=5)
        self.activity_comments = tk.Text(self.notes_frame, height=5, width=30)
        self.activity_comments.pack(pady=5)
    
    def update_habits_dropdown(self,event):
        """Update the habits dropdown when a category is selected"""
        selected_category = self.selected_cat.get()
        if selected_category:
            self.habit_details = db.get_habits(selected_category)
            self.selected_habits = list(self.habit_details.keys())
            self.habit_dropdown['values'] = self.selected_habits

    def on_habit_select(self, event=None):
        """Generate appropriate prompt for user entry based on selected habit"""
        selected_habit = self.selected_habit.get()
        self.tracking_type = self.habit_details.get(selected_habit)
        if selected_habit:
            self.activity_frame.pack(before=self.rating_frame)
            if self.tracking_type == "Daily":
                self.yes_no_prompts.pack()
                self.yes_radio.pack()
                self.no_radio.pack()
                self.count_prompt.pack_forget()
                self.duration_prompts.pack_forget()
                self.other_tracking_entry.pack_forget()
            elif self.tracking_type == "Weekly":
                self.count_prompt.pack()
                self.other_tracking_entry.pack()
                self.yes_radio.pack_forget()
                self.no_radio.pack_forget()
                self.yes_no_prompts.pack_forget()
                self.duration_prompts.pack_forget()
            elif self.tracking_type == "Monthly":
                self.duration_prompts.pack()
                self.other_tracking_entry.pack()
                self.yes_radio.pack_forget()
                self.no_radio.pack_forget()
                self.yes_no_prompts.pack_forget()
                self.count_prompt.pack_forget()
    
    def create_final_buttons(self):
        """Create final buttons for frame"""
        # frame for final buttons
        self.btns_frame = tk.Frame(self.main_frame)
        self.btns_frame.pack(pady=10)
        # save activity button
        tk.Button(self.btns_frame, text="Save Activity", command=self.save_activity).pack()
        # back to main window button
        tk.Button(self.btns_frame, text="Back to Main Window", command=lambda: hp.back_to_main_window(self)).pack()

    def save_activity(self):
        """Save activity by inserting entered values into db, after checking for nulls"""
        category = self.selected_cat.get()
        habit = self.selected_habit.get()
        activity_date = self.calendar.get_date()
        if self.tracking_type == "Daily":
            activity = self.activity.get()
        else:
            activity = self.other_tracking_entry.get()
        rating = self.rating_entry.get()
        comments = self.activity_comments.get("1.0", tk.END).strip()

        # list of tuples to hold corresponding field names
        fields = [
            (category, "Category"),
            (habit, "Habit"),
            (activity_date, "Activity Date"),
            (activity, "Tracking Input"),
            (rating, "Rating")
        ]
        # missing fields
        missing = [label for value, label in fields if not value]
        # check for any null values
        if missing:
            messagebox.showerror("Error", f"{', '.join(missing)} cannot be blank.")
            return
        
        if self.tracking_type != "Daily" and not activity.isdigit():
            messagebox.showerror("Error", "Please enter a valid value for tracking input")
            return
        elif self.tracking_type != "Daily" and int(activity) <= 0:
            messagebox.showerror("Error", "Tracking input cannot be zero or negative")
            return
        elif self.tracking_type == "Weekly" and int(activity) >= 300 and self.confirmed_save == False:
            warning = messagebox.askyesno("High Value Input", "The minutes you entered is unusually large. Are you sure you want to continue?")
            if warning:
                self.confirmed_save = True
            return
        elif self.tracking_type == "Monthly" and int(activity) > 10 and self.confirmed_save == False:
            warning = messagebox.askyesno("High Value Input", "The number of times you performed this activity is unusually high. Are you sure you want to continue?")
            if warning:
                self.confirmed_save = True
            return

# run the main application loop
if __name__ == "__main__":
    root = tk.Tk()  # create the main application window
    app = Activity(root)  # create an instance of the Activity class
    root.mainloop()  # run the main application loop