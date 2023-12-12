import os
import tkinter as tk
from tkinter import messagebox
from typing import List
from ui import UI

class Utils:
    @staticmethod
    def set_min_size(window: tk.Tk) -> None:
        """
        Set the minimum size of a Tkinter window to its current size.

        Parameters:
            window (tk.Tk): The Tkinter window for which to set the minimum size.

        This function sets the minimum size of the Tkinter window to its current size,
        ensuring that the window cannot be resized to a smaller, unusable size.

        Example usage:
            Utils.set_min_size(window)
        """
        # Update the window to ensure it's fully rendered
        window.update_idletasks()
        # Get the current window width and height
        width = window.winfo_width()
        height = window.winfo_height()

        # Set the minimum size to the current size
        window.minsize(width, height)

    @staticmethod
    def shorten_file_name(file_path: str, max_chars: int) -> str:
        """
        Shorten a file name to fit within a specified maximum character limit.

        Parameters:
            file_path (str): The path to the file whose name needs to be shortened.
            max_chars (int): The maximum number of characters the shortened name should have.

        Returns:
            str: The shortened file name.

        If the file name is longer than the specified character limit, it is truncated
        and "..." is added to indicate truncation.

        Example usage:
            shortened_name = Utils.shorten_file_name("/path/to/long_file_name.txt", 20)
        """
        file_name = os.path.basename(file_path)
        if len(file_name) <= max_chars:
            return file_name
        else:
            return file_name[:max_chars - 3] + "..."

    @staticmethod
    def toggle_button_color(button: tk.Button, canvas: tk.Canvas, microphone_button: tk.Button, audio_buttons: List[tk.Button], output_button: tk.Button) -> None:
        """
        Toggle the color of a button between active and inactive states.

        Parameters:
            button (tk.Button): The Tkinter button to toggle the color of.
            canvas (tk.Canvas): The Tkinter canvas to update lines on.
            microphone_button (tk.Button): The microphone button.
            audio_buttons (List[tk.Button]): A list of audio buttons.
            output_button (tk.Button): The output button.

        This function changes the background color of the button to indicate its state.

        If the button is currently inactive (original color), it changes the background color
        to green when selected and updates the lines on the canvas to reflect the new state.
        If the button is currently active (green), it changes the background color back to
        the original color and updates the lines on the canvas accordingly.
        """
        current_color = button.cget("background")
        original_color = button.data["original_color"]
        if current_color == original_color:
            button.configure(background="#2ECC71")  # Change to green when selected
            Utils.update_lines(canvas, microphone_button, audio_buttons, output_button)  # Call to update lines when a button is toggled
        else:
            button.configure(background=original_color)
            Utils.update_lines(canvas, microphone_button, audio_buttons, output_button)

    
    @staticmethod
    def update_lines(canvas: tk.Canvas, microphone_button: tk.Button, audio_buttons: List[tk.Button], output_button: tk.Button) -> None:
        """
        Update lines on a canvas connecting UI elements.

        Parameters:
            canvas (tk.Canvas): The Tkinter canvas to update lines on.
            microphone_button (tk.Button): The microphone button.
            audio_buttons (List[tk.Button]): A list of audio buttons.
            output_button (tk.Button): The output button.

        Returns:
            None

        This function updates lines on the canvas to visually connect UI elements
        based on their states and positions.

        If the microphone is 'on' (green background), lines are drawn connecting
        the microphone button to the active audio buttons and from each active
        audio button to the output button.
        """
        canvas.delete("all")  # Clear existing lines
        if microphone_button.cget("background") == "#2ECC71":  # Check if microphone is 'on'
            for audio_button in audio_buttons:
                if audio_button.cget("background") == "#2ECC71":  # Check if any audio button is 'on'
                    UI.draw_line(canvas, microphone_button, audio_button)
                    UI.draw_line(canvas, audio_button, output_button)


    @staticmethod
    def show_select_audio_dialog() -> None:
        """
        Show a dialog box indicating the need to select an audio button.
        """
        messagebox.showinfo("Select Audio Button", "Please select an audio button before converting.")