import random

from impl.Robot.Robot import Robot
from impl.Robot.RobotType import RobotType
from impl.config import ROBOT_CAPACITIES
from impl.exceptions import StatsInvalidesException, NomInvalideException


class RobotFactory:
    """
    Fabrique de robots.
    Centralise la construction, la validation et la génération aléatoire.
    """

    PV_MIN, PV_MAX    = 50, 150
    ATK_MIN, ATK_MAX  = 10, 50
    DEF_MIN, DEF_MAX  = 5,  40
    SPD_MIN, SPD_MAX  = 5,  40
    TOTAL_STATS       = 100
    NOM_MIN, NOM_MAX  = 3,  20
    BASE_ENERGY       = 100

    @staticmethod
    def valider_stats(pv: int, attaque: int, defense: int, vitesse: int) -> None:
        """
        Vérifie que les statistiques respectent les plages et que leur somme vaut 100.
        Lève StatsInvalidesException avec un message explicite en cas d'erreur.
        """
        erreurs = []

        if not (RobotFactory.PV_MIN <= pv <= RobotFactory.PV_MAX):
            erreurs.append(
                f"PV hors plage : {pv} (attendu {RobotFactory.PV_MIN}–{RobotFactory.PV_MAX})"
            )
        if not (RobotFactory.ATK_MIN <= attaque <= RobotFactory.ATK_MAX):
            erreurs.append(
                f"Attaque hors plage : {attaque} (attendu {RobotFactory.ATK_MIN}–{RobotFactory.ATK_MAX})"
            )
        if not (RobotFactory.DEF_MIN <= defense <= RobotFactory.DEF_MAX):
            erreurs.append(
                f"Défense hors plage : {defense} (attendu {RobotFactory.DEF_MIN}–{RobotFactory.DEF_MAX})"
            )
        if not (RobotFactory.SPD_MIN <= vitesse <= RobotFactory.SPD_MAX):
            erreurs.append(
                f"Vitesse hors plage : {vitesse} (attendu {RobotFactory.SPD_MIN}–{RobotFactory.SPD_MAX})"
            )

        total = pv + attaque + defense + vitesse
        if total != RobotFactory.TOTAL_STATS:
            erreurs.append(
                f"La somme des stats doit être {RobotFactory.TOTAL_STATS} (obtenu {total})"
            )

        if erreurs:
            raise StatsInvalidesException(" | ".join(erreurs))

    @staticmethod
    def valider_nom(nom: str, robots_existants: list[Robot] | None = None) -> None:
        """
        Vérifie que le nom fait entre 3 et 20 caractères et est unique dans la liste fournie.
        Lève NomInvalideException en cas d'erreur.
        """
        if not (RobotFactory.NOM_MIN <= len(nom) <= RobotFactory.NOM_MAX):
            raise NomInvalideException(
                f"Le nom '{nom}' doit contenir entre {RobotFactory.NOM_MIN} "
                f"et {RobotFactory.NOM_MAX} caractères (longueur actuelle : {len(nom)})."
            )

        if robots_existants:
            noms_existants = {r.name.lower() for r in robots_existants}
            if nom.lower() in noms_existants:
                raise NomInvalideException(f"Un robot nommé '{nom}' existe déjà.")

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    @staticmethod
    def creer_robot_manuel(
        nom: str,
        robot_type: RobotType,
        pv: int,
        attaque: int,
        defense: int,
        vitesse: int,
        robots_existants: list[Robot] | None = None,
    ) -> Robot:
        """
        Crée un robot avec les statistiques fournies après validation complète.
        Lève NomInvalideException ou StatsInvalidesException si les données sont invalides.
        """
        RobotFactory.valider_nom(nom, robots_existants)
        RobotFactory.valider_stats(pv, attaque, defense, vitesse)
        return RobotFactory.build(nom, robot_type, pv, attaque, defense, vitesse)

    @staticmethod
    def creer_robot_aleatoire(
        nom: str,
        robot_type: RobotType,
        robots_existants: list[Robot] | None = None,
    ) -> Robot:
        """
        Génère un robot avec des statistiques aléatoires dont la somme vaut exactement 100
        et qui respectent les plages du cahier des charges.
        Lève NomInvalideException si le nom est invalide.
        """
        RobotFactory.valider_nom(nom, robots_existants)

        pv_max_pratique = (
            RobotFactory.TOTAL_STATS
            - RobotFactory.ATK_MIN
            - RobotFactory.DEF_MIN
            - RobotFactory.SPD_MIN
        )

        for _ in range(1000):
            pv = random.randint(RobotFactory.PV_MIN, pv_max_pratique)
            restant = RobotFactory.TOTAL_STATS - pv

            atk_max = min(RobotFactory.ATK_MAX, restant - RobotFactory.DEF_MIN - RobotFactory.SPD_MIN)
            if atk_max < RobotFactory.ATK_MIN:
                continue
            attaque = random.randint(RobotFactory.ATK_MIN, atk_max)
            restant -= attaque

            def_max = min(RobotFactory.DEF_MAX, restant - RobotFactory.SPD_MIN)
            if def_max < RobotFactory.DEF_MIN:
                continue
            defense = random.randint(RobotFactory.DEF_MIN, def_max)
            vitesse = restant - defense

            if RobotFactory.SPD_MIN <= vitesse <= RobotFactory.SPD_MAX:
                return RobotFactory.build(nom, robot_type, pv, attaque, defense, vitesse)

        raise StatsInvalidesException(
            "Impossible de générer des stats aléatoires valides."
        )

    @staticmethod
    def build(
        name: str,
        robot_type: RobotType,
        hp: int,
        attack: int,
        defense: int,
        speed: int,
    ) -> Robot:
        """Construit un Robot et lui assigne ses capacités. L'énergie démarre à 100."""
        robot = Robot(name, robot_type, hp, hp, attack, defense, speed, energy=RobotFactory.BASE_ENERGY)
        RobotFactory.assign_capacities(robot)
        return robot

    @staticmethod
    def assign_capacities(robot: Robot) -> Robot:
        """Instancie et assigne les deux capacités correspondant au type du robot."""
        capacity_classes = ROBOT_CAPACITIES.get(robot.type, [])
        robot.capacities = [cls() for cls in capacity_classes]
        return robot
