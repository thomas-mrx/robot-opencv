import math
from random import randint

import cv2

from utils.constants import FRAME_WIDTH
from utils.functions import current_time

class Coin:

    def __init__(self, x, y, size, max_frame):
        self.x = int(x - (size/2))
        self.y = int(y - (size/2))
        self.size = int(size)
        self.current_frame = randint(0, max_frame)
        self.max_frame = max_frame
        self.buffer = []

    def next_frame(self):
        self.current_frame = int((self.current_frame + 1) % self.max_frame)

    def draw(self, frame):
        pixel_count = 0
        for row in self.buffer[self.current_frame]:
            for pixel in row:
                if sum(pixel) > 10:
                    frame[self.y + math.floor(pixel_count / self.size), self.x + (pixel_count % self.size), :] = pixel
                pixel_count += 1
        return frame


class Game:

    def __init__(self, min_bound, max_bound, coin_number):
        self.min = min_bound
        self.max = max_bound
        self.last_draw = 0
        self.coins = []

        coin = cv2.VideoCapture("static/coin.mp4")
        base_size = FRAME_WIDTH / 20

        for i in range(0, coin_number):
            # do even distribution on x by splitting by coin number
            part = int((max_bound[0] - min_bound[0]) / coin_number)
            x = randint(min_bound[0] + (part * i), min_bound[0] + (part * (i + 1)))
            y = randint(min_bound[1], max_bound[1])

            # distance check between coins, too slow + distance is fine without it
            # x = y = None
            # distance = FRAME_WIDTH
            # while not x or not y or distance < 2:
            #     x = randint(min_bound[0], max_bound[0])
            #     y = randint(min_bound[1], max_bound[1])
            #     for c in self.coins:
            #         c_dist = math.dist((x, y), (c.x, c.y))
            #         if c_dist < distance:
            #             distance = c_dist
            #     cv2.waitKey(25)
            bottomY = max_bound[1]
            topY = min_bound[1]
            if bottomY == topY:
                scaleFactor = 0
            else:
                scaleFactor = ((y - bottomY) / (topY - bottomY))
            scale = 1.5 - scaleFactor
            self.coins.append(Coin(x, y, int(scale * base_size), coin.get(cv2.CAP_PROP_FRAME_COUNT)))

        while coin.get(cv2.CAP_PROP_POS_FRAMES) < coin.get(cv2.CAP_PROP_FRAME_COUNT):
            success, image = coin.read()
            if success:
                for c in self.coins:
                    c.buffer.append(cv2.resize(image, (c.size, c.size), interpolation=cv2.INTER_AREA))

    def render(self, frame, robot_pos, active):
        if self.last_draw + 80 < current_time():
            for c in self.coins:
                c.next_frame()
            self.last_draw = current_time()

        remove_coins = []
        for c in self.coins:
            frame = c.draw(frame)
            if active and math.dist((c.x + (c.size/2), c.y + (c.size/2)), robot_pos) < 20:
                remove_coins.append(c)

        for c in remove_coins:
            self.coins.remove(c)

        return frame

