from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class QuickRecharge(Capacity):
    """Recharge Rapide : restaure 40 énergie immédiatement (coût : 20 énergie)."""

    def __init__(self):
        super().__init__("Recharge Rapide", 20)

    def execute(self, source: "Robot", target: "Robot") -> str:
        gain = 40
        source.energy = min(100, source.energy + gain)
        return f"{source.name} utilise Recharge Rapide et récupère {gain} énergie ! (Énergie : {source.energy}/100)"
