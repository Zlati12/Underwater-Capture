// change setup.h to switch between buffered and pixel-by-pixel processing
#include "setup.h"
#include <NewPing.h>
#include <MedianFilter.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

const int chipSelectPin = 9;  // Choose any digital pin as chip select

#define TRIGGER_PIN  8  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     11  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 400 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
MedianFilter filter(31,0);

void setup() {
  Serial.begin(9600);
  // This is not necessary and has no effect for ATMEGA based Arduinos.\
  // WAVGAT Nano has slower clock rate by default. We want to reset it to maximum speed
  CLKPR = 0x00; // enter clock rate change mode
  CLKPR = 0; // set prescaler to 0. WAVGAT MCU has it 3 by default.
  
  Serial.print(F("Initializing SD card..."));
    if (!SD.begin(chipSelectPin)) {
    Serial.println("Initialization failed!");
    return;
  }
  Serial.println("Initialization done.");
  
  initializeScreenAndCamera();
}

void loop() {
  delay(100);                      // Wait 50ms between pings (about 20 pings/sec). 29ms should be the shortest delay between pings.
  unsigned int dis,o,uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).

  filter.in(uS);
  o = filter.out();

  if(o / US_ROUNDTRIP_CM <= 40)
  {
    processFrame();
  }
}
