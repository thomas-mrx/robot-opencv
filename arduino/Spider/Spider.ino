#include <Arduino.h>
#include "motors.h"
#include "armcontroller.h"
#include "body.h"

#include <SPI.h>    //nRF24L01 module need 1/3
#include <nRF24L01.h>         //nRF24L01 module need 2/3
#include <RF24.h>   //nRF24L01 module need 3/3

/* Joystick ------------------------------------------------------------------*/
int order;
int last_order = 0;
unsigned long time;

//List of servo pins connected to the arduino
// Hanche / Femur / Tibia
int servo_pin[12] = { 4,  2,  3,
    7,  5,  6,
    16,  14, 15,
    19, 17, 18
};

//Controller motors
Motors<MOTORS_NUMBER> motors;

const float OFFSET_Z = 27;

// On choisit 4 bras qui ont chacun 3 axes
ArmController<4, 3> armController{motors};
//Vectorf corrections[] = {{100, 70, 42}, {100, 70, 42}, {100, 70, 42}, {100, 70, 42}}; // Default
//Vectorf corrections[] = {{114, 73, 59}, {90, 71, 58}, {103, 83, 50}, {115, 75, 54}}; // Bleue
//Vectorf corrections[] = {{106, 84, 62}, {109, 85, 45}, {92, 87, 40}, {104, 69, 30}}; // grise
//Vectorf corrections[] = {{103,53,33},{95,63,28},{105,66,75},{96,65,46}}; // Default
Vectorf corrections[] = {{112, 60, 57}, {112, 63, 50}, {110, 60, 69}, {98, 83, 50}};
//Vectorf corrections[] = {
//  { 110, 60, 80 - OFFSET_Z }, // Leg 1 - Front right (R2) - {H, F, T}
//  { 100, 65, 85 - OFFSET_Z }, // Leg 2 - Back right (R1) - {H, F, T}
//  { 105, 75, 20 - OFFSET_Z }, // Leg 3 - Front left (L1) - {H, F, T}
//  { 120, 30, 55 - OFFSET_Z }  // Leg 4 - Back left (L2) - {H, F, T}
//};

// On choisit le modèle d'arraignée (toutes les dimensions)
SpiderJDMI model;
//On utilise un body à 4 bras
Body4 body(armController, model);

/* Wireless communication ----------------------------------------------------*/
//dfine RF24 for nRF24l01
RF24 radio(9, 10);  

//define RF24 transmit pipe
//NOTE: the "LL" at the end of the constant is "LongLong" type
const uint64_t pipe = 0xE8E8E800E1LL;

// L'object qui gère et stock la trajectoire
Trajectory trajectory;
const int safe_zone = 16;

void setup()
{
    Serial.begin(9600);

    //start listen radio
    radio.begin();
    radio.openReadingPipe(1,pipe);
    radio.setRetries(0, 15);
    radio.setPALevel(RF24_PA_HIGH);
    radio.startListening();
    Serial.println("Radio listening started");
  
    motors.attachServo(servo_pin); //First things to do. Arms will go to neutral
    body.init(corrections);
    trajectory.setup();
    //delay(3000);
    //trajectory.turn_angle(0);
    time = millis();
}

// Marche
void loop()
{
    //trajectory.reset(); //Reset counter to 0

    if ( radio.available() )
    {
      
        // get to the end of the buffer
        while(radio.available()){
          radio.read( &order, sizeof(int) );
        }
        int timeoutDelay = (order > 2) ? 3000 : 1500;
        timeoutDelay = 0;
        if(order > 0 && (order != last_order || time+timeoutDelay < millis())){
          last_order = order;
          time = millis();
          Serial.print("ORDER = ");
          Serial.println(order);
          switch(order){
              case 2:
                trajectory.step_forward(1);
                break;
              case 1:
                trajectory.step_back(1);
                break;
              case 4:
                trajectory.turn_left(1);
                break;
              case 3:
                trajectory.turn_right(1);
                break;
              case 5:
                trajectory.stand();
                break;
            }
        }
    }

    //block the loop while servo are moving
    body.process(trajectory);

    // empty buffer after move
        while(radio.available()){
          radio.read( &order, sizeof(int) );
        }

}


/*//Calibration
void loop()
   {
   for (int i = 0; i < 4; i++) {
   armController.addPosition({Order::POS, i, 10000, {100, 70, 15}});
   armController.addPosition({Order::WAIT});
   }
   armController.process_orders();
   delay(1000);
   }
*/
/* //Avancer
   void loop()
   {
   float speed = 200;
   speed = model.leg_move_speed;
   armController.addPosition({Order::POS, 0, speed, {KEEP, KEEP, model.z_up}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 0, speed, {model.x_default, model.y_default + (2.) * model.y_step, KEEP}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 0, speed, {KEEP, KEEP, model.z_default}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);

   speed = model.body_move_speed;
   armController.addPosition({Order::POS, 0, speed, {model.x_default, model.y_default + (1.) * model.y_step, model.z_default}});
   armController.addPosition({Order::POS, 1, speed, {model.x_default, model.y_default + (2.) * model.y_step, model.z_default}});
   armController.addPosition({Order::POS, 2, speed, {model.x_default, model.y_default + (0.) * model.y_step, model.z_default}});
   armController.addPosition({Order::POS, 3, speed, {model.x_default, model.y_default + (2.) * model.y_step, model.z_default}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);

   speed = model.leg_move_speed;
   armController.addPosition({Order::POS, 1, speed, {KEEP, KEEP, model.z_up}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 1, speed, {model.x_default, model.y_default + (1.) * model.y_step, KEEP}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 1, speed, {KEEP, KEEP, model.z_default}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);

   armController.addPosition({Order::POS, 3, speed, {KEEP, KEEP, model.z_up}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 3, speed, {model.x_default, model.y_default + (1.) * model.y_step, KEEP}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 3, speed, {KEEP, KEEP, model.z_default}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);

   armController.addPosition({Order::POS, 2, speed, {KEEP, KEEP, model.z_up}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 2, speed, {model.x_default, model.y_default + (1.) * model.y_step, KEEP}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 2, speed, {KEEP, KEEP, model.z_default}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);
   }
//*/

/* //Mouvement
   void loop()
   {

   for (int i = 0; i < 4; i++) {
   armController.addPosition({Order::POS, i, 1000, {100, 80, 15}});
   }

   float speed = 200;
   armController.addPosition({Order::POS, 0, speed, {140, 10, -27}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 0, speed, {90, 10, -27}});
   armController.addPosition({Order::WAIT});
   armController.addPosition({Order::POS, 0, speed, {90, 80, -27}});
   armController.addPosition({Order::WAIT});

   armController.process_orders();
   delay(1000);
   }
//*/
