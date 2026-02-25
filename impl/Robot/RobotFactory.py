from impl.Robot.Robot import Robot
from impl.Robot.RobotType import RobotType
from impl.config import ROBOT_CAPACITIES


class RobotFactory:
    """Fabrique de robots : construit un Robot et lui assigne ses capacités selon son type."""

    BASE_ENERGY = 100

    @staticmethod
    def build(name: str, robot_type: RobotType, hp: int, attack: int, defense: int, speed: int) -> Robot:
        """Crée un robot avec ses capacités."""
        robot = Robot(name, robot_type, hp, hp, attack, defense, speed, RobotFactory.BASE_ENERGY)
        RobotFactory.assign_capacities(robot)
        return robot

    @staticmethod
    def assign_capacities(robot: Robot) -> Robot:
        """Instancie et assigne les capacités correspondant au type du robot."""
        capacity_classes = ROBOT_CAPACITIES.get(robot.type, [])
        robot.capacities = [cls() for cls in capacity_classes]
        return robot
