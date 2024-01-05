# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_wavebuilder`
===============================================================================
A CircuitPython class to construct a ``synthio.ReadableBuffer`` composite wave
table object from a simple list of fundamental and overtone frequencies,
amplitudes, and wave types (sine, square, triangle, saw).
https://github.com/CedarGroveStudios/CircuitPython_WaveBuilder

Acknowledgement and thanks to:
* Liz Clark, 'Circle of Fifths Euclidean Synth with synthio and CircuitPython'
  for example waveform and noise methods;
* Todd Kurt for essential ``synthio`` hints, tricks, and examples
  (https://github.com/todbot/circuitpython-synthio-tricks).
* Special thanks to Jeff Epler for the comprehensive design and implementation
  of the CircuitPython ``synthio`` module.

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------
**Software and Dependencies:**
* ulab for CircuitPython
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import random
import ulab.numpy as np


# pylint: disable=too-few-public-methods
class WaveShape:
    """The predefined wave shapes."""

    Noise = "noise"
    Saw = "saw"
    Sine = "sine"
    Square = "square"
    Triangle = "triangle"


class WaveBuilder:
    """The WaveBuilder class creates a composite ``synthio`` waveform table
    from a collection of oscillators. The table is created from a list
    of oscillator characteristics, sample length, maximum sample value, a
    lambda factor, and loop smoothing parameters. The resulting waveform
    table is a ``synthio.ReadableBuffer`` of type ‘h’ (signed 16 bit).

    :param list oscillators: A list of oscillator characteristics. Each
    oscillator is described as a tuple of wave shape, frequency or
    overtone ratio, and amplitude. The wave shape is specified by using
    a member of the ``WaveShape`` class (type: string). The floating point
    oscillator frequency is defined as either a frequency in Hertz or
    overtone ratio based on the fundamental (lowest) frequency. The
    amplitude is a floating point value between -1.0 and 1.0 (inclusive).
    Amplitude values less than zero will flip the phase of the resultant
    oscillator waveform 180 degrees. No default.
    :param integer table_length: The number of samples contained in the
    resultant waveform table. No default.
    :param integer sample_max: The maximum positive value of a sample,
    limited to a signed 16-bit integer value (0 to 32767). The maximum
    negative value will be derived from this value. Default is 32767.
    :param float lambda_factor: The number of fundamental oscillator
    wavelengths per wave table, useful to improve waveform rendering when
    an oscillator with a much higher frequency than the fundamental is
    included. Use cautiously since synthio expects a single wavelength to
    be contained in a wave table. Defaults to 1.0.
    :param boolean loop_smoothing: Smooth the transition between the start
    and end of the waveform table to reduce loop distortion. Defaults
    to ``True`` (smooth the last two sample values in the waveform table).
    :param bool debug: A boolean value to enable debug print messages.
    Defaults to ``False`` (no debug print messages)."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        oscillators,
        table_length,
        sample_max=32767,
        lambda_factor=1.0,
        loop_smoothing=True,
        debug=False,
    ):
        self._oscillators = oscillators
        self._table_length = table_length
        self._sample_max = int(sample_max)
        self._lambda_factor = lambda_factor
        self._loop_smoothing = loop_smoothing
        self._debug = debug

        self._update_table()

    @property
    def oscillators(self):
        """The tuple list of updated oscillator characteristics. An oscillator
        tuple contains (wave_shape, frequency or ratio, amplitude)."""
        return self._oscillators

    @oscillators.setter
    def oscillators(self, new_oscillators):
        self._oscillators = new_oscillators
        self._update_table()

    @property
    def table_length(self):
        """The number of samples contained in the resultant waveform table."""
        return self._oscillators

    @table_length.setter
    def table_length(self, new_table_length):
        self._table_length = new_table_length
        self._update_table()

    @property
    def sample_max(self):
        """The maximum positive value of a sample, limited to a signed
        16-bit integer value (0 to 32767)."""
        return int(self._sample_max)

    @sample_max.setter
    def sample_max(self, new_sample_max=32767):
        self._sample_max = int(new_sample_max)
        self._update_table()

    @property
    def lambda_factor(self):
        """The number of fundamental oscillator wavelengths per wave table."""
        return self._lambda_factor

    @lambda_factor.setter
    def lambda_factor(self, new_lambda_factor=1.0):
        self._lambda_factor = new_lambda_factor
        self._update_table()

    @property
    def loop_smoothing(self):
        """Smooth the transition between the start and end of the waveform table
        to reduce loop distortion."""
        return self._loop_smoothing

    @loop_smoothing.setter
    def loop_smoothing(self, new_loop_smoothing):
        self._loop_smoothing = new_loop_smoothing
        self._update_table()

    @property
    def debug(self):
        """Enable debug print messages."""
        return self._loop_smoothing

    @debug.setter
    def debug(self, new_debug):
        self._debug = new_debug

    @property
    def wave_table(self):
        """The composite waveform wave table; synthio.ReadableBuffer of type
        ‘h’ (signed 16 bit)."""
        return self._waveform

    @property
    def loop_distortion(self):
        """The loop distortion value. The value is based on the difference
        between the first and last sample values of the wave table,
        calculated as a percentage."""
        return self._loop_distortion

    @property
    def summed_amplitude(self):
        """The sum of all oscillator amplitudes."""
        return self._summed_amplitude

    # pylint: disable=unused-argument
    def _noise_wave(self, ratio, amplitude):
        """Returns a sample array with a noise waveform adjusted to a specified amplitude."""
        amp_factor = abs(
            min(int(round(self._sample_max * amplitude, 0)), self._sample_max)
        )
        _temporary = np.array(
            [
                random.randint(-amp_factor, amp_factor)
                for _ in range(self._table_length)
            ],
            dtype=np.int16,
        )
        return _temporary

    def _saw_wave(self, ratio, amplitude):
        """Returns a waveform array with a saw wave waveform proportional
        to the frequency ratio and adjusted to a specified amplitude."""
        amp_factor = min(int(round(self._sample_max * amplitude, 0)), self._sample_max)
        _temporary = np.array([], dtype=np.int16)  # Create a zero-length array

        # Calculate the array length and subtract the initial zero element
        half_lambda = int((self._table_length / (self._lambda_factor * 2)) / ratio)

        # Build the waveform array from a full-lambda waveform
        while len(_temporary) < self._table_length:
            _temporary = np.concatenate(
                (
                    _temporary,
                    np.linspace(
                        0,
                        int(amp_factor),
                        half_lambda - 1,
                        dtype=np.int16,
                    ),
                    np.array([0], dtype=np.int16),
                    np.linspace(
                        int(-amp_factor),
                        0,
                        half_lambda - 1,
                        dtype=np.int16,
                    ),
                )
            )

        # Truncate the temporary array to match table_length
        _temporary = _temporary[: self._table_length]
        return _temporary

    def _sine_wave(self, ratio, amplitude):
        """Returns a waveform array with a sine wave waveform proportional
        to the frequency ratio and adjusted to a specified amplitude."""
        amp_factor = min(int(round(self._sample_max * amplitude, 0)), self._sample_max)
        _temporary = np.array(
            np.sin(
                np.linspace(
                    0,
                    self._lambda_factor * 2 * np.pi * ratio,
                    self._table_length,
                    endpoint=False,
                )
            )
            * amp_factor,
            dtype=np.int16,
        )
        return _temporary

    def _square_wave(self, ratio, amplitude):
        """Returns a waveform array with a square wave waveform proportional
        to the frequency ratio and adjusted to a specified amplitude."""
        amp_factor = min(int(round(self._sample_max * amplitude, 0)), self._sample_max)
        # Create a zero-length temporary array
        _temporary = np.array([], dtype=np.int16)

        # Calculate the sample length of one-half lambda
        half_lambda = int((self._table_length / (self._lambda_factor * 2)) / ratio)

        # Build the waveform array from a full-lambda waveform
        while len(_temporary) < self._table_length:
            _temporary = np.concatenate(
                (
                    _temporary,
                    np.array([0], dtype=np.int16),
                    np.ones(half_lambda - 1, dtype=np.int16) * int(amp_factor),
                    np.array([0], dtype=np.int16),
                    np.ones(half_lambda - 1, dtype=np.int16) * int(-amp_factor),
                )
            )

        # Truncate the temporary array to match table_length
        _temporary = _temporary[: self._table_length]
        return _temporary

    def _triangle_wave(self, ratio, amplitude):
        """Returns a waveform array with a triangle wave waveform proportional
        to the frequency ratio and adjusted to a specified amplitude."""
        amp_factor = min(int(round(self._sample_max * amplitude, 0)), self._sample_max)
        # Create a zero-length temporary array
        _temporary = np.array([], dtype=np.int16)

        # Calculate the sample length of one-quarter lambda
        quarter_lambda = int((self._table_length / (self._lambda_factor * 4)) / ratio)

        # Calculate a one-step increment for even quarter-lambda segments
        increment = int(amp_factor / quarter_lambda)

        # Build the waveform array from a full-lambda waveform
        while len(_temporary) < self._table_length:
            _temporary = np.concatenate(
                (
                    _temporary,
                    np.linspace(
                        0,
                        amp_factor,
                        quarter_lambda,
                        dtype=np.int16,
                    ),
                    np.linspace(
                        amp_factor - increment,
                        0,
                        quarter_lambda,
                        dtype=np.int16,
                    ),
                    np.linspace(
                        0 - increment,
                        -amp_factor,
                        quarter_lambda,
                        dtype=np.int16,
                    ),
                    np.linspace(
                        -amp_factor + increment,
                        0 - increment,
                        quarter_lambda,
                        dtype=np.int16,
                    ),
                )
            )

        # Truncate the temporary array to match table_length
        _temporary = _temporary[: self._table_length]
        return _temporary

    # pylint: disable=consider-using-generator
    # pylint: disable=too-many-branches
    def _update_table(self):
        # Replace frequencies in _oscillators with ratios based on the fundamental
        fundamental_frequency = min([osc[1] for osc in self._oscillators])
        self._oscillators = [
            (t, freq / fundamental_frequency, a) for t, freq, a in self._oscillators
        ]

        self._summed_amplitude = sum([abs(osc[2]) for osc in self._oscillators])
        if self._summed_amplitude > 1.0:
            raise ValueError("Summed amplitude of oscillators exceeds 1.0.")

        # Test each oscillator ratio to confirm that table_length has sufficient resolution
        for overtone in self._oscillators:
            fraction = 1  # Set one lambda for sine and noise wave shapes
            if WaveShape.Square or WaveShape.Saw in overtone[0]:
                fraction = 2  # For one-half lambda
            if WaveShape.Triangle in overtone:
                fraction = 4  # For one-quarter lambda

            if (
                int(
                    (self._table_length / (self._lambda_factor * fraction))
                    / overtone[1]
                )
                < 2
            ):
                # A fractional lambda array must be two elements or larger
                min_length = 2 + (2 * int(self._lambda_factor * fraction * overtone[1]))
                message = f"Increase to {min_length} or larger."
                raise ValueError(
                    f"table_length {self._table_length} is too small for oscillator {overtone}. "
                    + message
                )

        # Add oscillator waveforms to an empty self._waveform wave table array
        self._waveform = np.zeros(self._table_length, dtype=np.int16)
        for wave_type, ratio, amplitude in self._oscillators:
            if wave_type == WaveShape.Noise:
                self._waveform = self._waveform + self._noise_wave(ratio, amplitude)
            if wave_type == WaveShape.Saw:
                self._waveform = self._waveform + self._saw_wave(ratio, amplitude)
            if wave_type == WaveShape.Sine:
                self._waveform = self._waveform + self._sine_wave(ratio, amplitude)
            if wave_type == WaveShape.Square:
                self._waveform = self._waveform + self._square_wave(ratio, amplitude)
            if wave_type == WaveShape.Triangle:
                self._waveform = self._waveform + self._triangle_wave(ratio, amplitude)

        if self._loop_smoothing and (self._waveform[-1] != self._waveform[0]):
            # Reduce loop distortion by smoothing the last 2 elements of the array
            self._waveform[-2] = int((self._waveform[-2] + self._waveform[0]) / 2)
            self._waveform[-1] = self._waveform[0]

        # Calculate loop distortion
        self._loop_distortion = (
            abs(self._waveform[0] - self._waveform[-1]) / self._sample_max * 100
        )

        if self._debug:
            print(f"oscillators: {self._oscillators}")
            print(f"waveform table length: {self._table_length}")
            print(f"sample_max: {self._sample_max}")
            print(f"lambda_factor: {self._lambda_factor}")
            print(f"loop_smoothing: {self._loop_smoothing}")
            print(f"summed_amplitude: {self._summed_amplitude}")
            print(f"loop_distortion: {self._loop_distortion:3.1f}%")
