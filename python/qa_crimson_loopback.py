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
from gnuradio import uhd

from crimson_source_c import crimson_source_c
from crimson_sink_s import crimson_sink_s

import time
import util

class qa_crimson_loopback(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_000_t(self):
        """
        Test Type:
            Manual.

        Procedure:
            1. Connect TX channels to corresponding RX channels
               for all channels.
            2. Verify that a sinewave is printed for all channels.

        Hints:
            1. Be sure to use the attenuator on the RX else the RX channel
               will be damaged with (potential) high TX channel gain.
            2. Running `make test` will not print test output so run this
               test individually to get printings.

        Flow Diagram:
            |<------------ TX CHAIN ---------->| |<----- RX CHAIN ---->|
                                        +------+ +------+
            +--------+    +--------+    |      | |      |    +---------+
            | sig[0] |--->| c2s[0] |--->|ch0   | |   ch0|--->| vsnk[0] |
            +--------+    +--------+    |      | |      |    +---------+
            +--------+    +--------+    |      | |      |    +---------+
            | sig[1] |--->| c2s[1] |--->|ch1   | |   ch1|--->| vsnk[1] | 
            +--------+    +--------+    |      | |      |    +---------+
            +--------+    +--------+    |      | |      |    +---------+
            | sig[2] |--->| c2s[2] |--->|ch2   | |   ch2|--->| vsnk[2] |
            +--------+    +--------+    |      | |      |    +---------+
            +--------+    +--------+    |      | |      |    +---------+
            | sig[3] |--->| c2s[3] |--->|ch3   | |   ch3|--->| vsnk[3] | 
            +--------+    +--------+    | csnk | | csrc |    +---------+
                                        +------+ +------+
        """
    
        # Variables.
        channels = [0, 1, 2, 3]
        sample_rate = 20e6
        center_freq = 15e6
        gain = 10.0

        wave_freq = 1.0e6
        wave_ampl = [0.5e4, 1.0e4, 1.5e4, 2.0e4]
        wave_complex_offset = 0

        test_time = 5.0

        # Blocks and Connections (TX CHAIN).
        sig = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE,
                wave_freq,
                wave_ampl[channel],
                wave_complex_offset)
            for channel in channels]

        c2s = [
            blocks.complex_to_interleaved_short(True)
            for channel in channels]

        csnk = crimson_sink_s(
            channels, sample_rate, center_freq, gain)

        for channel in channels:
            self.tb.connect(sig[channel], c2s[channel])
            self.tb.connect(c2s[channel], (csnk, channel))

        # Blocks and Connections (RX CHAIN).
        csrc = crimson_source_c(
            channels, sample_rate, center_freq, gain)

        vsnk = [blocks.vector_sink_c()
            for channel in channels]

        for channel in channels:
            self.tb.connect((csrc, channel), vsnk[channel])

        # Reset TX and RX times to be roughly in sync.
        csnk.set_time_now(uhd.time_spec_t(0.0))
        csrc.set_time_now(uhd.time_spec_t(0.0))

        # Issue the stream command.
        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 128
        sc.stream_now = False
        sc.time_spec = uhd.time_spec_t(test_time / 2.0)
        csrc.issue_stream_cmd(sc)

        # Run the test.
        self.tb.start()
        time.sleep(test_time)
        self.tb.stop()
        self.tb.wait()

        # Print RX results.
        util.dump(vsnk)

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_loopback)
