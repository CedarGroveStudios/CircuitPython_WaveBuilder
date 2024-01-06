# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_wavetile`
===============================================================================
A CircuitPython class to create a ``displayio.Group`` graphic object from a
``synthio.ReadableBuffer`` composite wave table object.
https://github.com/CedarGroveStudios/CircuitPython_WaveBuilder/examples

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------
**Software and Dependencies:**
* ulab for CircuitPython
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line


class WaveTile(displayio.Group):
    """The WaveTile class creates a displayio.Group "tile" from a composite
    ``synthio`` waveform table. The tile is created from size and color parameters.

    :param synthio.ReadableBuffer wave_table: The synthio waveform object of type 'h'
    (signed 16-bit). No default.
    :param tuple origin: The tile's origin coordinate integer value (x, y). The
    origin is where the x-axis and y-axis cross at the middle left side of the tile.
    No default.
    :param tuple size: The tile size (width, height) integer value in pixels.
    No default.
    :param integer plot_color: The waveform trace color. Defaults to 0x00FF00 (green).
    :param integer grid_color: The perimeter grid color. Defaults to 0x808080 (gray).
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, wave_table, origin, size, plot_color=0x00FF00, grid_color=0x808080
    ):
        """Instantiate the tile generator class."""
        self._wave_table = wave_table
        self._origin = origin
        self._size = size
        self._colors = [plot_color, grid_color]
        self._next_point = (0, 0)  # Initialize the first point in the wave plot

        super().__init__()  # self becomes a displayio.Group
        self._plot_grid()  # Plot the grid
        self._plot_wave()  # Plot the wave

    @property
    def wave_table(self):
        """The synthio waveform object of type 'h' (signed 16-bit). No default."""
        return self._wave_table

    @wave_table.setter
    def wave_table(self, new_wave_table):
        self._wave_table = new_wave_table
        self._plot_grid()
        self._plot_wave()

    def _plot_wave(self):
        """Plot the wave_table using a series of displayio.Line objects."""
        samples = len(self._wave_table)
        max_value = max(abs(min(self._wave_table)), abs(max(self._wave_table)))
        scale_y = self._size[1] / max_value / 2

        self._prev_point = (0, 0)  # (display x index, wave_table index)

        for x in range(0, self._size[0]):
            table_index = int(x * (samples / self._size[0]))
            self._next_point = (x, table_index)

            self.append(
                Line(
                    self._prev_point[0] + self._origin[0],
                    self._origin[1]
                    + (-int(self._wave_table[self._prev_point[1]] * scale_y)),
                    self._next_point[0] + self._origin[0],
                    self._origin[1]
                    + (-int(self._wave_table[self._next_point[1]] * scale_y)),
                    self._colors[0],
                )
            )
            self._prev_point = self._next_point

        # Always plot the final point
        self.append(
            Line(
                self._prev_point[0] + self._origin[0],
                self._origin[1]
                + (-int(self._wave_table[self._prev_point[1]] * scale_y)),
                self._next_point[0] + self._origin[0],
                self._origin[1] + (-int(self._wave_table[-1] * scale_y)),
                self._colors[0],
            )
        )

    def _plot_grid(self):
        """Plot the window grid lines."""
        self.append(
            Rect(
                self._origin[0],
                self._origin[1] - (self._size[1] // 2),
                self._size[0],
                self._size[1],
                outline=self._colors[1],
            )
        )
        self.append(
            Line(
                self._origin[0],
                self._origin[1],
                self._origin[0] + self._size[0],
                self._origin[1],
                self._colors[1],
            )
        )
