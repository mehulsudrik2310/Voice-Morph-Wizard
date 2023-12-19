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
from utils import Utils
from ui import UI
from filters import Filters

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global Variables for Audio Playback
selected_file_path = None        # Path to the currently selected audio file
play_obj = None                  # Represents the currently playing audio object
audio_length = 0                 # Length of the audio in seconds
is_playing = False                # Indicates whether the audio is currently playing
paused_position = 0              # The position where playback was paused (in milliseconds)
update_bar_thread_running = False # Flag to control the thread updating the play bar
last_played_button = None        # Represents the last played audio button for audio_clips

# Global Variables for Microphone and Real-time Audio Processing
MIC_RATE = 16000            # Microphone sampling rate in frames per second
MIC_CHANNELS = 2            # Number of channels for the microphone
BLOCKLEN = 2048             # Number of frames per block for real-time audio processing

# Global Variables for Modulated Audio Playback
modulated_audio_data = None                  # Modulated audio data
modulated_is_playing = False                 # Indicates whether the modulated audio is currently playing
modulated_paused_position = 0                # The position where modulated playback was paused (in milliseconds)
modulated_update_bar_thread_running = False  # Flag to control the thread updating the modulated play bar
modulated_play_obj = None                    # Represents the currently playing modulated audio object
modulated_audio_length = 0                   # Length of the modulated audio in seconds

# Global Variables for Audio Properties
CHANNELS = 0    # Number of audio channels
RATE = 0        # Audio sampling rate (frames per second)
WIDTH = 0       # Number of bytes per sample
LENGTH = 0      # Number of frames in the audio file

# Global Variables for Audio Playback Control
current_play_obj = None         # Represents the currently playing audio object
audio_thread = None             # Thread for audio playback
current_active_button = None    # Currently active button for audio playback control
is_audio_playing = False         # Indicates whether any audio is currently playing
current_filter = ""              # Currently selected audio filter
filter_options = ["Normal", "Alien Voice", "Robotic Voice", "Male Voice", "Female Voice", "Baby Voice", "Echoed Voice", "Ping Pong Voice", "Alternate Channel Effect", "Mutation Effect", "Flanger Effect"]

# Global Variables for UI Styling
button_off_color = "#3498DB"    # Color when buttons are off or not pressed
button_on_color = "#2ECC71"     # Color when buttons are on or pressed

# Global Variables for Real-time Audio Streaming
stream = None                   # Represents the audio stream from the microphone
mic_active = False               # Indicates whether the microphone is active


def play_raw_audio() -> None:
    """
    Play the raw audio from the selected file.

    Global Variables:
        selected_file_path (str): Path to the selected audio file.
        play_obj (pydub.AudioSegment): Represents the currently playing audio object.
        is_playing (bool): Indicates whether the audio is currently playing.
        paused_position (int): The position where playback was paused (in milliseconds).
        update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        raw_play_bar (tk.Scale): Represents the play bar widget.
        AudioSegment (class): Represents an audio segment from the pydub library.
        sa (pydub.AudioSegment): Represents the play buffer function from pydub.
        threading.Thread (class): Represents a thread for parallel execution.
        update_play_bar() (function): Function to update the play bar.

    Returns:
        None

    This function plays the raw audio from the selected file and updates the play bar.

    Example usage:
        play_raw_audio()
    """
    # Access global variables that will be modified in this function
    global selected_file_path, play_obj, is_playing, paused_position, update_bar_thread_running, raw_play_bar, AudioSegment, sa, threading, update_play_bar

    # Check if a file path has been selected
    if selected_file_path:
        # Signal to stop the current play bar update thread
        update_bar_thread_running = False

        # Stop any currently playing or paused audio and reset the play bar
        if play_obj:
            play_obj.stop()
            raw_play_bar.set(0)  # Reset the play bar to the start
            paused_position = 0  # Reset the paused position

        # Wait briefly to ensure the thread stops before starting new playback
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

        # Update the state of the toggle button to show "Pause" and enable it
        raw_pause_continue_button.config(text="Pause", state=tk.NORMAL)

def toggle_pause_continue() -> None:
    """
    Toggle between pausing and continuing playback of the audio.

    Global Variables:
        play_obj (pydub.AudioSegment): Represents the currently playing audio object.
        is_playing (bool): Indicates whether the audio is currently playing.
        paused_position (int): The position where playback was paused (in milliseconds).
        update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        raw_play_bar (tk.Scale): Represents the play bar widget.
        selected_file_path (str): Path to the selected audio file.
        AudioSegment (class): Represents an audio segment from the pydub library.
        sa (pydub.AudioSegment): Represents the play buffer function from pydub.
        threading.Thread (class): Represents a thread for parallel execution.

    Returns:
        None

    This function toggles between pausing and continuing playback of the audio.

    Example usage:
        toggle_pause_continue()
    """
    # Access global variables that will be modified in this function
    global play_obj, is_playing, paused_position, update_bar_thread_running, raw_play_bar, selected_file_path, AudioSegment, sa, threading

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
            # Load the selected audio file
            audio = AudioSegment.from_file(selected_file_path)
            # Start playing from the slider's position
            start_position = int(raw_play_bar.get() * 1000)  # Convert slider position to milliseconds
            audio = audio[start_position:]  # Resume from this position
            # Play the audio buffer
            play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
            is_playing = True
            paused_position = start_position  # Update paused_position
            threading.Thread(target=update_play_bar, daemon=True).start()
            # Update the toggle button to show "Pause"
            raw_pause_continue_button.config(text="Pause")

def update_play_bar() -> None:
    """
    Continuously update the play bar while the audio is playing.

    Global Variables:
        is_playing (bool): Indicates whether the audio is currently playing.
        play_obj (pydub.AudioSegment): Represents the currently playing audio object.
        paused_position (int): The position where playback was paused (in milliseconds).
        update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        raw_play_bar (tk.Scale): Represents the play bar widget.
        audio_length (float): Length of the audio in seconds.

    Returns:
        None

    This function continuously updates the play bar based on the current playback position.

    Example usage:
        update_play_bar()
    """
    # Access global variables used in this function
    global is_playing, play_obj, paused_position, update_bar_thread_running, raw_play_bar, audio_length

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

def on_microphone_click() -> None:
    """
    Handle the event when the microphone button is clicked.

    Global Variables:
        mic_active (bool): Indicates whether the microphone is active.
        stream (pyaudio.Stream): Represents the audio stream for real-time input and output.
        start_stream() (function): Function to start the audio stream.
        stop_stream() (function): Function to stop the audio stream.
        process_realtime_audio() (function): Function to process real-time audio.

    Returns:
        None

    This function toggles the microphone state, starts or stops the audio stream accordingly,
    and triggers real-time audio processing in a separate thread.

    Example usage:
        on_microphone_click()
    """
    # Use global variables and functions
    global mic_active, stream, start_stream, stop_stream, process_realtime_audio

    # Check if the microphone is not active
    if not mic_active:
        # Start the audio stream
        start_stream()
        # Set the microphone state to active
        mic_active = True
        # Start a separate thread for real-time audio processing
        threading.Thread(target=process_realtime_audio, daemon=True).start()
        # Toggle button colors for the microphone and output buttons
        UI.toggle_button_color(microphone_button, canvas, microphone_button, filter_button, output_button)
        UI.toggle_button_color(output_button, canvas, microphone_button, filter_button, output_button)

    else:
        # Stop the audio stream
        stop_stream()
        # Set the microphone state to inactive
        mic_active = False
        # Toggle button colors for the microphone and output buttons
        UI.toggle_button_color(microphone_button, canvas, microphone_button, filter_button, output_button)
        UI.toggle_button_color(output_button, canvas, microphone_button, filter_button, output_button)

def stop_stream() -> None:
    """
    Stop the audio stream for real-time input and output.

    Global Variables:
        stream (pyaudio.Stream): Represents the audio stream for real-time input and output.

    Returns:
        None

    This function stops the audio stream for real-time input and output.

    Example usage:
        stop_stream()
    """
    # Use global variable
    global stream

    # Check if the stream is not None
    if stream is not None:
        # Stop the audio stream
        stream.stop_stream()
        # Note: Uncomment the following lines if you also want to close the stream
        # stream.close()
        # stream = None
        
def process_realtime_audio() -> None:
    """
    Process real-time audio from the microphone and apply modulation effects.

    Global Variables:
        mic_active (bool): Indicates whether the microphone is active.
        current_filter (str): Current audio filter selected.
        stream (pyaudio.Stream): Represents the audio stream for real-time input and output.
        BLOCKLEN (int): Number of frames per buffer.

    Returns:
        None

    This function continuously reads audio from the microphone, applies modulation effects based
    on the selected filter, and writes the processed audio to the output stream.

    Example usage:
        process_realtime_audio()
    """
    # Use global variables
    global mic_active, current_filter, stream, BLOCKLEN

    # Continue processing audio while the microphone is active
    while mic_active:
        # Read audio from the microphone
        input_audio = stream.read(BLOCKLEN)
        input_array = np.frombuffer(input_audio, dtype=np.int16)
        output_array = np.empty(1)

        # Check if the filter is turned on
        if filter_button.data["is_on"] == True:
            # Apply modulation based on the selected filter
            if current_filter == "Alien Voice":
                output_array = Filters.alien_effect(input_array)
            elif current_filter == "Robotic Voice":
                output_array = Filters.robotize_effect(input_array)
            elif current_filter == "Male Voice":
                output_array = Filters.male_effect(input_array)
            elif current_filter == "Female Voice":
                output_array = Filters.female_effect(input_array)
            elif current_filter == "Baby Voice":
                output_array = Filters.baby_effect(input_array)
            elif current_filter == "Echoed Voice":
                output_array = Filters.echo_effect(input_array)
            elif current_filter == "Ping Pong Voice":
                output_array = Filters.ping_pong_effect(input_array)
            elif current_filter == "Alternate Channel Effect":
                output_array = Filters.alternate_channels(input_array)
            elif current_filter == "Mutation Effect":
                output_array = Filters.mutation_effect(input_array)
            elif current_filter == "Flanger Effect":
                output_array = Filters.flanger_effect(input_array)
            else:
                output_array = input_array  # No modulation if no button is selected
        else:
            output_array = input_array  # No modulation if no button is selected

        # Write the processed audio to the output stream
        stream.write(output_array.astype(np.int16).tobytes())

def on_filter_click() -> None:
    """
    Handle the event when the filter button is clicked.

    Global Variables:
        filter_button (tk.Button): Represents the filter button.
        canvas (tk.Canvas): Represents the canvas for drawing lines.
        microphone_button (tk.Button): Represents the microphone button.
        output_button (tk.Button): Represents the output button.

    Returns:
        None

    This function prints a message when the filter button is clicked and toggles the button color.

    Example usage:
        on_filter_click()
    """
    # Access the global variable that tracks the currently selected audio button
    UI.toggle_button_color(filter_button, canvas, microphone_button, filter_button, output_button)

def start_stream() -> None:
    """
    Start the audio stream for real-time input and output.

    Global Variables:
        stream (pyaudio.Stream): Represents the audio stream for real-time input and output.
        MIC_RATE (int): Sample rate for the microphone input.
        MIC_CHANNELS (int): Number of channels for the microphone input.
        BLOCKLEN (int): Number of frames per buffer.

    Returns:
        None

    This function initializes and starts the audio stream for real-time input and output using PyAudio.

    Example usage:
        start_stream()
    """
    # Use global variables
    global stream, MIC_RATE, MIC_CHANNELS, BLOCKLEN

    # Open the audio stream for real-time input and output
    stream = p.open(
        format=pyaudio.paInt16,     # Set the audio format to 16-bit PCM
        channels=MIC_CHANNELS,      # Set the number of channels for the microphone input
        rate=MIC_RATE,              # Set the sample rate for the microphone input
        input=True,                 # Enable input (microphone)
        output=True,                # Enable output (speakers)
        frames_per_buffer=BLOCKLEN  # Set the number of frames per buffer
    )

def on_output_click():
    pass

def on_upload_audio() -> None:
    """
    Handle the event of uploading an audio file.

    Global Variables:
        selected_file_path (str): Represents the path of the selected audio file.
        audio_length (float): Length of the original audio in seconds.
        paused_position (float): Stores the position where audio playback was paused.
        is_playing (bool): Indicates whether audio is currently playing.
        play_obj (SimpleAudioObject): Represents the audio playback object for the original audio.
        modulated_audio_data (bytes): Represents the modulated audio data.
        modulated_play_obj (SimpleAudioObject): Represents the modulated audio playback object.
        modulated_is_playing (bool): Indicates whether modulated audio is currently playing.
        modulated_paused_position (int): Stores the position where modulated audio was paused.
        modulated_play_bar (tk.Scale): Progress bar for modulated audio playback.

    Returns:
        None

    This function handles the event of uploading an audio file. It updates the UI with the selected
    file's name, enables the Convert button, and sets up the state for the original audio playback.

    Example usage:
        on_upload_audio()
    """
    # Use global variables
    global selected_file_path, audio_length, paused_position, is_playing, play_obj
    global modulated_audio_data, modulated_play_obj, modulated_is_playing, modulated_paused_position, modulated_play_bar

    # Open a file dialog for the user to select an audio file
    file_path = filedialog.askopenfilename(title="Upload Audio File", filetypes=[("Audio Files", "*.mp3;*.wav")])

    # Check if a file was selected (file_path is not empty)
    if file_path:
        # If there's audio playing, stop it to load the new file
        if play_obj:
            play_obj.stop()

        # Reset playback variables to ensure a clean state for new audio
        is_playing = False
        paused_position = 0
        raw_play_bar.set(0)

        # Update the UI with the selected file's name and enable the Convert button
        shortened_file_name = Utils.shorten_file_name(file_path, max_chars=15)
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

        # Reset modulated audio-related variables
        modulated_audio_data = None
        modulated_play_obj = None
        modulated_is_playing = False
        modulated_paused_position = 0

def on_convert() -> None:
    """
    Convert the selected audio file and apply modulation effects.

    Global Variables:
        selected_file_path (str): Represents the path of the selected audio file.
        modulated_audio_data (bytes): Represents the modulated audio data.
        modulated_audio_length (float): Length of the modulated audio in seconds.
        modulated_play_button (tk.Button): Button for playing modulated audio.
        modulated_pause_continue_button (tk.Button): Button for pausing/continuing modulated audio playback.
        modulated_play_bar (tk.Scale): Progress bar for modulated audio playback.
        modulated_is_playing (bool): Indicates whether modulated audio is currently playing.
        modulated_paused_position (int): Stores the position where modulated audio was paused.
        modulated_update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        modulated_play_obj (SimpleAudioObject): Represents the modulated audio playback object.
        current_filter (str): Current audio filter selected.
        CHANNELS (int): Number of audio channels.
        RATE (int): Sample rate in Hertz.
        WIDTH (int): Sample width (in bytes) for audio data.
        LENGTH (int): Number of frames in the audio.

    Returns:
        None

    This function converts the selected audio file, applies modulation effects based on the
    selected filter, and sets up the modulated audio controls for playback.

    Example usage:
        on_convert()
    """
    # Use global variables
    global selected_file_path, modulated_audio_data, modulated_audio_length, modulated_play_button, modulated_pause_continue_button, modulated_play_bar, modulated_is_playing, modulated_paused_position, modulated_update_bar_thread_running, modulated_play_obj, current_filter, CHANNELS, RATE, WIDTH, LENGTH

    # Check if a file is selected
    if selected_file_path:
        # Open the selected audio file for reading
        wf = wave.open(selected_file_path, 'rb')

        # Retrieve audio properties
        CHANNELS = wf.getnchannels()     # Number of channels
        RATE = wf.getframerate()     # Sampling rate (frames/second)
        WIDTH = wf.getsampwidth()     # Number of bytes per sample
        LENGTH = wf.getnframes()    # Number of frames in the audio

        # Read the entire file
        input_bytes = wf.readframes(LENGTH)
        wf.close()  # Close the file after reading

        # Convert the input bytes to a numpy array
        input_array = np.frombuffer(input_bytes, dtype='int16')

        # Check if the filter is turned on
        if filter_button.data["is_on"] == True:
            # Apply modulation based on the selected filter
            if current_filter == "Alien Voice":
                modulated_array = Filters.alien_effect(input_array)
            elif current_filter == "Robotic Voice":
                modulated_array = Filters.robotize_effect(input_array)
            elif current_filter == "Male Voice":
                modulated_array = Filters.male_effect(input_array)
            elif current_filter == "Female Voice":
                modulated_array = Filters.female_effect(input_array)
            elif current_filter == "Baby Voice":
                modulated_array = Filters.baby_effect(input_array)
            elif current_filter == "Echoed Voice":
                modulated_array = Filters.echo_effect(input_array)
            elif current_filter == "Ping Pong Voice":
                modulated_array = Filters.ping_pong_effect(input_array)
            elif current_filter == "Alternate Channel Effect":
                modulated_array = Filters.alternate_channels(input_array)
            elif current_filter == "Mutation Effect":
                modulated_array = Filters.mutation_effect(input_array)
            elif current_filter == "Flanger Effect":
                modulated_array = Filters.flanger_effect(input_array)
        else:
            # Show a dialog if the filter is not turned on
            Utils.show_select_audio_dialog()
            return

        # Convert the modulated array back to bytes
        modulated_audio_data = modulated_array.astype('int16').tobytes()

        # Set the length of the modulated audio (in seconds)
        modulated_audio_length = LENGTH / RATE

        # Configure and make modulated audio controls visible
        modulated_play_bar.config(to=modulated_audio_length)
        modulated_play_bar.grid()
        modulated_play_button.config(state=tk.NORMAL)
        modulated_play_button.grid()
        modulated_pause_continue_button.config(state=tk.DISABLED)
        modulated_pause_continue_button.grid()
        download_modulated_button.grid()

        # Optional: Uncomment the following lines to automatically play the modulated audio
        # modulated_is_playing = True
        # modulated_paused_position = 0
        # modulated_update_bar_thread_running = True
        # threading.Thread(target=update_modulated_play_bar, daemon=True).start()

def play_modulated_audio() -> None:
    """
    Play modulated audio from the beginning.

    Global Variables:
        modulated_audio_data (bytes): Represents the modulated audio data.
        modulated_play_obj (SimpleAudioObject): Represents the modulated audio playback object.
        modulated_is_playing (bool): Indicates whether modulated audio is currently playing.
        modulated_paused_position (int): Stores the position where modulated audio was paused.
        modulated_update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        CHANNELS (int): Number of audio channels.
        WIDTH (int): Sample width (in bytes) for audio data.
        RATE (int): Sample rate in Hertz.

    Returns:
        None

    This function plays modulated audio from the beginning, stopping any existing playback
    and updating thread. It resets the modulated play bar and paused position, starts playing
    the modulated audio, and launches a thread to update the play bar during playback.

    Example usage:
        play_modulated_audio()
    """
    # Use global variables
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
        return

    # Start playing the modulated audio from the beginning
    modulated_audio_segment = AudioSegment(
        data=modulated_audio_data,
        sample_width=WIDTH,
        frame_rate=RATE,
        channels=CHANNELS
    )
    modulated_play_obj = sa.play_buffer(
        modulated_audio_segment.raw_data,
        num_channels=CHANNELS,
        bytes_per_sample=WIDTH,
        sample_rate=RATE
    )
    modulated_is_playing = True
    modulated_update_bar_thread_running = True

    # Start a new thread to update the play bar while audio is playing
    threading.Thread(target=update_modulated_play_bar, daemon=True).start()

    # Update the toggle button to show "Pause" and enable it
    modulated_pause_continue_button.config(text="Pause", state=tk.NORMAL)

def update_modulated_play_bar() -> None:
    """
    Update the progress bar during modulated audio playback.

    Global Variables:
        modulated_is_playing (bool): Indicates whether modulated audio is currently playing.
        modulated_play_obj (SimpleAudioObject): Represents the modulated audio playback object.
        modulated_audio_length (float): Length of the modulated audio in seconds.
        modulated_paused_position (int): Stores the position where modulated audio was paused.
        modulated_update_bar_thread_running (bool): Indicates whether the update bar thread is running.

    Returns:
        None

    This function continuously updates the progress bar during modulated audio playback.
    It calculates the current position in the audio file based on the elapsed time and the
    paused position if the audio was previously paused.

    Example usage:
        threading.Thread(target=update_modulated_play_bar, daemon=True).start()
    """
    # Use global variables
    global modulated_is_playing, modulated_play_obj, modulated_audio_length, modulated_paused_position, modulated_update_bar_thread_running

    # Record the start time of the update
    start_time = time.time()

    # Continue updating the progress bar while the update thread is running
    while modulated_update_bar_thread_running:
        if modulated_is_playing and modulated_play_obj.is_playing():
            # Calculate the current position in the audio file
            current_pos = (time.time() - start_time) + modulated_paused_position / 1000  # in seconds

            # Set the current position on the progress bar
            modulated_play_bar.set(current_pos)

            # Break out of the loop if the end of the audio is reached
            if current_pos >= modulated_audio_length:
                break

        # Wait for a short duration before the next update
        time.sleep(0.1)

def toggle_modulated_pause_continue() -> None:
    """
    Toggle between pausing and continuing playback of modulated audio.

    Global Variables:
        modulated_play_obj (SimpleAudioObject): Represents the modulated audio playback object.
        modulated_is_playing (bool): Indicates whether modulated audio is currently playing.
        modulated_paused_position (int): Stores the position where modulated audio was paused.
        modulated_update_bar_thread_running (bool): Indicates whether the update bar thread is running.
        modulated_audio_data (bytes): Represents the modulated audio data.
        CHANNELS (int): Number of audio channels.
        WIDTH (int): Sample width (in bytes) for audio data.
        RATE (int): Sample rate in Hertz.

    Returns:
        None

    This function toggles between pausing and continuing playback of modulated audio. If the audio is
    currently playing, it pauses the audio and updates the button text to "Continue." If the audio is
    paused, it resumes playback from the current slider position and updates the button text to "Pause."

    Example usage:
        toggle_modulated_pause_continue()
    """
    # Use global variables
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

        # Play the modulated audio from the specified start position
        modulated_play_obj = sa.play_buffer(
            modulated_audio_segment.raw_data,
            num_channels=CHANNELS,
            bytes_per_sample=WIDTH,
            sample_rate=RATE
        )

        # Set flags to indicate audio is now playing
        modulated_is_playing = True
        modulated_paused_position = start_position
        modulated_update_bar_thread_running = True

        # Start a new thread to update the play bar while audio is playing
        threading.Thread(target=update_modulated_play_bar, daemon=True).start()

        # Update the toggle button to show "Pause"
        modulated_pause_continue_button.config(text="Pause")

def download_modulated_audio() -> None:
    """
    Download the modulated audio data to a WAV file.

    Global Variables:
        modulated_audio_data (bytes): Represents the modulated audio data.
        selected_file_path (str): Represents the path of the selected audio file.
        CHANNELS (int): Number of audio channels.
        WIDTH (int): Sample width (in bytes) for audio data.
        RATE (int): Sample rate in Hertz.

    Returns:
        None

    This function prompts the user to choose a file name and location to save the modulated
    audio data as a WAV file. If modulated audio data is not available, it prints a message
    indicating that there is no modulated audio to save.

    Example usage:
        download_modulated_audio()
    """
    # Use global variables
    global modulated_audio_data, selected_file_path, CHANNELS, WIDTH, RATE

    # Check if modulated audio data is available
    if modulated_audio_data is None:
        return

    # Extract the original filename without extension
    original_filename = os.path.splitext(os.path.basename(selected_file_path))[0]

    # Set a default filename for saving the modulated audio
    default_filename = f"modulated_{original_filename}.wav"

    # Open a save file dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav")],
        initialfile=default_filename
    )

    # If the user cancels the save operation
    if not file_path:
        return

    # Write the modulated audio data to the WAV file
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(WIDTH)
        wf.setframerate(RATE)
        wf.writeframes(modulated_audio_data)

def on_closing() -> None:
    """
    Handle the closing of the main window.

    Returns:
        None

    This function is intended to be bound to the closing event of the main window.
    It stops the playback if it is currently in progress, sets a global flag to stop
    an update thread, prints a message to the console, and destroys the main window.

    Example usage:
        window.protocol("WM_DELETE_WINDOW", on_closing)
    """
    # Use the global variable
    global update_bar_thread_running

    # Check if audio playback is in progress
    if play_obj:
        play_obj.stop()

    # Set the flag to stop the update thread
    update_bar_thread_running = False

    # Destroy the main window
    window.destroy()
    
def open_audio_clips_window() -> None:
    """
    Open a window displaying buttons for playing audio clips.

    Returns:
        None

    This function creates a new window (Toplevel) displaying buttons for playing
    audio clips fetched from the 'audio_clips' directory. Each button corresponds to
    an audio file, and clicking the button triggers audio playback.

    Example usage:
        open_audio_clips_window()
    """
    # Create a new Toplevel window
    clips_window = tk.Toplevel(window)
    clips_window.title("Audio Clips")

    # Bind the callback function to the window close event
    clips_window.wm_protocol("WM_DELETE_WINDOW", lambda: stop_audio_on_window_close(clips_window))

    # Fetch audio files
    audio_files = fetch_audio_files()

    # Configure the grid layout of the Toplevel window
    rows = (len(audio_files) + 2) // 3
    for i in range(rows):
        clips_window.rowconfigure(i, weight=1)
        clips_window.columnconfigure(i, weight=1)

    # Define button style
    button_padx = 35  # Horizontal padding
    button_pady = 15  # Vertical padding
    button_font = ("Helvetica", 10, "bold")  # Font style

    # Create buttons dynamically based on audio files
    for i, (file_name, file_path) in enumerate(audio_files.items()):
        label = os.path.splitext(file_name)[0]
        btn = tk.Button(clips_window, text=label, background=button_off_color, font=button_font)

        # Bind the play_audio function to the button click event
        btn.config(command=lambda path=file_path, button=btn: play_audio(path, button))

        # Place the button in the grid layout
        btn.grid(row=i // 3, column=i % 3, sticky='nsew', padx=button_padx, pady=button_pady)

def stop_audio_on_window_close(window: tk.Toplevel) -> None:
    """
    Stop audio playback when the window is closed.

    Parameters:
        window (tk.Toplevel): The Toplevel window.

    Returns:
        None
    """
    global current_play_obj, audio_thread, current_active_button, is_audio_playing

    # Stop the currently playing audio if there is one
    if is_audio_playing:
        current_play_obj.stop()
        is_audio_playing = False

        # Reset the color of the previous active button
        if current_active_button:
            current_active_button.config(background=button_off_color)

    # Destroy the window
    window.destroy()

def fetch_audio_files() -> dict:
    """
    Fetch audio files from the 'audio_clips' directory and return a dictionary.

    Returns:
        dict: A dictionary mapping audio file names to their full paths.

    This function searches the 'audio_clips' directory for audio files with '.mp3' or '.wav'
    extensions and creates a dictionary mapping file names to their full paths.

    Example usage:
        audio_files = fetch_audio_files()
    """
    # Specify the directory where audio files are stored
    directory = os.path.join(os.path.dirname(__file__), 'audio_clips')

    # Initialize an empty dictionary to store audio file names and paths
    audio_files = {}

    # Iterate through files in the directory
    for file in os.listdir(directory):
        # Check if the file has a '.mp3' or '.wav' extension
        if file.endswith('.mp3') or file.endswith('.wav'):
            # Construct the full path of the audio file
            path = os.path.join(directory, file)

            # Add the file name and path to the dictionary
            audio_files[file] = path

    # Return the dictionary containing audio file names and paths
    return audio_files

def play_audio(file_path: str, button: tk.Button) -> None:
    """
    Play audio from a specified file path and update the button appearance.

    Parameters:
        file_path (str): The path to the audio file to be played.
        button (tk.Button): The Tkinter button associated with playing the audio.

    Global Variables:
        current_play_obj (SimpleAudioObject): Represents the current audio playback object.
        audio_thread (threading.Thread): Represents the thread used for audio playback.
        last_played_button (tk.Button): Represents the last played audio button.
        is_audio_playing (bool): Indicates whether audio is currently playing.

    Returns:
        None

    This function plays audio from the specified file path and updates the appearance of
    the associated button. It starts a new thread for audio playback and stops the currently
    playing audio if there is one.

    If the same button is clicked again, the playback is restarted.

    Example usage:
        play_audio("/path/to/audio/file.mp3", play_button)
    """
    # Use the global variables
    global current_play_obj, audio_thread, last_played_button, is_audio_playing

    def audio_worker():
        """
        Worker function for audio playback in a separate thread.

        This function handles the audio playback, updates the button color while playing,
        and resets the button color when the audio finishes or an error occurs.
        """
        global current_play_obj, is_audio_playing
        try:
            # Change the button color to green while playing
            button.config(background="#2ECC71")

            # Create a SimpleAudioObject from the audio file and play it
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            current_play_obj = wave_obj.play()
            is_audio_playing = True

            # Wait for the audio to finish playing
            while current_play_obj.is_playing():
                time.sleep(0.1)

            # Audio finished playing
            is_audio_playing = False
        except Exception as e:
            # Handle errors during audio playback
            print(f"Error playing file {file_path}: {e}")
        finally:
            # Reset the color of the button (even if an error occurs)
            button.config(background=button_off_color)

    # Stop the currently playing audio if there is one
    if is_audio_playing:
        current_play_obj.stop()
        is_audio_playing = False

        # Reset the color of the last played button
        if last_played_button and last_played_button != button:
            last_played_button.config(background=button_off_color)

    # If the same button is clicked again, restart the playback
    if last_played_button == button:
        current_play_obj.stop()
        is_audio_playing = False
    else:
        last_played_button = button
        audio_thread = threading.Thread(target=audio_worker)
        audio_thread.start()

def on_filter_option_change(event: tk.Event) -> None:
    """
    Handle the change event of the filter option combobox.

    Parameters:
        event (tk.Event): The event object triggered by the change in the combobox.

    Global Variables:
        current_filter (str): Represents the current filter option.

    Returns:
        None

    This method handles the change event of the filter option combobox. It updates the
    global variable `current_filter` with the selected option, changes the text of the filter button,
    and performs additional actions based on the selected filter option.

    Note:
        This function relies on global variables: current_filter, filter_option_combobox,
        filter_button, canvas, microphone_button, output_button. Ensure that these variables
        are properly defined before calling this function.

    Example usage:
        on_filter_option_change(event)
    """
    # Use the global variable current_filter
    global current_filter

    # Get the selected filter option from the combobox
    selected_option = filter_option_combobox.get()

    # Update the global variable current_filter with the selected option
    current_filter = selected_option

    # Change the text of the filter button to the selected option
    filter_button.config(text=selected_option)

    # Check if the current filter is "Normal" and perform actions accordingly
    if current_filter == "Normal":
        filter_button.data["is_on"] = True
        UI.toggle_button_color(filter_button, canvas, microphone_button, filter_button, output_button)


# Create the main window
window = tk.Tk()
window.title("Voice Changer")

# Configure the grid rows and columns to expand proportionally
for i in range(6):  # Adjust the range based on your number of rows
    window.rowconfigure(i, weight=1)
for j in range(3):  # Adjust the range based on your number of columns
    window.columnconfigure(j, weight=1)

# Create the canvas and place it below the buttons
canvas = tk.Canvas(window, height=200, width=300)  # Adjust size as needed
canvas.grid(row=0, column=0, rowspan=6, columnspan=3, sticky='nsew')

# Create and place the Microphone button in the middle of the audio button stack
microphone_button = tk.Button(window, text="Microphone", command=on_microphone_click, background=button_off_color, font=("Helvetica", 10, "bold"), width=13, height=1)
microphone_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
microphone_button.data = {"is_on": False}

# Create and place the Filter button
filter_button = tk.Button(window, text="Normal", command=on_filter_click, background=button_off_color, font=("Helvetica", 10, "bold"), width=13, height=1)
filter_button.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
filter_button.data = {"is_on": False}

# Create and place the Output button in the middle of the audio button stack
output_button = tk.Button(window, text="Output", command=on_output_click, background=button_off_color, font=("Helvetica", 10, "bold"), width=10, height=1)
output_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
output_button.data = {"is_on": False}

# Create and place the Filter Options Combobox
filter_option_combobox = ttk.Combobox(window, values=filter_options, state="readonly")
filter_option_combobox.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
filter_option_combobox.set("Normal")  # Set the default value
filter_option_combobox.bind("<<ComboboxSelected>>", on_filter_option_change)

# Create a label to display the selected file name
selected_file_label = tk.Label(window, text="Selected File: None", font=("Helvetica", 10))
selected_file_label.grid(row=3, column=0, columnspan=2, pady=5, sticky='nsew')

# Create a "Convert" button
convert_button = tk.Button(window, text="Convert", command=on_convert, state=tk.DISABLED, font=("Helvetica", 10, "bold"))
convert_button.grid(row=3, column=2, padx=10, pady=5, sticky='nsew')

# Create play bar
raw_play_bar = ttk.Scale(window, from_=0, to=100, orient='horizontal')
raw_play_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
raw_play_bar.grid_remove()  # Hide the play bar initially

# Create play and toggle (pause/continue) buttons
raw_play_button = tk.Button(window, text="Play", command=play_raw_audio, state=tk.NORMAL)
raw_play_button.grid(row=5, column=0, padx=10, pady=5, sticky='nsew')
raw_play_button.grid_remove()  # Hide the play button initially

raw_pause_continue_button = tk.Button(window, text="Pause", command=toggle_pause_continue, state=tk.DISABLED)
raw_pause_continue_button.grid(row=5, column=1, padx=10, pady=5, sticky='nsew')
raw_pause_continue_button.grid_remove()  # Hide the pause/continue button initially

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

# Create a menu bar
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# Create a "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Upload Audio", command=on_upload_audio)
file_menu.add_command(label="Upload Effects", command=Utils.on_upload_effects)

# Create an "Audio Clips" menu item
# audio_clips_menu_item = tk.Menu(menu_bar, tearoff=0)
# Add "Audio Clips" directly to the menu bar
menu_bar.add_command(label="Audio Clips", command=open_audio_clips_window)

# Bind the closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Bind the window resize event
window.bind("<Configure>", lambda event: UI.on_window_resize(event, canvas, microphone_button, filter_button, output_button))

# Disable resizing of the window
window.resizable(True, True)

# After all widgets are added, call the function to set the minimum size
Utils.set_min_size(window)

# Start the Tkinter event loop
window.mainloop()