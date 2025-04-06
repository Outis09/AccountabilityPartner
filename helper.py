# import libraries
import tkinter as tk
from tkinter import ttk, messagebox


# class for scrollable frame
class ScrollableFrame:
    def __init__(self, parent, width=400, height=300):
        self.parent = parent

        # create container frame
        self.container = tk.Frame(self.parent)
        self.container.pack(fill="both", expand=True)

        # create canvas with scrollbar
        self.canvas = tk.Canvas(self.container, width=width, height=height)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical",command=self.canvas.yview)

        # configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # pack scrollbar first
        self.scrollbar.pack(side="right", fill="y")
        # pack canvas
        self.canvas.pack(side="left", fill="both", expand=True)

        # create main frame inside canvas
        self.main_frame = tk.Frame(self.canvas)

        # add main frame to canvas
        self.inner_window = self.canvas.create_window((0,0), window=self.main_frame, anchor="nw")

        # minimum width of the frame
        self.main_frame.configure(width=width)

        # update scrollregion when frame changes
        self.main_frame.bind("<Configure>", self._on_frame_configure)

        # make inner window adjust to canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # bind mouse wheel to scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_frame_configure(self, event=None):
        """" Update the scrollregion to include the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Resize the inner frame to match canvas, if resized"""
        if event:
            self.canvas.itemconfig(self.inner_window, width=event.width)

    def _on_mouse_wheel(self, event=None):
        """Handle mouse scrolling"""
        if event:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def pack(self, **kwargs):
        """Pass pack geometry manager arguments to container"""
        self.container.pack(**kwargs)

    def get_frame(self):
        "Return the inner frame where widgets should be placed"
        return self.main_frame


