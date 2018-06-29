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

from gnuradio import gr
from gnuradio import gr_unittest
from gnuradio import blocks
from gnuradio import analog

from crimson_sink_s import crimson_sink_s

import time

class qa_crimson_sink_s(gr_unittest.TestCase):
    """
    Manual Testing Procedure:
        1. Hook up an oscilloscope to the TX channels.
        2. Ensure the signal is a clean sine wave.

    Automatic Testing Procedure:
        1. Ensure the Crimson Sink object can connect to the Crimson.
           eg. Let the test pass on its own without doing the manual testing.

    Hints:
        1. Signal amplitude varies with channel.
        2. Use spectrum analyzer if you are unsure of signal integerity.
    """

    def setUp(self):
        self.test_time = 5.0

    def tearDown(self):
        pass

    def coreTest(self):
        """
                                      +-----------+        
        +---------+    +---------+    |           |
        | sigs[0] |--->| c2ss[0] |--->|ch0        |
        +---------+    +---------+    |           |
        +---------+    +---------+    |           |
        | sigs[1] |--->| c2ss[1] |--->|ch1        |    
        +---------+    +---------+    |           |
        +---------+    +---------+    |           |
        | sigs[2] |--->| c2ss[2] |--->|ch2        |
        +---------+    +---------+    |           |
        +---------+    +---------+    |           |
        | sigs[3] |--->| c2ss[3] |--->|ch3        | 
        +---------+    +---------+    |      csnk |
                                      +-----------+
        """
        tb = gr.top_block()

        # Variables.
        channels = range(4)
        sample_rate = 20e6
        center_freq = 15e6

        wave_freq = 1.0e6
        wave_ampl = [0.5e4, 1.0e4, 1.5e4, 2.0e4]

        # Blocks.
        sigs = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE, wave_freq, wave_ampl[channel], 0.0)
            for channel in channels]

        c2ss = [
            blocks.complex_to_interleaved_short(True)
            for channel in channels]

        csnk = crimson_sink_s(channels, sample_rate, center_freq, 0.0)
    
        # Connections.
        for channel in channels:
            tb.connect(sigs[channel], c2ss[channel])
            tb.connect(c2ss[channel], (csnk, channel))

        # Run.
        tb.start()
        time.sleep(self.test_time)
        tb.stop()
        tb.wait()

    def test_000_t(self):
        self.coreTest()

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_sink_s)
