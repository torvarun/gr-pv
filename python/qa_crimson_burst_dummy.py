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

from numpy import arange

class qa_crimson_flow(gr_unittest.TestCase):
    """
    - Dumb class that shouldn't need to exist but does because GRC isn't polite.
    - GRC sends overlfow and underflow errors to the stderr instead of throwing them.
    - With Python's lack of ability to read the stderr, this standalone test is needed.
    - This will be executed in a subprocess from the main loopback thread, and the stderr of that subprocess is caputred for processing.
    - Since the higher level test in qa_crimson_loopback.py expects a failure, this works decently (albeit in an ugly manner).
    """

    def setUp(self):
        """
        Runs before every test is called.
        """

        self.channels = range(4)
        self.test_time = 10.0

    def coreTest(self, rx_gain, tx_amp, centre_freq, sample_rate=20e6):
        """
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

        # Is above 40 MHz, disable Channels C & D
        if centre_freq > 40e6:
            self.channels = range(2)

        tb = gr.top_block()

        # Variables.
        wave_freq = 1e6

        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 64

        # Blocks and Connections (TX CHAIN).
        sigs = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE, wave_freq, tx_amp, 0.0)
            for channel in self.channels]

        c2ss = [
            blocks.complex_to_interleaved_short(True)
            for channel in self.channels]

        csnk = crimson_sink_s(self.channels, sample_rate, centre_freq, 0.0)

        for channel in self.channels:
            tb.connect(sigs[channel], c2ss[channel])
            tb.connect(c2ss[channel], (csnk, channel))

        # Blocks and Connections (RX CHAIN).
        csrc = crimson_source_c(self.channels, sample_rate, centre_freq, rx_gain)

        vsnk = [blocks.vector_sink_c()
            for channel in self.channels]

        for channel in self.channels:
            tb.connect((csrc, channel), vsnk[channel])

        # Reset TX and RX times to be roughly in sync.
        csnk.set_time_now(uhd.time_spec_t(0.0))
        csrc.set_time_now(uhd.time_spec_t(0.0))

        # Issue stream command to start RX chain somewhere in the middle of the test.
        sc.stream_now = False
        sc.time_spec = uhd.time_spec_t(self.test_time / 2.0)
        csrc.issue_stream_cmd(sc)

        # Run the test.
        tb.start()
        time.sleep(self.test_time)
        tb.stop()
        tb.wait()

        # Return a vsnk sample for further processing and verification.
        # vsnk are to be processed in individual unit tests, eg. def test_xyz_t(self):
        # Read sigproc.py for further information on signal processing and vsnks.

        return vsnk, csnk, csrc

    def test_flow(self):
        # Should only fail on the last iteration of the loop
        for sample_rate in arange(20e6, 260e6, 40e6):
            self.coreTest(8.0, 3.0e4, 15e6, sample_rate)

if __name__ == '__main__':
    test_suite = gr_unittest.TestSuite()
    test_suite.addTest(qa_crimson_flow('test_flow'))
    gr_unittest.TextTestRunner(verbosity=0).run(test_suite)
