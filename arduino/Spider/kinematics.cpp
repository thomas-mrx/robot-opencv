#include "kinematics.h"
#include <math.h>
#include <Arduino.h>
void
Kinematics3::cartesianToPolar(const Vectorf& pos_, float output_angles[3]) const
{
    // Main part of the algorithm

    // What is servo_median_angle, servo_distal_angle and servo_proximal_angle ?
    // They are results to find. Each represent an angle of one servo motor.
    // x, y, z represente the future position of one leg

    // This program use the law of cosinus. It's also named Al-Kashi theorem.
    Vectorf pos = pos_;

    // calculate w-z angle degree
    float w = sqrt(pos.x*pos.x + pos.y*pos.y); //Distance on ground

    float v = w - lengths[0];

    float a = lengths[1];
    float a_2 = a*a;

    float b = lengths[2];
    float b_2 = b*b;

    float d = sqrt(pos.z*pos.z + v*v);

    output_angles[1] = atan2(pos.z, v) + acos((a_2 + d*d - b_2) / (2. * a * d));

    output_angles[2] = acos((a_2 + b_2 - d*d) / (2. * a * b)); //Beta

    output_angles[0] = atan2(pos.y, pos.x);
    /*
       Serial.println("Radians");
       for (int i = 0; i < 3; i++) {
       Serial.print(output_angles[i]);
       Serial.print(" ");
       }*/

    // transforme radians pi in degre 180
    output_angles[0] = output_angles[0] / M_PI * 180.;
    output_angles[1] = output_angles[1] / M_PI * 180.;
    output_angles[2] = output_angles[2] / M_PI * 180.;
}
