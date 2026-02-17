from abc import ABC, abstractmethod

import pygame


class Window(ABC):
    def __init__(self, ui):
        self.ui = ui

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self):
        pass

    def render(self):
        pass
