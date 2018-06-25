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

from gnuradio import gr
from gnuradio import gr_unittest
from gnuradio import uhd
from gnuradio import blocks
from crimson_source_c import crimson_source_c
from time import sleep

import util

class qa_crimson_source_c(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_t(self):

        # Test parameters.
        channels = [0, 1, 2, 3]
        samp_rate = 20e6
        center_freq = 15e6
        gain = 1.0
        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 512
        sc.stream_now = True

        # Blocks.
        csrc_c = crimson_source_c(channels, samp_rate, center_freq, gain)
        vsnk_c = [blocks.vector_sink_c() for sink in channels]

        # Connections.
        # +----------+       +-----------+
        # |       ch0|------>| vsnk_c[0] |
        # |          |       +-----------+
        # |          |    
        # |          |       +-----------+
        # |       ch1|------>| vsnk_c[1] |
        # |          |       +-----------+
        # |  csrc_c  |    
        # |          |       +-----------+
        # |       ch2|------>| vsnk_c[2] |
        # |          |       +-----------+
        # |          |    
        # |          |       +-----------+
        # |       ch3|------>| vsnk_c[3] |
        # +----------+       +-----------+
        for channel in channels:
            self.tb.connect((csrc_c, channel), vsnk_c[channel])

        # Run.
        csrc_c.issue_stream_cmd(sc)
        self.tb.start()
        sleep(5.0)
        self.tb.stop()

        # Dump.
        util.dump(vsnk_c, channels, sc.num_samps)

        # Verify.
        for channel in channels:
            self.assertEqual(len(vsnk_c[channel].data()), sc.num_samps)

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_source_c)
