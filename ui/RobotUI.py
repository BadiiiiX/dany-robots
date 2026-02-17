import pygame as pg
from ui.Window.Menu import Menu


class RobotUI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pg.init()
        self.display = pg.display
        self.screen = self.display.set_mode((1280, 720))
        self.clock = pg.time.Clock()
        self.running = True
        self.current_window = Menu(self)

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    break

                self.current_window.handle_event(event)

            self.current_window.update()
            self.current_window.render()

            self.display.flip()
            self.clock.tick(30)

        self.end()

    def set_window(self, window):
        self.current_window.on_leave()
        self.current_window = window
        self.current_window.on_enter()

    def end(self):
        pg.quit()
