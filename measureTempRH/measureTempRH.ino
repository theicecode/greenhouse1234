// Arduino Uno Code for greemhouse1234

#include <DHT.h>
#include <DHT.cpp>


/* Refered codes
 * DHT22 -> https://github.com/adafruit/DHT-sensor-library


 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 */

/* Wiring summary
  DI2 --- DHT22 sensor #2 pin
  TX  --- Serial out
*/

// DHT 22 sensor
#define DHTPIN 2
// Uncomment whatever type you're using!
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22   // DHT 22  (AM2302)
//#define DHTTYPE DHT21   // DHT 21 (AM2301)
// Connect pin 1 (on the left) of the sensor to +5V
// NOTE: If using a board with 3.3V logic like an Arduino Due connect pin 1
// to 3.3V instead of 5V!
// Connect pin 2 of the sensor to whatever your DHTPIN is
// Connect pin 4 (on the right) of the sensor to GROUND
// Connect a 10K resistor from pin 2 (data) to pin 1 (power) of the sensor

// Initialize DHT sensor for normal 16mhz Arduino
DHT dht(DHTPIN, DHTTYPE);
// NOTE: For working with a faster chip, like an Arduino Due or Teensy, you
// might need to increase the threshold for cycle counts considered a 1 or 0.
// You can do this by passing a 3rd parameter for this threshold.  It's a bit
// of fiddling to find the right value, but in general the faster the CPU the
// higher the value.  The default for a 16mhz AVR is a value of 6.  For an
// Arduino Due that runs at 84mhz a value of 30 works.
// Example to initialize DHT sensor for Arduino Due:
//DHT dht(DHTPIN, DHTTYPE, 30);


// Set Digital Pin that communicate with xBee
#define serialTriggerPin 4

void setup()
{
 Serial.begin(9600);
  dht.begin();
  //configure pin2 as an input and enable the internal pull-up resistor
  pinMode(serialTriggerPin, INPUT_PULLUP);

}


void loop()
{
    //read the pushbutton value into a variable
    delay(100);
    int serailState = digitalRead(serialTriggerPin);


  if (serailState == HIGH) {

    // Measure Temp & RH
    delay(2000);
    float tempDHT22 = dht.readTemperature();
    float rhDHT22 = dht.readHumidity();

    // Send data to xBee
    Serial.print("start:"); // Indicate data flow start
    Serial.print(tempDHT22,2);
    Serial.print(":"); // put : in between data
    Serial.print(rhDHT22,2);
    Serial.println(":end"); // Inticate data flow end

  }
  else {
    delay(100);
  }
}
