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
        self.window.title("Add New Habit")
        self.window.geometry("400x300")

        # handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # center window content
        main_frame = tk.Frame(self.window)
        main_frame.pack(expand=True)

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
