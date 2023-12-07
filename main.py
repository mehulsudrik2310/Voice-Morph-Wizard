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

def play_audio():
    global selected_file_path, play_obj, is_playing, paused_position, update_bar_thread_running
    if selected_file_path:
        # Signal to stop the current play bar update thread
        update_bar_thread_running = False

        if play_obj:
            play_obj.stop()

        # Wait briefly to ensure the thread stops
        time.sleep(0.1)

        play_bar.set(0)
        audio = AudioSegment.from_file(selected_file_path)
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        is_playing = True
        paused_position = 0

        # Start a new thread to update the play bar
        update_bar_thread_running = True
        threading.Thread(target=update_play_bar, daemon=True).start()
        # Update button states
        toggle_button.config(text="Pause", state=tk.NORMAL)

def toggle_pause_continue():
    global play_obj, is_playing, paused_position, update_bar_thread_running
    if is_playing:
        # Pause the audio
        play_obj.stop()
        is_playing = False
        paused_position = int(play_bar.get() * 1000)  # Convert to milliseconds
        toggle_button.config(text="Continue")
    else:
        # Continue playing from paused position
        if selected_file_path:
            audio = AudioSegment.from_file(selected_file_path)
            audio = audio[paused_position:]
            play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
            is_playing = True
            threading.Thread(target=update_play_bar, daemon=True).start()
            toggle_button.config(text="Pause")

def update_play_bar():
    global is_playing, play_obj, paused_position, update_bar_thread_running
    start_time = time.time()
    while is_playing and play_obj.is_playing() and update_bar_thread_running:
        current_pos = (time.time() - start_time) + paused_position / 1000  # in seconds
        play_bar.set(current_pos)
        if current_pos >= audio_length:
            break
        time.sleep(0.1)

def on_microphone_click():
    print("Microphone button clicked")
    toggle_button_color(microphone_button)

def on_audio_click(audio_number):
    print(f"Audio {audio_number} button clicked")
    global selected_audio_button
    if selected_audio_button and selected_audio_button != output_button:
        toggle_button_color(selected_audio_button)
    if selected_audio_button == audio_buttons[audio_number]:
        selected_audio_button = None
    else:
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
    global selected_file_path, audio_length, paused_position, is_playing, play_obj
    file_path = filedialog.askopenfilename(title="Upload Audio File", filetypes=[("Audio Files", "*.mp3;*.wav")])
    if file_path:
        # Stop currently playing audio, if any
        if play_obj:
            play_obj.stop()

        # Reset playback variables
        is_playing = False
        paused_position = 0
        play_bar.set(0)

        # Update UI elements
        print(f"Selected file: {file_path}")
        shortened_file_name = shorten_file_name(file_path, max_chars=15)
        selected_file_label.config(text=f"Selected File: {shortened_file_name}")
        convert_button.config(state=tk.NORMAL)  # Enable the Convert button
        selected_file_path = file_path

        # Load the audio file and set the play bar's range
        audio = AudioSegment.from_file(file_path)
        audio_length = len(audio) / 1000  # Length of audio in seconds
        play_bar.config(to=audio_length)

        # Update button states
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

# Set the original button color
default_button_color = "#3498DB"
selected_button_color = "#2ECC71"

# Create and place the Microphone button
microphone_button = tk.Button(window, text="Microphone", command=on_microphone_click, background=default_button_color, font=("Helvetica", 10, "bold"))
microphone_button.grid(row=0, column=0, padx=10, pady=10)
microphone_button.data = {"original_color": default_button_color}

# Create and place the Audio buttons
audio_buttons = []
selected_audio_button = None
for i in range(3):
    audio_button = tk.Button(window, text=f"Audio {i}", command=lambda i=i: on_audio_click(i), background=default_button_color, font=("Helvetica", 10, "bold"))
    audio_button.grid(row=i, column=1, padx=10, pady=5)
    audio_button.data = {"original_color": default_button_color}
    audio_buttons.append(audio_button)

# Create and place the Output button
output_button = tk.Button(window, text="Output", command=on_output_click, background=default_button_color, font=("Helvetica", 10, "bold"))
output_button.grid(row=0, column=2, padx=10, pady=10)
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
selected_file_label.grid(row=3, column=0, columnspan=2, pady=5)

# Create a "Convert" button
convert_button = tk.Button(window, text="Convert", command=on_convert, state=tk.DISABLED, font=("Helvetica", 10, "bold"))
convert_button.grid(row=3, column=2, padx=10, pady=5)

# Create a play bar
play_bar = ttk.Scale(window, from_=0, to=100, orient='horizontal')
play_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='ew')

# Create play and toggle (pause/continue) buttons
play_button = tk.Button(window, text="Play", command=play_audio, state=tk.NORMAL)
play_button.grid(row=5, column=0, padx=10, pady=5)

toggle_button = tk.Button(window, text="Pause", command=toggle_pause_continue, state=tk.DISABLED)
toggle_button.grid(row=5, column=1, padx=10, pady=5)

# Bind the closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter event loop
window.mainloop()
