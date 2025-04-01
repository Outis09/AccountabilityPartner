"""
Accountability Partner

This application allows users to enter daily goals they want to achieve and track their progress. 
Users can add, view, and delete goals, as well as mark them as completed. 
The application uses a simple text-based interface for interaction.
The application uses Tkinter for the GUI, Pandas for data storage,csv for data storage, and PIL for image handling.
"""
# import required libraries
import tkinter as tk  # GUI framework for Python
from tkinter import ttk, messagebox, Label  # Widgets and dialogs for Tkinter
from PIL import Image, ImageTk  # For image handling and display
import pandas as pd  # For handling data manipulation and export
from datetime import datetime  # For timestamping exported files
import os  # For interacting with the operating system
from pathlib import Path  # For managing file paths

# main function to display the application's primary interface
def show_application_interface():
    """
    Displays the main application interface for the Accountability Partner app.
    """
    # destroy the get started button and quote label
    get_started_btn.destroy()   
    quote.destroy()

    # Add new daily habit button
    add_habit_btn = tk.Button(main_frame, text = "Add New Daily Habit", width=25)
    add_habit_btn.pack() #display the button in the main frame

    # Record today's activity button
    record_activity_btn = tk.Button(main_frame, text = "Record Today's Activity", width=25)
    record_activity_btn.pack() #display the button in the main frame

    # Export data button
    export_data_btn = tk.Button(main_frame, text = "Export habit data", width=25)
    export_data_btn.pack() #display the button in the main frame


# Main application window setup
root=tk.Tk()
root.geometry("800x700")
root.title("Accountability Partner")

# display application logo
image = Image.open('AppLogo.png')
image = image.resize((400,400)) # resize the image to fit the window
photo = ImageTk.PhotoImage(image) # convert the image to a PhotoImage object
logo = Label(root, image=photo, text="Accountability Partner logo") # create a label to display the image
logo.image = photo # keep a reference to the image to prevent garbage collection
logo.pack(pady=20) # pack the label into the window with some padding

# add text below logo
quote = tk.Label(root, text="""
We are what we repeatedly do… therefore excellence is not an act, but a habit.
                 
                 ~Aristotle
                 
Track your habits today!""", font=("Arial", 12), wraplength=500, justify="center")
quote.pack(pady=10) # pack the label into the window with some padding

main_frame = tk.Frame(root) # create a frame to hold the main content
main_frame.pack(fill=tk.BOTH, expand=True) # pack the frame into the window
main_frame.grid_rowconfigure(0, weight=1) # configure the row to expand with the window

# create a get started button to show the main interface
get_started_btn = ttk.Button(main_frame, text="Get Started", command=show_application_interface)
get_started_btn.pack(pady=20) # pack the button into the window with some padding

# run the main application loop
root.mainloop()