"""
Module d'intelligence artificielle.
Décide de l'action d'un robot contrôlé par l'ordinateur.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from impl.Capacity.Defender.Regeneration import Regeneration

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot

# Actions disponibles (miroir des constantes de Combat)
ACTION_ATTAQUE    = "attaque"
ACTION_CAPACITE_1 = "capacite_1"
ACTION_CAPACITE_2 = "capacite_2"
ACTION_DEFENSE    = "defense"


def decider_action_ia(robot: "Robot", adversaire: "Robot") -> str:
    """
    Décide de l'action de l'IA selon l'état du robot et de son adversaire.

    Algorithme (par ordre de priorité) :
    1. Énergie < 30 → défense
    2. PV < 30 % et possède Régénération avec assez d'énergie → Régénération
    3. Énergie ≥ 60 et au moins une capacité disponible → capacité aléatoire parmi celles disponibles
    4. Sinon → attaque normale
    """

    if robot.energy < 30:
        return ACTION_DEFENSE

    if robot.hp < robot.max_hp * 0.3:
        for i, capacite in enumerate(robot.capacities):
            if (
                capacite.name == Regeneration.name
                and robot.energy >= capacite.energy_cost
            ):
                return ACTION_CAPACITE_1 if i == 0 else ACTION_CAPACITE_2

    # Priorité 3 : utiliser une capacité si énergie suffisante
    if robot.energy >= 60:
        disponibles = [
            ACTION_CAPACITE_1 if i == 0 else ACTION_CAPACITE_2
            for i, cap in enumerate(robot.capacities)
            if robot.energy >= cap.energy_cost
        ]
        if disponibles:
            return random.choice(disponibles)

    # Par défaut : attaque normale
    return ACTION_ATTAQUE
