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

# angle safeguard value for direction (in degrees)
ANGLE_MARGIN = 10

# video source for position detection (used in a VideoCapture object from OpenCV)
# - can be an index (0 for main device camera, 1 for external USB camera if device has another one) or a file sequence or a webcam URL
# - see doc for more: https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
VIDEO_SRC = 0

# arduino remote serial port address
REMOTE_PORT = '/dev/ttyS0'

# duration of a game (in milliseconds)
GAME_DURATION = 20000
