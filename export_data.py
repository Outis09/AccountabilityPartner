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

        # create widgets
        self.create_widgets()



    
    def create_widgets(self):
        self.download_options = ['Export all habit data', 'Export all activity logs', 'Export filtered data']
        self.download_option = tk.StringVar()
        for option in self.download_options:
            ttk.Radiobutton(self.main_frame,
                            text=option,
                            variable=self.download_option,
                            value=option).pack()
    
        # create frame to hold widgets
        self.final_widgets_frame = tk.Frame(self.main_frame)
        self.final_widgets_frame.pack()
        # create export data button widget
        tk.Button(self.final_widgets_frame, text="Export Data").pack()
        # create back to main window widget
        tk.Button(self.final_widgets_frame, text="Back to Main Window").pack()

        


# run the window
if __name__ == "__main__":
    root = tk.Tk()
    data_export = DataExporter(root)
    root.mainloop()