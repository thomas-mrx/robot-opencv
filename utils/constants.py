# shows debug markers
DEBUG_MARKERS = False
# shows debug robot helpers
DEBUG_ROBOT = False
# shows interpolated points
DEBUG_INTERPOLATION = False

# camera frame width and height
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# delay between each point when moving mouse
DELAY_MS = 25

# distance between each interpolated point
DISTANCE = 60

# angle minimum safeguard value for direction (in degrees)
# - this margin value will be used if the robot is further than ANGLE_DISTANCE distance (in pixels on the webcam frame)
# - else it will automatically be wider proportionally to the distance (i.e. ANGLE_MARGIN_MAX tolerance when robot is really nearby ANGLE_MIN_DISTANCE dist.)
# - when distance is lower than ANGLE_MIN_DISTANCE, current interpolated point will be collected and cursor will switch to the next one
# - /!\ ANGLE_MAX_DISTANCE > ANGLE_MIN_DISTANCE ==> ANGLE_MAX_DISTANCE != ANGLE_MIN_DISTANCE
ANGLE_MIN_MARGIN = 20
ANGLE_MAX_MARGIN = 110
ANGLE_MIN_DISTANCE = 20
ANGLE_MAX_DISTANCE = 60

# video source for position detection (used in a VideoCapture object from OpenCV)
# - can be an index (0 for main device camera, 1 for external USB camera if device has another one) or a file sequence or a webcam URL
# - see doc for more: https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
VIDEO_SRC = 0

# arduino remote serial port address
REMOTE_PORT = 'COM4'

# serial sending interval in ms if the order is the same as the last one
SERIAL_INTERVAL = 25

# duration of a game (in milliseconds)
GAME_DURATION = 60000
