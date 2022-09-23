import math
import numpy as np
import cv2
from shapely.geometry import Point, Polygon

from src.draw import Draw
from utils.constants import DISTANCE, FRAME_WIDTH, FRAME_HEIGHT, DEBUG_MARKERS, DEBUG_ROBOT
from utils.functions import midpoint


class App:
    def __init__(self, name="live transmission"):
        self.name = name

        self.arGroundMarkers = {
            'bottom_left': None,
            'bottom_right': None,
            'top_right': None,
            'top_left': None
        }
        self.arRobotMarkers = {
            'front': None,
            'back': None
        }
        self.robotFront = (0, 0)
        self.robotBack = (0, 0)
        self.robotPosition = lambda: midpoint(self.robotFront, self.robotBack)

        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
        self.arucoDetector = cv2.aruco.DetectorParameters_create()

        self.drawingManager = Draw()

    def loop(self):
        cv2.namedWindow(self.name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.name, self.drawingManager.append_point, {'app': self})

        cap = cv2.VideoCapture(0)
        cap.set(3, FRAME_WIDTH)
        cap.set(4, FRAME_HEIGHT)

        while cap.isOpened():

            success, frame = cap.read()
            if success:
                # detect ArUco markers in the input frame
                (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, self.arucoDict, parameters=self.arucoDetector)

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
                        if DEBUG_MARKERS:
                            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

                        # compute and draw the center (x, y)-coordinates of the
                        # ArUco marker
                        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                        # cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

                        marker_name = ""
                        if 0 <= markerID <= 3:
                            marker_name = list(self.arGroundMarkers)[markerID]
                            self.arGroundMarkers[marker_name] = (cX, cY)
                        elif markerID == 4:
                            marker_name = "Front"
                            self.robotFront = (cX, cY)
                        elif markerID == 5:
                            marker_name = "Back"
                            self.robotBack = (cX, cY)

                        # draw the ArUco marker name on the frame
                        if DEBUG_MARKERS:
                            cv2.putText(frame, marker_name,
                                        (topLeft[0] + 20, topLeft[1] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5, (0, 0, 255) if markerID > 3 else (255, 0, 0), 2)

                    if len([v for k, v in self.arGroundMarkers.items() if v is not None]) == 4:
                        self.drawingManager.boundaries = Polygon([*self.arGroundMarkers.values()])

                # if debug robot, draw helpers
                if DEBUG_ROBOT and self.robotBack != (0, 0) and self.robotFront != (0, 0):
                    cv2.circle(frame, self.robotPosition(), 3, (0, 0, 255), -1)
                    cv2.arrowedLine(frame, self.robotBack, self.robotFront, (0, 0, 255), 4, tipLength=0.5)

                # if all markers are in the scene, draw the playground
                if not self.drawingManager.boundaries.is_empty:
                    frame = self.drawingManager.render(frame)

                cv2.imshow(self.name, frame)

                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break

        cv2.destroyAllWindows()
