from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class CombatRage(Capacity):
    """Rage de Combat : +20 ATT pendant 2 tours (coût : 40 énergie)."""

    def __init__(self):
        super().__init__("Rage de Combat", 40)

    def execute(self, source: "Robot", target: "Robot") -> str:
        source.attack += 20
        source.active_buffs["attack_boost"] = {"stat": "attack", "value": 20, "turns": 2}
        return f"{source.name} entre en Rage de Combat ! +20 ATT pendant 2 tours."
