"""
Module de sauvegarde et persistance.
Sérialise et désérialise la liste des robots au format JSON.
"""
import json
import os

from impl.Robot.Robot import Robot
from impl.Robot.RobotFactory import RobotFactory
from impl.Robot.RobotType import RobotType

FICHIER_PAR_DEFAUT = "robots.json"


# ------------------------------------------------------------------
# Sérialisation
# ------------------------------------------------------------------

def _robot_vers_dict(robot: Robot) -> dict:
    """Convertit un Robot en dictionnaire sérialisable."""
    return {
        "name":    robot.name,
        "type":    robot.type.name,   # Nom de l'enum (ex. "ASSAULT"), pas la valeur
        "hp":      robot.hp,
        "max_hp":  robot.max_hp,
        "attack":  robot.attack,
        "defense": robot.defense,
        "speed":   robot.speed,
        "energy":  robot.energy,
    }


def _dict_vers_robot(data: dict) -> Robot:
    """
    Recrée un objet Robot depuis un dictionnaire.
    Assigne les capacités via RobotFactory.
    Lève KeyError si des clés sont manquantes, ValueError si le type est inconnu.
    """
    robot_type = RobotType[data["type"]]  # Lève KeyError si type inconnu
    robot = Robot(
        name    = data["name"],
        type    = robot_type,
        hp      = data["hp"],
        max_hp  = data["max_hp"],
        attack  = data["attack"],
        defense = data["defense"],
        speed   = data["speed"],
        energy  = data["energy"],
    )
    RobotFactory.assign_capacities(robot)
    return robot


# ------------------------------------------------------------------
# API publique
# ------------------------------------------------------------------

def sauvegarder_robots(
    liste_robots: list[Robot],
    fichier: str = FICHIER_PAR_DEFAUT,
) -> bool:
    """
    Sauvegarde la liste de robots dans un fichier JSON.

    Retourne True si l'écriture a réussi, False sinon.
    Les erreurs sont attrapées silencieusement pour ne pas faire crasher le jeu.
    """
    try:
        donnees = [_robot_vers_dict(robot) for robot in liste_robots]
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"[Sauvegarde] Erreur lors de l'écriture de '{fichier}' : {e}")
        return False
    except Exception as e:
        print(f"[Sauvegarde] Erreur inattendue : {e}")
        return False


def charger_robots(fichier: str = FICHIER_PAR_DEFAUT) -> list[Robot]:
    """
    Charge la liste de robots depuis un fichier JSON.

    Retourne une liste vide si le fichier est absent, illisible ou corrompu.
    Les entrées invalides sont ignorées avec un message d'avertissement.
    """
    if not os.path.exists(fichier):
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            donnees = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Chargement] Impossible de lire '{fichier}' : {e}")
        return []

    robots = []
    for i, data in enumerate(donnees):
        try:
            robot = _dict_vers_robot(data)
            robots.append(robot)
        except (KeyError, ValueError) as e:
            print(f"[Chargement] Entrée #{i} ignorée (données invalides) : {e}")

    return robots
