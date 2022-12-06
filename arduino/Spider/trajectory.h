#pragma once
#include <Arduino.h>

#define TRAJ_MAX_LENGTH 20

struct Path {
    enum:uint8_t{SIT, STAND, FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT, TURN_ANGLE} type;
    uint8_t number; //Repeat number of order
    uint16_t angle;
};

class Trajectory {
    public:

        /*
         * Method to add high level orders to the array
         */
        void setup();

        /*
         * Reset the counter of the current processing order
         */
        void reset() {
            traj_length = 0;
            cur_index = 0;
        };

        void step_forward(uint8_t n) { addTraj({Path::FORWARD,    n, 0}); }
        void step_back(uint8_t n)    { addTraj({Path::BACKWARD,   n, 0}); }
        void turn_left(uint8_t n)    { addTraj({Path::TURN_LEFT,  n, 0}); }
        void turn_right(uint8_t n)   { addTraj({Path::TURN_RIGHT, n, 0}); }
        void turn_angle(uint16_t a)   { addTraj({Path::TURN_RIGHT, 1, a}); }
        void sit()                   { addTraj({Path::SIT,        1, 0}); }
        void stand()                 { addTraj({Path::STAND,      1, 0}); }

        /*
         * Util function to add a node to the trajectory
         * next - path order to enqueue
         */
        void addTraj(Path next) {
            if (traj_length >= TRAJ_MAX_LENGTH)
                reset();

            traj[traj_length].type = next.type;
            traj[traj_length].number = next.number;
            traj_length++;
        }

        /*
         * Get next order to execute to process the trajectory
         */
        bool getNext(Path& next) {
            if (cur_index < traj_length) {
                next.type = traj[cur_index].type;
                next.number = traj[cur_index].number;
                next.angle = traj[cur_index].angle;
                cur_index++;
                return true;
            }
            return false;
        }

    private:
        Path traj[TRAJ_MAX_LENGTH];
        short traj_length;
        short cur_index;
};
