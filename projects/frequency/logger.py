from time import time, strftime
from numpy import savetxt, array
from agilentcounter import AgilentCounter
from agilentmultimeter import AgilentMultimeter

# Config settings
countergpib = 1
multigpib = 6
vrange = 1
vresolution = 0.0001

# Setting up frequency counter
counter = AgilentCounter(gpib = countergpib)
if (counter == None):
    exit
counter.reset()
counter.setupFast()
counter.write(":FUNC 'FREQ 1'")
counter.setupGating(0.1)

# Setting up multimeter
multi = AgilentMultimeter(gpib = multigpib)
if (multi == None):
    exit
multi.reset()
# 5-1/2 digits fast
multi.write("CONF:VOLT:DC %d" %(vrange))
multi.write("VOLT:DC:NPLC 0.2")
multi.write("TRIG:SOUR IMM")
# Need to do one reading to set up Wait-For-Trigger state!
multi.ask("READ?")

# Setting up output file
datafile = "beat_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')
out.write("#Time(UnixTime) BeatFrequency(Hz) Voltage(V)\n")

# Do logging until stopped by Ctrl-C
while True:
    try:
        start = time()
        counter.initMeasure()
        volts = float(multi.ask("READ?"))
        freq = counter.getFreq()
        now = time()
        measuretime = (now + start) / 2
        elapsed = now - start
        result = array([[measuretime, freq, volts]])
        savetxt(out, result)
        print "%f Hz / %f V / %f s" %(freq, volts, elapsed)
    except (KeyboardInterrupt):
        break
out.close()