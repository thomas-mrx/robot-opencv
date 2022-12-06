# Spider arduino

# Architecture

## Motors

Cette partie sert à gérer les moteurs directement.
Elle s'occupe d'utiliser le bon driver en fonction du moteur (Servo.h pour des servomoteurs classiques).
On renseigne les pin utilisé et cette partie expose un tableau de 0 à N moteurs pour s'abstraire du numéro des pin.

## ArmController
Le Arm controller s'occupe d'ordonnancer les pattes, et de les initialiser.
Le controller peut avoir N pattes de K noeuds.
Il contient la queue d'ordre à effectuer sur les pattes, et va les ordonnancer dans le bon ordre en prenant en compte le temps.

### Arm

Le Arm (Bras) est initialisé par la liste de ses moteurs (identifiants issue de Motors), la longeur entre chaque axe, et la fonctions de transformation pour passer du repère mathématique au repère réel.

Cet objet correspond au bras, il va gérer sont déplacement.

#### Kinematics
Cet partie est la partie calcul de la cinématique du bras. C'est ici que le caclul de la cinématique inverse est fait et que la calibration est calculée puis sauvegardée.

## Body

Le body initialise tous les composants de l'arraignée.
On peut lui envoyer une trajectoire de mouvement.

### Motion

Motion comporte les enchainement qui permettent le mouvement de l'arraignée.

Ainsi la fonction step_forward(); contient l'enchainement de position des pattes pour effectuer un mouvement vers l'avant.

## Trajectory

Cette partie la sert a planifier la trajectoire de l'arraignée.
La ou le bras s'occupe du mouvement des servo, le body du mouvement des de tous les bras, la trajectoire c'est l'enchainement (avant, arrière, gauche, droite) pour suivre une trajectoire.

# Exemples

## Setup
Ainsi un code de base d'exemple serait :
```
#include <Arduino.h>
#include "motors.h"
#include "armcontroller.h"
#include "body.h"

//List of servo pins connected to the arduino
// Hanche / Femur / Tibia
int servo_pin[12] = { 4,  2,  3,
                      7,  5,  6,
                      16,  14, 15,
                      19, 17, 18
                    };

//Controller motors
Motors<MOTORS_NUMBER> motors;

// On choisit 4 bras qui ont chacun 3 axes
ArmController<4, 3> armController{motors};
Vectorf corrections[] = {{100, 70, 42}, {100, 70, 42}, {100, 70, 42}, {100, 70, 42}};

// On choisit le modèle d'arraignée (toutes les dimensions)
SpiderJDMI model;
//On utilise un body à 4 bras
Body4 body(armController, model);

// L'object qui gère et stock la trajectoire
Trajectory trajectory;

void setup()
{
    Serial.begin(115200);
    motors.attachServo(servo_pin); //First things to do. Arms will go to neutral
    body.init(corrections);
    trajectory.setup(); // Load of the trajectory to do
}
```
Le setup de l'arraignée classique commenté.

## Cas classique

La fonction loop s'adaptera en fonction des besoins.
Dans le cas classique ou l'arraignée suivra le trajet :
```
void loop()
{
    trajectory.reset(); //Reset trajectory position to 0
    body.process(trajectory); // Do the trajectory supplied
    armController.process_orders(); // process last orders
}
```

## Calibration

Avant la marche, il sera nécessaire de faire la calibration des servomoteurs.
Pour se faire on place les pattes à {100, 70, 15} pour les mesurer sur la mire de calibration.

```
void loop()
{
    for (int i = 0; i < 4; i++) {
        armController.addPosition({Order::POS, i, 10000, {100, 70, 15}});
        armController.addPosition({Order::WAIT});
    }
    armController.process_orders();
    delay(1000);
}
```
On messure les position à l'aide de la règle graduée et on place ces positions dans :
```
Vectorf corrections[] = {{100, 70, 42}, {100, 70, 42}, {100, 70, 42}, {100, 70, 42}};
```
Vous êtes sensé mesurer {100, 70, 42} car 42 - 27 = 15. Il faut compenser pour la hauteur des bras au sol.

La valeur mesurée directement depuis la grille doit donc être mise dans le tableau corrections.

## Mouvement d'une patte

```
void loop()
{
    for (int i = 0; i < 4; i++) {
      armController.addPosition({Order::POS, i, 1000, {100, 70, 15}});
    }

    float speed = 200;
    armController.addPosition({Order::POS, 0, speed, {140, 10, -27}});
    armController.addPosition({Order::WAIT});
    armController.addPosition({Order::POS, 0, speed, {90, 10, -27}});
    armController.addPosition({Order::WAIT});
    armController.addPosition({Order::POS, 0, speed, {90, 80, -27}});
    armController.addPosition({Order::WAIT});

    armController.process_orders();
    delay(1000);
}
```

