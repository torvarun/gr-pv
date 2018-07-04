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

from crimson_source_c import crimson_source_c
from crimson_sink_s import crimson_sink_s

import time
import sigproc
import sys
import numpy

from log import log

class qa_crimson_loopback(gr_unittest.TestCase):
    """
    Manual Testing Procedure:
        1. Connect TX channels to corresponding RX channels
           for all channels.
        2. Verify that a sinewave is printed for all channels.
        3. Verify change in iteration parameters affects output.

    Hints:
        1. Be sure to use the attenuator on the RX else the RX channel
           will be damaged with (potential) high TX channel gain.
        2. Running `make test` will not print test output so run this
           test individually to get printings.
        3. Only one connector and attenuator may be available. If so,
           manually test each channel one after another.

    Issue 4698.
    """

    def coreTest(self, rx_gain, tx_amp, center_freq):
        """
        |<------------ TX CHAIN ---------->| |<----- RX CHAIN ---->|
                                    +------+ +------+
        +--------+    +--------+    |      | |      |    +---------+
        | sig[0] |--->| c2s[0] |--->|ch0   | |   ch0|--->| vsnk[0] |
        +--------+    +--------+    |      | |      |    +---------+
        +--------+    +--------+    |      | |      |    +---------+
        | sig[1] |--->| c2s[1] |--->|ch1   | |   ch1|--->| vsnk[1] | 
        +--------+    +--------+    |      | |      |    +---------+
        +--------+    +--------+    |      | |      |    +---------+
        | sig[2] |--->| c2s[2] |--->|ch2   | |   ch2|--->| vsnk[2] |
        +--------+    +--------+    |      | |      |    +---------+
        +--------+    +--------+    |      | |      |    +---------+
        | sig[3] |--->| c2s[3] |--->|ch3   | |   ch3|--->| vsnk[3] | 
        +--------+    +--------+    | csnk | | csrc |    +---------+
                                    +------+ +------+
        """
        tb = gr.top_block()

        # Variables.
        sample_rate = 20e6
        wave_freq = 1e6
        test_time = 6.0
        channels = range(1)

        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 32

        # Blocks and Connections (TX CHAIN).
        sigs = [
            analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE, wave_freq, tx_amp, 0.0)
            for channel in channels]

        c2ss = [
            blocks.complex_to_interleaved_short(True)
            for channel in channels]

        csnk = crimson_sink_s(channels, sample_rate, center_freq, 0.0)

        for channel in channels:
            tb.connect(sigs[channel], c2ss[channel])
            tb.connect(c2ss[channel], (csnk, channel))

        # Blocks and Connections (RX CHAIN).
        csrc = crimson_source_c(channels, sample_rate, center_freq, rx_gain)

        vsnk = [blocks.vector_sink_c()
            for channel in channels]

        for channel in channels:
            tb.connect((csrc, channel), vsnk[channel])

        # Reset TX and RX times to be roughly in sync.
        csnk.set_time_now(uhd.time_spec_t(0.0))
        csrc.set_time_now(uhd.time_spec_t(0.0))

        # Issue the stream command to start somewhere in the middle of the test.
        sc.stream_now = False
        sc.time_spec = uhd.time_spec_t(test_time / 2.0)
        csrc.issue_stream_cmd(sc)

        # Run the test.
        tb.start()
        time.sleep(test_time)
        tb.stop()
        tb.wait()

        # Return a vsnk sample for further processing and verification.
        # vsnk are to be processed in individual unit tests, eg. def test_xyz_t(self):
        # Read sigproc.py for further information on signal processing and vsnks.
        return vsnk

    # Quick Debug Testing.
    if False:
        def test_000_t(self):
            vsnk = self.coreTest(8.0, 3.0e4, 15e6)
            sigproc.dump(vsnk)

    # Full Testing.
    else:
        def test_001_t(self):
            """
            Ramps up TX signal amplitude
            """

            for center_freq in numpy.arange(20e6, 500e6, 20e6):

                areas = []
                for tx_amp in numpy.arange(10e3, 30e3, 2.5e3):

                    # High band requires stronger reception if center_freq > 120e6:
                    rx_gain = 30.0 if center_freq > 120e6 else 8.0

                    log.info("center freq %.2f: tx_amp %.2f: rx_gain %.2f" % (center_freq, tx_amp, rx_gain))

                    # Get a vsnk.
                    vsnk = self.coreTest(rx_gain, tx_amp, center_freq)

                    # Process vsnk and get an area list.
                    # An area list contains one average absolute voltage per channel.
                    area = sigproc.absolute_area(vsnk)

                    # Append for later processing.
                    areas.append(area)

                # A list of area lists needs to be tranposed to group up channel data.
                ramps = numpy.array(areas).T.tolist()

                # With each ramp, assert that average absolute voltage numbers increases.
                # A quick way to do this is just to check if the list is sorted.
                for ramp in ramps:
                    log.info(ramp)
                    self.assertEqual(ramp, sorted(ramp))
    
        def test_002_t(self):
            pass

        def test_003_t(self):
            # Phase coherancy high priority.
            pass

        def test_004_t(self):
            pass

        def test_005_t(self):
            pass
    
if __name__ == '__main__':
    gr_unittest.run(qa_crimson_loopback)
