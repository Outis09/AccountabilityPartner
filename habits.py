"""
Add new habit window

This module implements the functionality for adding a new habit to the user's list of daily habits.
"""

# import required libraries
import tkinter as tk
from tkinter import ttk,messagebox

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

        # habit category
        category_prompt = tk.Label(main_frame, text="Select Habit Category:")
        category_prompt.pack(pady=10)
        category = tk.StringVar()
        ttk.Radiobutton(main_frame, text="Health", variable=category, value="Health").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Productivity", variable=category, value="Productivity").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Finance", variable=category, value="Finance").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Mindfulness", variable=category, value="Mindfulness").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Learning", variable=category, value="Learning").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Social", variable=category, value="Social").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Fun", variable=category, value="Fun").pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="Other", variable=category, value="Other").pack(anchor=tk.W)


        # button to go back to the main window
        tk.Button(main_frame, text="Back to Main Window", command=self.back_to_main_window).pack(pady=10)
    
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
