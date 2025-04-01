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
    Displays the main application interface for the Accountability Partner af
    """

# Main application window setup
root=tk.Tk()
root.geometry("600x600")
root.title("Accountability Partner")

# display application logo
image = Image.open('AppLogo.png')
image = image.resize((400,400)) # resize the image to fit the window
photo = ImageTk.PhotoImage(image) # convert the image to a PhotoImage object
logo = Label(root, image=photo, text="Accountability Partner logo") # create a label to display the image
logo.image = photo # keep a reference to the image to prevent garbage collection
logo.pack(pady=20) # pack the label into the window with some padding

# run the main application loop
root.mainloop()