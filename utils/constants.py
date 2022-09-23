import time

# shows debug markers
DEBUG_MARKERS = False
# shows debug robot helpers
DEBUG_ROBOT = True

# camera frame width and height
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# delay between each point when moving mouse
DELAY_MS = 25

# distance between each interpolated point
DISTANCE = 60

# return current time in MS
CURRENT_TIME = lambda: time.time() * 1000
