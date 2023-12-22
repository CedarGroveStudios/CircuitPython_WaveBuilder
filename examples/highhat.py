# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

# import dc_dac_test
# import weather_chimes_code
# import cedargrove_chime_simpletest
# import chime_wind_algorithm

import gc
import time
import microcontroller
import board
import digitalio
import synthio
import ulab.numpy as np
import math
import random
from simpleio import map_range
import adafruit_dotstar
import audiobusio
import audiomixer


# Define ADSR envelope settings
closed_env = synthio.Envelope(
    attack_time=0.01,
    attack_level=1.0,
    decay_time=0.09,
    release_time=0.0,
    sustain_level=0.0,
)
open_env = synthio.Envelope(
    attack_time=0.01,
    attack_level=0.9,
    decay_time=0.09,
    release_time=0.1,
    sustain_level=0.02,
)

# Instantiate the synthesizer
WAVEFORM = sine  # None, sine, square, saw, noise
RING_WAVEFORM = None  # None, sine, square, saw, noise

audio_output = audiobusio.I2SOut(
    bit_clock=board.D12, word_select=board.D9, data=board.D6
)
mixer = audiomixer.Mixer(
    sample_rate=11020, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)
mixer.voice[0].level = 1.0

synth = synthio.Synthesizer(sample_rate=WAVE_RATE, waveform=WAVEFORM)
mixer.play(synth)

# Create the first bandpass filter
noise_filter = synth.band_pass_filter(10000, 10)

# Set up the operational parameters
OSCILLATORS = roland_osc  # None, roland_osc, klein_osc, test_osc
TUNE_CONTROL = 1.0
NOTE_ENVELOPE = None  # None, closed_env, open_env
NOTE_FILTER = None  # None, noise_filter

# Build the dissonant note oscillators
oscillators = [freq * TUNE_CONTROL for freq in OSCILLATORS]
# with ring modulator (to simulate resonance)
notes = [
    synthio.Note(
        note_freq,
        amplitude=1 / 7,
        envelope=NOTE_ENVELOPE,
        filter=NOTE_FILTER,
        ring_frequency=note_freq,
        ring_waveform=RING_WAVEFORM,
    )
    for note_freq in oscillators
]
# without ring modulator
# notes = [synthio.Note(note_freq, amplitude=1/7, envelope=NOTE_ENVELOPE, filter=NOTE_FILTER) for note_freq in oscillators]


while True:
    synth.press(notes)
    time.sleep(0.2)
    synth.release(notes)
    time.sleep(0.8)
