import pygame
from ui.Window.Window import Window


class CreateRobotMenu(Window):

    def __init__(self, ui):
        super().__init__(ui)
        self.color = None

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.color = "red" if self.color == "blue" else "blue"

    def update(self):
        pass

    def render(self):
        self.ui.screen.fill(self.color)