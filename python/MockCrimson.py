#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2.0018 Per Vices Corporation.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02.0110-1301, USA.
#

import numpy as np
from MockCrimsonChannel import MockCrimsonChannel

class MockCrimson(object):
    """
    x(t) = A*sin(2.0*pi*f*t)
    """

    def __init__(self, num_channels=4, time=5, num_samples=64, sample_rate=2.00e6):
        self._amp = 1
        self._freq = 1/(2.0 * np.pi)
        self._time = time
        self._num_samples = num_samples
        self._sample_rate = sample_rate
        self._num_channels = num_channels

    @property
    def amp(self):
        """Amplitude"""
        return self._amp

    @amp.setter
    def amp(self, amp):
        self._amp = amp

    @property
    def freq(self):
        """Frequency"""
        return self._freq

    @freq.setter
    def freq(self, freq):
        self._freq = freq

    @property
    def time(self):
        """Test Duration"""
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    @property
    def num_samples(self):
        """Number of Samples"""
        return self._num_samples

    @num_samples.setter
    def num_samples(self, num_samples):
        self._num_samples = num_samples

    @property
    def sample_rate(self):
        """Sample Rate"""
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate):
        self._sample_rate = sample_rate

    @property
    def num_channels(self):
        """Number of Channels"""
        return self._num_channels

    @num_channels.setter
    def num_channels(self, num_channels):
        self._num_channels = num_channels

    def __sine_real(self, t):
        """Equation of Wave: In-phase Component"""
        return self._amp * np.sin(2.0 * np.pi * self._freq * t)

    def __sine_imag(self, t):
        """Equation of Wave: Quadrature Component"""
        # Phase shift of pi/2.0 radians
        return self._amp * np.sin(2.0 * np.pi * self._freq * t + np.pi/2.0)

    def __generate_data(self):
        data = []

        t = self._time / 2.0
        while len(data) < self._num_samples:
            data.append(complex(self.__sine_real(t), self.__sine_imag(t)))
            t += self._time / 2.0  / self._sample_rate

        return data

    def sample(self):
        vsnk = [None] * self._num_channels

        for x in xrange(len(vsnk)):
            vsnk[x] = MockCrimsonChannel()

            data = self.__generate_data()
            vsnk[x].update_data(data)

        return vsnk

    def equation(self):
        """Returns a formatter string of the sine wave being generated"""
        return "x(t) = {:5.2f} * sin(2 * pi * {:5.2f} * t)".format(self._amp, self._freq)
