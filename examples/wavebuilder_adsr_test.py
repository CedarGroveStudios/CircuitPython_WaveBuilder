# SPDX-FileCopyrightText: 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

import time
import ulab.numpy as np
import board
import audiobusio

# import audioio
# import audiopwmio
import audiomixer
import synthio

SAMPLE_RATE = 44100
SAMPLE_SIZE = 256
loudness = 1
VOLUME = int(loudness * 32760)  # 0-32767 (signed 16-bit)

# waveforms, envelopes and synth setup
sine = np.array(
    np.sin(np.linspace(0, 4 * np.pi, SAMPLE_SIZE, endpoint=False)) * VOLUME,
    dtype=np.int16,
)
dc_max = np.array([VOLUME for i in range(SAMPLE_SIZE)], dtype=np.int16)
dc_min = np.array([-VOLUME for i in range(SAMPLE_SIZE)], dtype=np.int16)


lfo = synthio.LFO(rate=0.5, waveform=sine)

amp_env0 = synthio.Envelope(
    attack_time=0.25, decay_time=1, release_time=0.2, attack_level=1, sustain_level=0.5
)

synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)

# ADSR envelope test
# note_0 = synthio.Note(frequency=440, envelope=amp_env0, waveform=dc_max)

# LFO test
note_0 = synthio.Note(frequency=440, amplitude=lfo, waveform=dc_max)

# Instantiate output path
# I2S
audio = audiobusio.I2SOut(bit_clock=board.D24, word_select=board.D25, data=board.A3)

# Analog DAC
# audio = audioio.AudioOut(board.A0)

# PWM pin
# audio = audiopwmio(board.D13)

mixer = audiomixer.Mixer(
    voice_count=4,
    sample_rate=SAMPLE_RATE,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=2048,
)
audio.play(mixer)

mixer.voice[0].play(synth)
mixer.voice[0].level = 0.75

print("Test CV Output")
while True:
    print("press note_0", note_0)
    synth.press(note_0)
    time.sleep(10)  # 10s for LFO, 1s for ADSR envelope
    print("release note_0")
    synth.release(note_0)
    time.sleep(1)
