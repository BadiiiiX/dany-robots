from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class PowerfulStrike(Capacity):
    """Frappe Puissante : inflige 1.3× les dégâts normaux (coût : 35 énergie)."""

    MULTIPLIER = 1.3

    def __init__(self):
        super().__init__("Frappe Puissante", 35)

    def execute(self, source: "Robot", target: "Robot") -> str:
        degats = self._calc_damage(source, target, self.MULTIPLIER)
        target.hp = max(0, target.hp - degats)
        return f"{source.name} utilise Frappe Puissante et inflige {degats} dégâts à {target.name} !"
