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

"""
sigproc (Signal Processor) performs operations on vsnks (Vector Sinks).

vsnks contain channel data in complex format.
To access a vsnk's channel data:
    vsnk[channel].data()

To access a specific sample:
    vsnk[channel].data()[sample].

The value `sample` must be within the number of samples of the channel.
To determine the number of samples of a channel:
    xrange(len(vsnk[channel].data())

Assume all channels have an equal sample size. The number of
channels can be inferred by doing:
    xrange(len(vsnk))
"""

import sys

def dump(vsnk):
    """
    Prints a vsnk in channel column layout in IQ format for all channels.
    """

    for sample in xrange(len(vsnk[0].data())):
        for channel in xrange(len(vsnk)):

            datum = vsnk[channel].data()[sample]
            sys.stdout.write("%10.5f %10.5f\t" % (datum.real, datum.imag))

        sys.stdout.write("\n")
