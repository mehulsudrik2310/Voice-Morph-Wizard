import tkinter as tk

class UI:
    @staticmethod
    def draw_line(canvas, start_button, end_button):
        start_x = start_button.winfo_x() + start_button.winfo_width() / 2
        start_y = start_button.winfo_y() + start_button.winfo_height() / 2
        end_x = end_button.winfo_x() + end_button.winfo_width() / 2
        end_y = end_button.winfo_y() + end_button.winfo_height() / 2
        canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=2)  # Adjust color and width as needed
