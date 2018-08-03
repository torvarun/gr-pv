#!/usr/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/jade/vven-workspace/gr-pv/python
export PATH=/home/jade/vven-workspace/gr-pv/build/python:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export PYTHONPATH=/home/jade/vven-workspace/gr-pv/build/swig:$PYTHONPATH

if [ -z "$1" ]; then
    /usr/bin/python2 /home/jade/vven-workspace/gr-pv/python/qa_crimson_loopback.py
else
    /usr/bin/python2 /home/jade/vven-workspace/gr-pv/python/qa_crimson_loopback.py -d $1
fi
