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
 ____  __  ___  ____  ____   __    ___
/ ___)(  )/ __)(  _ \(  _ \ /  \  / __)
\___ \ )(( (_ \ ) __/ )   /(  O )( (__
(____/(__)\___/(__)  (__\_) \__/  \___)

SigProc (Signal Processor) performs operations on vsnks (Vector Sinks).

vsnk layout:

     ch[0]   ch[0]   ...  ch[n]
    -----------------------------
     a + bi  a + bi  ...  a + bi             
     a + bi  a + bi  ...  a + bi             
     a + bi  a + bi  ...  a + bi             
     a + bi  a + bi  ...  a + bi             

Each channel column holds a complex number sample.

"""

import sys
import numpy
import math
from scipy import fftpack

def absolute_area(vsnk):
    """
    Returns the aboslute area of a vsnk as the modulous of the complex number.
    """
    areas = []
    for channel in xrange(len(vsnk)):
        absolute = numpy.absolute(vsnk[channel].data())
        integral = numpy.trapz(absolute)

        # abs(complex) is complex modulous
        areas.append(abs(integral))

    return areas

def dump(vsnk):
    """
    Prints a vsnk in channel column layout in IQ format for all channels.
    """
    for sample in xrange(len(vsnk[0].data())):

        for channel in xrange(len(vsnk)):
            datum = vsnk[channel].data()[sample]
            sys.stdout.write("%10.5f %10.5f\t" % (datum.real, datum.imag))
        sys.stdout.write("\n")

    # For extra separation.
    sys.stdout.write("\n")
