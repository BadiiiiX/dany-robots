"""
Classe abstraite représentant un joueur (humain ou IA).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot


class Player(ABC):
    """
    Base commune pour tous les types de joueurs.
    Un joueur possède un robot et sait choisir une action lors d'un tour de combat.
    """

    def __init__(self, robot: "Robot"):
        self.robot = robot

    @abstractmethod
    def choisir_action(self, adversaire: "Robot") -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(robot={self.robot.name!r})"
