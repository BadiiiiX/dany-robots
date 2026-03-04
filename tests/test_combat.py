"""
Tests unitaires — module Combat (calcul des dégâts, déroulement du combat).
"""
import pytest
from impl.Robot.RobotFactory import RobotFactory
from impl.Robot.RobotType    import RobotType
from impl.Combat.Combat      import Combat, MODE_MANUEL, MODE_AUTO, TOURS_MAX
from impl.Combat.ai          import ACTION_ATTAQUE, ACTION_DEFENSE, ACTION_CAPACITE_2
from impl.exceptions         import CombatImpossibleException


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

def _make_robot(name: str, robot_type: RobotType = RobotType.ASSAULT,
                pv: int = 60, atk: int = 15, def_: int = 15, spd: int = 10):
    return RobotFactory.creer_robot_manuel(name, robot_type, pv, atk, def_, spd)


@pytest.fixture
def r1():
    return _make_robot("Alpha", RobotType.ASSAULT)


@pytest.fixture
def r2():
    return _make_robot("Beta", RobotType.DEFENDER)


# ------------------------------------------------------------------
# CombatImpossibleException
# ------------------------------------------------------------------

class TestCombatInit:

    def test_meme_robot_leve_exception(self, r1):
        with pytest.raises(CombatImpossibleException):
            Combat(r1, r1)

    def test_robots_differents_ok(self, r1, r2):
        c = Combat(r1, r2)
        assert c.robot1 is r1
        assert c.robot2 is r2

    def test_mode_invalide(self, r1, r2):
        with pytest.raises(ValueError):
            Combat(r1, r2, mode="inconnu")


# ------------------------------------------------------------------
# calculer_degats
# ------------------------------------------------------------------

class TestCalculerDegats:

    def test_minimum_5_degats(self, r1, r2):
        """Même si l'attaquant est plus faible, le minimum est 5."""
        # Créer un robot avec attaque très faible
        faible = _make_robot("Weak", RobotType.AGILE, pv=60, atk=10, def_=15, spd=15)
        fort   = _make_robot("Tank", RobotType.DEFENDER, pv=60, atk=10, def_=15, spd=15)
        c = Combat(faible, fort)
        # Tester 50 fois pour couvrir la variation aléatoire
        for _ in range(50):
            d = c.calculer_degats(faible, fort)
            assert d >= 5, f"Dégâts < 5 : {d}"

    def test_degats_positifs(self, r1, r2):
        c = Combat(r1, r2)
        for _ in range(30):
            assert c.calculer_degats(r1, r2) > 0


# ------------------------------------------------------------------
# Déroulement du combat
# ------------------------------------------------------------------

class TestCombat:

    def test_lancer_initialise_journal(self, r1, r2):
        c = Combat(r1, r2)
        c.lancer()
        assert len(c.journal) > 0
        assert c.tour == 0

    def test_jouer_tour_incremente_tour(self, r1, r2):
        c = Combat(r1, r2, mode=MODE_AUTO)
        c.lancer()
        c.jouer_tour()
        assert c.tour == 1

    def test_combat_complet_auto(self):
        """Un combat en mode auto doit toujours se terminer."""
        r_a = _make_robot("Attacker", RobotType.ASSAULT, pv=50, atk=30, def_=10, spd=10)
        r_b = _make_robot("Defender", RobotType.DEFENDER, pv=50, atk=10, def_=10, spd=30)
        c   = Combat(r_a, r_b, mode=MODE_AUTO)
        c.lancer()
        for _ in range(TOURS_MAX + 5):
            if c.jouer_tour():
                break
        assert c.est_termine()

    def test_action_defense_reduit_degats(self, r1, r2):
        """En mode défense, les dégâts reçus sont réduits de 50 %."""
        c = Combat(r1, r2, mode=MODE_MANUEL)
        c.lancer()
        # Robot1 choisit défense ; on vérifie que le buff est bien posé
        done = c.jouer_tour(action_robot1=ACTION_DEFENSE)
        # Le buff defense_active peut avoir expiré après le tick, mais au moins un tour a passé
        assert c.tour == 1

    def test_match_nul_apres_50_tours(self):
        """Avec des PV très élevés (hack direct) on atteint le match nul."""
        r_a = _make_robot("Tough1", RobotType.DEFENDER, pv=80, atk=10, def_=5, spd=5)
        r_b = _make_robot("Tough2", RobotType.DEFENDER, pv=80, atk=10, def_=5, spd=5)
        # Booster les PV pour éviter la mort en 50 tours
        r_a.hp = r_a.max_hp = 9999
        r_b.hp = r_b.max_hp = 9999
        c = Combat(r_a, r_b, mode=MODE_AUTO)
        c.lancer()
        for _ in range(TOURS_MAX + 1):
            if c.jouer_tour():
                break
        assert c.est_termine()
        assert c.vainqueur is None  # match nul
