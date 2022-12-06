#pragma once
#include "Arduino.h"

class SpiderModel
{
    public:
        SpiderModel() = delete;

        template <int NNode>
            struct Length {

                template<typename... Args>
                Length(Args... args)
                  : values{args...}
                {}
                
                Length(const float values_[NNode])
                {
                    for (int i = 0; i < NNode; i++)
                        values[i] = values_[i];
                }
                
                int operator[](int index) const {
                    return values[index];
                }

                private:
                float values[NNode];
            };

    protected:
        SpiderModel(
                // Expected position for calibrations
                //const float adjustSite[3],
                // Calibration values
                const float zAbsolute, const float xDefault, const float yDefault,
                const float yStep, const float zDefault, const float zUp,
                const float zBoot,
                // Body lengths
                const float lengthSide, const Length<3> legsLengths,
                // Speeds configuration
                const float spotTurnSpeed, const float legMoveSpeed,
                const float bodyMoveSpeed, const float standSeatSpeed)
            : //adjust_site{ adjustSite[0], adjustSite[1], adjustSite[2] }
                z_absolute(zAbsolute)
                , x_default(xDefault)
                , y_default(yDefault)
                , y_step(yStep)
                , z_default(zDefault)
                , z_up(zUp)
                , z_boot(zBoot)
                , length_side(lengthSide)
                , legs_lengths{ legsLengths }
                , spot_turn_speed(spotTurnSpeed)
                    , leg_move_speed(legMoveSpeed)
                    , body_move_speed(bodyMoveSpeed)
                    , stand_seat_speed(standSeatSpeed)
                    {}

    public:
                // Expected cartesian coordinates
                //const float adjust_site[3];
                const float z_absolute;
                // Calibration values
                const float x_default;

                const float y_default;
                const float y_step;

                const float z_default;
                const float z_up;
                const float z_boot;

                // Distance between body servos
                const float length_side;

                // Legs length configuration
                const Length<3> legs_lengths;

                // Speed configuration
                const float spot_turn_speed;
                const float leg_move_speed;
                const float body_move_speed;
                const float stand_seat_speed;
};
