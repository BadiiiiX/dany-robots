"""
Joueur contrôlé par l'IA.
Délègue la prise de décision à decider_action_ia().
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from impl.Player.Player import Player
from impl.Combat.ai import decider_action_ia

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot


class AIPlayer(Player):
    """Joueur dont les actions sont décidées automatiquement par l'algorithme d'IA."""

    def choisir_action(self, adversaire: "Robot") -> str:
        """Délègue à decider_action_ia pour choisir l'action optimale."""
        return decider_action_ia(self.robot, adversaire)
