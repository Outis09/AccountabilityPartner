# import modules
import tkinter as tk
from tkinter import ttk, messagebox
import helper as hp

class DataExporter:
    def __init__(self, window, main_window=None):
        self.window = window
        self.main_window = main_window
        
        # window properties
        self.window.title("Export Data")
        self.window.geometry("400x300")

        # create scrollable frame
        self.scroll = hp.ScrollableFrame(self.window)
        self.scroll.pack(fill="both", expand=True)

        # get frame
        self.main_frame = self.scroll.get_frame()

# run the window
if __name__ == "__main__":
    root = tk.Tk()
    data_export = DataExporter(root)
    root.mainloop()