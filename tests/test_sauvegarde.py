"""
Tests unitaires — module Sauvegarde (sérialisation/désérialisation JSON).
"""
import json
import os
import tempfile

import pytest
from impl.Robot.RobotFactory import RobotFactory
from impl.Robot.RobotType    import RobotType
from impl.sauvegarde         import sauvegarder_robots, charger_robots


@pytest.fixture
def tmp_file(tmp_path):
    return str(tmp_path / "robots_test.json")


def _make_robot(name: str):
    return RobotFactory.creer_robot_manuel(name, RobotType.AGILE, 60, 15, 15, 10)


class TestSauvegarder:

    def test_retourne_true_si_succes(self, tmp_file):
        robot = _make_robot("TestBot")
        assert sauvegarder_robots([robot], tmp_file) is True

    def test_fichier_cree(self, tmp_file):
        robot = _make_robot("TestBot")
        sauvegarder_robots([robot], tmp_file)
        assert os.path.exists(tmp_file)

    def test_json_valide(self, tmp_file):
        robot = _make_robot("TestBot")
        sauvegarder_robots([robot], tmp_file)
        with open(tmp_file, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert data[0]["name"] == "TestBot"

    def test_liste_vide(self, tmp_file):
        assert sauvegarder_robots([], tmp_file) is True
        with open(tmp_file, encoding="utf-8") as f:
            data = json.load(f)
        assert data == []


class TestCharger:

    def test_fichier_absent_retourne_liste_vide(self, tmp_path):
        chemin = str(tmp_path / "inexistant.json")
        assert charger_robots(chemin) == []

    def test_charge_robot_correctement(self, tmp_file):
        robot = _make_robot("Reload")
        sauvegarder_robots([robot], tmp_file)
        robots = charger_robots(tmp_file)
        assert len(robots) == 1
        assert robots[0].name    == "Reload"
        assert robots[0].type    == RobotType.AGILE
        assert robots[0].hp      == 60
        assert robots[0].attack  == 15
        assert len(robots[0].capacities) == 2

    def test_json_corrompu_retourne_liste_vide(self, tmp_file):
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("{invalid json{{")
        assert charger_robots(tmp_file) == []

    def test_entree_invalide_ignoree(self, tmp_file):
        # Une entrée valide et une invalide
        robot = _make_robot("Valide")
        sauvegarder_robots([robot], tmp_file)
        # Corrompre une entrée dans le fichier
        with open(tmp_file, encoding="utf-8") as f:
            data = json.load(f)
        data.append({"name": "Corrompu"})  # clés manquantes
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        robots = charger_robots(tmp_file)
        assert len(robots) == 1  # seul le robot valide est chargé
        assert robots[0].name == "Valide"

    def test_aller_retour(self, tmp_file):
        """Sauvegarde puis rechargement : toutes les stats préservées."""
        robot = RobotFactory.creer_robot_manuel("Omega", RobotType.BALANCE, 65, 15, 10, 10)
        sauvegarder_robots([robot], tmp_file)
        loaded = charger_robots(tmp_file)[0]
        assert loaded.name    == robot.name
        assert loaded.type    == robot.type
        assert loaded.hp      == robot.hp
        assert loaded.attack  == robot.attack
        assert loaded.defense == robot.defense
        assert loaded.speed   == robot.speed
        assert loaded.energy  == robot.energy
