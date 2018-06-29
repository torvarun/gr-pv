# Per Vices Functional Test System

This test system employs functional tests to verify the operation of Per Vices RX/TX devices.

# Install

```
mkdir build

cd build

cmake ..

make test
```

# Functional Tests

Functional tests are marked qith a "qa" prefix.

Functional tests may either be automatic or manual or in some cases both.

Functional tests are composed of smaller iterative tests.

Each iteration of an iterative test is tested clean slate with a new connection to the crimson device.

# Test System Requirements

The Per Vices Functional Test System is based on the GNURadio Out-Of-Tree-Modules Test system. Ensure
GNURadio for Python2 is installed before continuing.

Additionally, automatic tests within the Per Vies Functional Test System employ
SciPy for internal self verification. Ensure SciPy for Python2 is installed as well before continuing.

Finally, said test system requires the Per Vices UHD driver to be installed.

Ensure one BNC cable per channel is looped from its TX to RX channel. Ensure an attenuator is fixed to
each RX line as driving a TX line with max gain will damage the RX line at max gain.

# Test System Layout

The Per Vices Functional Test System relies on TX/RX channel loop-backs for signal transmitting, receiving,
processing, and verification. The test system, from a high level, transmits a signal from a TX channel to
a corresponding RX channel using the GNURadio library. Data packet signal integrity is verified with the
SciPy library. Once all tests pass the Crimson TNG is marked functional.
