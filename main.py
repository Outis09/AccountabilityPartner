"""
Accountability Partner

This application allows users to enter daily goals they want to achieve and track their progress. 
Users can add, view, and delete goals, as well as mark them as completed. 
The application uses a simple text-based interface for interaction.
The application uses Tkinter for the GUI, Pandas for data storage,csv for data storage, and PIL for image handling.
"""
# import required libraries
import tkinter as tk  # GUI framework for Python
from tkinter import ttk, messagebox, Label, PhotoImage  # Widgets and dialogs for Tkinter
from PIL import Image, ImageTk  # For image handling and display
import pandas as pd  # For handling data manipulation and export
from datetime import datetime  # For timestamping exported files
import os  # For interacting with the operating system
from pathlib import Path  # For managing file paths

from habits import Habits  # Importing the Habits class from the habits module
from db import init_db

class AccountabilityPartner:
    """
    Accountability Partner application class.
    
    This class initializes the main application window and handles the display of the main interface.
    """
    def __init__(self,root):
        self.root = root
        # Main application window setup
        root.geometry("800x700")
        root.title("Accountability Partner")

        # load and resize image
        self.load_and_resize_image('AppLogo.png', (400, 400))

        # show welcome screen
        self.show_welcome_screen()

        # initialize db
        init_db.initialize_database()

    def load_and_resize_image(self, image_path, size):
        # load image
        image = Image.open(image_path)
        # resize image
        image = image.resize(size)
        # convert to PhotoImage
        self.logo = ImageTk.PhotoImage(image)        
    
    def show_welcome_screen(self):
        """
        Displays the welcome screen with the application logo and a quote.
        """
        # destroy the previous widgets if any
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # create welcome frame
        welcome_frame = tk.Frame(self.root)
        welcome_frame.pack(fill=tk.BOTH, expand=True) # pack the frame into the window

        # display application logo
        image_label = Label(welcome_frame,image=self.logo)
        image_label.pack(pady=20)

        # add text below logo
        quote = tk.Label(welcome_frame, text="""
        We are what we repeatedly do… therefore excellence is not an act, but a habit.
                        
                        ~Aristotle
                        
        Track your habits today!""", font=("Arial", 12), wraplength=500, justify="center")
        quote.pack(pady=10) # pack the label into the window with some padding

        # create a get started button to show the main interface
        get_started_btn = ttk.Button(welcome_frame, text="Get Started", command=self.show_application_interface)
        get_started_btn.pack(pady=20) # pack the button into the window with some padding

        # main function to display the application's primary interface
    def show_application_interface(self):
        """
        Displays the main application interface for the Accountability Partner app.
        """
        # destroy the welcome screen and create the main frame
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root) # create a frame to hold the main content
        main_frame.pack(fill=tk.BOTH, expand=True) # pack the frame into the window
        main_frame.grid_rowconfigure(0, weight=1) # configure the row to expand with the window

        # display application logo
        image_label = Label(main_frame,image=self.logo)
        image_label.pack(pady=20)
        
        # Add new daily habit button
        add_habit_btn = tk.Button(main_frame, text = "Create Habit", width=25, command=self.open_habits)
        add_habit_btn.pack() #display the button in the main frame

        # Record today's activity button
        record_activity_btn = tk.Button(main_frame, text = "Log Activity", width=25)
        record_activity_btn.pack() #display the button in the main frame

        # Analyze progress button
        analyze_progress_btn = tk.Button(main_frame, text = "View Progress", width=25)
        analyze_progress_btn.pack()

        # Export data button
        export_data_btn = tk.Button(main_frame, text = "Download Report", width=25)
        export_data_btn.pack() #display the button in the main frame

    # function to open habits window
    def open_habits(self):
        """
        Opens the Add New Habit window.
        """
        # hide the main window and open the habits window
        self.root.withdraw()
        habits_window = tk.Toplevel(root)  # create a new top-level window
        Habits(habits_window, self.root)  # pass the new window and main window to the Habits class

# run the main application loop
if __name__ == "__main__":
    root = tk.Tk()  # create the main application window
    app = AccountabilityPartner(root)  # create an instance of the AccountabilityPartner class
    root.mainloop()  # run the main application loop