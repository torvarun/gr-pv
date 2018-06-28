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
#

import sys

def dump(vsnk):

    channels = xrange(len(vsnk))
    samples = xrange(len(vsnk[0].data()))

    for s in samples: 
        for c in channels:
            sample = vsnk[c].data()[s]
            sys.stdout.write("%10.5f %10.5f\t" % (sample.real, sample.imag))
        sys.stdout.write("\n")
