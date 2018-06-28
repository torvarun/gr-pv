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

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_000_t(self):
        """
        Test Type:
            Manual.

        Procedure:
            1. Hook up an oscilloscope to the TX channels.
            2. Ensure the signal is a clean sine wave.

        Hints:
            1. Signal amplitude varies with channel.
            2. Use spectrum analyzer if you are unsure of signal integerity.

        Flow Diagram:
                                        +-----------+        
            +--------+    +--------+    |           |
            | sig[0] |--->| c2s[0] |--->|ch0        |
            +--------+    +--------+    |           |
            +--------+    +--------+    |           |
            | sig[1] |--->| c2s[1] |--->|ch1        |    
            +--------+    +--------+    |           |
            +--------+    +--------+    |           |
            | sig[2] |--->| c2s[2] |--->|ch2        |
            +--------+    +--------+    |           |
            +--------+    +--------+    |           |
            | sig[3] |--->| c2s[3] |--->|ch3        | 
            +--------+    +--------+    |      csnk |
                                        +-----------+
        """

        # Variables.
        sample_rate = 52e6
        center_freq = 15e6
        channels = [0, 1, 2, 3]
        gain = 0.0

        wave_freq = 1.0e6
        wave_ampl = [0.5e4, 1.0e4, 1.5e4, 2.0e4]
        wave_complex_offset = 0

        # Blocks.
        sig = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE,
                wave_freq,
                wave_ampl[channel],
                wave_complex_offset)
            for channel in channels]

        c2s = [
            blocks.complex_to_interleaved_short(True)
            for channel in channels]

        csnk = crimson_sink_s(channels, sample_rate, center_freq, gain)
    
        # Connections.
        for channel in channels:
            self.tb.connect(sig[channel], c2s[channel])
            self.tb.connect(c2s[channel], (csnk, channel))

        # Run.
        self.tb.start()
        time.sleep(5.0)
        self.tb.stop()
        self.tb.wait()

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_sink_s)
