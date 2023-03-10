from pysine import sine

notes = {
    'C': 16.352,
    'D': 18.354,
    'E': 20.602,
    'F': 21.827,
    'G': 24.500,
    'A': 27.500,
    'B': 30.868,
}

octave = 6
tune = notes['A'] * (2**octave)
print(tune)
sine(frequency=tune, duration=10.0)  # plays a 1s sine wave at 440 Hz
