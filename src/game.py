import math
from random import randint

import cv2

from utils.constants import FRAME_WIDTH, FRAME_HEIGHT, GAME_DURATION, ANGLE_MIN_DISTANCE
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

    def __init__(self, coords, coin_number):
        min_bound = (max(coords[0][0], coords[3][0]), max(coords[2][1], coords[3][1]))
        max_bound = (min(coords[1][0], coords[2][0]), min(coords[0][1], coords[1][1]))
        self.min = min_bound
        self.max = max_bound
        self.last_draw = 0
        self.last_frame = None
        self.coins = []
        self.coin_icon = None
        self.coin_number = coin_number
        self.remaining_time = GAME_DURATION
        self.stopped = False

        coin = cv2.VideoCapture("static/coin.mp4")
        base_size = FRAME_WIDTH / 20

        for i in range(0, coin_number):
            # do even distribution on x by splitting by coin number
            part = int((max_bound[0] - min_bound[0]) / coin_number)
            x = randint(min_bound[0] + (part * i), min_bound[0] + (part * (i + 1)) + 1)
            y = randint(min_bound[1], max_bound[1] + 1)

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
            perspectiveFactor = 1 - min(0.5, max(abs(coords[0][0] - coords[3][0]), abs(coords[1][0] - coords[2][0])) / (FRAME_WIDTH * 0.075))
            scale = min(1, 1 - scaleFactor + perspectiveFactor)
            self.coins.append(Coin(x, y, int(scale * base_size), coin.get(cv2.CAP_PROP_FRAME_COUNT)))
            if not self.coin_icon:
                self.coin_icon = Coin(FRAME_WIDTH - 56, FRAME_HEIGHT - 32, 32, 0)

        while coin.get(cv2.CAP_PROP_POS_FRAMES) < coin.get(cv2.CAP_PROP_FRAME_COUNT):
            success, image = coin.read()
            if success:
                if len(self.coin_icon.buffer) == 0:
                    self.coin_icon.buffer.append(cv2.resize(image, (self.coin_icon.size, self.coin_icon.size), interpolation=cv2.INTER_AREA))
                for c in self.coins:
                    c.buffer.append(cv2.resize(image, (c.size, c.size), interpolation=cv2.INTER_AREA))

    def score(self):
        return self.coin_number - len(self.coins)

    def win(self):
        return self.score() == self.coin_number

    def has_stopped(self):
        return self.stopped

    def stop(self):
        self.stopped = True

    def render(self, frame, robot_pos, active):
        if self.last_draw + 80 < current_time():
            for c in self.coins:
                c.next_frame()
            self.last_draw = current_time()

        remove_coins = []
        for c in self.coins:
            frame = c.draw(frame)
            if active and math.dist((c.x + (c.size/2), c.y + (c.size/2)), robot_pos) < ANGLE_MIN_DISTANCE and self.remaining_time > 0 and not self.has_stopped():
                remove_coins.append(c)

        for c in remove_coins:
            self.coins.remove(c)

        # draw score
        self.coin_icon.draw(frame)
        cv2.putText(frame, str(self.score()), (FRAME_WIDTH - 32, FRAME_HEIGHT - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # calc remaining time and draw it
        if self.last_frame and active and self.remaining_time > 0 and not self.win() and not self.has_stopped():
            self.remaining_time -= current_time() - self.last_frame
            if self.remaining_time < 0:
                self.remaining_time = 0
        sec = str(math.floor(self.remaining_time / 1000)).rjust(2, "0")
        msec = str(round((self.remaining_time % 1000) / 1000, 2)).ljust(4, "0")
        extra_text = ""
        if self.win():
            extra_text = " - You WIN!"
        elif self.has_stopped():
            extra_text = " - " + str(len(self.coins)) + " coins MISSED :'("
        elif self.remaining_time == 0:
            extra_text = " - You LOSE :("
        cv2.putText(frame, sec + msec[1:] + extra_text, (16, FRAME_HEIGHT - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255) if self.remaining_time > GAME_DURATION / 4 and not self.has_stopped() else (0, 0, 204), 2)

        self.last_frame = current_time()
        return frame

