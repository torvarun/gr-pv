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
from crimson_sink_c import crimson_sink_c
from time import sleep

class qa_crimson_sink_c(gr_unittest.TestCase):

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
        
        # Blocks.
        csnk_c = crimson_sink_c(channels, samp_rate, center_freq, gain)

        # Run.
        self.tb.start()
        sleep(5.0)
        self.tb.stop()

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_sink_c)
