#Tone detection shamelessly stolen from:
#https://benchodroff.com/2017/02/18/using-a-raspberry-pi-with-a-microphone-to-hear-an-audio-alarm-using-fft-in-python/
#!/usr/bin/env python
import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose,log
from scipy import fft
from time import sleep
from collections import deque
import requests

import subprocess


#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY= 1.0

#Bandwidth for detection (i.e., detect frequencies within this margin of error of the TONE)
BANDWIDTH = 25

#heard note sequence deque
notes = deque(['G','G','G','G','G','G'], maxlen=6)

# Show the most intense frequency detected (useful for configuration)
frequencyoutput=True
freqNow = 1.0
freqPast = 1.0

#Set up audio sampler - 
NUM_SAMPLES = 2048
SAMPLING_RATE = 48000 #make sure this matches the sampling rate of your mic!
pa = pyaudio.PyAudio()
_stream = pa.open(format=pyaudio.paInt16,
                  channels=1, rate=SAMPLING_RATE,
                  input=True,
                  frames_per_buffer=NUM_SAMPLES)



#########################

def check_note(freqPast,freqNow):
	note = {}
	note["D4"] = 630
	note["E"] = 685
	note["F"] = 755
	note["G"] = 806
	note["A"] = 890
	note["B"] = 1000
	note["D5"] = 1175
	for index_note in note:
		min_note = note[index_note] - BANDWIDTH;
		max_note = note[index_note] + BANDWIDTH; 
		if min_note<=freqPast<=max_note and min_note<=freqNow<=max_note and notes[-1]!= index_note:
			notes.append(index_note)
			print "You played " , index_note , "!"
	  
#########################
#      MAIN LOOP        #
#########################

while True:
    while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
    audio_data  = fromstring(_stream.read(
        _stream.get_read_available()), dtype=short)[-NUM_SAMPLES:]
    # Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
    normalized_data = audio_data / 32768.0
    intensity = abs(fft(normalized_data))[:NUM_SAMPLES/2]
    frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    if frequencyoutput:
        which = intensity[1:].argmax()+1
        # use quadratic interpolation around the max
        if which != len(intensity)-1:
            y0,y1,y2 = log(intensity[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            freqPast = freqNow
            freqNow = (which+x1)*SAMPLING_RATE/NUM_SAMPLES
        else:
            freqNow = which*SAMPLING_RATE/NUM_SAMPLES
       	# print "\t\t\t\tfreq=",freqNow,"\t",freqPast
      	print freqNow	
    	check_note(freqPast,freqNow)
	


  


