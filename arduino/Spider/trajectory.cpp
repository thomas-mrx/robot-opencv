#include "trajectory.h"
#include <SPI.h>    //nRF24L01 module need 1/3
#include <nRF24L01.h>         //nRF24L01 module need 2/3
#include <RF24.h>   //nRF24L01 module need 3/3

volatile int rest_counter;
const int wait_rest_time = 3 * 50; 


void Trajectory::setup()
{
  stand();
}
