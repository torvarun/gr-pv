#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Per Vices Corporation.
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
# Boston, MA 02110-1301, USA.
#

import numpy as np
import ChannelMock

class crimson_mock:
    """
    x(t) = A*sin(2*pi*f*t)
    """

    def __init__(self, time=5, num_samples=64, sample_rate=20e6):
        self._amp = 1
        self._freq = 1/(2 * np.pii)
        self._time = time
        self._num_samples = num_samples
        self._sample_rate = sample_rate
        self._vsnk = VsnkMock(4)
        self._num_channels = 4 #Crimson has 4 channels

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


    def __sine_real(self, t):
        """Equation of Wave: In-phase Component"""
        return self._amp * np.sin(2 * np.pi * self._freq * t)

    def __sine_imag(self, t):
        """Equation of Wave: Quadrature Component"""
        # Phase shift of pi/2 radians
        return self._amp * np.sin(2 * np.pi * self._freq * t + np.pi/2)

    def __generate_data(self):
        data = []

        t = self._time / 2
        i = 0
        while len(data) < self._num_samples:
            data[i].real = __sine_real(x)
            data[i].imag = __sine_imag(x)

            t += self._sample_rate
            i++

        return data

    def sample(self):
        vsnk = []

        for x in xrange(self._num_channels):
            vsnk[x] = ChannelMock()

            data = __generate_data()
            vsnk[x].update_data(data)

        return vnsk
