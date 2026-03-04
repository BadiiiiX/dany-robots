from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot


class Regeneration(Capacity):
    """Régénération : restaure 30 PV (coût : 50 énergie)."""

    name = "Régénération"

    def __init__(self):
        super().__init__(Regeneration.name, 50)

    def execute(self, source: "Robot", target: "Robot") -> str:
        soin = 30
        source.hp = min(source.max_hp, source.hp + soin)
        return f"{source.name} utilise Régénération et récupère {soin} PV ! (PV : {source.hp}/{source.max_hp})"
