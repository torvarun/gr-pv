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

from gnuradio import uhd

def crimson_sink_c(channels, samp_rate, center_freq, gain):
    """
    Connects to the crimson and returns a complex sink object.
    """
    sink = uhd.usrp_sink(
        uhd.device_addr_t(""),
        uhd.stream_args(
            cpu_format = "fc32",
            otw_format = "sc16",
            channels = channels), "")
    sink.set_samp_rate(samp_rate)
    sink.set_center_freq(center_freq)
    sink.set_gain(gain)
    sink.set_time_now(uhd.time_spec_t(0.0))
    return sink
