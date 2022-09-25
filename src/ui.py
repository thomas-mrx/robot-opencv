import cv2
import numpy as np

from utils.constants import FRAME_HEIGHT, FRAME_WIDTH


class Ui:
    def __init__(self, toolbar_size=32, sidebar_size=192, border_size=3):
        self.toolbarSize = toolbar_size
        self.sidebarSize = sidebar_size
        self.borderSize = border_size
        self.ui = np.zeros((FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH + self.sidebarSize, 3), np.uint8)

    def layers(self):
        cv2.putText(self.ui, "LAYERS", (int(FRAME_WIDTH + (self.sidebarSize / 4)), self.toolbarSize), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

        layer_size = 96
        margin = 8
        for i in range(0, 4):
            cv2.rectangle(self.ui, (FRAME_WIDTH + 10, 50 + ((layer_size + margin)*i)), (FRAME_WIDTH + self.sidebarSize - 10, 50 + layer_size + ((layer_size + margin)*i)), [52, 33, 20], -1)
            cv2.rectangle(self.ui, (FRAME_WIDTH + 10, 50 + ((layer_size + margin)*i)), (FRAME_WIDTH + self.sidebarSize - 10, 50 + layer_size + ((layer_size + margin)*i)), [8, 5, 3], int(self.borderSize / 2))
            cv2.putText(self.ui, "(empty)", (FRAME_WIDTH + int(self.sidebarSize / 2.85), layer_size + margin + ((layer_size + margin)*i)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (201, 176, 160), 1)

        cv2.rectangle(self.ui, (FRAME_WIDTH + 10, 50 + ((layer_size + margin)*4)), (FRAME_WIDTH + self.sidebarSize - 10, 50 + 42 + ((layer_size + margin)*4)), (201, 176, 160), int(self.borderSize / 2))
        cv2.putText(self.ui, "reset", (int(FRAME_WIDTH + (self.sidebarSize / 2.65)), self.toolbarSize + ((layer_size + margin)*4) + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (201, 176, 160), 2)

    def toolbar(self):
        cv2.putText(self.ui, "Waiting for AR markers...", (10, int(self.toolbarSize / 1.6)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (201, 176, 160), 1)
        # add red/green dot on the right to indicate if the robot is detected or not

    def render(self, frame):
        self.ui[self.toolbarSize:FRAME_HEIGHT + self.toolbarSize, 0:FRAME_WIDTH] = frame
        self.ui[0:self.toolbarSize, 0:FRAME_WIDTH + self.sidebarSize] = [52, 33, 20]
        self.ui[self.toolbarSize - 1 - self.borderSize:self.toolbarSize - 1, 0:FRAME_WIDTH + self.sidebarSize] = [8, 5, 3]
        self.ui[0:FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH:FRAME_WIDTH + self.sidebarSize] = [41, 26, 16]
        self.ui[0:FRAME_HEIGHT + self.toolbarSize, FRAME_WIDTH:FRAME_WIDTH + self.borderSize] = [8, 5, 3]
        self.layers()
        self.toolbar()
        return self.ui