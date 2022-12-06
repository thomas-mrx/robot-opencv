#pragma once

#include "utils/vectors.h"
#include "spider_model.h"

template<int NNode>
class Kinematics {
    public:

        Kinematics() {}

        /*
         * Setup the length of the model for leg compute
         */
        void setLength(const SpiderModel::Length<NNode> lengths_)
        {
            lengths = lengths_;
        }

        /*
         * Setup the orientation function to move final order to arm orientation
         */
        void setOrientation(void (*arm_pos_)(float angle[NNode]))
        {
            arm_pos = arm_pos_;
        }

        /*
         * Method which compute polar coordinate from cartesian position.
         */
        virtual void cartesianToPolar(const Vectorf& pos, float output[NNode]) const;

        /*
         * Provide a measured value and compare it to the real intended value.
         * It compute the error and save it in internal array.
         */
        void computeError(Vectorf measured, Vectorf real)
        {
            measured.z -= 27;
            real.z -= 27;// Height form the ground of the spider

            float measure_angles[NNode];
            cartesianToPolar(measured, measure_angles);//TODO -12 on Z don't know why
            //calculate real degree and errors
            float real_angles[NNode];
            cartesianToPolar(real, real_angles);//TODO -12 on Z don't know why

            //save errors
            for (int j = 0; j < NNode; j++) {
                corrections[j] = real_angles[j] - measure_angles[j];
            }
        }

        /*
         * Apply the previously computed correction to the inputed servo orders
         */
        void applyCorrection(float angles[NNode]) const
        {
            for (int i = 0; i < NNode; i++)
                angles[i] += corrections[i];
        }

        /*
         * Apply the orientation angle correction to the inputed servo orders
         */
        void orientAngles(float angles[NNode]) const
        {
            if (arm_pos)
                (*arm_pos)(angles);
        }

    protected:
        SpiderModel::Length<NNode> lengths;
        float corrections[NNode];
        void (*arm_pos)(float angle[NNode]); //Function to handle angle depending on arm
};

class Kinematics3 : public Kinematics<3> {
    public:
        Kinematics3() {}

        void cartesianToPolar(const Vectorf& pos, float output[3]) const override;

    private:

};
