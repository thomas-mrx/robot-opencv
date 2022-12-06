#pragma once

#include <math.h>
#include "utils/vectors.h"

#include "spider_model_jdmi.h"
#include "armcontroller.h"

template<int NArm>
class Motion {
    public:
        Motion(){}

        //virtual void path(const Vectorf& direction, const Vectorf& attitude){}

    protected:
};

class Motion4 : public Motion<4> {
    public:

        Motion4(ArmController<4, 3>& armController_);

        void setModel(SpiderModel* model_){
            model = model_;
        }

        //void path(const Vectorf& direction, const Vectorf& attitude) override;
        
        /*
         * Initialize arms current position and compute turn points
         */
        void initArms();

        /*
         * Compute arm positions to turn left
         * lastmovement - if true, will finish with arm at center position,
         * otherwise, will keep arm at turn position
         */
        void turn_left(bool lastmovement = true);

        /*
         * Compute arm positions to turn left
         * lastmovement - if true, will finish with arm at center position,
         * otherwise, will keep arm at turn position
         */
        void turn_right(bool lastmovement = true);

        /*
         * Compute arm positions to turn specified angle in degree
         */
        void turn_angle(uint16_t angle = 0);

        /*
         * Compute positions to go forward
         */
        void step_forward();
        /*
         * Compute positions to go backward
         */
        void step_back();


        /*
         * Compute positions to sit
         */
        void sit();
        /*
         * Compute positions to stand
         */
        void stand();

        double rad2deg(double angleRadian);

        double deg2rad(double angleDegre);

    private:
        Vectorf turn0;
        Vectorf turn1;
        ArmController<4, 3>& armController;
        SpiderModel* model;

        float current_speed;
        // Direction management
        enum direction
        {
            FORWARD,
            BACKWARD
        };
        int direction = direction::FORWARD;
        int last_moved_leg;

        /*
         * apply default position orders
         */
        void default_pos();

        /*
         * Sugar syntax to call the armcontroller to add the correct order for the arm
         * index - the index of desired arm
         * pos - the position to go
         * wait - should the spider wait for this arm to go to this position before executing next orders
         */
        void armMove(int index, Vectorf pos, bool wait = false);
        /*
         * Sugar syntax to call the armcontroller to force a wait instruction
         * This will force the controller to wait for all previous orders to complete before assigning new orders
         */
        void armWait();

};
