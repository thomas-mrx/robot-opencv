## Installation / Requirements

``pip install opencv-python==4.5.5.62``

``pip install opencv-contrib-python``

``pip install numpy``

``pip install shapely``

``pip install pyserial``

> ⚠️ If a bug occurs during the importation of **serial** module (" ...has no attribute 'Serial' "), please do ``pip uninstall serial`` & ``pip uninstall pyserial`` **and then** reinstall **pyserial** using ``pip install pyserial``. 

## Configuration

Configure common variables (such as angle margin, game timer, video source, serial port for remote, etc.) in the ```utils/constants.py``` file (see comments in the file for full documentation about the variables).

## In-App Shortcuts

``q`` quit the app nicely

``d`` enable/disable debug mode

``r`` reload every layer (a.k.a. randomize coins everywhere and delete all drawings)

## Arduino

Both Arduino codes for the remote and the spider are located in the ```arduino``` folder. Few updates have been made into these and are required to allow this project to run smoothly.