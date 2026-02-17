from impl.Capacity.Capacity import Capacity


class ReinforcedShield(Capacity):

    def __init__(self):
        super().__init__("Bouclier Renforcé", 35)

    def execute(self):
        print("J'ai lancé Bouclier renforcé !!!!")