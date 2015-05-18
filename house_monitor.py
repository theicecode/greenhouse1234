# coding: utf-8
#!/usr/bin/python

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# DHT Sensor Data-logging Example

# Hardwares: Zigbee, Arduino, raspberry pi, etc.
# Thingspeak API
# Python-xbee API
# Zigbees modes are Coordinator API and Enddevice AT modes

import sys
import time
import datetime
import serial
from xbee import XBee, ZigBee

# import Adafruit_DHT
import gspread
import httplib, urllib

TNGSPK_KEY = 'TNGSPK_KEY' # Watanabe

# USB port
#port='/dev/ttyUSB0' # if Rasberry pi
port='COM5' # if windows

# Communicate using Serial

def serial_init(port):
    # API mode
    ''' Function trys to onnect a serial port
        parameter
        port = e.g., "/dev/ttyUSB0"
    '''
    try:
        ser = serial.Serial(port, 9600)
        xbee = ZigBee(ser)
        print "Serial Initialized"
        return ser, xbee
    except:
        print "Connection didn't establish"
        return False
    
        
def serial_read(num_data, num_loop = 10):
    ''' serail read and cut out the data
        return data in a line
        data that was sent from Arduino is start,xx,xx,xx\n\r
        parameters
        num_data : when xx, xx, xx then 3
        num_loop : max number of attempting loop (default 10)
        return data if fail return False
    ''' 
    while num_loop:
        # read data
        print num_loop
        try:
            response = xbee.wait_read_frame()
            #print response
            if response['id'] == 'rx':
                serial_data = response['rf_data'].strip('\n\r').split(':')
                if serial_data[0] == 'start' and serial_data[-1] == 'end':
                    data = serial_data[1:num_data+1]
                    print data
                    return data
                else:
                    continue
            else:
                continue
        except:
            time.sleep(0.1)
            continue
        num_loop -= 1
    return False


def arduinoPower(sw):
    ''' This function is switching of arduino power
        attribute sw must be 'on' or 'off'
    '''
    dic_sw = {'off':'\x04', 'on':'\x05'}
    xbee.remote_at(frame_id='A',\
            dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
            dest_addr='\xFF\xFF', command='D4', parameter=dic_sw[sw])
    try:
        response = xbee.wait_read_frame()
        print response
    except:
        pass

    return


def arduinoSerial(sw):
    ''' This function is switching of arduino power
        attribute sw must be 'on' or 'off'
    '''
    dic_sw = {'off':'\x04', 'on':'\x05'}
    xbee.remote_at(frame_id='B',\
            dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
            dest_addr='\xFF\xFF', command='D3', parameter=dic_sw[sw])
    try:
        response = xbee.wait_read_frame()
        print response
    except:
        print 'Fail to operate arduino Serial'

    return


def xbeeIsCmd():
    print "IS command"
    xbee.remote_at(frame_id='C',\
            dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
            dest_addr='\xFF\xFF',\
            command='IS')    
    try:
        response = xbee.wait_read_frame()
        print response['parameter'][0]['adc-1']
    except:
        print 'Fail to measure the battery voltage'

    return


def update_thingspeak(tngspk_data1, tngspk_data2, tngspk_key):
    ''' This function pushing data to the thingspeak 
        parameters
        temp : measured temperature will be plotted on fig field1.
        tngspk_key : password provied from thingspeak.com
    '''
    try:
        params = urllib.urlencode({'field1': tngspk_data1,\
                'field2': tngspk_data2,\
                'key': tngspk_key})
        headers = {"Content-type":"application/x-www-form-urlencoded",
        "Accept":"text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print response.status, response.reason
        #print response.read()
        conn.close()
    except:
        print 'Append error, sorry'

# # the following part is the main program.

# In[6]:
if __name__ == "__main__":
    # Opening the serial port
    global ser
    global xbee
    ser, xbee = serial_init(port)

    print "# make arduino awake\n"
    arduinoPower('on')
    print "# make arduino serial on\n"
    arduinoSerial('on')

#    print "# Read data from arduino.\n"
    num_data = 2
    data = serial_read(num_data, num_loop = 10)
    if data != False:
        tempDHT22 = float(data[0])
        rhDHT22 = float(data[1])
    
#    print "# get the time."
#    TS = datetime.datetime.now()
#    TS = TS.replace(microsecond=0)

    print "# make arduino serial off\n"
    arduinoSerial('off')

    print "# measure the battery voltage\n"
    xbeeIsCmd()

    print "# make arduino sleep\n"
    arduinoPower('off')

    # upload data to thingspeak
    update_thingspeak(tempDHT22, rhDHT22, TNGSPK_KEY) # TMP36 sensor data

    # close serial
    ser.close()
