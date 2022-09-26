import cv2
import numpy as np
from shapely.geometry import Polygon, Point

from utils.constants import FRAME_HEIGHT, FRAME_WIDTH


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

    def event_handler(self, event, x, y, flags, params):
        mouse_position = Point(x,y)

        if event == cv2.EVENT_LBUTTONDOWN:
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position):
                    self.clickLayer = i

        elif event == cv2.EVENT_LBUTTONUP:
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position) and self.clickLayer == i:
                    self.drawInstance.set_layer(self.clickLayer)

        elif event == cv2.EVENT_MOUSEMOVE:
            inside_layer = False
            for (i, l) in enumerate(self.layersButtons):
                if l.contains(mouse_position):
                    inside_layer = True
                    self.hoverLayer = i
            if not inside_layer:
                self.clickLayer = self.drawInstance.currentLayer
                self.hoverLayer = self.drawInstance.currentLayer


    def layers(self):
        cv2.putText(self.ui, "LAYERS", (int(FRAME_WIDTH + (self.sidebarSize / 4)), self.toolbarSize),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

        layer_size = 96
        margin = 8
        for i in range(0, 4):
            borderColor = [8, 5, 3]
            if self.drawInstance.currentLayer == i or self.clickLayer == i:
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
                      int(self.borderSize / 2))
        cv2.putText(self.ui, "PLAY",
                    (int(FRAME_WIDTH + 15 + 12), self.toolbarSize + ((layer_size + margin) * 4) + 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (201, 176, 160), 2)
        cv2.rectangle(self.ui, (FRAME_WIDTH + int(self.sidebarSize / 2) + 5, 50 + ((layer_size + margin) * 4)),
                      (FRAME_WIDTH + self.sidebarSize - 15, 50 + 36 + ((layer_size + margin) * 4)), (0, 0, 204),
                      -1)
        cv2.putText(self.ui, "DELETE",
                    (int(FRAME_WIDTH + int(self.sidebarSize / 2) + 5 + 12), self.toolbarSize + ((layer_size + margin) * 4) + 42 - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

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
