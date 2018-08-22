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
from MockCrimson import MockCrimson
import numpy as np

from log import log
from subprocess import Popen, PIPE
from threading import Timer

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

        # Start with 4 channels. When central frequency cross 40 MHz
        # channels 3 and 4 must be disabled.
        self.channels = range(4)

        # In seconds.
        self.test_time = 5.0

        # Extra white space for test seperation.
        print("")

        self.failures = [] # List of all the failures from a specific unittest

        log.info('{:25}'.format(self.shortDescription()) + " Start")


    def tearDown(self):
        # Log the status of the test
        if self.failures == []:
            log.info('{:25}'.format(self.shortDescription()) + " Pass")
        else:
            # Failure message with relevant info
            log.info('{:25}'.format(self.shortDescription()) +  " Fail\n" + " "*26 + ("\n" + " "*26).join(self.failures))

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

        # Is above 40 MHz, disable Channels C & D
        if centre_freq > 40e6:
            self.channels = range(2)

        tb = gr.top_block()

        # Variables.
        sample_rate = 20e6 #260e6 is the max
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
            crimson = MockCrimson(len(self.channels), self.test_time, sc.num_samps, sample_rate)
            #crimson.amp = tx_amp
            crimson.freq = centre_freq
            #print crimson.equation()

            vsnk = crimson.sample()

            return vsnk, None, None # Match tuple
    #-----------------------------------------------------------------------------------#

    #@unittest.skip("Skipping the debug check test")
    def test_000_t(self):
        """Quick Debug Test"""

        vsnk = self.coreTest(8.0, 3.0e4, 15e6)[0]
        #sigproc.dump(vsnk)

    def test_001_t(self):
        """Trigger"""

        pass

    def test_002_t(self):
        """Channel Independence"""

        pass

    def test_003_t(self):
        """Phase Coherency"""

        for centre_freq in np.arange(15e6, 4e9, 25e6):
            log.debug("%.2f Hz" % centre_freq)

            runs = []

            # Run 3 iterations at each centre frequency
            for x in xrange(3):
                vsnk = self.coreTest(8.0, 3.0e4, centre_freq)[0]
                #sigproc.dump(vsnk)

                runs.append(vsnk)

            for channel in xrange(len(runs[0])):
                # Find phase shift of the channel between runs
                # Format: phase_diff = [diff(0,1), diff(0,2)]
                phase_diff = sigproc.phase_diff([row[channel] for row in runs])
                log.debug(phase_diff)

                try:
                    self.assertLessEqual(phase_diff[0] + phase_diff[1], np.pi/90.0, # Check less than 2 deg total
                        "Channel {} out of phase at {:.0f}  MHz Centre Frequency".format(channel, centre_freq))
                except AssertionError, e:
                    self.failures.append(str(e))
                    pass

    def test_004_t(self):
        """Start of Burst"""

        cmd = "./build/python/qa_crimson_burst_dummy.sh"
        p = Popen(cmd, stderr = PIPE)
        stderr = p.communicate()[1]
        log.debug(stderr)

        # Should only fail on the last iteration of the loop
        try:
            self.assertEqual(stderr.count("rx error code: 15"), 1,
                "Crimson does not have the expected amount of empties/overs.")
        except AssertionError, e:
            self.failures.append(str(e))
            pass

    def test_005_t(self):
        """Set and Get"""
        # Does not work

        centre_freq = np.random.randint(1, 1e9)

        #csnk = self.coreTest(10, 5e3, centre_freq)[1]

        #for ch in self.channels:
        #    log.debug("Channel: %1d Gain: %.2f dB" % (ch, 1.0))

        #    csnk.set_gain(1.0, ch) # Set the gain on the channel
        #    log.debug("%.2f | %.2f" % (1.0, csnk.get_gain(ch)))

        #    try: self.assertEqual(1.0, csnk.get_gain(ch))
        #    except AssertionError, e: self.failures.append(str(e))

        pass

    def test_006_t(self):
        """Gain (LB + HB)"""
        # Checks using the areas of the waves and the peaks to verify (x2)

        for centre_freq in np.arange(10e6, 4e9, 20e6):

            log.debug("%.2f Hz" % centre_freq)

            areas = []

            # For each centre frequency, sweep the TX Gain.
            for tx_amp in np.arange(5e3, 30e3, 5.0e3):

                vsnk = self.coreTest(# High band requires stronger reception when centre_freq is greater 120 Mhz.
                    30.0 if centre_freq > 120e6 else 10.0,
                    tx_amp,
                    centre_freq)[0]

                #sigproc.dump(vsnk)

                area = sigproc.absolute_area(vsnk)
                areas.append(area)

            # Transpose to defragment channel data.
            areas = np.array(areas).T.tolist()

            # Log
            log.debug("Absolute Areas")
            for ch, area in enumerate(areas):
                log.debug("ch[%d]: %r" % (ch, np.around(area, decimals = 4)))

            # Verify areas are increasing (just check if list if sorted).
            for area in areas:
                try:
                    self.assertEqual(area, sorted(area),
                        "{:.0f} MHz central freqeuncy".format(centre_freq/1e6))
                except AssertionError, e:
                    self.failures.append(str(e))
                    pass

    def test_007_t(self):
        """Channel Repeatability"""

        for centre_freq in np.arange(10e6, 4e9, 20e7):
            log.debug("%.2f Hz" % centre_freq)

            data = []

            # 10 runs and store the vsnk data
            for x in xrange(10):
                vsnk = self.coreTest(8.0, 3.0e4, 15e6)[0]
                runs = sigproc.to_mag(vsnk) # Convert to real number
                data.append(runs)

            # Compare the channels to the first one. Make sure they are within +/-0.05
            for run in xrange(1, len(data)):
                for channel in xrange(len(data[0])):
                    try:
                        self.assertTrue(np.allclose(data[0][channel], data[run][channel], 0.05, 0.05),
                            "Ch {} at {:.0f} MHz central freqeuncy".format(channel, centre_freq/1e6))
                    except AssertionError, e:
                        self.failures.append(str(e))
                        pass

    def test_008_t(self):
        """Channel Consistency"""

        for centre_freq in np.arange(15e6, 4e9, 100e6):

            log.debug("%.2f Hz" % centre_freq)

            #3 iterations at each centre frequency
            for x in xrange(3):
                vsnk = self.coreTest(8.0, 3.0e4, centre_freq)[0]

                #Convert to magnitude
                vsnk = sigproc.to_mag(vsnk)

                #Check that the channels are all similar to each other
                for channel in xrange(1, len(vsnk)):
                    try:
                        self.assertTrue(np.allclose(vsnk[0], vsnk[channel], 0.05, 0.05),
                            "{:.0f} MHz Central Frequency".format(centre_freq/1e6))
                    except AssertionError, e:
                        self.failures.append(str(e))
                        pass

    def test_009_t(self):
        """Flow Control"""

        # NOTE: This test cannot be mocked.

        cmd = "./python/crimson_test_underflow"
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)

        def endProcess():
            p.kill()

            try:
                self.assertTrue(False, "Underflow Check Timed Out")
            except AssertionError, e:
                self.failures.append(str(e))
                pass

        # Use a timer for timeout functionality
        # 20 second timeout
        timer = Timer(20, endProcess)

        try:
            timer.start()

            stdout = p.communicate()[0]
            log.debug(stdout)

            # Should fail only on the last iteration of the loop
            try:
                self.assertEqual(stdout.count("Got event code underflow message."), 1,
                    "TX underflows could not be requested async")
            except AssertionError, e:
                self.failures.append(str(e))
                pass
        finally:
            timer.cancel()

if __name__ == '__main__':

    crimson_test_suite  = gr_unittest.TestSuite()

    # Flag for test development
    IS_DEV = False

    if IS_DEV:
        # Runs only the specified test in isolation
        crimson_test_suite.addTest(qa_crimson_loopback('test_000_t'))
    else:
        crimson_test_suite  = gr_unittest.TestLoader().loadTestsFromTestCase(qa_crimson_loopback)

    print "Test results availible in test_results.log"

    #gr_unittest.TextTestRunner(verbosity=2).run(crimson_test_suite)
    gr_unittest.TextTestRunner().run(crimson_test_suite)
