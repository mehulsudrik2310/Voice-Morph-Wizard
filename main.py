import tkinter as tk
from tkinter import filedialog, ttk
import os
from pydub import AudioSegment
import simpleaudio as sa
import threading
import time

# Initialize global variables
selected_file_path = None
play_obj = None
audio_length = 0
is_playing = False
paused_position = 0  # Track the paused position
update_bar_thread_running = False  # New flag to control the thread

# Function to set the minimum size of the window to its current size
def set_min_size():
    window.update_idletasks()  # Update the window to ensure it's fully rendered
    set_minimum_width = window.winfo_width()
    set_minimum_height = window.winfo_height()
    window.minsize(set_minimum_width, set_minimum_height)

def play_audio():
    # Access global variables that will be modified in this function
    global selected_file_path, play_obj, is_playing, paused_position, update_bar_thread_running

    # Check if a file path has been selected
    if selected_file_path:
        # Signal to stop the current play bar update thread
        update_bar_thread_running = False

        # Stop any currently playing or paused audio and reset the play bar
        if play_obj:
            play_obj.stop()
            play_bar.set(0)  # Reset the play bar to the start
            paused_position = 0  # Reset the paused position

        # Wait briefly to ensure the thread stops before starting a new playback
        time.sleep(0.1)

        # Load the audio file and prepare it for playback from the beginning
        audio = AudioSegment.from_file(selected_file_path)
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)

        # Set flags to indicate audio is now playing and update the paused position
        is_playing = True
        paused_position = 0  # Start from the beginning

        # Start a new thread to update the play bar
        update_bar_thread_running = True
        threading.Thread(target=update_play_bar, daemon=True).start()

        # Update the state of toggle button to show "Pause" and enable it
        toggle_button.config(text="Pause", state=tk.NORMAL)

# def on_slider_move(event):
#     # Access global variables that will be modified in this function
#     global play_obj, is_playing, paused_position, update_bar_thread_running

#     if is_playing:
#         # Stop any currently playing audio
#         if play_obj:
#             play_obj.stop()

#         # Calculate the new playback position from the slider
#         paused_position = int(play_bar.get() * 1000)  # Convert to milliseconds

#         # Load the audio file and prepare it for playback from the new position
#         audio = AudioSegment.from_file(selected_file_path)
#         audio = audio[paused_position:]  # Start playing from this position
#         play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)

#         # Start a new thread to update the play bar, if not already running
#         if not update_bar_thread_running:
#             update_bar_thread_running = True
#             threading.Thread(target=update_play_bar, daemon=True).start()

# def on_slider_click(event):
#     # Access global variable
#     global paused_position

#     # Calculate the relative position (0.0 to 1.0) of the click on the slider track
#     relative_position = event.x / play_bar.winfo_width()

#     # Calculate the new value for the slider based on its range and the relative position
#     new_value = relative_position * audio_length
#     play_bar.set(new_value)

#     # Update paused_position to the new value in milliseconds
#     paused_position = int(new_value * 1000)

def toggle_pause_continue():
    # Access global variables that will be modified in this function
    global play_obj, is_playing, paused_position, update_bar_thread_running

    # Check if the audio is currently playing
    if is_playing:
        # Pause the audio
        play_obj.stop()
        # Set flags to indicate audio is now paused
        is_playing = False
        # Save the current position of the audio for resuming later
        paused_position = int(play_bar.get() * 1000)  # Convert to milliseconds
        # Update the toggle button to show "Continue"
        toggle_button.config(text="Continue")
    else:
        # Resume playing audio from the current slider position
        if selected_file_path:
            audio = AudioSegment.from_file(selected_file_path)
            # Start playing from the slider's position
            start_position = int(play_bar.get() * 1000)  # Convert slider position to milliseconds
            audio = audio[start_position:]  # Resume from this position
            play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
            is_playing = True
            paused_position = start_position  # Update paused_position
            threading.Thread(target=update_play_bar, daemon=True).start()
            # Update the toggle button to show "Pause"
            toggle_button.config(text="Pause")

def update_play_bar():
    # Access global variables used in this function
    global is_playing, play_obj, paused_position, update_bar_thread_running

    # Record the start time for calculating the current position
    start_time = time.time()

    # Continuously update the play bar while the audio is playing
    while is_playing and play_obj.is_playing() and update_bar_thread_running:
        # Calculate the current position in the audio file
        current_pos = (time.time() - start_time) + paused_position / 1000  # in seconds
        # Update the play bar with the current position
        play_bar.set(current_pos)
        # Break the loop if the end of the audio is reached
        if current_pos >= audio_length:
            break
        # Sleep briefly to avoid overloading the CPU
        time.sleep(0.1)

def on_microphone_click():
    print("Microphone button clicked")
    toggle_button_color(microphone_button)
    toggle_button_color(output_button)  # Also toggle the color of the output button

def on_audio_click(audio_number):
    print(f"Audio {audio_number} button clicked")

    # Access the global variable that tracks the currently selected audio button
    global selected_audio_button

    # Deselect the previously selected button if it's not the output button
    if selected_audio_button and selected_audio_button != output_button:
        toggle_button_color(selected_audio_button)

    # If the same button is clicked again, set selected_audio_button to None,
    # effectively deselecting it
    if selected_audio_button == audio_buttons[audio_number]:
        selected_audio_button = None
    else:
        # Select the newly clicked button and update its color
        selected_audio_button = audio_buttons[audio_number]
        toggle_button_color(selected_audio_button)

def on_output_click():
    print("Output button clicked")

def toggle_button_color(button):
    current_color = button.cget("background")
    original_color = button.data["original_color"]
    if current_color == original_color:
        button.configure(background="#2ECC71")  # Change to green when selected
    else:
        button.configure(background=original_color)

def on_upload_audio():
    # Access the global variables that will be modified in this function
    global selected_file_path, audio_length, paused_position, is_playing, play_obj

    # Open a file dialog for the user to select an audio file
    file_path = filedialog.askopenfilename(title="Upload Audio File", filetypes=[("Audio Files", "*.mp3;*.wav")])
    
    # Check if a file was selected (file_path is not empty)
    if file_path:
        # If there's an audio playing, stop it to load the new file
        if play_obj:
            play_obj.stop()

        # Reset playback variables to ensure clean state for new audio
        is_playing = False
        paused_position = 0
        play_bar.set(0)

        # Update the UI with the selected file's name and enable the Convert button
        print(f"Selected file: {file_path}")
        shortened_file_name = shorten_file_name(file_path, max_chars=15)
        selected_file_label.config(text=f"Selected File: {shortened_file_name}")
        convert_button.config(state=tk.NORMAL)  # Enable the Convert button

        # Update the global variable for the selected file path
        selected_file_path = file_path

        # Load the audio file to determine its length
        audio = AudioSegment.from_file(file_path)
        audio_length = len(audio) / 1000  # Length of audio in seconds

        # Configure the play bar's range to match the length of the audio
        play_bar.config(to=audio_length)

        # Reset the state of play and toggle buttons for the new audio
        play_button.config(state=tk.NORMAL)
        toggle_button.config(state=tk.DISABLED, text="Pause")


def on_upload_effects():
    effects_path = filedialog.askopenfilename(title="Upload Effects File", filetypes=[("Audio Files", "*.mp3;*.wav")])
    if effects_path:
        print(f"Effects file uploaded: {effects_path}")

def on_convert():
    selected_file_path = selected_file_label.cget("text").replace("Selected File: ", "")
    if selected_file_path:
        print(f"Converting {selected_file_path}...")
        # Add your conversion logic here

def on_closing():
    global update_bar_thread_running
    if play_obj:
        play_obj.stop()
    update_bar_thread_running = False
    print("Window closed")
    window.destroy()

def shorten_file_name(file_path, max_chars):
    file_name = os.path.basename(file_path)
    if len(file_name) <= max_chars:
        return file_name
    else:
        return file_name[:max_chars - 3] + "..."

# Create the main window
window = tk.Tk()
window.title("Voice Changer")

# Configure the grid rows and columns to expand proportionally
for i in range(6):  # Adjust the range based on your number of rows
    window.rowconfigure(i, weight=1)
for j in range(3):  # Adjust the range based on your number of columns
    window.columnconfigure(j, weight=1)

# Set the original button color
default_button_color = "#3498DB"
selected_button_color = "#2ECC71"

# Create and place the Microphone button
microphone_button = tk.Button(window, text="Microphone", command=on_microphone_click, background=default_button_color, font=("Helvetica", 10, "bold"))
microphone_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
microphone_button.data = {"original_color": default_button_color}

# Create and place the Audio buttons
audio_buttons = []
selected_audio_button = None
for i in range(3):
    audio_button = tk.Button(window, text=f"Audio {i}", command=lambda i=i: on_audio_click(i), background=default_button_color, font=("Helvetica", 10, "bold"))
    audio_button.grid(row=i, column=1, padx=10, pady=5, sticky='nsew')
    audio_button.data = {"original_color": default_button_color}
    audio_buttons.append(audio_button)

# Create and place the Output button
output_button = tk.Button(window, text="Output", command=on_output_click, background=default_button_color, font=("Helvetica", 10, "bold"))
output_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
output_button.data = {"original_color": default_button_color}

# Create a menu bar
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# Create a "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Upload Audio", command=on_upload_audio)
file_menu.add_command(label="Upload Effects", command=on_upload_effects)

# Create a label to display the selected file name
selected_file_label = tk.Label(window, text="Selected File: None", font=("Helvetica", 10))
selected_file_label.grid(row=3, column=0, columnspan=2, pady=5, sticky='nsew')

# Create a "Convert" button
convert_button = tk.Button(window, text="Convert", command=on_convert, state=tk.DISABLED, font=("Helvetica", 10, "bold"))
convert_button.grid(row=3, column=2, padx=10, pady=5, sticky='nsew')

# Create a play bar
play_bar = ttk.Scale(window, from_=0, to=100, orient='horizontal')
play_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
# Bind the left mouse click event to the slider
# play_bar.bind("<Button-1>", on_slider_click)
# Bind the slider movement event to the function
# play_bar.bind("<B1-Motion>", on_slider_move)

# Create play and toggle (pause/continue) buttons
play_button = tk.Button(window, text="Play", command=play_audio, state=tk.NORMAL)
play_button.grid(row=5, column=0, padx=10, pady=5, sticky='nsew')

toggle_button = tk.Button(window, text="Pause", command=toggle_pause_continue, state=tk.DISABLED)
toggle_button.grid(row=5, column=1, padx=10, pady=5, sticky='nsew')

# Bind the closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# After all widgets are added, call the function to set the minimum size
set_min_size()

# Start the Tkinter event loop
window.mainloop()
