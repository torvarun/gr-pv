from sys import stdout

def dump(vsnk, channels, num_samps):
    """
    """
    for s in range(num_samps):
        for c in channels:
            sample = vsnk[c].data()[s]
            stdout.write("%10.5f %10.5f\t" % (sample.real, sample.imag))
        stdout.write("\n")
