import tkinter as tk
from tkinter import filedialog

def on_microphone_click():
    print("Microphone button clicked")
    toggle_button_color(microphone_button)

def on_audio_click(audio_number):
    print(f"Audio {audio_number} button clicked")
    global selected_audio_button
    # Deselect the previously selected button (if any)
    if selected_audio_button and selected_audio_button != output_button:
        toggle_button_color(selected_audio_button)
    # If the same button is clicked again, set selected_audio_button to None
    if selected_audio_button == audio_buttons[audio_number]:
        selected_audio_button = None
    else:
        # Select the clicked button
        selected_audio_button = audio_buttons[audio_number]
        toggle_button_color(selected_audio_button)

def on_output_click():
    print("Output button clicked")
    # Do something when the Output button is clicked

def toggle_button_color(button):
    current_color = button.cget("background")
    original_color = button.data["original_color"]
    if current_color == original_color:
        button.configure(background="#2ECC71")  # Change to green when selected
    else:
        button.configure(background=original_color)

def on_open_file():
    file_path = filedialog.askopenfilename(title="Open File", filetypes=[("Audio Files", "*.mp3;*.wav")])
    if file_path:
        print(f"Selected file: {file_path}")

def on_closing():
    print("Window closed")
    window.destroy()

# Create the main window
window = tk.Tk()
window.title("Voice Changer")

# Set the original button color
default_button_color = "#3498DB"  # A different default color
selected_button_color = "#2ECC71"  # A green color when selected

# Create and place the Microphone button with a modern style
microphone_button = tk.Button(window, text="Microphone", command=on_microphone_click, background=default_button_color, foreground="white", font=("Helvetica", 10, "bold"))
microphone_button.grid(row=0, column=0, padx=10, pady=10)
microphone_button.data = {"original_color": default_button_color}

# Create and place the Audio buttons in the second column with a modern style
audio_buttons = []
selected_audio_button = None  # Variable to track the selected button
for i in range(0, 3):
    audio_button = tk.Button(window, text=f"Audio {i}", command=lambda i=i: on_audio_click(i), background=default_button_color, foreground="white", font=("Helvetica", 10, "bold"))
    audio_button.grid(row=i, column=1, padx=10, pady=10)
    audio_button.data = {"original_color": default_button_color}
    audio_buttons.append(audio_button)

# Create and place the Output button in the third column with a modern style
output_button = tk.Button(window, text="Output", command=on_output_click, background=default_button_color, foreground="white", font=("Helvetica", 10, "bold"))
output_button.grid(row=0, column=2, padx=10, pady=10)
output_button.data = {"original_color": default_button_color}

# Create a menu bar
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# Create a "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=on_open_file)

# Bind the closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter event loop
window.mainloop()
