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

# Thingspeak DHT Sensor  Data-logging Example
# Copyright (c) 2014 Adafruit Industries
# Author: mi123

# Hardwares: Zigbee, Arduino, raspberry pi, etc.
# Zigbees modes are Coordinator API and Enddevice AT modes

import sys
import time
import datetime
import serial
from xbee import XBee, ZigBee

# import Adafruit_DHT
import gspread
import httplib, urllib

#TNGSPK_KEY = 'xxxxxx'# you need Thingspeak registration to get key
TNGSPK_KEY = 'xxxxxx' # W

# USB port
#port='/dev/ttyUSB0'
#port='COM5'
port='/dev/ttyACM0'

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
    

def arduinoPower(sw):
    ''' This function is switching of arduino power
        attribute sw must be 'on' or 'off'
    '''
    dic_sw = {'off':'\x04', 'on':'\x05'}
    xbee.remote_at(frame_id = 'B',\
        dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
        dest_addr='\xFF\xFF', command='D4', parameter=dic_sw[sw])

    response = xbee.wait_read_frame()
    print response
    return


def arduinoSerial(sw):
    ''' This function is switching of arduino power
        attribute sw must be 'on' or 'off'
    '''
    dic_sw = {'off':'\x04', 'on':'\x05'}
    xbee.remote_at(frame_id = 'C',\
        dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
        dest_addr='\xFF\xFF', command='D3', parameter=dic_sw[sw])

    response = xbee.wait_read_frame()
    print response

    return


def serial_read(num_data, num_loop = 10):
    ''' serail read and cut out the data
        return data in a line
        data that was sent from Arduino is start,xx,xx,xx\n\r
        parameters
        num_data : when xx, xx, xx then 3
        num_loop : max number of attempting loop (default 10)
        return data if fail return False
    ''' 
    num_loop = num_loop + 1
    while num_loop:
        # read data
        num_loop -= 1
        print num_loop
        response = xbee.wait_read_frame()
        print response
        print "\n"
        try:
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
    return False


def xbeeIsCmd():
    """
    check pins status
    
    """
    print "IS command"
    xbee.remote_at(frame_id='D',\
            dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
            dest_addr='\xFF\xFF',\
            command='IS')    
    num_loop = 11
    while num_loop:
        # read data
        num_loop -= 1
        print num_loop
        response = xbee.wait_read_frame()
        print response
        print '\n'
        if response['frame_id'] == 'D':
            print response['parameter'][0]['adc-1']
            return float(response['parameter'][0]['adc-1'])
        else:
           continue
    
    return False


def xbeeSiCmd():
    print "Sleep Immediately"
    xbee.remote_at(frame_id = 'E',\
            dest_addr_long='\x00\x00\x00\x00\x00\x00\xFF\xFF',\
            dest_addr='\xFF\xFF',\
            command='SI')    
    response = xbee.wait_read_frame()
    print response
    print '\n'
    return


def update_thingspeak(tngspk_data1, tngspk_data2, tngspk_data3, tngspk_key):
    ''' This function pushing data to the thingspeak 
        parameters
        temp : measured temperature will be plotted on fig field1.
        tngspk_key : password provied from thingspeak.com
    '''
    try:
        params = urllib.urlencode({'field1': tngspk_data1,\
                'field2': tngspk_data2,\
                'field3': tngspk_data3,\
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
if __name__ == "__main__":
    # Opening the serial port
    global ser
    global xbee
    ser, xbee = serial_init(port)

    print "# Arduino awake\n"
    arduinoPower('on')
    print "\n"

    print "# Arduino serial on\n"
    arduinoSerial('on')
    print "\n"

    print "# Read data from arduino.\n"
    num_data = 2
    data = serial_read(num_data, num_loop = 10)
    if data != False:
        tempDHT22 = float(data[0])
        rhDHT22 = float(data[1])
    
    print "# Arduino serial off\n"
    arduinoSerial('off')
    print "\n"

    print "# measure the battery voltage\n"
    volt_battery = xbeeIsCmd()
    # calc supply voltage (1:11), 10bit, 1.2V@1023digit
    volt_battery = volt_battery/1023.0 * 1.2 * 11.0
    print '%f\n' %volt_battery

    print "# Arduino sleep\n"
    arduinoPower('off')
    print "\n"

    print "Xbee gonna Sleep\n"
    xbeeSiCmd()
    print "\n"

    # upload data to thingspeak
    update_thingspeak(tempDHT22, rhDHT22, volt_battery, TNGSPK_KEY) # TMP36 sensor data

    # close serial
    ser.close()

