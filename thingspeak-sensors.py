#!/usr/bin/env python

# 1. Setup your Pi [B+]/2/3 to support 1wire on a pin i.e. GPIO4 pin 
# 2. Hookup 18B20 temperature sensor on GPIO4, 1wire will automatically detect it as a file, value of temp will be inside 
# 3. Hookup: 3.3V<---LDR---[GPIO18]----1uF----GND: script will measure/count time till capacitor is charged
# 4. Copy API write key down from your Thingspeak channel 
# 5. Run script as process: "sudo python thingspeak-sensors.py > /dev/null &" or simply "sudo python thingspeak-sensors.py"
# Happy logging of temperature and daynight intervals.

import os
import glob
import time
import RPi.GPIO as GPIO
import sys
import datetime
import urllib

baseURL = 'http://api.thingspeak.com/update'
api_key = 'XXXXXXXXXXXXXXXXX' #enter here write API from your Thingspeak channel

#initiate the temperature sensor
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

#set up
GPIO.setmode(GPIO.BCM)
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
pin_ldr = 18 

def read_temp_raw(): #a function that grabs the raw temperature data from the sensor
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(): #a function that checks that the connection was good and strips out the temperature
    lines = read_temp_raw()
    
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
 
    equals_pos = lines[1].find('t=')
 
    if equals_pos !=-1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string)/1000.0
        temp_f = temp_c * 9.0/5.0 + 32.0
        return temp_c
    
def read_ldr(pin_ldr):
    count = 0    
    GPIO.setup(pin_ldr, GPIO.OUT)
    GPIO.output(pin_ldr, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(pin_ldr, GPIO.IN)
    
    while (GPIO.input(pin_ldr)==GPIO.LOW):
        count += 1
                
    countf = float(count)/1000.0
    return countf
    
    
if __name__ == "__main__":
    while True: #infinite loop
        tempin = read_temp() #get the temp and ldr
        print "Temperature is: "+str(tempin)
        ldrvalue = read_ldr(pin_ldr)
        print "LDR value is: "+str(ldrvalue)
        #values = [datetime.datetime.now(), tempin]
        params = urllib.urlencode({'api_key': api_key, 'field1': tempin, 'field2': ldrvalue})
        #g = urllib2.urlopen(baseURL + "&field1=%s" % (tempin))
        try:    
            g = urllib.urlopen(baseURL, data=params)
        except (IOError) as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error: ", sys.exc_info()[0]
        
        time.sleep(5)
