from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot


class Capacity(ABC):
    """Classe abstraite représentant une capacité spéciale d'un robot."""

    def __init__(self, name: str, energy_cost: int):
        self.name = name
        self.energy_cost = energy_cost

    @abstractmethod
    def execute(self, source: "Robot", target: "Robot") -> str:
        """Applique l'effet de la capacité et retourne un message pour le journal de combat."""
        pass

    @staticmethod
    def _calc_damage(source: "Robot", target: "Robot", multiplier: float = 1.0) -> int:
        """Calcule les dégâts infligés par une attaque avec variation aléatoire et critique."""
        degats_base = max(5, source.attack - target.defense)
        degats = round(degats_base * random.uniform(0.9, 1.1) * multiplier)

        if random.random() < 0.1:
            degats = round(degats * 1.5)
        return degats
