import math
import tkinter as tk
from tkinter import filedialog, ttk
import os
import wave
import pyaudio
from pydub import AudioSegment
import simpleaudio as sa
import threading
import time
import numpy as np
from tkinter import messagebox

# Initialize global variables
selected_file_path = None
play_obj = None
audio_length = 0
is_playing = False
paused_position = 0  # Track the paused position
update_bar_thread_running = False  # New flag to control the thread
num_audio_buttons = 3 # Number of audio buttons\# Calculate the middle row position
middle_row = num_audio_buttons // 2
f0 = 800
RATE = 16000         # frames per second
ca_om = 2 * math.pi * f0 / RATE
theta = 0
BLOCKLEN = 1024
modulated_audio_data = None
modulated_is_playing = False
modulated_paused_position = 0
modulated_update_bar_thread_running = False
modulated_play_obj = None
modulated_audio_length = 0
CHANNELS = 0
RATE = 0
WIDTH = 0
LENGTH = 0

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
            raw_play_bar.set(0)  # Reset the play bar to the start
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
        raw_pause_continue_button.config(text="Pause", state=tk.NORMAL)

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

def on_window_resize(event):
    # Update lines on window resize
    update_lines()

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
        paused_position = int(raw_play_bar.get() * 1000)  # Convert to milliseconds
        # Update the toggle button to show "Continue"
        raw_pause_continue_button.config(text="Continue")
    else:
        # Resume playing audio from the current slider position
        if selected_file_path:
            audio = AudioSegment.from_file(selected_file_path)
            # Start playing from the slider's position
            start_position = int(raw_play_bar.get() * 1000)  # Convert slider position to milliseconds
            audio = audio[start_position:]  # Resume from this position
            play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
            is_playing = True
            paused_position = start_position  # Update paused_position
            threading.Thread(target=update_play_bar, daemon=True).start()
            # Update the toggle button to show "Pause"
            raw_pause_continue_button.config(text="Pause")

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
        raw_play_bar.set(current_pos)
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
        update_lines()  # Call to update lines when a button is toggled
    else:
        button.configure(background=original_color)
        update_lines()

def draw_line(start_button, end_button):
    start_x = start_button.winfo_x() + start_button.winfo_width() / 2
    start_y = start_button.winfo_y() + start_button.winfo_height() / 2
    end_x = end_button.winfo_x() + end_button.winfo_width() / 2
    end_y = end_button.winfo_y() + end_button.winfo_height() / 2
    canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=2)  # Adjust color and width as needed

def update_lines():
    canvas.delete("all")  # Clear existing lines
    if microphone_button.cget("background") == "#2ECC71":  # Check if microphone is 'on'
        for audio_button in audio_buttons:
            if audio_button.cget("background") == "#2ECC71":  # Check if any audio button is 'on'
                draw_line(microphone_button, audio_button)
                draw_line(audio_button, output_button)


def on_upload_audio():
    global selected_file_path, audio_length, paused_position, is_playing, play_obj
    global modulated_audio_data, modulated_play_obj, modulated_is_playing, modulated_paused_position, modulated_play_bar

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
        raw_play_bar.set(0)

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
        raw_play_bar.config(to=audio_length)

        # Reset the state of play and toggle buttons for the new audio
        raw_play_button.config(state=tk.NORMAL)
        raw_pause_continue_button.config(state=tk.DISABLED, text="Pause")

        # Make the play bar and the play pause button visible
        raw_play_bar.grid()  
        raw_play_button.grid()
        raw_pause_continue_button.grid()

        # Hide and reset all modulated elements
        modulated_play_bar.set(0)
        modulated_play_bar.grid_remove()
        modulated_play_button.grid_remove()
        modulated_pause_continue_button.grid_remove()
        download_modulated_button.grid_remove()

        # Reset modulated audio related variables
        modulated_audio_data = None
        modulated_play_obj = None
        modulated_is_playing = False
        modulated_paused_position = 0


def on_upload_effects():
    effects_path = filedialog.askopenfilename(title="Upload Effects File", filetypes=[("Audio Files", "*.mp3;*.wav")])
    if effects_path:
        print(f"Effects file uploaded: {effects_path}")

def on_convert():
    global selected_file_path, modulated_audio_data, modulated_audio_length, modulated_play_button, modulated_pause_continue_button, modulated_play_bar, modulated_is_playing, modulated_paused_position, modulated_update_bar_thread_running, modulated_play_obj, CHANNELS, RATE, WIDTH, LENGTH

    if selected_file_path:
        print(f"Converting {selected_file_path}...")
        wf = wave.open(selected_file_path, 'rb')
        CHANNELS = wf.getnchannels()     # Number of channels
        RATE = wf.getframerate()     # Sampling rate (frames/second)
        WIDTH = wf.getsampwidth()     # Number of bytes per sample
        LENGTH = wf.getnframes()

        # Read the entire file
        input_bytes = wf.readframes(LENGTH)
        wf.close()  # Close the file after reading

        # Convert the bytes to numpy array
        input_array = np.frombuffer(input_bytes, dtype='int16')

        # Apply modulation based on selected audio button
        if selected_audio_button == audio_buttons[0]:
            modulated_array = my_modulation(input_array)
        elif selected_audio_button == audio_buttons[1]:
            modulated_array = my_modulation1(input_array)
        elif selected_audio_button == audio_buttons[2]:
            modulated_array = my_modulation2(input_array)
        else:
            show_select_audio_dialog()
            return

        # Convert the modulated array back to bytes
        modulated_audio_data = modulated_array.astype('int16').tobytes()

        # Play the modulated audio
        # modulated_play_obj = sa.play_buffer(modulated_audio_data, num_channels=CHANNELS, bytes_per_sample=WIDTH, sample_rate=RATE)

        # Set the length of the modulated audio (in seconds)
        modulated_audio_length = LENGTH / RATE

        # Now that the modulation is done, make the modulated audio controls visible
        modulated_play_bar.config(to=modulated_audio_length)
        modulated_play_bar.grid()
        modulated_play_button.config(state=tk.NORMAL)
        modulated_play_button.grid()
        modulated_pause_continue_button.config(state=tk.DISABLED)
        modulated_pause_continue_button.grid()
        download_modulated_button.grid()

        # modulated_is_playing = True
        # modulated_paused_position = 0
        # modulated_update_bar_thread_running = True
        # threading.Thread(target=update_modulated_play_bar, daemon=True).start()

def play_modulated_audio():
    global modulated_audio_data, modulated_play_obj, modulated_is_playing, modulated_paused_position, modulated_update_bar_thread_running, CHANNELS, WIDTH, RATE

    # Stop any existing playback and updating thread
    if modulated_play_obj:
        modulated_play_obj.stop()

    if modulated_update_bar_thread_running:
        modulated_update_bar_thread_running = False
        time.sleep(0.1)  # Allow time for the thread to stop

    # Reset the modulated play bar and paused position
    modulated_play_bar.set(0)
    modulated_paused_position = 0

    # Ensure the modulated audio data is not None
    if modulated_audio_data is None:
        print("No modulated audio data to play.")
        return

    # Start playing the modulated audio from the beginning
    modulated_audio_segment = AudioSegment(
        data=modulated_audio_data,
        sample_width=WIDTH,
        frame_rate=RATE,
        channels=CHANNELS
    )
    modulated_play_obj = sa.play_buffer(modulated_audio_segment.raw_data, num_channels=CHANNELS, bytes_per_sample=WIDTH, sample_rate=RATE)
    modulated_is_playing = True
    modulated_update_bar_thread_running = True
    threading.Thread(target=update_modulated_play_bar, daemon=True).start()

    # Update the toggle button to show "Pause" and enable it
    modulated_pause_continue_button.config(text="Pause", state=tk.NORMAL)

def update_modulated_play_bar():
    global modulated_is_playing, modulated_play_obj, modulated_audio_length, modulated_paused_position, modulated_update_bar_thread_running

    start_time = time.time()

    while modulated_update_bar_thread_running:
        if modulated_is_playing and modulated_play_obj.is_playing():
            # Calculate the current position in the audio file
            current_pos = (time.time() - start_time) + modulated_paused_position / 1000  # in seconds
            modulated_play_bar.set(current_pos)
            if current_pos >= modulated_audio_length:
                break
        time.sleep(0.1)

def toggle_modulated_pause_continue():
    global modulated_play_obj, modulated_is_playing, modulated_paused_position, modulated_update_bar_thread_running, modulated_audio_data, CHANNELS, WIDTH, RATE

    # Check if the audio is currently playing
    if modulated_is_playing:
        # Pause the audio
        modulated_play_obj.stop()
        # Set flags to indicate audio is now paused
        modulated_is_playing = False
        # Save the current position of the audio for resuming later
        modulated_paused_position = int(modulated_play_bar.get() * 1000)  # Convert to milliseconds
        # Update the toggle button to show "Continue"
        modulated_pause_continue_button.config(text="Continue")
        # Stop updating the play bar
        modulated_update_bar_thread_running = False
    else:
        # Resume playing modulated audio from the current slider position
        start_position = int(modulated_play_bar.get() * 1000)  # Convert slider position to milliseconds
        modulated_audio_segment = AudioSegment(
            data=modulated_audio_data,
            sample_width=WIDTH,
            frame_rate=RATE,
            channels=CHANNELS
        )[start_position:]
        modulated_play_obj = sa.play_buffer(modulated_audio_segment.raw_data, num_channels=CHANNELS, bytes_per_sample=WIDTH, sample_rate=RATE)
        modulated_is_playing = True
        modulated_paused_position = start_position
        modulated_update_bar_thread_running = True
        threading.Thread(target=update_modulated_play_bar, daemon=True).start()
        # Update the toggle button to show "Pause"
        modulated_pause_continue_button.config(text="Pause")

def download_modulated_audio():
    global modulated_audio_data, selected_file_path, CHANNELS, WIDTH, RATE

    if modulated_audio_data is None:
        print("No modulated audio to save.")
        return

    # Extracting original filename without extension
    original_filename = os.path.splitext(os.path.basename(selected_file_path))[0]
    default_filename = f"modulated_{original_filename}.wav"

    # Open a save file dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        initialfile=default_filename
    )

    if not file_path:  # If the user cancels the save operation
        return

    # Write the modulated audio data to the file
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(WIDTH)
        wf.setframerate(RATE)
        wf.writeframes(modulated_audio_data)


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
    
def my_modulation(input):
    global theta
    print("In modulation")
    y = np.zeros(len(input))
    for n in range(0, len(input)):
        theta = theta + ca_om
        y[n] = int( input[n] * math.cos(theta) )
        # output_block[n] = input_block[n]  # for no processing
    # keep theta betwen -pi and pi
    while theta > math.pi:
        theta = theta - 2*math.pi
    return y

def my_modulation1(input):
    global theta
    print("In modulation 1")
    y = np.zeros(len(input))
    for n in range(0, len(input)):
        theta = theta + ca_om
        y[n] = int( input[n] * math.cos(theta) )
        # output_block[n] = input_block[n]  # for no processing
    # keep theta betwen -pi and pi
    while theta > math.pi:
        theta = theta - 2*math.pi*math.pi
    return y

def my_modulation2(input):
    global theta
    print("In modulation 2")
    y = np.zeros(len(input))
    for n in range(0, len(input)):
        theta = theta + ca_om
        y[n] = int( input[n] * math.cos(theta) )
        # output_block[n] = input_block[n]  # for no processing
    # keep theta betwen -pi and pi
    while theta > math.pi:
        theta = theta - 2*math.pi*math.pi*math.pi*math.pi
    return y

def show_select_audio_dialog():
    tk.messagebox.showinfo("Select Audio Button", "Please select an audio button before converting.")



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

# Create the canvas and place it below the buttons
canvas = tk.Canvas(window, height=200, width=300)  # Adjust size as needed
canvas.grid(row=0, column=0, rowspan=6, columnspan=3, sticky='nsew')

# Create and place the Microphone button in the middle of the audio button stack
microphone_button = tk.Button(window, text="Microphone", command=on_microphone_click, background=default_button_color, font=("Helvetica", 10, "bold"), width=13, height=1)
microphone_button.grid(row=middle_row, column=0, padx=10, pady=10, sticky='nsew')
microphone_button.data = {"original_color": default_button_color}

# Create and place the Audio buttons
audio_buttons = []
selected_audio_button = None
for i in range(num_audio_buttons):
    audio_button = tk.Button(window, text=f"Audio {i}", command=lambda i=i: on_audio_click(i), background=default_button_color, font=("Helvetica", 10, "bold"))
    audio_button.grid(row=i, column=1, padx=35, pady=15, sticky='nsew')
    audio_button.data = {"original_color": default_button_color}
    audio_buttons.append(audio_button)

# Create and place the Output button in the middle of the audio button stack
output_button = tk.Button(window, text="Output", command=on_output_click, background=default_button_color, font=("Helvetica", 10, "bold"), width=10, height=1)
output_button.grid(row=middle_row, column=2, padx=10, pady=10, sticky='nsew')
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
raw_play_bar = ttk.Scale(window, from_=0, to=100, orient='horizontal')
raw_play_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
raw_play_bar.grid_remove()  # Hide the play bar initially
# Bind the left mouse click event to the slider
# play_bar.bind("<Button-1>", on_slider_click)
# Bind the slider movement event to the function
# play_bar.bind("<B1-Motion>", on_slider_move)

# Create play and toggle (pause/continue) buttons
raw_play_button = tk.Button(window, text="Play", command=play_audio, state=tk.NORMAL)
raw_play_button.grid(row=5, column=0, padx=10, pady=5, sticky='nsew')
raw_play_button.grid_remove()  # Hide the play bar initially

raw_pause_continue_button = tk.Button(window, text="Pause", command=toggle_pause_continue, state=tk.DISABLED)
raw_pause_continue_button.grid(row=5, column=1, padx=10, pady=5, sticky='nsew')
raw_pause_continue_button.grid_remove()  # Hide the play bar initially

# Create modulated play bar
modulated_play_bar = ttk.Scale(window, from_=0, to=100, orient='horizontal')
modulated_play_bar.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
modulated_play_bar.grid_remove()  # Hide the modulated play bar initially

# Create modulated play and toggle (pause/continue) buttons
modulated_play_button = tk.Button(window, text="Play Modulated", command=play_modulated_audio, state=tk.DISABLED)
modulated_play_button.grid(row=7, column=0, padx=10, pady=5, sticky='nsew')
modulated_play_button.grid_remove()  # Hide the modulated play button initially

modulated_pause_continue_button = tk.Button(window, text="Pause", command=toggle_modulated_pause_continue, state=tk.DISABLED)
modulated_pause_continue_button.grid(row=7, column=1, padx=10, pady=5, sticky='nsew')
modulated_pause_continue_button.grid_remove()  # Hide the modulated pause/continue button initially

# Create a download button for modulated audio
download_modulated_button = tk.Button(window, text="Download", command=download_modulated_audio, state=tk.NORMAL)
download_modulated_button.grid(row=7, column=2, padx=10, pady=5, sticky='nsew')
download_modulated_button.grid_remove() # Hide the modulated button initially

# Bind the closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Bind the window resize event
window.bind("<Configure>", on_window_resize)

# Disable resizing of the window
window.resizable(True, True)

# After all widgets are added, call the function to set the minimum size
set_min_size()

# Start the Tkinter event loop
window.mainloop()
