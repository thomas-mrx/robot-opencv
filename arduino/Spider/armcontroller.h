#pragma once

#include "utils/vectors.h"
#include "motors.h"
#include "arm.h"

#include "lib/ArduinoQueue/ArduinoQueue.h"

struct Order {
enum:uint8_t{POS, WAIT} tag;
     uint8_t index; //Index number of the arm
     float speed; //Speed in mm/s
     Vectorf target; //position target in cm
};

extern Motors<MOTORS_NUMBER> motorsController;

template<int NArm, int NNode>
class ArmController {
public:

    /*
     * Constructor with the previously initialised instance of motor controller
     */
    ArmController(Motors<NArm * NNode>& motors_)
        : motors(motors_)
    {}

    /*
     * Return reference to arm at index
     */
    Arm<NNode>& getArm(int index) {
        return arms[index];
    }

    /*
     * Add an order to the queue to be processed.
     * The order is specified before.
     */
    void addPosition(Order ord) {
        q.enqueue(ord);
    }

    /*
     * Process all currently queued orders. Respecting the speed time defined
     */
    void process_orders() {
        //Pop angles, speed for motors to execute

        while (pop_orders()) {
            unsigned long mtime = micros();
            sei();
            while (!execute_orders(micros() - mtime)) {
                mtime = micros();
                //delay(1);
                delayMicroseconds(500);
            }
        }
    }

private:
    Motors<NArm * NNode>& motors;
    Arm<NNode> arms[NArm];

    ArduinoQueue<Order> q{100};

    /*
     * Dequeue orders and apply it to the correct arm until a wait order or end of queue
     */
    bool pop_orders() {
        if (q.isEmpty())
            return false;

        while (!q.isEmpty()) {
            Order ord = q.dequeue();
            if (ord.tag == Order::WAIT)
                break;
            arms[ord.index].setTargetPos(ord.target);
            //if (ord.speed > 0)
            arms[ord.index].setMoveSpeed(ord.speed);
        }

        return true;
    }

    /*
     * Execute orders applyed for each arm
     * Return when all arm reached their target
     */
    bool execute_orders(double elapsed_time) {
        bool arrived = true;
        for (int i = 0; i < NArm; i++) {
            if (!arms[i].process(1000000./elapsed_time))
                arrived = false;
        }
        return arrived;
    }

};
