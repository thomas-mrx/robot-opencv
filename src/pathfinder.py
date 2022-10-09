import math
import cv2
from numpy import rad2deg

from utils.constants import DISTANCE, ANGLE_MARGIN, REMOTE_PORT, SERIAL_INTERVAL
from utils.functions import ang, current_time


class Pathfinder:
    def __init__(self, points, app_instance):
        self.path = []
        self.currentPoint = 0
        self.originalIndexes = []
        self.app = app_instance
        self.remote = app_instance.serial

        self.lastOrder = None
        self.lastSend = 0

        last_last_point = None
        last_point = points[0]
        i = 0
        self.path.append(points[0])
        self.originalIndexes.append(i)
        for x, y in points:
            angle = 0
            if last_last_point:
                angle = ang([last_last_point, last_point], [last_point, (x, y)])
            dist = math.dist((x, y), last_point)
            if dist > DISTANCE or (angle > 10 and dist > DISTANCE / 2):
                self.path.append((x, y))
                self.originalIndexes.append(i)
                last_last_point = last_point
                last_point = (x, y)
            i += 1
        self.path.append(points[-1])
        self.originalIndexes.append(len(points)-1)

    def get_current_point(self):
        return self.originalIndexes[self.currentPoint % len(self.originalIndexes)]

    def calc_angle(self, robot_position):
        angle1 = math.atan2(self.path[self.currentPoint][1] - robot_position[1],
                            self.path[self.currentPoint][0] - robot_position[0])
        angle2 = math.atan2(self.app.robotFront[1] - robot_position[1], self.app.robotFront[0] - robot_position[0])

        angle_deg = rad2deg(angle2 - angle1)
        if angle_deg > 180:
            angle_deg = -180 + (angle_deg % 180)
        elif angle_deg < -180:
            angle_deg = (angle_deg % 180) if angle1 >= 0 else 180 - (angle_deg % 180)

        return angle_deg

    def debug(self, frame):
        if self.currentPoint >= len(self.path):
            return

        i = 0
        for x, y in self.path:
            cv2.circle(frame, (x, y), 6, (0, 255, 255) if i >= self.currentPoint else (0, 255, 0), -1)
            i += 1
        robot_pos = self.app.robotPosition()
        angle_deg = self.calc_angle(robot_pos)
        radius = math.dist(robot_pos, self.path[self.currentPoint])
        angle = math.atan2(self.app.robotFront[1] - robot_pos[1], self.app.robotFront[0] - robot_pos[0]) + 2 * math.pi
        cv2.circle(frame, robot_pos, int(radius), (0, 255, 255), 1)
        cv2.line(frame, robot_pos, self.path[self.currentPoint], (0, 255, 255), 2)
        cv2.line(frame, robot_pos,
                 (int(robot_pos[0] + (radius * math.cos(angle))), int(robot_pos[1] + (radius * math.sin(angle)))),
                 (0, 0, 255), 2)
        cv2.putText(frame, str(round(rad2deg(math.atan2(self.path[self.currentPoint][1] - robot_pos[1],
                                                        self.path[self.currentPoint][0] - robot_pos[0])), 2)),
                    (self.path[self.currentPoint][0] + 20, self.path[self.currentPoint][1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, str(round(angle_deg, 2)),
                    (self.path[self.currentPoint][0] + 20, self.path[self.currentPoint][1]), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1)

    def send_order(self, order):
        if self.lastOrder != order or self.lastSend + SERIAL_INTERVAL < current_time():
            if self.remote:
                print(f"SENDING \"{order}\" to {REMOTE_PORT}")
                self.remote.write(order.encode())
            else:
                print(f"FAILED TO SEND \"{order}\" to {REMOTE_PORT}. NO SERIAL CONNECTION")
            self.lastOrder = order
            self.lastSend = current_time()

    def next_point(self):
        if self.currentPoint >= len(self.path):
            self.send_order("STOP")
            return

        robot_pos = self.app.robotPosition()
        angle_deg = self.calc_angle(robot_pos)
        if angle_deg > ANGLE_MARGIN:
            self.send_order("LEFT")
        elif angle_deg < -ANGLE_MARGIN:
            self.send_order("RIGHT")
        elif self.currentPoint < len(self.path):
            self.send_order("FORWARD")

        if math.dist(robot_pos, self.path[self.currentPoint]) < 20:
            self.app.drawingManager.set_progression_index(self.get_current_point())
            self.currentPoint += 1

