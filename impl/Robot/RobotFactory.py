from impl.Capacity.Defender.ReinforcedShield import ReinforcedShield

from impl.Robot.Robot import Robot
from impl.Robot.RobotType import RobotType


class RobotFactory:

    @staticmethod
    def build(name: str, robot_type: RobotType, hp: int, max_hp: int, attack: int, defense: int, speed: int, energy: int) -> Robot:

        robot = Robot(name, robot_type, hp, max_hp, attack, defense, speed, energy)

        robot = RobotFactory.assign_capacities(robot)

        return robot

    @staticmethod
    def assign_capacities(robot: Robot) -> Robot:

        robot_type = robot.type

        match robot_type:
            case RobotType.BALANCE:
                robot.capacities.push(ReinforcedShield())

        return robot