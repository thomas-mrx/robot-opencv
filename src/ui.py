import cv2
import numpy as np
from shapely.geometry import Polygon, Point

from utils.constants import FRAME_HEIGHT, FRAME_WIDTH
from utils.functions import remap, hsv2bgr


class Ui:
    def __init__(self, draw_instance, toolbar_size=32, sidebar_size=192, border_size=3):
        self.drawInstance = draw_instance
        self.toolbarSize = toolbar_size
        self.sidebarSize = sidebar_size
        self.borderSize = border_size
        self.toolbarMessage = "Hello world"
        self.ui = np.zeros((FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH + self.sidebarSize, 3), np.uint8)
        self.layersButtons = [None, None, None, None]
        self.clickLayer = self.drawInstance.currentLayer
        self.hoverLayer = self.drawInstance.currentLayer
        self.deleteBtn = Polygon()
        self.hoverDeleteBtn = False
        self.playBtn = Polygon()
        self.hoverPlayBtn = False
        self.clickBtn = None

    def reset_hover(self):
        if self.hoverPlayBtn:
            self.hoverPlayBtn = False
        if self.hoverDeleteBtn:
            self.hoverDeleteBtn = False
        if self.hoverLayer != self.drawInstance.currentLayer:
            self.hoverLayer = self.drawInstance.currentLayer


    def event_handler(self, event, x, y, flags, params):
        mouse_position = Point(x,y)

        if event == cv2.EVENT_LBUTTONDOWN:
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position):
                    self.clickLayer = i
            if not self.deleteBtn.is_empty and self.deleteBtn.contains(mouse_position):
                self.clickBtn = self.deleteBtn
            if not self.playBtn.is_empty and self.playBtn.contains(mouse_position):
                self.clickBtn = self.playBtn

        elif event == cv2.EVENT_LBUTTONUP:
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position) and self.clickLayer == i:
                    self.drawInstance.set_layer(self.clickLayer)
            if not self.deleteBtn.is_empty and self.deleteBtn.contains(mouse_position) and self.clickBtn == self.deleteBtn:
                self.clickBtn = None
                self.drawInstance.empty_layer()
            if not self.playBtn.is_empty and self.playBtn.contains(mouse_position) and self.clickBtn == self.playBtn:
                self.clickBtn = None
                self.drawInstance.set_pathfinder()

        elif event == cv2.EVENT_MOUSEMOVE:
            inside_layer = False
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position):
                    inside_layer = True
                    self.hoverLayer = i
            if not inside_layer:
                self.clickLayer = self.drawInstance.currentLayer
                self.hoverLayer = self.drawInstance.currentLayer
            if not self.deleteBtn.is_empty and self.deleteBtn.contains(mouse_position):
                self.hoverDeleteBtn = True
            elif self.hoverDeleteBtn:
                self.hoverDeleteBtn = False
            if not self.playBtn.is_empty and self.playBtn.contains(mouse_position):
                self.hoverPlayBtn = True
            elif self.hoverPlayBtn:
                self.hoverPlayBtn = False


    def layers(self):
        cv2.putText(self.ui, "LAYERS", (int(FRAME_WIDTH + (self.sidebarSize / 4)), self.toolbarSize),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

        layer_size = 96
        margin = 8
        for i in range(0, 4):
            borderColor = [8, 5, 3]
            if self.drawInstance.is_pathfinder_active(i):
                borderColor = [0, 223, 255]
            elif self.drawInstance.currentLayer == i or self.clickLayer == i:
                borderColor = [255, 255, 255]
            elif self.hoverLayer == i:
                borderColor = [201, 176, 160]

            cv2.rectangle(self.ui, (FRAME_WIDTH + 10, 50 + ((layer_size + margin) * i)),
                          (FRAME_WIDTH + self.sidebarSize - 10, 50 + layer_size + ((layer_size + margin) * i)),
                          [52, 33, 20], -1)
            cv2.rectangle(self.ui, (FRAME_WIDTH + 10, 50 + ((layer_size + margin) * i)),
                          (FRAME_WIDTH + self.sidebarSize - 10, 50 + layer_size + ((layer_size + margin) * i)),
                          borderColor,
                          int(self.borderSize / 2))
            path = self.drawInstance.get_layer(i)
            if len(path):
                x = np.array(self.drawInstance.boundaries.exterior.coords[:-1])[:, 0]
                y = np.array(self.drawInstance.boundaries.exterior.coords[:-1])[:, 1]
                minX = min(x)
                maxX = max(x)
                minY = min(y)
                maxY = max(y)
                last_point = None
                color_random = self.drawInstance.get_color(i)
                for p in path:
                    pX = remap(p[0], minX, maxX, FRAME_WIDTH + 20, FRAME_WIDTH + self.sidebarSize - 20)
                    pY = remap(p[1], minY, maxY, 50 + ((layer_size + margin) * i) + 10, 50 + layer_size + ((layer_size + margin) * i) - 10)

                    if last_point:
                        color = hsv2bgr(color_random, 1, 1)
                        cv2.line(self.ui, last_point, (pX, pY), color, 1)
                        color_random += 0.01
                        if color_random > 1:
                            color_random = 0
                    last_point = (pX,pY)
            else:
                cv2.putText(self.ui, "(empty)",
                        (FRAME_WIDTH + int(self.sidebarSize / 2.85), layer_size + margin + ((layer_size + margin) * i)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (201, 176, 160), 1)
            if not self.layersButtons[i]:
                self.layersButtons[i] = Polygon(
                    (
                        (FRAME_WIDTH + 10, 50 + ((layer_size + margin) * i)),
                        (FRAME_WIDTH + self.sidebarSize - 10, 50 + ((layer_size + margin) * i)),
                        (FRAME_WIDTH + self.sidebarSize - 10, 50 + layer_size + ((layer_size + margin) * i)),
                        (FRAME_WIDTH + 10, 50 + layer_size + ((layer_size + margin) * i))
                    )
                )

        cv2.rectangle(self.ui, (FRAME_WIDTH + 15, 50 + ((layer_size + margin) * 4)),
                      (FRAME_WIDTH + int(self.sidebarSize / 2) - 5, 50 + 36 + ((layer_size + margin) * 4)), (201, 176, 160),
                      -1 if self.hoverPlayBtn else int(self.borderSize / 2))
        self.playBtn = Polygon(
            (
                (FRAME_WIDTH + 15, 50 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + int(self.sidebarSize / 2) - 5, 50 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + int(self.sidebarSize / 2) - 5, 50 + 36 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + 15, 50 + 36 + ((layer_size + margin) * 4)),
            )
        )
        cv2.putText(self.ui, "PLAY",
                    (int(FRAME_WIDTH + 15 + 12), self.toolbarSize + ((layer_size + margin) * 4) + 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255) if self.hoverPlayBtn else (201, 176, 160), 2)
        cv2.rectangle(self.ui, (FRAME_WIDTH + int(self.sidebarSize / 2) + 5, 50 + ((layer_size + margin) * 4)),
                      (FRAME_WIDTH + self.sidebarSize - 15, 50 + 36 + ((layer_size + margin) * 4)), (0, 0, 154) if self.hoverDeleteBtn else (0, 0, 204),
                      -1)
        self.deleteBtn = Polygon(
            (
                (FRAME_WIDTH + int(self.sidebarSize / 2) + 5, 50 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + self.sidebarSize - 15, 50 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + self.sidebarSize - 15, 50 + 36 + ((layer_size + margin) * 4)),
                (FRAME_WIDTH + int(self.sidebarSize / 2) + 5, 50 + 36 + ((layer_size + margin) * 4)),
            )
        )
        cv2.putText(self.ui, "RESET",
                    (int(FRAME_WIDTH + int(self.sidebarSize / 2) + 5 + 14), self.toolbarSize + ((layer_size + margin) * 4) + 42 - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def toolbar(self):
        cv2.putText(self.ui, self.toolbarMessage, (10, int(self.toolbarSize / 1.6)), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (201, 176, 160), 1)

    def render(self, frame):
        self.ui[self.toolbarSize:FRAME_HEIGHT + self.toolbarSize, 0:FRAME_WIDTH] = frame
        self.ui[0:self.toolbarSize, 0:FRAME_WIDTH + self.sidebarSize] = [52, 33, 20]
        self.ui[self.toolbarSize - 1 - self.borderSize:self.toolbarSize - 1, 0:FRAME_WIDTH + self.sidebarSize] = [8, 5,
                                                                                                                  3]
        self.ui[0:FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH:FRAME_WIDTH + self.sidebarSize] = [41, 26, 16]
        self.ui[0:FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH:FRAME_WIDTH + self.borderSize] = [8, 5, 3]
        self.layers()
        self.toolbar()
        return self.ui
