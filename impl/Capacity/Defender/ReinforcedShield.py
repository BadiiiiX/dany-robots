from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class ReinforcedShield(Capacity):
    """Bouclier renforcé : +15 DEF pendant 3 tours (coût : 35 énergie)."""

    def __init__(self):
        super().__init__("Bouclier Renforcé", 35)

    def execute(self, source: "Robot", target: "Robot") -> str:
        source.defense += 15
        source.active_buffs["defense_boost"] = {"stat": "defense", "value": 15, "turns": 3}
        return f"{source.name} active Bouclier Renforcé ! +15 DEF pendant 3 tours."
