import math
from scipy import signal
import numpy as np
import librosa

f0 = 100
RATE = 16000
theta = 0
ca_om = 2 * math.pi * f0 / RATE
ping_pong_buffer = np.zeros(RATE)
ping_pong_pointer = 0

class Filters:
    @staticmethod
    def alien_effect(input: np.ndarray) -> np.ndarray:
        """
        Apply an alien voice modulation effect to the input signal.

        Parameters:
        - input (numpy.ndarray): Input audio signal.

        Returns:
        - numpy.ndarray: Alien voice modulated audio signal.
        """
        global theta, ca_om
        y = np.zeros(len(input))  # Initialize an array for the modulated signal
        for n in range(0, len(input)):
            theta = theta + ca_om  # Increment the phase by the modulation frequency
            y[n] = int(input[n] * math.cos(theta))  # Apply modulation to the input signal
        # Keep theta between -pi and pi
        while theta > math.pi:
            theta = theta - 2*math.pi
        return y

    
    @staticmethod
    def echo_effect(input: np.ndarray, delay_samples: int = 512, decay_factor: float = 1.2) -> np.ndarray:
        """
        Apply an echo effect to the input signal.

        Parameters:
        - input (numpy.ndarray): Input audio signal.
        - delay_samples (int): Number of samples to delay for the echo effect (default is 512).
        - decay_factor (float): Factor to attenuate the delayed signal (default is 1.2).

        Returns:
        - numpy.ndarray: Audio signal with echo effect applied.
        """
        output = np.zeros(len(input) + delay_samples, dtype=np.int16)  # Initialize an array for the output signal
        input_padded = np.pad(input, (delay_samples, 0), mode='constant')  # Pad the input signal for delayed samples

        for i in range(len(input)):
            output[i] += input_padded[i]  # Add the direct audio to the output
            if i - delay_samples >= 0:
                # Add the delayed audio with attenuation to the output
                output[i] += int(input_padded[i - delay_samples] * decay_factor)

        return output[:len(input)]  # Trim the output to match the length of the input


    @staticmethod
    def robotize_effect(input: np.ndarray, sr: int = 16000, mod_freq: int = 100, pitch_shift_steps: int = -2) -> np.ndarray:
        """
        Apply a robotic effect to the input signal with amplitude modulation and pitch shift.

        Parameters:
        - input (numpy.ndarray): Input audio signal.
        - sr (int): Sampling rate of the audio signal (default is 16000).
        - mod_freq (int): Modulation frequency for amplitude modulation (default is 100).
        - pitch_shift_steps (int): Number of pitch shift steps (default is -2).

        Returns:
        - numpy.ndarray: Audio signal with robotic effect applied.
        """
        # Convert input to float for processing
        input_float = input.astype(float)

        # Apply amplitude modulation for a robotic effect
        t = np.linspace(0, len(input_float) / sr, num=len(input_float))
        modulation = (1 + np.cos(2 * np.pi * mod_freq * t)) / 2
        modulated = input_float * modulation

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        # Apply pitch shift without using librosa
        pitch_shifted = np.interp(np.arange(0, len(modulated), pitch_shift_factor),
                                np.arange(len(modulated)),
                                modulated)

        return pitch_shifted.astype(np.int16)


    @staticmethod
    def male_effect(input: np.ndarray, pitch_shift_steps: int = -3) -> np.ndarray:
        """
        Apply a pitch shift to make the input signal sound like a male voice.

        Parameters:
        - input (numpy.ndarray): Input audio signal.
        - pitch_shift_steps (int): Number of pitch shift steps (default is -3).

        Returns:
        - numpy.ndarray: Audio signal with male voice pitch shift applied.
        """
        # Convert input to float for processing
        input_float = input.astype(float)

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        # Apply pitch shift without using librosa
        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)


    @staticmethod
    def female_effect(input: np.ndarray, pitch_shift_steps: int = 3) -> np.ndarray:
        """
        Apply a pitch shift to make the input signal sound like a female voice.

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

        # Apply pitch shift without using librosa
        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)

    
    @staticmethod
    def ping_pong_effect(input_array: np.ndarray) -> np.ndarray:
        """
        Apply a ping-pong effect to the input audio signal.

        Parameters:
        - input_array (numpy.ndarray): Input audio signal.

        Returns:
        - numpy.ndarray: Audio signal with ping-pong effect applied (stereo output).
        """
        global ping_pong_buffer, ping_pong_pointer

        # Length of the ping-pong buffer
        N = len(ping_pong_buffer)

        # Initialize the output array with stereo channels
        output = np.zeros((len(input_array), 2))

        for i, x in enumerate(input_array):
            # Store the current sample in the buffer and get the delayed sample
            delayed_sample = ping_pong_buffer[ping_pong_pointer]
            ping_pong_buffer[ping_pong_pointer] = x
            ping_pong_pointer = (ping_pong_pointer + 1) % N

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

    
    # @staticmethod
    # def autobots(input_array, rate = RATE, dly_in_sec=0.2, delay_gain=1):
    #     bufferLen = int(rate * dly_in_sec)
    #     buffer = bufferLen * [0]
    #     k = 0
    #     output = np.zeros(len(input_array))

    #     for i, x_i in enumerate(input_array):
    #         output[i] = x_i * np.cos(2 * np.pi * 0.6 * i) + delay_gain * buffer[k]
    #         buffer[k] = output[i]
    #         k = (k + 1) % len(buffer)

    #     return output
    
    # @staticmethod
    # def drunk(input_array, rate = RATE, delay_sec=0.2):
    #     bufferLen = int(delay_sec * rate)
    #     buffer = [0] * bufferLen
    #     k = 0
    #     output = np.zeros(len(input_array))

    #     for i, x_i in enumerate(input_array):
    #         y_i = x_i * np.cos(i) + x_i * np.sin(i) + buffer[k]
    #         output[i] = y_i
    #         buffer[k] = x_i
    #         k = (k + 1) % bufferLen

    #     return output
    
    # def autobots(input, sr=16000, vibrato_rate=7, vibrato_depth=70):
    #     """
    #     Apply a vibrato effect to the input signal.
        
    #     :param input: Input audio signal (numpy array).
    #     :param sr: Sampling rate of the audio signal.
    #     :param vibrato_rate: Rate of vibrato in Hz.
    #     :param vibrato_depth: Depth of vibrato in samples.
    #     :return: Vibrato applied audio signal.
    #     """
    #     output = np.zeros_like(input)
    #     t = np.arange(len(input))
    #     vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t / sr)
    #     for i in range(len(input)):
    #         vibrato_index = int(i + vibrato[i])
    #         if 0 <= vibrato_index < len(input):
    #             output[i] = input[vibrato_index]
    #     return output.astype(np.int16)
    @staticmethod
    def flanger_effect(input_array: np.ndarray, sr: int = 16000, delay: float = 0.03, depth: float = 0.02, rate: float = 0.55) -> np.ndarray:
        """
        Apply a flanger effect to the input audio signal.
        
        Parameters:
        - input_array (numpy.ndarray): Input audio signal.
        - sr (int): Sampling rate of the audio signal.
        - delay (float): Base delay in seconds.
        - depth (float): Modulation depth in seconds.
        - rate (float): Rate of flange modulation in Hz.

        Returns:
        - numpy.ndarray: Audio signal with flanger effect applied.
        """
        output = np.zeros_like(input_array)
        max_delay = int((delay + depth) * sr)
        
        for i in range(max_delay, len(input_array)):
            # Calculate the modulated delay based on the modulation depth and rate
            mod_delay = int(delay * sr + depth * sr * np.sin(2 * np.pi * rate * i / sr))
            
            # Apply the flanger effect by combining the current sample with a delayed sample
            output[i] = input_array[i] + input_array[i - mod_delay]

        return output.astype(np.int16)