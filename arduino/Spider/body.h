#pragma once

#include "utils/vectors.h"

#include "motion.h"
#include "armcontroller.h"

#include "spider_model_jdmi.h"

#include "trajectory.h"


template<int NArm, int NNode>
class Body {
    public:
        Body(ArmController<NArm, NNode>& armController_)
            : armController(armController_)
        {}

    protected:
        ArmController<NArm, NNode>& armController;

};

class Body4 : public Body<4, 3> {

    public:
        Body4(ArmController<4, 3>& armController_, SpiderModel& model_)
            : Body(armController_), motionController{armController_}, model{model_}
        {
            motionController.setModel(&model);
        }
        /*
         * Initialize all arms with correct orientation (lambda functions)
         * and calibration value for the correction of the arm.
         * Calibration is based for {100, 70, 42}
         */
        void init(Vectorf corrections[4]) {

            auto angles0 = [](float angles[3]){
                //0 ou 3 / R2 et L2
                angles[0] = 90. + angles[0];  // servo_proximal_angle proximal angle of the leg
                angles[1] = 90. - angles[1]; // servo_median_angle median angle of the leg
                angles[2] = 90. - ( 90. - angles[2]);  // servo_distal_angle distal angle of the leg
            };

            auto angles1 = [](float angles[3]){
                // 1 ou 2 / R1 et L1
                angles[0] = 90. - angles[0];
                angles[1] = 90. + angles[1];
                angles[2] = 90. + ( 90. - angles[2]);
            };
            for (int i = 0; i < 4; i++) {
                int k = i * 3;
                int ids[] = {k + 0, k + 1, k + 2};
                armController.getArm(i).init(ids, model.legs_lengths, (i == 0 || i == 3) ? angles0 : angles1);
                if (corrections)
                    armController.getArm(i).correct(corrections[i]);
                else
                    armController.getArm(i).correct();
            }
            motionController.initArms();
        }

        /*
         * Execute a trajectory provided.
         * It will read the trajectory buffer and effectively execute the asked trajectory
         */
        void process(Trajectory& traj) {
            Path next;
            while (traj.getNext(next)) {
                for (int i = 0; i < next.number; ++i) {
                    switch (next.type) {
                        case Path::SIT:
                            sit();
                            break;
                        case Path::STAND:
                            stand();
                            break;
                        case Path::TURN_LEFT:
                            turn_left(i >= next.number-1);
                            break;
                        case Path::TURN_RIGHT:
                            turn_right(i >= next.number-1);
                            break;
                        case Path::FORWARD:
                            step_forward();
                            break;
                        case Path::BACKWARD:
                            step_back();
                            break;
                    };
                    armController.process_orders();
                }
                delay(150);
            }
        }

        /*
         * Wrapper for motion to turn_left
         */
        void turn_left(bool lastmovement) {
            motionController.turn_left(lastmovement);
        }

        /*
         * Wrapper for motion to turn_right
         */
        void turn_right(bool lastmovement) {
            motionController.turn_right(lastmovement);
        }

        /*
         * Wrapper for motion to turn_angle
         */
        void turn_angle(uint16_t angle) {
            motionController.turn_angle(angle);
        }

        /*
         * Wrapper for motion to step_forward
         */
        void step_forward() {
            motionController.step_forward();
        }

        /*
         * Wrapper for motion to step_back
         */
        void step_back() {
            motionController.step_back();
        }

        /*
         * Wrapper for motion to sit
         */
        void sit() {
            motionController.sit();
        }

        /*
         * Wrapper for motion to stand
         */
        void stand() {
            motionController.stand();
        }

    private:
        Motion4 motionController;
        SpiderModel& model;

};
