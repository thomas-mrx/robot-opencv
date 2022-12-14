import math
import random

import cv2
import numpy as np

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from src.game import Game
from src.pathfinder import Pathfinder, Order
from utils.constants import DELAY_MS, FRAME_WIDTH, ANGLE_MIN_DISTANCE
from utils.functions import midpoint, hsv2bgr, current_time


class Draw:
    def __init__(self):
        self.activePathfinder = None
        self.activeGame = None
        self.currentLayer = 0
        self.layers = [[], [], [], []]
        self.pathfinders = [None, None, None, None]
        self.games = [None, None, None, None]
        self.boundaries = Polygon()
        self.active = False
        self.lastInteraction = current_time()
        self.animateX = 0
        self.animateY = 1
        self.color_init = [0, 0, 0, 0]
        self.progressionIndex = [0, 0, 0, 0]

    def empty_layer(self, i=-1):
        if i == -1:
            i = self.currentLayer
        self.layers[i] = []
        if self.pathfinders[i] == self.activePathfinder:
            if self.activePathfinder:
                self.activePathfinder.send_order("LOSE")
            self.activePathfinder = None
            self.activeGame = None
        self.pathfinders[i] = None
        self.progressionIndex[i] = 0
        self.games[i] = None

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

    def get_game(self):
        return self.activeGame

    def set_pathfinder(self):
        self.activeGame = self.games[self.currentLayer]
        self.activePathfinder = self.pathfinders[self.currentLayer]

    def get_pathfinder(self):
        return self.activePathfinder

    def is_pathfinder_active(self, i=-1):
        if i == -1:
            i = self.currentLayer
        return self.activePathfinder and self.pathfinders[i] == self.activePathfinder

    def set_progression_index(self, val):
        if val > self.progressionIndex[self.currentLayer]:
            self.progressionIndex[self.currentLayer] = val

    def event_handler(self, event, x, y, flags, params):
        y = y - params["app"].uiManager.toolbarSize
        robot_position = params["app"].robotPosition()
        in_boundaries = self.boundaries.contains(Point(x, y))

        if event == cv2.EVENT_LBUTTONDOWN and in_boundaries and math.dist(robot_position, (x, y)) < 20 and not self.is_pathfinder_active():
            self.active = True
            self.pathfinders[self.currentLayer] = None
            self.progressionIndex[self.currentLayer] = 0
            self.layers[self.currentLayer] = []
            self.layers[self.currentLayer].append(robot_position)
            self.color_init[self.currentLayer] = random.uniform(0, 1)
            self.lastInteraction = current_time()

        elif self.active and (event == cv2.EVENT_LBUTTONUP or not in_boundaries):
            self.active = False
            self.layers[self.currentLayer].append((x, y))
            self.pathfinders[self.currentLayer] = Pathfinder(self.layers[self.currentLayer], params["app"])
            self.lastInteraction = current_time()

        elif self.active and event == cv2.EVENT_MOUSEMOVE and self.lastInteraction + DELAY_MS < current_time():
            self.layers[self.currentLayer].append((x, y))
            self.lastInteraction = current_time()

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

            if self.pathfinders[self.currentLayer] and self.pathfinders[
                self.currentLayer] == self.activePathfinder and i <= self.pathfinders[
                self.currentLayer].get_current_point() and math.dist(robot_pos, (x, y)) < ANGLE_MIN_DISTANCE:
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
                perspectiveFactor = 1 - min(0.75, max(abs(corners[0][0] - corners[3][0]), abs(corners[1][0] - corners[2][0])) / (FRAME_WIDTH * 0.075))
                scale = min(1, 1 - scaleFactor + perspectiveFactor)

            if last_point:
                color = hsv2bgr(color_random, 1, 1)
                if i <= self.progressionIndex[self.currentLayer]:
                    cv2.line(frame, last_point, (x, y), color, max(math.ceil(6 * scale), 1))
                cv2.line(transparency, last_point, (x, y), color, max(math.ceil(6 * scale), 1))
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
        mask_array = cv2.inRange(frame, np.array([0, 0, 0]), np.array([0, 0, 0]))
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
                cv2.line(frame, limitStart if self.animateX > 0 else start, limitEnd if self.animateX < 0 else end,
                         (255, 255, 255), 4)
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
        if not self.games[self.currentLayer] and not self.boundaries.is_empty:
            coords = self.boundaries.exterior.coords[:-1]
            self.games[self.currentLayer] = Game(coords, random.randint(2, 5))
        if self.games[self.currentLayer]:
            frame = self.games[self.currentLayer].render(frame, robot_pos, self.is_pathfinder_active())
            if self.is_pathfinder_active():
                if self.games[self.currentLayer].remaining_time == 0:
                    self.pathfinders[self.currentLayer].send_order("LOSE")
                    self.activePathfinder = None
                    self.pathfinders[self.currentLayer] = None
                elif self.games[self.currentLayer].win():
                    self.pathfinders[self.currentLayer].send_order("WIN")
                    self.activePathfinder = None
                    self.pathfinders[self.currentLayer] = None
                elif self.games[self.currentLayer].has_stopped():
                    self.pathfinders[self.currentLayer].send_order("STOP")
                    self.activePathfinder = None
                    self.pathfinders[self.currentLayer] = None
        return frame
