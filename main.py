# import the necessary packages
import math

import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str,
                default="DICT_ARUCO_ORIGINAL",
                help="type of ArUCo tag to detect")
args = vars(ap.parse_args())

# define names of each possible ArUco tag OpenCV supports
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    #  "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    #  "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    #  "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    #  "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

# verify that the supplied ArUCo tag exists and is supported by
# OpenCV
if ARUCO_DICT.get(args["type"], None) is None:
    print("[INFO] ArUCo tag of '{}' is not supported".format(
        args["type"]))
    sys.exit(0)

# load the ArUCo dictionary and grab the ArUCo parameters
print("[INFO] detecting '{}' tags...".format(args["type"]))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
arucoParams = cv2.aruco.DetectorParameters_create()

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()
time.sleep(2.0)

mainCorners = [None, None, None, None]
bottomY=0
topY=0
circles = []
lastrecord = time.time() * 1000
drawing = False
delayMs = 25
distance = 60
polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
botPosition = (0,0)
botFront = (0,0)
botBack = (0,0)


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global lastrecord, circles, drawing,delayMs,polygon
    point = Point(x, y)

    if event == cv2.EVENT_LBUTTONDOWN and polygon.contains(point) and math.dist(botPosition, (x,y)) < 20:
        drawing = True
        circles = []
        circles.append(botPosition)
        lastrecord = time.time() * 1000
    elif drawing and (event == cv2.EVENT_LBUTTONUP or not polygon.contains(point)):
        drawing = False
        circles.append((x,y))
        lastrecord = time.time() * 1000
    elif drawing and event == cv2.EVENT_MOUSEMOVE and lastrecord + delayMs < time.time() * 1000:
        circles.append({x: x, y: y})
        lastrecord = time.time() * 1000

cv2.namedWindow("Frame", cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('Frame', draw_circle)


def midpoint(p1, p2, ratio = 0.5):
    return (int((p1[0]*ratio+p2[0]*(1-ratio))), int((p1[1]*ratio+p2[1]*(1-ratio))))
# loop over the frames from the video stream
animate = 0
animateOff = 1

while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 600 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=1000)

    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
                                                       arucoDict, parameters=arucoParams)

    overlay = frame.copy()
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            #cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            #cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            #cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            #cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            #cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            if markerID < 4 and (not mainCorners[markerID] or math.dist((cX, cY), mainCorners[markerID]) < 50):
                mainCorners[markerID] = (cX, cY)

            if polygon.contains(Point(cX,cY)):
                if markerID == 4:
                    botFront = (cX,cY)
                elif markerID == 5:
                    botBack = (cX,cY)

            markerName = ""
            if markerID == 0:
                markerName = "Bottom Left"
            elif markerID == 1:
                markerName = "Bottom Right"
            elif markerID == 2:
                markerName = "Top Right"
            elif markerID == 3:
                markerName = "Top Left"
            elif markerID == 4:
                markerName = "Front"
            elif markerID == 5:
                markerName = "Back"
            # draw the ArUco marker ID on the frame
            cv2.putText(frame, markerName,
                        (topLeft[0] + 20, topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 255) if markerID > 3 else (255, 0, 0), 2)

        if len(mainCorners) == 4 and len([i for i in mainCorners if i is not None]) == 4:
            polygon = Polygon([mainCorners[0], mainCorners[1], mainCorners[2], mainCorners[3]])
            contours = np.array(mainCorners)
            cv2.fillPoly(overlay,  pts=[contours], color=(255, 255, 255))
            animate -= 0.01
            animateOff -= 0.01
            xLine = midpoint(mainCorners[0], mainCorners[1])
            yLine = midpoint(mainCorners[1], mainCorners[2])
            for id, c in enumerate(mainCorners):
                #print("an:"+str(animate)+", anO:"+str(animateOff))
                limitStart = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], 1)
                limitEnd = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], 0)
                if id % 2 == 0:
                    start = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], 1+animate)
                    end = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], animate)
                    cv2.line(overlay, limitStart if animate > 0 else start, limitEnd if animate < 0 else end, (255, 0, 0), 4)
                else:
                    start = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], 1.+animateOff)
                    end = midpoint(mainCorners[id], mainCorners[(id+1) % len(mainCorners)], animateOff)
                    cv2.line(overlay, limitStart if animateOff > 0 else start, limitEnd if animateOff < 0 else end, (255, 0, 0), 4)
                if animate < -1:
                    animate = 1
                if animateOff < -1:
                    animateOff = 1
            if mainCorners[0] and mainCorners[3]:
                bottomY = mainCorners[0][1]
                topY = mainCorners[3][1]

    botPosition = midpoint(botFront, botBack)
    cv2.circle(frame, botPosition, 3, (0, 0, 255), -1)
    cv2.arrowedLine(frame, botBack, botFront, (0, 0, 255), 4, tipLength = 0.5)
    lastPoint = None
    lastInter = None
    for xy in circles:
        try:
            x, y = xy
        except ValueError:
            continue
        scale=1
        if mainCorners[0] and mainCorners[3]:
            bottomY = mainCorners[0][1]
            topY = mainCorners[3][1]
            scale = 1.5 - ((y-bottomY)/(topY-bottomY))

        if lastPoint:
            cv2.line(overlay, lastPoint, (x, y), (0, 0, 255), math.ceil(3*scale))

        if not lastInter or math.dist((x, y), lastInter) > distance:
            cv2.circle(frame, (x, y), int(3.5*scale), (0, 255, 0), -1)
            lastInter = (x, y)

        lastPoint = (x, y)

    alpha = 0.50
    result = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    # show the output frame
    cv2.imshow("Frame", result)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()