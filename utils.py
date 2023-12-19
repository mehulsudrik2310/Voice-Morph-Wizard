import os
import tkinter as tk
from tkinter import messagebox
from ui import UI
from tkinter import filedialog
from pydub import AudioSegment

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
    def show_select_audio_dialog() -> None:
        """
        Show a dialog box indicating the need to select an audio button.
        """
        messagebox.showinfo("Select Audio Button", "Please select an audio button before converting.")

    @staticmethod
    def on_filter_option_change(event, filter_option_combobox, canvas, microphone_button, filter_button, output_button, current_filter):
        selected_option = filter_option_combobox.get()
        current_filter = selected_option
        filter_button.config(text=selected_option)
        if current_filter == "Normal":
            filter_button.data["is_on"] = True
            UI.toggle_button_color(filter_button, canvas, microphone_button, filter_button, output_button)
    

    @staticmethod
    def on_upload_effects() -> None:
        """
        Open a file dialog to upload an effects file.

        Returns:
            None

        This method opens a file dialog to allow the user to upload an effects file.
        If a file is selected, the file path is printed to the console.

        Example usage:
            YourClass.on_upload_effects()
        """
        # Open a file dialog to select an effects file
        effects_path = filedialog.askopenfilename(title="Upload Effects File", filetypes=[("Audio Files", "*.mp3;*.wav")])

        # Check if a file was selected
        if effects_path:
            # Print the path of the uploaded effects file to the console
            print(f"Effects file uploaded: {effects_path}")