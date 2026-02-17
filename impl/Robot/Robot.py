from impl.Robot.RobotType import RobotType


class Robot:
    def __init__(self, name: str, type: RobotType, hp: int, max_hp: int, attack: int, defense: int, speed: int, energy: int):
        self.name = name #unique
        self.type = type
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.energy = energy
        self.capacities = []
        self.active_buffs = {}


    def __eq__(self, other):
        return self.name == other.name