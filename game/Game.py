from ui.RobotUI import RobotUI


class Game:

    def __init__(self):
        self.screen = None
        self.players = []

    def run_program(self):
        self.screen = RobotUI()