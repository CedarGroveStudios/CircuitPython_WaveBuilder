# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_wavetile`
===============================================================================
A CircuitPython class to create a ``displayio.Group`` graphic object from a
``synthio.ReadableBuffer`` composite wave table object. The class also makes
the underlying bitmap object available as a property.
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
import bitmaptools


class WaveTile(displayio.Group):
    """
    The WaveTile class creates a displayio.Group from a composite
    ``synthio`` waveform table. The group is created from size and color parameters.

    :param synthio.ReadableBuffer wave_table: The synthio waveform object of type 'h'
    (signed 16-bit). No default.
    :param tuple origin: The group's origin coordinate integer tuple value (x, y). The
    origin is the top left corner of the resultant group. No default.
    :param tuple size: The group size integer tuple value (width, height) in pixels.
    No default.
    :param integer plot_color: The waveform trace color. Defaults to 0x00FF00 (green).
    :param integer grid_color: The perimeter grid color. Defaults to 0x808080 (gray).
    :param integer back_color: The grid background color. Defaults to None (transparent).
    :param integer scale: The group scale factor. Defaults to 1.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        wave_table,
        origin,
        size,
        plot_color=0x00FF00,
        grid_color=0x808080,
        back_color=None,
        scale=1,
    ):
        """Instantiate the tile generator class."""
        self._wave_table = wave_table
        self._origin = origin
        self._size = size
        self._scale = scale

        self._palette = displayio.Palette(3)
        self._palette[1] = plot_color
        self._palette[2] = grid_color
        if back_color is None:
            self._palette[0] = 0x000000
            self._palette.make_transparent(0)

        # Instantiate the target bitmap
        self._bmp = displayio.Bitmap(self._size[0], self._size[1], len(self._palette))

        # self becomes a displayio.Group; plot grid and wave table
        super().__init__(scale=self._scale, x=self._origin[0], y=self._origin[1])
        self._plot_grid()  # Plot the grid
        self._plot_wave()  # Plot the wave table
        self._tile_grid = displayio.TileGrid(self._bmp, pixel_shader=self._palette)
        self.append(self._tile_grid)

    @property
    def wave_table(self):
        """The synthio waveform object of type 'h' (signed 16-bit). No default."""
        return self._wave_table

    @wave_table.setter
    def wave_table(self, new_wave_table):
        self._wave_table = new_wave_table
        self._plot_grid()
        self._plot_wave()

    @property
    def wave_bitmap(self):
        """The wave table plot bitmap."""
        return self._bmp

    def _plot_wave(self):
        """Plot the wave_table as a bitmap."""
        samples = len(self._wave_table)
        max_value = max(abs(min(self._wave_table)), abs(max(self._wave_table)))
        scale_y = self._size[1] / max_value / 2

        self._prev_point = (0, 0)  # (display x index, wave_table index)

        for x in range(0, self._size[0]):
            table_index = int(x * (samples / self._size[0]))
            self._next_point = (x, table_index)

            bitmaptools.draw_line(
                self._bmp,
                self._prev_point[0],
                (self._size[1] // 2)
                + (-int(round(self._wave_table[self._prev_point[1]] * scale_y, 0))),
                self._next_point[0],
                (self._size[1] // 2)
                + (-int(round(self._wave_table[self._next_point[1]] * scale_y, 0))),
                1,
            )

            self._prev_point = self._next_point

        # Always plot the final point
        bitmaptools.draw_line(
            self._bmp,
            self._prev_point[0],
            (self._size[1] // 2)
            + (-int(round(self._wave_table[self._prev_point[1]] * scale_y, 0))),
            self._next_point[0],
            (self._size[1] // 2) + (-int(round(self._wave_table[-1] * scale_y, 0))),
            1,
        )

    def _plot_grid(self):
        """Plot the grid lines as a bitmap."""
        bitmaptools.draw_line(
            self._bmp,
            0,
            0,
            self._size[0] - 1,
            0,
            2,
        )
        bitmaptools.draw_line(
            self._bmp,
            self._size[0] - 1,
            0,
            self._size[0] - 1,
            self._size[1] - 1,
            2,
        )
        bitmaptools.draw_line(
            self._bmp,
            self._size[0] - 1,
            self._size[1] - 1,
            0,
            self._size[1] - 1,
            2,
        )
        bitmaptools.draw_line(
            self._bmp,
            0,
            self._size[1] - 1,
            0,
            0,
            2,
        )
        bitmaptools.draw_line(
            self._bmp,
            0,
            self._size[1] // 2,
            self._size[0],
            self._size[1] // 2,
            2,
        )
