from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class HeavyStrike(Capacity):
    """Tir de Barrage : inflige 1.5× les dégâts normaux (coût : 30 énergie)."""

    MULTIPLIER = 1.5

    def __init__(self):
        super().__init__("Tir de Barrage", 30)

    def execute(self, source: "Robot", target: "Robot") -> str:
        degats = self._calc_damage(source, target, self.MULTIPLIER)
        target.hp = max(0, target.hp - degats)
        return f"{source.name} déclenche Tir de Barrage et inflige {degats} dégâts à {target.name} !"
