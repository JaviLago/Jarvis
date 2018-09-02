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
from datetime import datetime

note = {}
note["D4"] = 630
note["E"] = 685
note["F"] = 755
note["G"] = 806
note["A"] = 890
note["B"] = 1000
note["D5"] = 1175


# Song note sequences
sun = deque(['A','F','D','A','F','D'])
#time = deque(['A','D4','F','A','D4','F'])
#storm = deque(['D4','F','D5','D4','F','D5'])
#forest = deque(['D4','D5','B','A','B','A'])
saria = deque(['F','A','B','F','A','B'])
#fire = deque(['F','D4','F','D4','A','F']) #This is just 6 notes, play all 8 if you want ;)
#epona = deque(['D5','B','A','D5','B','A'])
#zelda = deque(['E','G','D4','E','G','D4'])
#heal = deque(['B','A','F','B','A','F'])
#test = deque(['D4','F','A','B','D5','D4']) #Not a Zelda song, just nice to make sure everything's working


#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY= 1.0

#Bandwidth for detection (i.e., detect frequencies within this margin of error of the TONE)
BANDWIDTH = 25

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
def init_array_notes():
	notes = deque(['G','G','G','G','G','G'], maxlen=6)

#########################
def play_correct():
	audio_file = "./songs/OOT_Song_Correct.wav"
	_stream.stop_stream()
	subprocess.call(["afplay", audio_file])
	_stream.start_stream()

#########################
def check_possible_song():
	found = 0

	if notes==sun:
		found = 1
		print "\t\t\t\tSun song!"

	if notes==saria:
		found = 1
		print "\t\t\t\tSaria song!"
		_stream.stop_stream()
		subprocess.call(["afplay", "./songs/saria.mp3"])
		_stream.start_stream()
		
	if found == 1:
		play_correct()
		notes.append('G')		
		

#########################

def check_note(freqPast,freqNow, reset_note):
	note = {}
	note["G"] = 0 #reset
	note["C"] = 514
	note["D"] = 565
	note["E"] = 612
	note["F"] = 658
	note["G"] = 728
	note["A"] = 818
	note["B"] = 915
	note["Cm"] = 980
	#note["D4"] = 630
	#note["E"] = 685
	#note["F"] = 755
	#note["G"] = 806
	#note["A"] = 890
	#note["B"] = 1000
	#note["D5"] = 1175
	
	min_last_note = note[notes[-1]]  - BANDWIDTH;
	if freqNow <= min_last_note:
		reset_note = True
		print "reseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet"
	for index_note in note:
		min_note = note[index_note] - BANDWIDTH;
		max_note = note[index_note] + BANDWIDTH; 

		if (reset_note):
			#print "daleh"
			if min_note<=freqPast<=max_note and min_note<=freqNow<=max_note:
				notes.append(index_note)
				print "--- You played " , index_note , "!"
				return True
		else:
			if min_note<=freqPast<=max_note and min_note<=freqNow<=max_note and notes[-1]!= index_note:
				notes.append(index_note)
				print "You played " , index_note , "!"
				return True
	# En caso de no encontrar ninguna "reiniciamos la nota"
	reset_note = True			
	return False

#########################
#      MAIN LOOP        #
#########################

reset_note = False
notes = deque(['G','G','G','G','G','G'], maxlen=6)
date_last_note = datetime.now()

print "hola"
print notes

if check_note(658,658,reset_note) == False:
	reset_note = True
print notes

if check_note(158,158,reset_note) == False:
	reset_note = True


print reset_note

print notes


if check_note(658,658,reset_note) == False:
	reset_note = True

print notes




while False:
    while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
    interval = datetime.now() - date_last_note
    #restart de queue
    if interval.seconds >= 2:
    	init_array_notes()
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
      	#print freqNow
    	new_note = check_note(freqPast,freqNow,reset_note)
    	if new_note:
    		date_last_note = datetime.now()
    	else:
    		reset_note = 
    	print notes
	check_possible_song()


  


