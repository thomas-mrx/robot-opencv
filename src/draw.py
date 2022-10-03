import math
import random

import cv2
import numpy as np

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from src.pathfinder import Pathfinder
from utils.constants import DELAY_MS, CURRENT_TIME
from utils.functions import midpoint, hsv2bgr


class Draw:
    def __init__(self):
        self.activePathfinder = None
        self.currentLayer = 0
        self.layers = [[], [], [], []]
        self.pathfinders = [None, None, None, None]
        self.boundaries = Polygon()
        self.active = False
        self.lastInteraction = CURRENT_TIME()
        self.animateX = 0
        self.animateY = 1
        self.color_init = [0, 0, 0, 0]
        self.progressionIndex = [0, 0, 0, 0]

    def empty_layer(self):
        self.layers[self.currentLayer] = []
        if self.pathfinders[self.currentLayer] == self.activePathfinder:
            self.activePathfinder = None
        self.pathfinders[self.currentLayer] = None
        self.progressionIndex[self.currentLayer] = 0

    def set_layer(self, i):
        self.currentLayer = i

    def get_layer(self, i=-1):
        if i == -1:
            i = self.currentLayer
        return self.layers[i]

    def get_color(self, i=-1):
        if i == -1:
            i = self.currentLayer
        return self.color_init[i]

    def set_pathfinder(self):
        self.activePathfinder = self.pathfinders[self.currentLayer]

    def get_pathfinder(self):
        return self.activePathfinder

    def set_progression_index(self, val):
        if val > self.progressionIndex[self.currentLayer]:
            self.progressionIndex[self.currentLayer] = val

    def event_handler(self, event, x, y, flags, params):
        y = y - params["app"].uiManager.toolbarSize
        robot_position = params["app"].robotPosition()
        in_boundaries = self.boundaries.contains(Point(x, y))

        if event == cv2.EVENT_LBUTTONDOWN and in_boundaries and math.dist(robot_position, (x, y)) < 20:
            self.active = True
            self.pathfinders[self.currentLayer] = None
            self.progressionIndex[self.currentLayer] = 0
            self.layers[self.currentLayer] = []
            self.layers[self.currentLayer].append(robot_position)
            self.color_init[self.currentLayer] = random.uniform(0, 1)
            self.lastInteraction = CURRENT_TIME()

        elif self.active and (event == cv2.EVENT_LBUTTONUP or not in_boundaries):
            self.active = False
            self.layers[self.currentLayer].append((x, y))
            self.pathfinders[self.currentLayer] = Pathfinder(self.layers[self.currentLayer], params["app"])
            self.lastInteraction = CURRENT_TIME()

        elif self.active and event == cv2.EVENT_MOUSEMOVE and self.lastInteraction + DELAY_MS < CURRENT_TIME():
            self.layers[self.currentLayer].append((x, y))
            self.lastInteraction = CURRENT_TIME()

    def draw_points(self, frame, robot_pos):
        transparency = frame.copy()
        last_point = None
        color_random = self.color_init[self.currentLayer]
        i = 0
        for xy in self.layers[self.currentLayer]:
            try:
                x, y = xy
            except ValueError:
                continue

            if self.pathfinders[self.currentLayer] and i <= self.pathfinders[self.currentLayer].get_current_point() and math.dist(robot_pos, (x, y)) < 20:
                self.progressionIndex[self.currentLayer] = i

            scale = 1
            corners = self.boundaries.exterior.coords[:-1]
            if corners[0] and corners[3]:
                bottomY = corners[0][1]
                topY = corners[3][1]
                if bottomY == topY:
                    scaleFactor = 0
                else:
                    scaleFactor = ((y - bottomY) / (topY - bottomY))
                scale = 1.5 - scaleFactor

            if last_point:
                color = hsv2bgr(color_random, 1, 1)
                if i <= self.progressionIndex[self.currentLayer]:
                    cv2.line(frame, last_point, (x, y), color, max(math.ceil(3 * scale), 1))
                cv2.line(transparency, last_point, (x, y), color, max(math.ceil(3 * scale), 1))
                color_random += 0.01
                if color_random > 1:
                    color_random = 0

            last_point = (x, y)
            i += 1

        alpha = 0.25
        frame = cv2.addWeighted(transparency, alpha, frame, 1 - alpha, 0)
        return frame

    def draw_playground(self, frame):
        contours = np.array(self.boundaries.exterior.coords[:-1]).astype(int)
        mask_array = cv2.inRange(frame, np.array([0,0,0]), np.array([0,0,0]))
        cv2.fillPoly(mask_array, [contours], (255, 255, 255))
        mask = cv2.bitwise_and(frame, frame, mask=mask_array)
        alpha = 0.25
        frame = cv2.addWeighted(frame, alpha, mask, 1 - alpha, 0)
        self.animateX -= 0.01
        self.animateY -= 0.01
        for i in range(0, len(contours)):
            limitStart = midpoint(contours[i], contours[(i + 1) % len(contours)], 1)
            limitEnd = midpoint(contours[i], contours[(i + 1) % len(contours)], 0)
            if i % 2 == 0:
                start = midpoint(contours[i], contours[(i + 1) % len(contours)], 1 + self.animateX)
                end = midpoint(contours[i], contours[(i + 1) % len(contours)], self.animateX)
                cv2.line(frame, limitStart if self.animateX > 0 else start, limitEnd if self.animateX < 0 else end, (255, 255, 255), 4)
            else:
                start = midpoint(contours[i], contours[(i + 1) % len(contours)], 1. + self.animateY)
                end = midpoint(contours[i], contours[(i + 1) % len(contours)], self.animateY)
                cv2.line(frame, limitStart if self.animateY > 0 else start,
                         limitEnd if self.animateY < 0 else end, (255, 255, 255), 4)
            if self.animateX < -1:
                self.animateX = 1
            if self.animateY < -1:
                self.animateY = 1
        return frame

    def render(self, frame, robot_pos, debug):
        frame = self.draw_points(frame, robot_pos)
        frame = self.draw_playground(frame)
        if debug and self.pathfinders[self.currentLayer]:
            self.pathfinders[self.currentLayer].debug(frame)
        return frame
