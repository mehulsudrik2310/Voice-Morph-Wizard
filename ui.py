import tkinter as tk

button_off_color = "#3498DB"
button_on_color = "#2ECC71"

class UI:
    @staticmethod
    def toggle_button_color(button: tk.Button, canvas: tk.Canvas, microphone_button: tk.Button, filter_button: tk.Button, output_button: tk.Button) -> None:
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
        if button.data["is_on"] == False:
            button.configure(background=button_on_color)  # Change to green when selected
            button.data["is_on"] = True
            UI.update_lines(canvas, microphone_button, filter_button, output_button)  # Call to update lines when a button is toggled
        else:
            button.configure(background=button_off_color)
            UI.update_lines(canvas, microphone_button, filter_button, output_button)
            button.data["is_on"] = False

    @staticmethod
    def draw_line(canvas: tk.Canvas, start_button: tk.Button, end_button: tk.Button) -> None:
        """
        Draw a line connecting the center points of two Tkinter buttons on a canvas.

        Parameters:
            canvas (tk.Canvas): The Tkinter canvas on which the line will be drawn.
            start_button (tk.Button): The starting button from which the line originates.
            end_button (tk.Button): The ending button to which the line extends.

        Returns:
            None

        This method calculates the center points of the start and end buttons and
        draws a line connecting them on the specified canvas with a red color and a width of 2.

        Example usage:
            root = tk.Tk()
            canvas = tk.Canvas(root)
            start_button = tk.Button(root, text="Start")
            end_button = tk.Button(root, text="End")
            UI.draw_line(canvas, start_button, end_button)
            canvas.pack()
            root.mainloop()
        """
        # Calculate the x-coordinate of the center point of the starting button
        start_x = start_button.winfo_x() + start_button.winfo_width() / 2
        # Calculate the y-coordinate of the center point of the starting button
        start_y = start_button.winfo_y() + start_button.winfo_height() / 2
        # Calculate the x-coordinate of the center point of the ending button
        end_x = end_button.winfo_x() + end_button.winfo_width() / 2
        # Calculate the y-coordinate of the center point of the ending button
        end_y = end_button.winfo_y() + end_button.winfo_height() / 2
        # Draw a line on the canvas connecting the center points of the start and end buttons
        canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=2)  # Adjust color and width as needed

    @staticmethod
    def update_lines(canvas: tk.Canvas, microphone_button: tk.Button, filter_button: tk.Button, output_button: tk.Button) -> None:
        """
        Update lines on a canvas connecting UI elements.

        Parameters:
            canvas (tk.Canvas): The Tkinter canvas to update lines on.
            microphone_button (tk.Button): The microphone button.
            filter_button (tk.Button): The filter button.
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
        if microphone_button.cget("background") == "#2ECC71" and filter_button.cget("background") == "#2ECC71":  # Check if microphone is 'on' 
            UI.draw_line(canvas, microphone_button, filter_button)
            UI.draw_line(canvas, filter_button, output_button)
    
    @staticmethod
    def on_window_resize(event: tk.Event, canvas: tk.Canvas, microphone_button: tk.Button, filter_button: tk.Button, output_button: tk.Button) -> None:
        """
        Update lines on window resize.

        Parameters:
            event (tk.Event): The event object triggered by the window resize.
            canvas (tk.Canvas): The Tkinter canvas containing the lines to be updated.
            microphone_button (tk.Button): The Tkinter button representing the microphone.
            filter_button (tk.Button): The Tkinter button representing the filter.
            output_button (tk.Button): The Tkinter button representing the output.

        Returns:
            None

        This function is typically bound to the window resize event and triggers the
        update of lines on the canvas based on the new positions of the specified buttons.

        Example usage:
            root = tk.Tk()
            canvas = tk.Canvas(root)
            microphone_button = tk.Button(root, text="Microphone")
            filter_button = tk.Button(root, text="Filter")
            output_button = tk.Button(root, text="Output")
            root.bind("<Configure>", lambda event: on_window_resize(event, canvas, microphone_button, filter_button, output_button))
            canvas.pack()
            root.mainloop()
        """
        # Update lines on window resize
        UI.update_lines(canvas, microphone_button, filter_button, output_button)