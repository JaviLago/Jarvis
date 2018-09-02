import sys 
import subprocess
import time
import threading

stop_output = True

EXPORT_FILENAME = "scan_result"
INTERFACE = "wlan0mon"
SCAN_TIME = 30

if (len(sys.argv) > 1 and sys.argv[1] != ""):
	INTERFACE = sys.argv[1]

def f(p):
    global stop_output
    while True:
        l = p.stdout.readline()
        if not l or stop_output:
            break
        print(l.rstrip())   # or whatever you want to do with the line

print "Scan Start!!"

while 1:
	#Borramos por si hubise algun fichero
	subprocess.Popen(["rm", EXPORT_FILENAME + "-01.csv"])
	airodump = subprocess.Popen(["airodump-ng", "-w", EXPORT_FILENAME, "--output-format", "csv", INTERFACE],stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                      )
  	t = threading.Thread(target=f,args=(airodump,))
  	t.start()
  	time.sleep(SCAN_TIME)
  	
	# kill the process and stop the display after 10 seconds whatever happens
  	airodump.terminate()
  	stop_output = True

	#Buscamos donde comience la linea de los dispositivos
	startLines = False
	arrayDevices = []

	with open(EXPORT_FILENAME + "-01.csv", "r") as ins:
    		for line in ins:
			# Comenzamos buscando la cabecera de los dispositivos	
			if line.find("Station MAC") >= 0:
				startLines = True
			# A partir de ahi ya se supone que son dispositivos
			elif (startLines == True and line.find(",") >= 0):
				arrayLine = line.split(",")
				MAC = arrayLine[0]
				#initTime = arrayLine[1]
				#endTime = arrayLine[2]	
				arrayDevices.append(MAC)
     		
	
		print arrayDevices
		#Llamada a la  API
