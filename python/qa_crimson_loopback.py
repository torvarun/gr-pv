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
import sigproc

class qa_crimson_loopback(gr_unittest.TestCase):
    """
    Manual Testing Procedure:
        1. Connect TX channels to corresponding RX channels
           for all channels.
        2. Verify that a sinewave is printed for all channels.
        3. Verify change in iteration parameters affects output.

    Hints:
        1. Be sure to use the attenuator on the RX else the RX channel
           will be damaged with (potential) high TX channel gain.
        2. Running `make test` will not print test output so run this
           test individually to get printings.
        3. Only one connector and attenuator may be available. If so,
           manually test each channel one after another.
    """

    def setUp(self):
        self.test_time = 5.0

    def tearDown(self):
        pass

    def coreTest(self, rx_gain, tx_amp):
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
        tb = gr.top_block()

        # Variables.
        channels = range(4)
        sample_rate = 20e6
        center_freq = 15e6
        wave_freq = 1e6

        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 32

        # Blocks and Connections (TX CHAIN).
        sigs = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE, wave_freq, tx_amp, 0.0)
            for channel in channels]

        c2ss = [
            blocks.complex_to_interleaved_short(True)
            for channel in channels]

        csnk = crimson_sink_s(channels, sample_rate, center_freq, 0.0)

        for channel in channels:
            tb.connect(sigs[channel], c2ss[channel])
            tb.connect(c2ss[channel], (csnk, channel))

        # Blocks and Connections (RX CHAIN).
        csrc = crimson_source_c(channels, sample_rate, center_freq, rx_gain)

        vsnk = [blocks.vector_sink_c()
            for channel in channels]

        for channel in channels:
            tb.connect((csrc, channel), vsnk[channel])

        # Reset TX and RX times to be roughly in sync.
        csnk.set_time_now(uhd.time_spec_t(0.0))
        csrc.set_time_now(uhd.time_spec_t(0.0))

        # Issue the stream command to start somewhere in the middle of the test.
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
        return vsnk

    if True: # Change this flag from True to False to switch between debug and full testing.
        """
        Quick test for debugging.
        """
        def test_000_t(self):
            vsnk = self.coreTest(8.0, 2.0e4)
            sigproc.dump(vsnk)

    else:
        """
        All tests with varying iterdata.
        """
        def test_001_t(self):
            for rx_gain in [2.0, 4.0, 6.0, 8.0, 10.0]:
                vsnk = self.coreTest(rx_gain, 2.0e4)
                sigproc.dump(vsnk)
    
        def test_002_t(self):
            for tx_amp in [1.0e4, 1.5e4, 2.0e4, 2.5e4, 3.0e4]:
                vsnk = self.coreTest(10.0, tx_amp)
                sigproc.dump(vsnk)

        # Fill in these tests as time goes on.
        def test_003_t(self):
            pass

        def test_004_t(self):
            pass

        def test_005_t(self):
            pass
    
if __name__ == '__main__':
    gr_unittest.run(qa_crimson_loopback)
