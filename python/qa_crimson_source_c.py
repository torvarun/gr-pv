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
# the Free Software Foundation, Inc., 51 Franklin Street, # Boston, MA 02110-1301, USA.  #

from gnuradio import gr
from gnuradio import gr_unittest
from gnuradio import uhd
from gnuradio import blocks
from crimson_source_c import crimson_source_c

import time
import sys
import util

class qa_crimson_source_c(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_t(self):
        """
        Test Type:
            Manual.

        Procedure:
            1. Hook up a signal generator to the RX channels.
            2. Generate a 1MHz sine wave.
            3. Receive and print the signal to stdout. Plot it.
            4. Ensure the signal is clean.
            5. Ensure the number of collected samples matches the
               the specified number of samples (this part is automatic).

        Hints:
            1. Run this test from the build folder.
               Using `make test` will pipe stdout to /dev/null.

        Flow Diagram:
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

        # Variables.
        channels = [0, 1, 2, 3]
        sample_rate = 20e6
        center_freq = 15e6
        gain = 1.0
        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 512
        sc.stream_now = True

        # Blocks.
        csrc = crimson_source_c(channels, sample_rate, center_freq, gain)

        vsnk = [blocks.vector_sink_c() for channel in channels]

        # Connections.
        for channel in channels:
            self.tb.connect((csrc, channel), vsnk[channel])

        # Run
        csrc.issue_stream_cmd(sc)
        self.tb.start()
        time.sleep(5.0)
        self.tb.stop()
        self.tb.wait()

        # Print.
        util.dump(vsnk)

        # Sample match check.
        for channel in channels:
            self.assertEqual(len(vsnk[channel].data()), sc.num_samps)

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_source_c)
