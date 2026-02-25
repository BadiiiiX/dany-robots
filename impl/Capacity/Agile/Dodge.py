from impl.Capacity.Capacity import Capacity
from impl.Robot.Robot import Robot



class Dodge(Capacity):
    """Esquive : évite la prochaine attaque ennemie (100%) (coût : 30 énergie)."""

    def __init__(self):
        super().__init__("Esquive", 30)

    def execute(self, source: "Robot", target: "Robot") -> str:
        source.active_buffs["evasion"] = {"turns": 1}
        return f"{source.name} se prépare à esquiver la prochaine attaque !"
