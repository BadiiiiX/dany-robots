from impl.Capacity.Capacity import Capacity

from impl.Robot.Robot import Robot


class QuickAttack(Capacity):
    """Attaque Rapide : effectue 2 attaques normales en un seul tour (coût : 25 énergie)."""

    def __init__(self):
        super().__init__("Attaque Rapide", 25)

    def execute(self, source: "Robot", target: "Robot") -> str:
        dmg1 = self._calc_damage(source, target)
        dmg2 = self._calc_damage(source, target)
        target.hp = max(0, target.hp - dmg1 - dmg2)
        return (
            f"{source.name} utilise Attaque Rapide et frappe 2 fois : "
            f"{dmg1} + {dmg2} = {dmg1 + dmg2} dégâts sur {target.name} !"
        )
