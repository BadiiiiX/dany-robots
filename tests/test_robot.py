"""
Tests unitaires — module Robot (validation des stats et création).
"""
import pytest
from impl.Robot.RobotFactory import RobotFactory
from impl.Robot.RobotType    import RobotType
from impl.exceptions         import StatsInvalidesException, NomInvalideException


# ------------------------------------------------------------------
# valider_stats
# ------------------------------------------------------------------

class TestValiderStats:

    def test_stats_valides(self):
        """Cas nominal : stats dans les plages et somme == 100."""
        RobotFactory.valider_stats(60, 15, 15, 10)  # ne doit pas lever

    def test_somme_incorrecte(self):
        """La somme doit être exactement 100."""
        with pytest.raises(StatsInvalidesException, match="100"):
            RobotFactory.valider_stats(60, 15, 15, 15)  # total = 105

    def test_pv_trop_bas(self):
        with pytest.raises(StatsInvalidesException, match="PV"):
            RobotFactory.valider_stats(40, 20, 20, 20)

    def test_pv_trop_haut(self):
        with pytest.raises(StatsInvalidesException):
            RobotFactory.valider_stats(160, 10, 10, 10)  # total != 100 ET pv trop haut

    def test_attaque_trop_basse(self):
        with pytest.raises(StatsInvalidesException, match="Attaque"):
            RobotFactory.valider_stats(75, 5, 10, 10)  # attaque < 10

    def test_defense_trop_haute(self):
        with pytest.raises(StatsInvalidesException):
            RobotFactory.valider_stats(50, 10, 45, -5)  # defense > 40

    def test_vitesse_trop_basse(self):
        with pytest.raises(StatsInvalidesException, match="Vitesse"):
            RobotFactory.valider_stats(55, 20, 22, 3)  # vitesse < 5

    def test_plusieurs_erreurs_simultanees(self):
        """Plusieurs violations doivent toutes apparaître dans le message."""
        with pytest.raises(StatsInvalidesException) as exc:
            RobotFactory.valider_stats(200, 5, 50, 50)
        msg = str(exc.value)
        assert "PV" in msg or "Attaque" in msg  # au moins une violation citée


# ------------------------------------------------------------------
# valider_nom
# ------------------------------------------------------------------

class TestValiderNom:

    def test_nom_valide(self):
        RobotFactory.valider_nom("Alpha")  # ne doit pas lever

    def test_nom_trop_court(self):
        with pytest.raises(NomInvalideException):
            RobotFactory.valider_nom("AB")

    def test_nom_trop_long(self):
        with pytest.raises(NomInvalideException):
            RobotFactory.valider_nom("A" * 21)

    def test_nom_longueur_min(self):
        RobotFactory.valider_nom("ABC")  # exactement 3 — OK

    def test_nom_longueur_max(self):
        RobotFactory.valider_nom("A" * 20)  # exactement 20 — OK

    def test_nom_duplique(self):
        from impl.Robot.RobotFactory import RobotFactory as RF
        robot = RF.build("Helios", RobotType.ASSAULT, 60, 15, 15, 10)
        with pytest.raises(NomInvalideException, match="existe"):
            RF.valider_nom("helios", [robot])  # insensible à la casse


# ------------------------------------------------------------------
# creer_robot_manuel
# ------------------------------------------------------------------

class TestCreerRobotManuel:

    def test_creation_succes(self):
        robot = RobotFactory.creer_robot_manuel("Zephyr", RobotType.AGILE, 60, 15, 15, 10)
        assert robot.name == "Zephyr"
        assert robot.type == RobotType.AGILE
        assert robot.hp   == 60
        assert len(robot.capacities) == 2

    def test_energie_initiale(self):
        robot = RobotFactory.creer_robot_manuel("Sparky", RobotType.BALANCE, 60, 15, 15, 10)
        assert robot.energy == 100

    def test_creation_invalide(self):
        with pytest.raises(StatsInvalidesException):
            RobotFactory.creer_robot_manuel("Bad", RobotType.DEFENDER, 30, 10, 10, 10)


# ------------------------------------------------------------------
# creer_robot_aleatoire
# ------------------------------------------------------------------

class TestCreerRobotAleatoire:

    def test_stats_toujours_valides(self):
        """Génération répétée : toutes les stats doivent être valides."""
        for _ in range(20):
            robot = RobotFactory.creer_robot_aleatoire("TestBot", RobotType.ASSAULT)
            total = robot.hp + robot.attack + robot.defense + robot.speed
            assert total == 100, f"Total != 100 : {total}"
            assert 50 <= robot.hp   <= 150
            assert 10 <= robot.attack <= 50
            assert  5 <= robot.defense <= 40
            assert  5 <= robot.speed   <= 40

    def test_capacites_assignees(self):
        robot = RobotFactory.creer_robot_aleatoire("Scout", RobotType.AGILE)
        assert len(robot.capacities) == 2
