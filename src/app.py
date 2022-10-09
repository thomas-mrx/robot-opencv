import os
import sys

import cv2
from shapely.geometry import Polygon

from src.draw import Draw
from src.ui import Ui
from utils.constants import FRAME_WIDTH, FRAME_HEIGHT, DEBUG_MARKERS, DEBUG_ROBOT, VIDEO_SRC
from utils.functions import midpoint

class App:
    def __init__(self, name="live transmission"):
        self.name = name

        self.debug = False

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
        self.uiManager = Ui(self.drawingManager)

    def event_dispatcher(self, event, x, y, flags, params):
        if x < FRAME_WIDTH and y > self.uiManager.toolbarSize:
            self.uiManager.reset_hover()
            self.drawingManager.event_handler(event, x, y, flags, params)
        else:
            self.uiManager.event_handler(event, x, y, flags, params)

    def loop(self):
        global DEBUG_ROBOT, DEBUG_MARKERS, DEBUG_INTERPOLATION

        cv2.namedWindow(self.name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.name, self.event_dispatcher, {'app': self})

        cap = cv2.VideoCapture(VIDEO_SRC)
        cap.set(3, FRAME_WIDTH)
        cap.set(4, FRAME_HEIGHT)

        try:
            while cap.isOpened():

                ar_status = "Waiting for AR markers..."
                robot_status = "Waiting for Robot markers..."
                DEBUG_ROBOT = DEBUG_MARKERS = DEBUG_INTERPOLATION = self.debug

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

                        markers_found = len([v for k, v in self.arGroundMarkers.items() if v is not None])
                        if markers_found == 4:
                            self.drawingManager.boundaries = Polygon([*self.arGroundMarkers.values()])
                            ar_status = "AR markers OK!"
                        else:
                            ar_status = str(markers_found) + " markers found (4 needed)..."


                    # if all markers are in the scene, draw the playground
                    if not self.drawingManager.boundaries.is_empty:
                        frame = self.drawingManager.render(frame, self.robotPosition(), self.debug)

                    # if robot is in the scene, draw helpers
                    if self.robotBack != (0, 0) and self.robotFront != (0, 0):
                        robot_position = self.robotPosition()
                        cv2.circle(frame, robot_position, 7, (0, 0, 0), -1)
                        cv2.circle(frame, robot_position, 6, (255, 255, 255), -1)
                        if len(self.drawingManager.get_layer()) == 0:
                            cv2.putText(frame, "Draw from here",
                                        (robot_position[0] + 15, robot_position[1] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.55, (0, 0, 0), 4)
                            cv2.putText(frame, "Draw from here",
                                        (robot_position[0] + 15, robot_position[1] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.55, (255, 255, 255), 2)
                        if DEBUG_ROBOT:
                            cv2.arrowedLine(frame, self.robotBack, self.robotFront, (0, 0, 255), 2, tipLength=0.5)
                        x, y = midpoint(self.robotBack, self.robotFront)
                        robot_status = "Robot markers OK! - x: " + str(x) + " - y: " + str(y)

                    self.uiManager.toolbarMessage = ar_status + " - " + robot_status + " - Press 'q' to quit"
                    frame = self.uiManager.render(frame)
                    cv2.imshow(self.name, frame)

                    pf = self.drawingManager.get_pathfinder()
                    if pf:
                        pf.next_point()

                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("d"):
                        self.debug = not self.debug

                    if key == ord("r"):
                        self.drawingManager.games = [None, None, None, None]

                    # if the `q` key was pressed, break from the loop
                    if key == ord("q"):
                        break

        except KeyboardInterrupt:
            print('sigint (keyboard)')
            pass

        cap.release()
        cv2.destroyAllWindows()
