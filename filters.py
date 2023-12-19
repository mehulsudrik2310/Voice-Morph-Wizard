import math
from scipy import signal
import numpy as np
import librosa

f0 = 100
RATE = 16000
theta = 0
ca_om = 2 * math.pi * f0 / RATE

class Filters:
    def alien_effect(input):
        global theta, ca_om
        y = np.zeros(len(input))
        for n in range(0, len(input)):
            theta = theta + ca_om
            y[n] = int(input[n] * math.cos(theta))
        # keep theta betwen -pi and pi
        while theta > math.pi:
            theta = theta - 2*math.pi
        return y
    
    def echo_effect(input, delay_samples=512, decay_factor=1.2):
        output = np.zeros(len(input) + delay_samples, dtype=np.int16)
        input_padded = np.pad(input, (delay_samples, 0), mode='constant')

        for i in range(len(input)):
            output[i] += input_padded[i]
            if i - delay_samples >= 0:
                output[i] += int(input_padded[i - delay_samples] * decay_factor)

        return output[:len(input)]

    def robotize_effect(input, sr=16000, mod_freq=100, pitch_shift_steps=-2):
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

    def male_effect(input, pitch_shift_steps=-3):
        # Convert input to float for processing
        input_float = input.astype(float)

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)

    def female_effect(input, pitch_shift_steps=3):
        # Convert input to float for processing
        input_float = input.astype(float)

        # Calculate the pitch shift factor
        pitch_shift_factor = 2 ** (pitch_shift_steps / 12.0)

        pitch_shifted = np.interp(np.arange(0, len(input_float), pitch_shift_factor),
                                np.arange(len(input_float)),
                                input_float)

        return pitch_shifted.astype(np.int16)
    
    @staticmethod
    def ping_pong_effect(input_array, rate = RATE, delay_sec=0.2):
        N = int(rate * delay_sec)
        buffer = np.zeros(N)  # Delay buffer
        output = np.zeros((len(input_array), 2))  # Stereo output: 2 channels
        k = 0  # Buffer index

        for i, x in enumerate(input_array):
            # Store current sample in buffer and get the delayed sample
            delayed_sample = buffer[k]
            buffer[k] = x
            k = (k + 1) % N

            # Assign direct and delayed audio to alternate channels
            if i % N < N // 2:
                output[i, 0] = x              # Left channel gets the direct audio
                output[i, 1] = delayed_sample  # Right channel gets the delayed audio
            else:
                output[i, 0] = delayed_sample  # Left channel gets the delayed audio
                output[i, 1] = x              # Right channel gets the direct audio
        return output
    
    @staticmethod
    def alternate_channels(input_array, samples_per_alternation=1024):
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
    
    def autobots(input, sr=16000, delay=0.03, depth=0.02, rate=0.55):
        """
        Apply a flanger effect to the input signal.
        
        :param input: Input audio signal (numpy array).
        :param sr: Sampling rate of the audio signal.
        :param delay: Base delay in seconds.
        :param depth: Modulation depth in seconds.
        :param rate: Rate of flange modulation in Hz.
        :return: Flanger applied audio signal.
        """
        output = np.zeros_like(input)
        max_delay = int((delay + depth) * sr)
        for i in range(max_delay, len(input)):
            mod_delay = int(delay * sr + depth * sr * np.sin(2 * np.pi * rate * i / sr))
            output[i] = input[i] + input[i - mod_delay]
        return output.astype(np.int16)
        
