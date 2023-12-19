import math
from scipy import signal
import numpy as np

RATE = 8000

# Global variables for various effects
global_theta = 0  # For alien effect
global_echo_buffer = np.zeros(1024)  # For echo effect
global_echo_pointer = 0
global_vibrato_buffer = np.zeros(1024)  # For mutation (vibrato) effect
global_vibrato_pointers = [0, 512]  # [read_pointer, write_pointer]
global_flanger_buffer = np.zeros(int(0.03 * RATE) + 1)  # For flanger effect
global_flanger_pointer = 0
global_ping_pong_buffer = np.zeros(RATE)  # For ping-pong effect
global_ping_pong_pointer = 0


class Filters:
    @staticmethod
    def alien_effect(input_array: np.ndarray) -> np.ndarray:
        """
        Apply an alien voice modulation effect to the input signal.

        This function modulates the input audio signal with an alien voice effect.
        It uses a cosine modulation with a frequency of 700 Hz to create the modulation effect.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.

        Returns:
        - numpy.ndarray: Alien voice modulated audio signal.
        """
        global global_theta
        modulation_frequency = 700
        modulation_angular_frequency = 2 * math.pi * modulation_frequency / (RATE * 2)
        
        modulated_signal = np.zeros(len(input_array))  # Initialize an array for the modulated signal

        for n in range(len(input_array)):
            global_theta += modulation_angular_frequency  # Increment the phase by the modulation frequency
            modulated_signal[n] = int(input_array[n] * math.cos(global_theta))  # Apply modulation to the input signal
            
            # Keep global_theta between -pi and pi
            while global_theta > math.pi:
                global_theta -= 2 * math.pi

        return modulated_signal

    @staticmethod
    def echo_effect(input_array: np.ndarray, delay_samples: int = 1024, decay_factor: float = 0.7) -> np.ndarray:
        """
        Apply an echo effect to the input signal.

        This function applies an echo effect to the input audio signal, creating a delayed repetition.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - delay_samples (int): Number of samples to delay for the echo effect (default is 1024).
        - decay_factor (float): Factor to attenuate the delayed signal (default is 0.8).

        Returns:
        - numpy.ndarray: Audio signal with echo effect applied.
        """
        global global_echo_buffer, global_echo_pointer
        
        # Initialize an array to store the output signal with echo
        output_signal = np.zeros(len(input_array) + delay_samples, dtype=np.int16)
        
        # Pad the input signal with zeros to accommodate the delayed samples
        input_padded = np.pad(input_array, (delay_samples, 0), mode='constant')

        for i in range(len(input_array)):
            # Add the current sample from the input signal
            output_signal[i] += input_padded[i]
            
            # Add the delayed signal with decay factor
            output_signal[i] += int(global_echo_buffer[global_echo_pointer] * decay_factor)
            
            # Update the echo buffer with the current sample
            global_echo_buffer[global_echo_pointer] = output_signal[i]
            
            # Update the echo buffer pointer (circular buffer)
            global_echo_pointer = (global_echo_pointer + 1) % delay_samples

        return output_signal[:len(input_array)]

    @staticmethod
    def robotize_effect(input_array: np.ndarray, sr: int = 16000, mod_freq: int = 100, pitch_shift_steps: int = -2) -> np.ndarray:
        """
        Apply a robotic effect to the input signal with amplitude modulation and pitch shift.

        This function modulates the input audio signal with amplitude modulation and applies pitch shift.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - sr (int): Sampling rate of the audio signal (default is 16000).
        - mod_freq (int): Modulation frequency for amplitude modulation (default is 100).
        - pitch_shift_steps (int): Number of pitch shift steps (default is -2).

        Returns:
        - numpy.ndarray: Audio signal with robotic effect applied.
        """
        # Convert input to float for processing
        input_float = input_array.astype(float)
        
        # Create a time vector for modulation
        t = np.linspace(0, len(input_float) / sr, num=len(input_float))
        
        # Generate amplitude modulation using a cosine function
        modulation = (1 + np.cos(2 * np.pi * mod_freq * t)) / 2
        
        # Apply amplitude modulation to the input signal
        modulated = input_float * modulation
        
        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)
        
        # Apply pitch shift
        pitch_shifted = np.interp(np.arange(0, len(modulated), pitch_shift_factor),
                                np.arange(len(modulated)),
                                modulated)
        
        return pitch_shifted.astype(np.int16)

    @staticmethod
    def male_effect(input_array: np.ndarray, pitch_shift_steps: int = -3) -> np.ndarray:
        """
        Apply a pitch shift to make the input signal sound like a male voice.

        This function shifts the pitch of the input audio signal to simulate a male voice.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - pitch_shift_steps (int): Number of pitch shift steps (default is -3).

        Returns:
        - numpy.ndarray: Audio signal with male voice pitch shift applied.
        """
        # Convert input to float for processing
        input_float = input_array.astype(float)

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        # Apply pitch shift
        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)
    
    @staticmethod
    def female_effect(input: np.ndarray, pitch_shift_steps: int = 3) -> np.ndarray:
        """
        Apply a pitch shift to make the input signal sound like a female voice.

        This function shifts the pitch of the input signal to create a female voice effect.

        Parameters:
        - input (numpy.ndarray): Input audio signal.
        - pitch_shift_steps (int): Number of pitch shift steps (default is 3).

        Returns:
        - numpy.ndarray: Audio signal with female voice pitch shift applied.
        """
        # Convert input to float for processing
        input_float = input.astype(float)

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        # Apply pitch shift
        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)

    @staticmethod
    def baby_effect(input_array: np.ndarray, pitch_shift_steps: int = 10) -> np.ndarray:
        """
        Apply a baby pitch effect to the input signal.

        This function shifts the pitch of the input audio signal to simulate a baby voice.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - pitch_shift_steps (int): Number of pitch shift steps (default is 10).

        Returns:
        - numpy.ndarray: Audio signal with baby pitch effect applied.
        """
        # Convert input to float for processing
        input_float = input_array.astype(float)

        # Calculate the pitch shift factor for a baby pitch
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        # Apply pitch shift
        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)


    @staticmethod
    def ping_pong_effect(input_array: np.ndarray) -> np.ndarray:
        """
        Apply a ping-pong effect to the input audio signal.

        This function creates a stereo ping-pong effect by storing and delaying samples alternately.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.

        Returns:
        - numpy.ndarray: Audio signal with ping-pong effect applied (stereo output).
        """
        global global_ping_pong_buffer, global_ping_pong_pointer

        # Length of the ping-pong buffer
        N = len(global_ping_pong_buffer)

        # Initialize the output array with stereo channels
        output = np.zeros((len(input_array), 2))

        for i, x in enumerate(input_array):
            # Store the current sample in the buffer and get the delayed sample
            delayed_sample = global_ping_pong_buffer[global_ping_pong_pointer]
            global_ping_pong_buffer[global_ping_pong_pointer] = x
            global_ping_pong_pointer = (global_ping_pong_pointer + 1) % N

            # Assign direct and delayed audio to alternate channels
            if i % N < N // 2:
                output[i, 0] = x              # Left channel gets the direct audio
                output[i, 1] = delayed_sample  # Right channel gets the delayed audio
            else:
                output[i, 0] = delayed_sample  # Left channel gets the delayed audio
                output[i, 1] = x              # Right channel gets the direct audio

        return output


    @staticmethod
    def alternate_channels(input_array: np.ndarray, samples_per_alternation: int = 1024) -> np.ndarray:
        """
        Apply an alternate channels effect to the input audio signal.

        This function alternates the output between left and right channels at each period.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - samples_per_alternation (int): Number of samples in each alternation period.

        Returns:
        - numpy.ndarray: Audio signal with alternate channels effect applied (stereo output).
        """
        output = np.zeros((len(input_array), 2))  # Stereo output: 2 channels

        for i, x in enumerate(input_array):
            # Determine which half of the alternation period we're in
            if (i // samples_per_alternation) % 2 == 0:
                # First half: Output to left channel
                output[i, 0] = x
                output[i, 1] = 0
            else:
                # Second half: Output to right channel
                output[i, 0] = 0
                output[i, 1] = x
        return output


    @staticmethod
    def mutation_effect(input_array: np.ndarray, rate: int = RATE, f0: float = 7, depth: float = 0.2, buffer_len: int = 1024) -> np.ndarray:
        """
        Apply an optimized vibrato effect to the input signal.

        This function applies a vibrato effect to the input audio signal.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - rate (int): Sampling rate of the audio signal.
        - f0 (float): Frequency of the vibrato modulation (Hz).
        - depth (float): Depth of the vibrato effect.
        - buffer_len (int): Length of the delay buffer.

        Returns:
        - numpy.ndarray: Audio signal with vibrato effect applied.
        """
        global global_vibrato_buffer, global_vibrato_pointers
        buffer_len = len(global_vibrato_buffer)
        kr, kw = global_vibrato_pointers
        output = np.zeros_like(input_array)
        mod_index = depth * np.sin(2 * math.pi * f0 * np.arange(len(input_array)) / rate)

        for n, x in enumerate(input_array):
            global_vibrato_buffer[kw] = x
            kr_int = int(np.floor(kr))
            frac = kr - kr_int
            y = (1 - frac) * global_vibrato_buffer[kr_int] + frac * global_vibrato_buffer[(kr_int + 1) % buffer_len]
            output[n] = y
            kr = (kr + 1 + mod_index[n]) % buffer_len
            kw = (kw + 1) % buffer_len

        global_vibrato_pointers = [kr, kw]
        return output

    @staticmethod
    def drunk(input_array: np.ndarray, rate: int = RATE, delay_sec: float = 0.2) -> np.ndarray:
        """
        Apply a drunk effect to the input audio signal.

        This function simulates a drunk effect by combining the current sample with a delayed sample.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - rate (int): Sampling rate of the audio signal.
        - delay_sec (float): Delay in seconds.

        Returns:
        - numpy.ndarray: Audio signal with drunk effect applied.
        """
        buffer_len = int(delay_sec * rate)
        buffer = [0] * buffer_len
        k = 0
        output = np.zeros(len(input_array))

        for i, x_i in enumerate(input_array):
            # Apply drunk effect by combining the current sample with a delayed sample
            y_i = x_i * np.cos(i) + x_i * np.sin(i) + buffer[k]
            output[i] = y_i
            buffer[k] = x_i
            k = (k + 1) % buffer_len

        return output

    @staticmethod
    def flanger_effect(input_array: np.ndarray, sr: int = 16000, delay: float = 0.03, depth: float = 0.02, rate: float = 0.55) -> np.ndarray:
        """
        Apply a flanger effect to the input audio signal.

        This function modulates the delay to create a flanger effect.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - sr (int): Sampling rate of the audio signal.
        - delay (float): Base delay in seconds.
        - depth (float): Modulation depth in seconds.
        - rate (float): Rate of flange modulation in Hz.

        Returns:
        - numpy.ndarray: Audio signal with flanger effect applied.
        """
        global global_flanger_buffer, global_flanger_pointer
        max_delay = int((delay + depth) * sr)
        output = np.zeros_like(input_array)

        for i in range(len(input_array)):
            mod_delay = int(delay * sr + depth * sr * np.sin(2 * np.pi * rate * i / sr))
            global_flanger_buffer[global_flanger_pointer] = input_array[i]
            flanger_index = (global_flanger_pointer - mod_delay + len(global_flanger_buffer)) % len(global_flanger_buffer)
            output[i] = input_array[i] + global_flanger_buffer[flanger_index]
            global_flanger_pointer = (global_flanger_pointer + 1) % len(global_flanger_buffer)

        return output.astype(np.int16)
