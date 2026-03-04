"""
Joueur humain.
En mode pygame, l'action est transmise directement par l'interface graphique
via Combat.jouer_tour(action_robot1=...) et cette classe n'est pas appelée.
Elle reste disponible pour des tests en mode console.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from impl.Player.Player import Player
from impl.Combat.ai import ACTION_ATTAQUE, ACTION_CAPACITE_1, ACTION_CAPACITE_2, ACTION_DEFENSE

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot

ACTIONS_VALIDES = {
    "1": ACTION_ATTAQUE,
    "2": ACTION_CAPACITE_1,
    "3": ACTION_CAPACITE_2,
    "4": ACTION_DEFENSE,
}


class HumanPlayer(Player):
    """
    Joueur humain.
    choisir_action() invite la console et retourne le choix de l'utilisateur.
    Utilisé uniquement hors interface pygame (tests, débogage).
    """

    def choisir_action(self, adversaire: "Robot") -> str:
        """Affiche un menu console et attend une saisie valide du joueur."""
        cap1 = self.robot.capacities[0].name if len(self.robot.capacities) > 0 else "—"
        cap2 = self.robot.capacities[1].name if len(self.robot.capacities) > 1 else "—"

        print(f"\n[{self.robot.name}] Choisissez une action :")
        print(f"  1 - Attaque normale")
        print(f"  2 - Capacité 1 : {cap1}")
        print(f"  3 - Capacité 2 : {cap2}")
        print(f"  4 - Défense")

        while True:
            choix = input("Votre choix (1-4) : ").strip()
            if choix in ACTIONS_VALIDES:
                return ACTIONS_VALIDES[choix]
            print("  Choix invalide, veuillez entrer 1, 2, 3 ou 4.")
