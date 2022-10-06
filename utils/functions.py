import colorsys
import math
import time

import numpy as np


def midpoint(p1, p2, ratio=0.5):
    return int((p1[0] * ratio + p2[0] * (1 - ratio))), int((p1[1] * ratio + p2[1] * (1 - ratio)))


def dot(vA, vB):
    return vA[0] * vB[0] + vA[1] * vB[1]


def ang(lineA, lineB, returnRadian=False):
    # Get nicer vector form
    vA = [(lineA[0][0] - lineA[1][0]), (lineA[0][1] - lineA[1][1])]
    vB = [(lineB[0][0] - lineB[1][0]), (lineB[0][1] - lineB[1][1])]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA) ** 0.5
    magB = dot(vB, vB) ** 0.5
    if magA == 0 or magB == 0 or magA / magB == 0:
        return 0
    # Get cosine value
    cos_ = dot_prod / magA / magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod / magB / magA)
    if returnRadian:
        return angle
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle) % 360

    if ang_deg - 180 >= 0:
        # As in if statement
        return 360 - ang_deg
    else:
        return ang_deg


def remap(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def hsv2bgr(h, s, v):
    color = tuple(np.flip(np.array(tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v)))))
    return [int(c) for c in color]


# return current time in MS
def current_time():
    return time.time() * 1000
