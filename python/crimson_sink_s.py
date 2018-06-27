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

def crimson_sink_s(channels, sample_rate, center_freq, gain):
    """
    Connects to the crimson and returns a sink object expecting interleaved
    shorts of complex data.
    """

    usrp_sink = uhd.usrp_sink(
        "crimson",
        uhd.stream_args(cpu_format="sc16", otw_format="sc16", channels=channels))   

    usrp_sink.set_samp_rate(sample_rate)
    usrp_sink.set_clock_source("internal")

    for channel in channels:
        usrp_sink.set_center_freq(center_freq, channel)
        usrp_sink.set_gain(gain, channel)

    usrp_sink.set_time_now(uhd.time_spec_t(0.0))

    return usrp_sink
