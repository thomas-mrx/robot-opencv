#include <Arduino.h>
#include "motors.h"
#include "armcontroller.h"
#include "body.h"


int servo_pin[12] = { 2,  3,  4,
                      5,  6,  7,
                      14, 15, 16,
                      17, 18, 19
                    };

Motors<MOTORS_NUMBER> motorsController;

ArmController<4, 3> armController{motorsController};

Vectorf corrections[] = {{100, 70, 30}, {100, 70, 30}, {100, 70, 30}, {100, 70, 30}}; // Default

Body4 body(armController);

Trajectory trajectory;

void setup()
{
    Serial.begin(115200);
    motorsController.attachServo(servo_pin); //First things to do. Arms will go to neutral
    body.init(corrections);
    trajectory.setup();
}

void loop()
{
    trajectory.reset(); //Reset counter to 0
    //body.process(trajectory);
    armController.addPosition({Order::POS, 0, 1000, {100, 70, 30}});
    armController.addPosition({Order::POS, 1, 1000, {100, 70, 30}});
    armController.addPosition({Order::POS, 2, 1000, {100, 70, 30}});
    armController.addPosition({Order::POS, 3, 1000, {100, 70, 30}});
    Serial.print(motorsController.getAngle(0));
    Serial.print(" ");
    Serial.print(motorsController.getAngle(1));
    Serial.print(" ");
    Serial.print(motorsController.getAngle(2));
    Serial.println(" ");
    armController.process_orders();
}
