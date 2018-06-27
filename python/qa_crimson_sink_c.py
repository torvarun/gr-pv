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
from crimson_sink_c import crimson_sink_c
from time import sleep
from threading import Thread

import util

class qa_crimson_sink_c(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def kill(self):
        sleep(20.0)
        self.tb.stop()

    def test_001_t(self):

        """ Test Parameters """
        channels = [0]
        samp_rate = 52e6
        center_freq = 15e6
        gain = 5.0
        
        """ Blocks and Connections """
        #                  +---------+
        # +--------+       |         |      +--------+
        # | ssrc_c |------>| s2ts_cc |----->| csnk_c |
        # +--------+       |         |      +--------+
        #                  +---------+

        # Signal Source (Complex).
        ssrc_c = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 10e6, 1.0, 0)

        # Stream to Tagged Stream (Complex to Complex).
        s2ts_cc = blocks.stream_to_tagged_stream(8, 1, 1024, "packet_len")

        # Crimson Sink (Complex).
        csnk_c = uhd.usrp_sink(
            uhd.device_addr_t(""),
            uhd.stream_args(
                cpu_format = "fc32",
                otw_format = "sc16",
                channels = channels),
            "packet_len")
        csnk_c.set_samp_rate(samp_rate)
        csnk_c.set_center_freq(center_freq)
        csnk_c.set_gain(gain)
        csnk_c.set_time_now(uhd.time_spec_t(0.0))

        # Connections.
        self.tb.connect(ssrc_c, s2ts_cc)
        self.tb.connect(s2ts_cc, csnk_c)

        """ Run """
        Thread(target = self.kill).start()
        self.tb.start()
        self.tb.wait()

        """ Verify """
        pass

if __name__ == '__main__':
    gr_unittest.run(qa_crimson_sink_c)
