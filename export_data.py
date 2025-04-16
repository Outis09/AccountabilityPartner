# import modules
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import helper as hp
from db import db_operations as db

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
                            value=option,
                            command=self.display_filters).pack()
    
        # frame to hold filter options
        self.filter_frame = tk.Frame(self.main_frame)
        # general filter label
        self.general_filter = tk.Label(self.filter_frame, text="Filter by:")
        # filter by category
        self.cat_filter_prompt = tk.Label(self.filter_frame, text="Category:")
        # categories
        self.categories = db.get_categories()
        self.category = tk.StringVar()
        self.cat_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.category)
        self.cat_dropdown['values'] = self.categories
        self.cat_dropdown.bind("<<ComboboxSelected>>", self.update_habits)
        # filter by habit
        self.habit_filter_prompt = tk.Label(self.filter_frame, text="Habit:")
        # habits
        self.habit = tk.StringVar()
        self.habit_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.habit)

        # tracking type
        self.tracking_prompt = tk.Label(self.filter_frame, text="Tracking Type:") 

        # frequency
        self.frequency_prompt = tk.Label(self.filter_frame, text="Frequency:")
        

        
        # create frame to hold widgets
        self.final_widgets_frame = tk.Frame(self.main_frame)
        self.final_widgets_frame.pack()
        # create export data button widget
        tk.Button(self.final_widgets_frame, text="Export Data", command=self.save_data).pack()
        # create back to main window widget
        tk.Button(self.final_widgets_frame, text="Back to Main Window").pack()

    def display_filters(self):
        selected = self.download_option.get()
        if selected == "Export filtered data":
            self.filter_frame.pack(before=self.final_widgets_frame)
            self.general_filter.grid(row=0, column=0, sticky='ne')
            self.cat_filter_prompt.grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.cat_dropdown.grid(row=1, column=1)
            self.habit_filter_prompt.grid(row=1, column=2)
            self.habit_dropdown.grid(row=1, column=3)
            self.tracking_prompt.grid(row=2, column=0)
            self.frequency_prompt.grid(row=2, column=2)
        else:
            self.filter_frame.pack_forget()

    def update_habits(self, event):
        """Update the habits dropdown when a category is selected"""
        selected_cat = self.category.get()
        if selected_cat:
            self.habit_details = db.get_habits(selected_cat)
            self.habits = list(self.habit_details.keys())
            self.habit_dropdown['values'] = self.habits
        else:
            prompt = ["Select a category to proceed"]
            self.habit_dropdown['values'] = prompt

    def save_data(self):
        option = self.download_option.get()
        if option == "Export all habit data":
            df = db.get_all_habits_to_df()
        elif option == "Export all activity logs":
            df = db.get_all_activity_logs()
        elif not option:
            messagebox.showinfo("Data Information", "No option selected!")
            return
        
        # file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Excel File As"
        )

        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data saved to: \n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to saved file:\n{e}")
        else:
            messagebox.showinfo("Cancelled", "Save operation was cancelled.")
            return


# run the window
if __name__ == "__main__":
    root = tk.Tk()
    data_export = DataExporter(root)
    root.mainloop()