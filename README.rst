Introduction
------------

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/CircuitPython_Chime/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A CircuitPython class to construct a composite ``synthio`` waveform table
from a collection of oscillators. The table is created from a list
of oscillator characteristics, sample length, maximum sample
value, a lambda factor, and loop smoothing parameters.

Dependencies
------------
This class depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Usage Example
-------------

.. code-block:: python

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


Documentation
-------------
API documentation for this library can be found in `Cedargrove_WaveBuilder <https://github.com/CedarGroveStudios/CircuitPython_WaveBuilder/blob/main/media/pseudo_rtd_cedargrove_wavebuilder.pdf>`_.

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/blob/main/media/chime_api_page3.png

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/blob/main/media/chime_initialize.png

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/blob/main/media/chime_strike.png

For additional detail about ``WaveBuilder``, see `Construct a synthio Waveform Object from a List of Oscillators <https://adafruit-playground.com/u/CGrover/pages/construct-a-synthio-waveform-object-from-a-list-of-oscillators>`_

Attribution: Patch Symbols from PATCH & TWEAK by Kim Bjørn and Chris Meyer, published by Bjooks, are licensed under Creative Commons CC BY-ND 4.0.
Some Patch Symbols were modified to create the synthio symbols ``BlockInput``, ``MixerVoice``, ``Note``, ``Synthesizer``, ``sample``, and ``voice``.

Planned Updates
---------------
* Add wave table file saving and inclusion.
* Include other wave types.
* Add examples for filtering and applying ``synthio.Math`` to wave tables.

Acknowledgements and Thanks
---------------------------
* Liz Clark, '`Circle of Fifths Euclidean Synth with synthio and CircuitPython`' Adafruit Learning Guide
  for the waveform and noise examples.
* Todd Kurt for fundamentally essential ``synthio`` hints, tricks, and examples
  (https://github.com/todbot/circuitpython-synthio-tricks).
* Special thanks to Jeff Epler and Adafruit for the comprehensive design and implementation
  of the CircuitPython ``synthio`` module.
