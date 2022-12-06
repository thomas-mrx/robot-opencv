#pragma once
#include <Arduino.h>
#include "utils/vectors.h"
#include "kinematics.h"
#include "motors.h"
#include "spider_model.h"

#define KEEP 255

extern Motors<MOTORS_NUMBER> motors;

template<int NNode, typename KinematicsController = Kinematics3>
class Arm {
    public:
        Arm() : speed_factor(100) {} //Default arm position

        /*
         * Initialise the arm
         * ids_     - Motors controller indexes (0, N), corresponding to the defined arm
         * lengths_ - The length of the differents segments of this arm
         * arm_pos_ - The function pointer to transform servo from theorical model to spider model
         */
        void init(int ids_[NNode],
                SpiderModel::Length<NNode> lengths_,
                void (*arm_pos_)(float angle[NNode]))
        {
            kinematics.setLength(lengths_);
            kinematics.setOrientation(arm_pos_);

            for (int i = 0; i < NNode; i++) {
                ids[i] = ids_[i];
            }
            setCurrentPos({100, 70, 15});
            initiated = true;
        }

        /*
         * Wrapper to call kinematics servo motors correction and save it in the servo correction array
         */
        void correct(const Vectorf measured = {100, 70, 42}, const Vectorf real = {100, 70, 42}) {
            kinematics.computeError(measured, real);
        }

        /*
         * Process the movement of the arm from the current position to the target
         * At a given call refreshrate to respect the speed
         */
        bool process(double refreshrate) {
            bool finished = true;
            if (!initiated)
                return finished;
            Vectorf target_speed = target_position - current_position;
            double local_speed = abs(speed_factor) / (refreshrate/2.); //Speed in mm/s so divide for refreshrate
            if (target_speed.magnitude() > local_speed) {
                target_speed.normalise();
                target_speed *= local_speed;
                current_position += target_speed;
                finished = false;
            } else {
                current_position = target_position;
                finished = true;
            }

            float servos[NNode];
            computeAngles(current_position, servos);
            setServos(servos);
            return finished;
        }

        /*
         * Get the current intermediate position of the arm
         */
        Vectorf getCurrentPos() const {
            return current_position;
        }

        /*
         * Init the starting position of the arm
         */
        void  setCurrentPos(const Vectorf pos_) {
            current_position = pos_;
            target_position = pos_;
        }

        /*
         * Set the new target for the arm for the next process
         */
        void  setTargetPos(const Vectorf pos_) {
            Vectorf newpos = pos_;
            if (newpos.x == KEEP)
                newpos.x = current_position.x;
            if (newpos.y == KEEP)
                newpos.y = current_position.y;
            if (newpos.z == KEEP)
                newpos.z = current_position.z;

            target_position = newpos;
        }
        /*
         * Set the speed factor of the arm for the movement
         */
        void setMoveSpeed(const double speed_) {
            speed_factor = speed_;
        }
        /*
         * Compute servo motors angle for a position
         * It include, cartesian to polar call
         * Servo motor correction offset
         * And remap to servo motor range via arm_pos function
         */
        void computeAngles(Vectorf pos, float servos[NNode])
        {
            /*Serial.print(pos.x);
              Serial.print(" ");
              Serial.print(pos.y);
              Serial.print(" ");
              Serial.print(pos.z);
              Serial.println(" ");*/
            kinematics.cartesianToPolar(pos, servos);
            /*Serial.println();
              for (int i = 0; i < NNode; i++) {
              Serial.print(servos[i]);
              Serial.print(" ");
              }
              Serial.println();*/
            kinematics.applyCorrection(servos);
            /*for (int i = 0; i < NNode; i++) {
              Serial.print(servos[i]);
              Serial.print(" ");
              }
              Serial.println();*/
            kinematics.orientAngles(servos);
            /*for (int i = 0; i < NNode; i++) {
              Serial.print(servos[i]);
              Serial.print(" ");
              }
              Serial.println();
              Serial.println("-------------------------");*/
        }

    private:
        Vectorf current_position;
        Vectorf target_position;
        float speed_factor;
        uint8_t ids[NNode];
        KinematicsController kinematics;
        bool initiated = false;

        void setServos(float servos[NNode])
        {
            for (int i = 0; i < NNode; i++) {
                motors.setServo(ids[i], servos[i]);
            }
        }


};
