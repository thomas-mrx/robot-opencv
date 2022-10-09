/* -----------------------------------------------------------------------------
 - File:      nRF24l01 Transmit Test
 - Copyright: Copyright (C) 2015 SunFounder. For details, check License folder.
 - Date:      2015/7/21
 * -----------------------------------------------------------------------------
 - Overview
  - This project was written to test nRF24l01 module. If it runs, arduino will 
    reads Analog values on A0, A1 and transmits them over a nRF24L01 Radio Link 
    to another transceiver.
 - Request
   - FR24 library
 - Connections
   - nRF24L01 to Arduino
     1 GND   	 GND
     2 VCC	 3V3
     3 CE	 D9
     4 CSN	 D10
     5 SCK	 D13
     6 MOSI	 D11
     7 MISO	 D12
     8 UNUSED	
   - Joystick to Arduino
     GND         GND
     VCC         5V
     X           A0
     Y           A1
 * ---------------------------------------------------------------------------*/

/* Includes ------------------------------------------------------------------*/
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
/* Ports ---------------------------------------------------------------------*/
#define CE_PIN   9
#define CSN_PIN 10
#define JOYSTICK_X A0
#define JOYSTICK_Y A1
/* nRF24l01 ------------------------------------------------------------------*/
// NOTE: the "LL" at the end of the constant is "LongLong" type
const uint64_t pipe = 0xE8E8F0F0E1LL; // Define the transmit pipe
RF24 radio(CE_PIN, CSN_PIN); // Create a Radio
/* Joystick ------------------------------------------------------------------*/
int joystick[2]; // 2 element array holding Joystick readings
/* ---------------------------------------------------------------------------*/
/* RainBowt ------------------------------------------------------------------*/
String last_order = ""; 
/* ---------------------------------------------------------------------------*/

/*
 - setup function
 * ---------------------------------------------------------------------------*/
void setup()
{
  radio.begin();
  radio.setRetries(0, 15);
  radio.setPALevel(RF24_PA_HIGH);
  radio.openWritingPipe(pipe);
  Serial.begin(9600);
}

/*
 - loop function
 * ---------------------------------------------------------------------------*/
void loop()
{
  
  if (last_order == "" || last_order == "WIN" || last_order == "LOSE"){
    joystick[0] = analogRead(JOYSTICK_X);
    joystick[1] = analogRead(JOYSTICK_Y);
  }
  else {
      String order = "";
      if (Serial.available())
      {
          order = Serial.readString().trim();
      }
      if (order != "" && order != last_order)
      {
          last_order = order;
          if (order == "LEFT"){
            joystick[0] = 0;
            joystick[1] = 511;
          }
          else if (order == "RIGHT"){
            joystick[0] = 1023;
            joystick[1] = 511;
          }
          else if (order == "FORWARD"){
            joystick[0] = 511;
            joystick[1] = 1023;
          }
      }
  }
    
  radio.write( joystick, sizeof(joystick) );
}