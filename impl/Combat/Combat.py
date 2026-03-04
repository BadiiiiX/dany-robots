"""
Module de système de combat.
Gère le déroulement d'un duel tour par tour entre deux robots.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from impl.exceptions import CombatImpossibleException, EnergieInsuffisanteException
from impl.Combat.ai import (
    decider_action_ia,
    ACTION_ATTAQUE,
    ACTION_CAPACITE_1,
    ACTION_CAPACITE_2,
    ACTION_DEFENSE,
)

if TYPE_CHECKING:
    from impl.Robot.Robot import Robot

# Modes de combat
MODE_MANUEL  = "manuel"
MODE_AUTO    = "auto"
MODE_RAPIDE  = "rapide"

MODES_VALIDES = (MODE_MANUEL, MODE_AUTO, MODE_RAPIDE)

# Limite de tours avant match nul
TOURS_MAX = 50

# Régénération d'énergie par tour
REGEN_ENERGIE = 20


class Combat:
    """
    Orchestre un combat tour par tour entre deux robots.

    En mode 'manuel', robot1 est contrôlé par le joueur humain :
    le module UI passe l'action choisie à jouer_tour().
    En mode 'auto' et 'rapide', les deux robots sont gérés par l'IA.
    """

    def __init__(self, robot1: "Robot", robot2: "Robot", mode: str = MODE_MANUEL):
        if robot1 is None or robot2 is None:
            raise CombatImpossibleException("Les deux robots doivent être non nuls.")
        if robot1 == robot2:
            raise CombatImpossibleException(
                f"Impossible de faire combattre '{robot1.name}' contre lui-même."
            )
        if mode not in MODES_VALIDES:
            raise ValueError(f"Mode invalide '{mode}'. Valeurs acceptées : {MODES_VALIDES}")

        self.robot1: "Robot" = robot1
        self.robot2: "Robot" = robot2
        self.mode: str       = mode
        self.tour: int       = 0
        self.journal: list[str] = []
        self.vainqueur: "Robot | None" = None

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def lancer(self) -> None:
        """
        Initialise le combat : réinitialise les états et logue les stats de départ.
        À appeler une fois avant le premier jouer_tour().
        """
        self.tour = 0
        self.journal.clear()
        self.vainqueur = None
        self._log(f"[Combat] {self.robot1.name} VS {self.robot2.name}  (mode : {self.mode})")
        self._log(
            f"  {self.robot1.name} — PV:{self.robot1.hp} ATT:{self.robot1.attack} "
            f"DEF:{self.robot1.defense} VIT:{self.robot1.speed}"
        )
        self._log(
            f"  {self.robot2.name} — PV:{self.robot2.hp} ATT:{self.robot2.attack} "
            f"DEF:{self.robot2.defense} VIT:{self.robot2.speed}"
        )

    def jouer_tour(self, action_robot1: str | None = None) -> bool:
        """
        Joue un tour complet.

        - mode 'manuel' : action_robot1 est l'action choisie par le joueur pour robot1.
                          L'IA décide automatiquement pour robot2.
        - mode 'auto' / 'rapide' : l'IA décide pour les deux robots ;
                                   action_robot1 est ignoré.

        Retourne True si le combat est terminé (victoire ou match nul).
        """
        if self.est_termine():
            return True

        self.tour += 1
        self._log(f"\n--- Tour {self.tour} ---")

        # Déterminer l'ordre d'attaque
        premier, second = self._ordre_attaque()

        # Déterminer les actions selon le mode
        if self.mode == MODE_MANUEL:
            # En mode manuel, action_robot1 doit être fournie par l'UI ;
            # on se rabat sur l'attaque normale si elle est absente (sécurité).
            action_joueur: str = action_robot1 if action_robot1 is not None else ACTION_ATTAQUE
            action_premier = (
                action_joueur
                if premier is self.robot1
                else decider_action_ia(premier, second)
            )
            action_second = (
                decider_action_ia(second, premier)
                if second is self.robot2
                else action_joueur
            )
        else:
            action_premier = decider_action_ia(premier, second)
            action_second  = decider_action_ia(second, premier)

        # Exécuter les actions dans l'ordre
        self._executer_action(premier, second, action_premier)
        if second.is_alive():
            self._executer_action(second, premier, action_second)

        # Fin de tour : régénération d'énergie + tick des buffs
        self._fin_de_tour()

        # Vérifier la condition de victoire
        return self.verifier_fin_combat()

    def est_termine(self) -> bool:
        """Retourne True si un vainqueur a été désigné ou si le tour max est dépassé."""
        return self.vainqueur is not None or self.tour >= TOURS_MAX

    def verifier_fin_combat(self) -> bool:
        """
        Vérifie si le combat doit s'arrêter.
        Retourne True si c'est le cas et met à jour self.vainqueur.
        """
        if not self.robot1.is_alive():
            self.vainqueur = self.robot2
            self._log(f"\n*** {self.robot2.name} remporte le combat ! ***")
            return True

        if not self.robot2.is_alive():
            self.vainqueur = self.robot1
            self._log(f"\n*** {self.robot1.name} remporte le combat ! ***")
            return True

        if self.tour >= TOURS_MAX:
            self._log(f"\n[Match nul] {TOURS_MAX} tours atteints sans vainqueur.")
            return True

        return False

    # ------------------------------------------------------------------
    # Mécanique de combat
    # ------------------------------------------------------------------

    def calculer_degats(self, attaquant: "Robot", defenseur: "Robot") -> int:
        """
        Calcule les dégâts d'une attaque normale.
        Formule : max(5, attaque - défense) × aléatoire(0.9, 1.1)
        10 % de chances de coup critique (×1.5).
        """
        degats_base = max(5, attaquant.attack - defenseur.defense)
        degats = round(degats_base * random.uniform(0.9, 1.1))
        if random.random() < 0.1:
            degats = round(degats * 1.5)
            self._log(f"  Coup critique !")
        return degats

    def _ordre_attaque(self) -> tuple["Robot", "Robot"]:
        """Retourne (premier, second) selon la vitesse. Égalité résolue aléatoirement."""
        if self.robot1.speed > self.robot2.speed:
            return self.robot1, self.robot2
        if self.robot2.speed > self.robot1.speed:
            return self.robot2, self.robot1
        # Égalité : tirage au sort
        if random.random() < 0.5:
            return self.robot1, self.robot2
        return self.robot2, self.robot1

    def _executer_action(
        self, actif: "Robot", adverse: "Robot", action: str
    ) -> None:
        """Dispatch vers la bonne mécanique selon l'action choisie."""
        if action == ACTION_ATTAQUE:
            self._attaque_normale(actif, adverse)
        elif action == ACTION_CAPACITE_1:
            self._utiliser_capacite(actif, adverse, index=0)
        elif action == ACTION_CAPACITE_2:
            self._utiliser_capacite(actif, adverse, index=1)
        elif action == ACTION_DEFENSE:
            self._action_defense(actif)
        else:
            self._log(f"  Action inconnue '{action}' pour {actif.name}. Attaque normale effectuée.")
            self._attaque_normale(actif, adverse)

    def _attaque_normale(self, actif: "Robot", adverse: "Robot") -> None:
        """Attaque normale gratuite en énergie."""
        # Vérifier l'esquive
        if "evasion" in adverse.active_buffs:
            del adverse.active_buffs["evasion"]
            self._log(f"  {adverse.name} esquive l'attaque de {actif.name} !")
            return

        degats = self.calculer_degats(actif, adverse)

        # Appliquer la réduction de la défense active (50 %)
        if "defense_active" in adverse.active_buffs:
            degats = max(1, degats // 2)
            self._log(f"  [Def] {adverse.name} est en defense : degats reduits de 50 %.")

        adverse.hp = max(0, adverse.hp - degats)
        self._log(f"  {actif.name} attaque {adverse.name} -> {degats} degats. "
                  f"(PV restants : {adverse.hp}/{adverse.max_hp})")

    def _utiliser_capacite(
        self, actif: "Robot", adverse: "Robot", index: int
    ) -> None:
        """
        Utilise la capacité à l'index donné (0 ou 1).
        Lève EnergieInsuffisanteException si l'énergie est insuffisante.
        """
        if index >= len(actif.capacities):
            self._log(f"  {actif.name} n'a pas de capacité #{index + 1}.")
            return

        capacite = actif.capacities[index]

        if actif.energy < capacite.energy_cost:
            raise EnergieInsuffisanteException(
                f"{actif.name} n'a pas assez d'énergie pour '{capacite.name}' "
                f"(nécessaire : {capacite.energy_cost}, disponible : {actif.energy})."
            )

        actif.energy -= capacite.energy_cost
        message = capacite.execute(actif, adverse)
        self._log(f"  [Cap] {message}")

    def _action_defense(self, actif: "Robot") -> None:
        """
        Le robot passe en mode défense : réduit de 50 % les dégâts reçus au prochain tour.
        Ajoute le buff 'defense_active' (durée : 1 tour).
        """
        actif.active_buffs["defense_active"] = {"turns": 1}
        self._log(f"  [Def] {actif.name} se met en defense (degats recus reduits de 50 % ce tour).")

    def _fin_de_tour(self) -> None:
        """Régénère l'énergie des deux robots et décrémente les buffs actifs."""
        for robot in (self.robot1, self.robot2):
            robot.energy = min(100, robot.energy + REGEN_ENERGIE)

        for robot in (self.robot1, self.robot2):
            messages_buff = robot.tick_buffs()
            for msg in messages_buff:
                self._log(f"  {msg}")

    # ------------------------------------------------------------------
    # Journal
    # ------------------------------------------------------------------

    def _log(self, message: str) -> None:
        """Ajoute un message au journal de combat."""
        self.journal.append(message)
