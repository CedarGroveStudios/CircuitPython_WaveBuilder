# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

import time
import board
import synthio
import audiobusio
import audiomixer
from cedargrove_wavebuilder import WaveBuilder, WaveShape

# Define synth parameters
SAMPLE_RATE = 22050  # The sample rate in SPS
WAVE_TABLE_LENGTH = 512  # The wave table length in samples
SAMPLE_MAXIMUM = 35000  # The maximum value of a sample

# Define the oscillator wave shape, overtone ratio, and amplitude
tone = [(WaveShape.Sine, 1.0, 0.6)]

# Create the wave table and show the debug messages
wave = WaveBuilder(
    oscillators=tone,
    table_length=WAVE_TABLE_LENGTH,
    sample_max=SAMPLE_MAXIMUM,
    lambda_factor=1.0,
    loop_smoothing=True,
    debug=True,
)

# Define the tone's ADSR envelope parameters
tone_envelope = synthio.Envelope(
    attack_time=0.02 + 0.01,
    attack_level=1.0 * 1.0,
    decay_time=0.0,
    release_time=2.0,
    sustain_level=1.0,
)

# Configure synthesizer for I2S output on a Feather S2
audio_output = audiobusio.I2SOut(
    bit_clock=board.D12, word_select=board.D9, data=board.D6, left_justified=False
)
mixer = audiomixer.Mixer(
    sample_rate=SAMPLE_RATE, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)
mixer.voice[0].level = 0.50

synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=wave.wave_table)
mixer.play(synth)

note_1 = synthio.Note(880, envelope=tone_envelope)

while True:
    synth.press(note_1)
    synth.release(note_1)
    time.sleep(0.5)
