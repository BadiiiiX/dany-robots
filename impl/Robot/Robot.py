from impl.Capacity.Capacity import Capacity
from impl.Robot.RobotBuff import Buffs
from impl.Robot.RobotType import RobotType


class Robot:
    """Représente un robot combattant avec ses statistiques, capacités et buffs actifs."""

    def __init__(self, name: str, type: RobotType, hp: int, max_hp: int,
                 attack: int, defense: int, speed: int, energy: int):
        self.name = name
        self.type = type
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.energy = energy
        self.capacities: list[Capacity] = []
        self.active_buffs: Buffs = {}

    def is_alive(self) -> bool:
        """Retourne True si le robot a encore des PV."""
        return self.hp > 0

    def tick_buffs(self) -> list[str]:
        """
        Décrémente la durée de chaque buff actif.
        """
        messages = []
        expired = []

        for buff_name, buff in self.active_buffs.items():
            buff["turns"] -= 1
            if buff["turns"] <= 0:
                expired.append(buff_name)

        for buff_name in expired:
            buff = self.active_buffs.pop(buff_name)
            if "stat" in buff:
                setattr(self, buff["stat"], getattr(self, buff["stat"]) - buff["value"])
                messages.append(f"Le buff '{buff_name}' de {self.name} a expiré.")

        return messages

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Robot):
            return False
        return self.name == other.name

    def __repr__(self) -> str:
        return f"Robot(name={self.name}, type={self.type.name}, hp={self.hp}/{self.max_hp})"
