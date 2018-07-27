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
import numpy as np

from log import log
from MockCrimson import MockCrimson

class qa_crimson_loopback(gr_unittest.TestCase):
    """
    Hints:
        1. Be sure to use the attenuator on the RX else the RX channel
           will be damaged with (potential) high TX channel gain.

        2. Running `make test` will not print test output so run this
           test individually to get printings.

        3. When developing, set the IS_DEV flag to true and change the
           name of the test being developed to run it in isolation.

    Testing Requirements:

        1. Channel Independence:
            All settings must be able to be changed independently.

        2. Channel to Channel Consistency:
            All channels must behave the same.

        3. Channel Repeatability:
            Channels must behave the same across multiple runs.

    Issue 4698.
    """

    def setUp(self):
        """
        Runs before every test is called.
        """

        # Flag to mock the vsnk or not
        self._TO_MOCK = False

        self.channels = range(4)

        # In seconds.
        self.test_time = 5.0

        # Extra white space for test seperation.
        print ""

    def coreTest(self, rx_gain, tx_amp, centre_freq):
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
        sample_rate = 40e6 #260e6 is the max
        wave_freq = 1e6

        sc = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        sc.num_samps = 64

        if not self._TO_MOCK:

            # Blocks and Connections (TX CHAIN).
            sigs = [
                analog.sig_source_c(sample_rate, analog.GR_SIN_WAVE, wave_freq, tx_amp, 0.0)
                for channel in self.channels]

            c2ss = [
                blocks.complex_to_interleaved_short(True)
                for channel in self.channels]

            csnk = crimson_sink_s(self.channels, sample_rate, centre_freq, 0.0)

            for channel in self.channels:
                tb.connect(sigs[channel], c2ss[channel])
                tb.connect(c2ss[channel], (csnk, channel))

            # Blocks and Connections (RX CHAIN).
            csrc = crimson_source_c(self.channels, sample_rate, centre_freq, rx_gain)

            vsnk = [blocks.vector_sink_c()
                for channel in self.channels]

            for channel in self.channels:
                tb.connect((csrc, channel), vsnk[channel])

            # Reset TX and RX times to be roughly in sync.
            csnk.set_time_now(uhd.time_spec_t(0.0))
            csrc.set_time_now(uhd.time_spec_t(0.0))

            # Issue stream command to start RX chain somewhere in the middle of the test.
            sc.stream_now = False
            sc.time_spec = uhd.time_spec_t(self.test_time / 2.0)
            csrc.issue_stream_cmd(sc)

            # Run the test.
            tb.start()
            time.sleep(self.test_time)
            tb.stop()
            tb.wait()

            # Return a vsnk sample for further processing and verification.
            # vsnk are to be processed in individual unit tests, eg. def test_xyz_t(self):
            # Read sigproc.py for further information on signal processing and vsnks.

            return vsnk, csnk, csrc

        else:
            crimson = MockCrimson(self.test_time, sc.num_samps, sample_rate)
            #crimson.amp = tx_amp
            crimson.freq = centre_freq
            print crimson.equation()
            vsnk = crimson.sample()
            return vsnk, None, None #Match tuple
    #-----------------------------------------------------------------------------------#

    def test_001_t(self):
        """Trigger"""

        vsnk = self.coreTest(8.0, 3.0e4, 15e6)[0]
        sigproc.dump(vsnk)

        print "done test"

        pass

    def test_002_t(self):
        """Flow Control"""

        pass

    def test_003_t(self):
        """Phase Coherency"""

        pass

    def test_004_t(self):
        """Start of Burst"""

        pass

    def test_005_t(self):
        """Set and Get"""

        #vsnk, csnk, csrc = self.coreTest(10,5e3,15e6)

        # Does not work
        #for ch in self.channels:
        #    log.info("Channel: %1d Gain: %.2f dB" % (ch, 1.0))

        #    csnk.set_gain(1.0, ch)
        #    log.info("%.2f | %.2f" % (1.0, csnk.get_gain(ch)))
        #    #self.assertEqual(1.0, csnk.get_gain(ch))

        pass


    def test_006_t(self):
        """Gain (Low and High Band): Subtask 4700"""

        # For each centre frequency, sweep the TX Gain.
        for centre_freq in np.arange(10e6, 4e9, 20e6):

            log.info("%.2f Hz" % centre_freq)

            areas = []
            peaks = []

            for tx_amp in np.arange(5e3, 30e3, 1.0e3):

                vsnk = self.coreTest(# High band requires stronger reception when centre_freq is greater 120 Mhz.
                    30.0 if centre_freq > 120e6 else 10.0,
                    tx_amp,
                    centre_freq)[0]

                sigproc.dump(vsnk)

                area = sigproc.absolute_area(vsnk)
                peak = sigproc.channel_peaks(vsnk)

                areas.append(area)
                peaks.append(peak)

            # Transpose to defragment channel data.
            areas = np.array(areas).T.tolist()
            peaks = np.array(peaks).T.tolist()

            # Print.
            log.info("Absolute Areas")
            for ch, area in enumerate(areas):
                log.info("ch[%d]: %r" % (ch, np.around(area, decimals = 4)))

            #log.info("Channel Peaks")
            #for ch, peak in enumerate(peaks):
            #    log.info("ch[%d]: %r" % (ch, np.around(peak, decimals = 4)))

            # Verify areas are increasing (just check if list if sorted).
            for area in areas:
                self.assertEqual(area, sorted(area))

            # Verify peaks are increasing (just check if list is sorted)
            #for peak in peaks:
            #    self.assertEqual(peak, sorted(peak))

    def test_007_t(self):
        """Phase Difference: Subtask 4812"""

        for centre_freq in np.arange(15e6, 4e9, 100e6):

            log.info("%.2f Hz" % centre_freq)

            #3 iterations at each centre frequency
            for x in xrange(0,3):
                vsnk = self.coreTest(8.0, 3.0e4, centre_freq)[0]

                diffs = sigproc.phase_diff(vsnk)

                # Check that all the list values are within 10%
                for diff in xrange(1, len(diffs)):
                    #Calculate the percent difference relative to phase diff of channels A and B
                    percent = np.abs(diffs[0] - diffs[diff]) / diffs[0]
                    self.assertLessEqual(percent, 0.1)

    def test_008_t(self):
        """Channel Repeatability"""

        data = []

        # 10 runs and store the vsnk data
        for x in xrange(10):
            vsnk = self.coreTest(8.0, 3.0e4, 15e6)[0]
            runs = sigproc.to_mag(vsnk)
            data.append(runs)

        # Compare the channels to the first one. Make sure they are within +/-0.05
        for run in xrange(1, len(data)):
            for channel in xrange(len(data[0])):
                self.assertTrue(np.allclose(data[0][channel], data[run][channel], 0.05, 0.05))

if __name__ == '__main__':

    crimson_test_suite  = gr_unittest.TestSuite()

    # Flag for test development
    IS_DEV = False

    if IS_DEV:
        # Runs only the specified test in isolation
        crimson_test_suite.addTest(qa_crimson_loopback('test_001_t'))
    else:
        crimson_test_suite  = gr_unittest.TestLoader().loadTestsFromTestCase(qa_crimson_loopback)

    gr_unittest.TextTestRunner(verbosity=2).run(crimson_test_suite)
