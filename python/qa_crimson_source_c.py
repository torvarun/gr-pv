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
from gnuradio import uhd
from gnuradio import blocks
from crimson_source_c import crimson_source_c

import time
import sys
import sigproc

class qa_crimson_source_c(gr_unittest.TestCase):
    """
    Manual Testing Procedure:
        1. Hook up a signal generator to the RX channels.
        2. Generate a 1MHz sine wave.
        3. Receive and print the signal to stdout. Plot it.
        4. Ensure the signal is clean.
        5. Ensure the number of collected samples matches the
           the specified number of samples (this part is automatic).

    Automatic Testing Procedure:
        1. Ensure the Crimson Source object connects to the Crimson.
           eg. Let the test pass on its own without doing the manual testing.

    Hints:
        1. Run this test from the build folder.
           Using `make test` will pipe stdout to /dev/null.
    """

    def setUp(self):
        self.test_time = 5.0

    def tearDown(self):
        pass

    def coreTest(self):
        """
        +-----------+
        |           |    +---------+
        |        ch0|--->| vsnk[0] |
        |           |    +---------+
        |           |    +---------+
        |        ch1|--->| vsnk[1] |    
        |           |    +---------+
        |           |    +---------+
        |        ch2|--->| vsnk[2] |
        |           |    +---------+
        |           |    +---------+
        |        ch3|--->| vsnk[3] | 
        | csrc      |    +---------+
        +-----------+
        """
        tb = gr.top_block()

        # Variables.
        channels = range(4)
        sample_rate = 20e6
        center_freq = 15e6
        gain = 1.0

        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 32

        # Blocks.
        csrc = crimson_source_c(channels, sample_rate, center_freq, gain)

        vsnk = [blocks.vector_sink_c() for channel in channels]

        # Connections.
        for channel in channels:
            tb.connect((csrc, channel), vsnk[channel])

        # Issue stream command to start right away.
        sc.stream_now = True
        csrc.issue_stream_cmd(sc)

        # Run the test.
        tb.start()
        time.sleep(self.test_time)
        tb.stop()
        tb.wait()

        # Check to see if sample size matches.
        for channel in channels:
            self.assertEqual(len(vsnk[channel].data()), sc.num_samps)

        return vsnk

    def test_000_t(self):
        vsnk = self.coreTest()
        sigproc.dump(vsnk)

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_source_c)
