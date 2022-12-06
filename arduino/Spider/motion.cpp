#include "motion.h"

#define OUVERTURE_ANGULAIRE_DEGRE_PAS_ROTATION 45.


Motion4::Motion4(ArmController<4, 3>& armController_)
    : armController(armController_)
{
}

void Motion4::initArms()
{
    /*   Forward
     *   y
     *   ^
     *   |
     *   o---> x
     */

    float x_side = 2.f * model->x_default + model->length_side;
    float y_side = 2.f * (model->y_default + model->y_step) + model->length_side;
    float y_side_step = 2.f * model->y_default + model->y_step + model->length_side;
    float y_step = model->y_step;
    float side_diagonal = sqrt(x_side*x_side + y_step*y_step);


    float c = sqrt(x_side*x_side + y_side_step*y_side_step);
    float alpha = acos((side_diagonal*side_diagonal + y_side*y_side - c*c) / 2.f / side_diagonal / y_side);

    // Site for turn
    turn1.x = (side_diagonal - model->length_side) / 2.f;
    turn1.y = model->y_default + model->y_step / 2.f;
    turn0.x = turn1.x - y_side * cos(alpha);
    turn0.y = y_side * sin(alpha) - turn1.y - model->length_side;

    /*Serial.println("Turn positions :");
      Serial.print(turn0.x);
      Serial.print(" ");
      Serial.println(turn0.y);
      Serial.print(turn1.x);
      Serial.print(" ");
      Serial.println(turn1.y);*/

    for (int i = 0; i < 4; i++) {
        armController.getArm(i).setCurrentPos({model->x_default, model->y_default + model->y_step,
                model->z_boot});
    }
    armWait();
}

void Motion4::armMove(int index, Vectorf pos, bool wait)
{
    //current_speed
    armController.addPosition({Order::POS, (uint8_t)index, current_speed, pos});
    if (wait) {
        armWait();
    }
}

void Motion4::armWait()
{
    armController.addPosition({Order::WAIT});
    armController.process_orders(); // process current orders because need to wait
}

void Motion4::turn_left(bool lastmovement)
{
    current_speed = model->spot_turn_speed;
    armMove(0, {KEEP, KEEP, model->z_up}, true);
    armMove(0, {turn0.x, turn0.y, model->z_up}, true);
    armMove(0, {turn0.x, turn0.y, model->z_default}, true);

    armMove(1, {KEEP, KEEP, model->z_up}, true);
    armMove(1, {turn1.x, turn1.y, model->z_up}, true);
    armMove(1, {turn1.x, turn1.y, model->z_default}, true);

    armMove(3, {KEEP, KEEP, model->z_up}, true);
    armMove(3, {turn0.x, turn0.y, model->z_up}, true);
    armMove(3, {turn0.x, turn0.y, model->z_default}, true);

    armMove(2, {KEEP, KEEP, model->z_up}, true);
    armMove(2, {turn1.x, turn1.y, model->z_up}, true);
    armMove(2, {turn1.x, turn1.y, model->z_default}, true);

    armMove(0, {turn1.x, turn1.y, model->z_default});
    armMove(1, {turn0.x, turn0.y, model->z_default});
    armMove(2, {turn0.x, turn0.y, model->z_default});
    armMove(3, {turn1.x, turn1.y, model->z_default}, true); //TURN

    //If last movement, reset arm to blue point for next movement.
    //Avoid useless reset to center
    if (lastmovement) {
        armMove(0, {KEEP, KEEP, model->z_up}, true);
        armMove(0, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(0, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(1, {KEEP, KEEP, model->z_up}, true);
        armMove(1, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(1, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(3, {KEEP, KEEP, model->z_up}, true);
        armMove(3, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(3, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(2, {KEEP, KEEP, model->z_up}, true);
        armMove(2, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(2, {model->x_default, model->y_default + model->y_step, model->z_default}, true);
    }
}

void Motion4::turn_right(bool lastmovement)
{
    current_speed = model->spot_turn_speed;
    armMove(0, {KEEP, KEEP, model->z_up}, true);
    armMove(0, {turn1.x, turn1.y, model->z_up}, true);
    armMove(0, {turn1.x, turn1.y, model->z_default}, true);

    armMove(1, {KEEP, KEEP, model->z_up}, true);
    armMove(1, {turn0.x, turn0.y, model->z_up}, true);
    armMove(1, {turn0.x, turn0.y, model->z_default}, true);

    armMove(3, {KEEP, KEEP, model->z_up}, true);
    armMove(3, {turn1.x, turn1.y, model->z_up}, true);
    armMove(3, {turn1.x, turn1.y, model->z_default}, true);

    armMove(2, {KEEP, KEEP, model->z_up}, true);
    armMove(2, {turn0.x, turn0.y, model->z_up}, true);
    armMove(2, {turn0.x, turn0.y, model->z_default}, true);

    armMove(0, {turn0.x, turn0.y, model->z_default});
    armMove(1, {turn1.x, turn1.y, model->z_default});
    armMove(2, {turn1.x, turn1.y, model->z_default});
    armMove(3, {turn0.x, turn0.y, model->z_default}, true); //TURN

    //If last movement, reset arm to blue point for next movement.
    //Avoid useless reset to center
    if (lastmovement) {
        armMove(0, {KEEP, KEEP, model->z_up}, true);
        armMove(0, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(0, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(1, {KEEP, KEEP, model->z_up}, true);
        armMove(1, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(1, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(3, {KEEP, KEEP, model->z_up}, true);
        armMove(3, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(3, {model->x_default, model->y_default + model->y_step, model->z_default}, true);

        armMove(2, {KEEP, KEEP, model->z_up}, true);
        armMove(2, {model->x_default, model->y_default + model->y_step, model->z_up}, true);
        armMove(2, {model->x_default, model->y_default + model->y_step, model->z_default}, true);
    }
}

void Motion4::turn_angle(uint16_t angle)
{
    
    //testing code for angle rotation
    double w = 7.15; //longueur araignee en cm (R2L1)
    double h = 6.5; //largeur araignee cm (R2R1)
    double xm; //coordonnees de l'intersection entre D1 et sa perpendiculaire 
    double ym; // a la distance w sur D1
    double beta; //angle abscisses / D1 en radian
    double alpha = deg2rad (OUVERTURE_ANGULAIRE_DEGRE_PAS_ROTATION); //ouverture anglaire d'un pas de rotation en radian
    double xp; //intersection perpendiculaire / abscisses
    double gamma1; //angle abscisses droite inferieure ouverture angulaire en radian
    double gamma2; //angle abscisses droite superieure ouverture angulaire en radian
    double xpr, ypr; //coordonnees du point rouge
    double xpj, ypj; //coordonnees du point jaune
    
    beta = atan(h/w);
    xm = w * cos(beta);
    ym = w * sin (beta);
    xp = w / cos (beta);
    gamma1 = beta - alpha / 2.; 
    gamma2 = beta + alpha / 2.;
    xpr = -(ym*xp) /((xm-xp)*tan (gamma1) - ym);
    ypr = xpr * tan(gamma1);  
    xpj = -(ym*xp) /((xm-xp)*tan (gamma2) - ym);
    ypj = xpj * tan(gamma2);  
    float turn1x = xpr;
    float turn1y = ypr;
    float turn0x = xpj;
    float turn0y = ypj;

    current_speed = model->spot_turn_speed;
    armMove(0, {KEEP, KEEP, model->z_up}, true);
    armMove(0, {turn1.x, turn1.y, model->z_up}, true);
    armMove(0, {turn1.x, turn1.y, model->z_default}, true);

    armMove(1, {KEEP, KEEP, model->z_up}, true);
    armMove(1, {turn0.x, turn0.y, model->z_up}, true);
    armMove(1, {turn0.x, turn0.y, model->z_default}, true);

    armMove(3, {KEEP, KEEP, model->z_up}, true);
    armMove(3, {turn1.x, turn1.y, model->z_up}, true);
    armMove(3, {turn1.x, turn1.y, model->z_default}, true);

    armMove(2, {KEEP, KEEP, model->z_up}, true);
    armMove(2, {turn0.x, turn0.y, model->z_up}, true);
    armMove(2, {turn0.x, turn0.y, model->z_default}, true);

    armMove(0, {turn0.x, turn0.y, model->z_default});
    armMove(1, {turn1.x, turn1.y, model->z_default});
    armMove(2, {turn1.x, turn1.y, model->z_default});
    armMove(3, {turn0.x, turn0.y, model->z_default}, true); //TURN

}

void Motion4::step_forward()
{
    //TODO add the step forward
    direction::FORWARD;
    current_speed = model->leg_move_speed;
    armMove(0, {KEEP, KEEP, model->z_up}, true);
    armMove(0, {model->x_default, model->y_default + 2.f * model->y_step, KEEP}, true);
    armMove(0, {KEEP, KEEP, model->z_default}, true);

    current_speed = model->body_move_speed;
    armMove(3, {model->x_default, model->y_default + 2.f * model->y_step, model->z_default});
    armMove(2, {model->x_default, model->y_default + 0.f * model->y_step, model->z_default});
    armMove(1, {model->x_default, model->y_default + 2.f * model->y_step, model->z_default});
    armMove(0, {model->x_default, model->y_default + 1.f * model->y_step, model->z_default}, true);

    current_speed = model->leg_move_speed;
    armMove(1, {KEEP, KEEP, model->z_up}, true);
    armMove(1, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(1, {KEEP, KEEP, model->z_default}, true);

    armMove(3, {KEEP, KEEP, model->z_up}, true);
    armMove(3, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(3, {KEEP, KEEP, model->z_default}, true);

    armMove(2, {KEEP, KEEP, model->z_up}, true);
    armMove(2, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(2, {KEEP, KEEP, model->z_default}, true);
}

void Motion4::step_back()
{
    // Set direction
    direction = direction::BACKWARD;
    current_speed = model->leg_move_speed;
    armMove(3, {KEEP, KEEP, model->z_up}, true);
    armMove(3, {model->x_default, model->y_default + 2.f * model->y_step, KEEP}, true);
    armMove(3, {KEEP, KEEP, model->z_default}, true);

    current_speed = model->body_move_speed;
    armMove(0, {model->x_default, model->y_default + 2.f * model->y_step, model->z_default});
    armMove(1, {model->x_default, model->y_default + 0.f * model->y_step, model->z_default});
    armMove(2, {model->x_default, model->y_default + 2.f * model->y_step, model->z_default});
    armMove(3, {model->x_default, model->y_default + 1.f * model->y_step, model->z_default}, true);

    current_speed = model->leg_move_speed;
    armMove(2, {KEEP, KEEP, model->z_up}, true);
    armMove(2, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(2, {KEEP, KEEP, model->z_default}, true);

    armMove(0, {KEEP, KEEP, model->z_up}, true);
    armMove(0, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(0, {KEEP, KEEP, model->z_default}, true);

    armMove(1, {KEEP, KEEP, model->z_up}, true);
    armMove(1, {model->x_default, model->y_default + 1.f * model->y_step, KEEP}, true);
    armMove(1, {KEEP, KEEP, model->z_default}, true);
}

void Motion4::default_pos()
{
    for (int i = 0; i < 4; i++) {
        armMove(i, {model->x_default, model->y_default + model->y_step,
                model->z_boot});
    }
    for (int i = 0; i < 4; i++) {
        armMove(i, {model->x_default, model->y_default + model->y_step,
                model->z_boot}, true);
    }
}

void Motion4::sit()
{
    current_speed = model->stand_seat_speed;

    for (int i = 0; i < 4; i++)
        armMove(i, {KEEP, KEEP, model->z_boot});

    armWait();
}


void Motion4::stand()
{
    current_speed = model->stand_seat_speed;

    for (int i = 0; i < 4; i++)
        armMove(i, {KEEP, KEEP, model->z_default});

    armWait();
}



double Motion4::rad2deg(double angleRadian){

	return (180. *  angleRadian / M_PI);
}

double Motion4::deg2rad(double angleDegre){
	return (angleDegre * M_PI / 180.);
}
