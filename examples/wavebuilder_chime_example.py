# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
===============================================================================
An example of using the WaveBuilder class to simulate wind chimes. The
oscillator values are from the CedarGrove Chime class.
"""

import time
import board
import synthio
import audiobusio
import audiomixer
from cedargrove_wavebuilder import WaveBuilder, WaveShape

print("=== WaveBuilder Simpletest===")

# Define synth parameters
SAMPLE_RATE = 22050  # The sample rate in SPS
WAVE_TABLE_LENGTH = 512  # The wave table length in samples
PLOT = False  # Plot the wave table array via the REPL

# Define the wave type, overtone ratio, and amplitude (0.0 to 1.0)
chimes = [
    (WaveShape.Sine, 1.0, 0.6),
    (WaveShape.Sine, 2.76, 0.2),
    (WaveShape.Sine, 5.40, 0.1),
    (WaveShape.Sine, 8.93, 0.1),
]

wave = WaveBuilder(
    oscillators=chimes,
    table_length=WAVE_TABLE_LENGTH,
    sample_max=32700,
    lambda_factor=1,
    loop_smoothing=True,
)

if PLOT:
    # Plot the wave_table array contents
    for point in wave.wave_table:
        print(f"({point / 1000}, )")

# Define Chime ADSR envelope parameters
chime_envelope = synthio.Envelope(
    attack_time=0.02 + 0.01,
    attack_level=1.0 * 1.0,
    decay_time=0.0,
    release_time=2.0,
    sustain_level=1.0,
)

# Configure synthesizer for I2S output on a Feather S2
audio_output = audiobusio.I2SOut(
    bit_clock=board.D19, word_select=board.D18, data=board.D17, left_justified=False
)
mixer = audiomixer.Mixer(
    sample_rate=SAMPLE_RATE, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)
mixer.voice[0].level = 0.50

synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=wave.wave_table)
mixer.play(synth)

note_1 = synthio.Note(880, envelope=chime_envelope)

print("===")

while True:
    synth.press(note_1)
    synth.release(note_1)
    time.sleep(0.5)
