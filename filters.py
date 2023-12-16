import math
import numpy as np

f0 = 800
RATE = 16000
theta = 0
ca_om = 2 * math.pi * f0 / RATE


class Filters:
    def my_modulation(input):
        global theta, ca_om
        print("In modulation")
        y = np.zeros(len(input))
        for n in range(0, len(input)):
            theta = theta + ca_om
            y[n] = int(input[n] * math.cos(theta))
            # output_block[n] = input_block[n]  # for no processing
        # keep theta betwen -pi and pi
        while theta > math.pi:
            theta = theta - 2*math.pi
        return y

    def my_modulation1(input):
        global theta, ca_om
        print("In modulation 1")
        y = np.zeros(len(input))
        for n in range(0, len(input)):
            theta = theta + ca_om
            y[n] = 10*int(input[n] * math.cos(theta))
            # output_block[n] = input_block[n]  # for no processing
        # keep theta betwen -pi and pi
        while theta > math.pi:
            theta = theta - 2*math.pi*math.pi
        return y

    def my_modulation2(input):
        global theta, ca_om
        print("In modulation 2")
        y = np.zeros(len(input))
        for n in range(0, len(input)):
            theta = theta + ca_om
            y[n] = int(input[n] * math.cos(theta))
            # output_block[n] = input_block[n]  # for no processing
        # keep theta betwen -pi and pi
        while theta > math.pi:
            theta = theta - 2*math.pi*math.pi*math.pi*math.pi
        return y