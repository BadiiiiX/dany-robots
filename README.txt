================================================================================
  ROBOT ARENA — Guide d'installation et de jeu
================================================================================

DESCRIPTION
-----------
Robot Arena est un jeu de combat de robots tour par tour developpé en Python 3.12
avec la bibliothèque pygame. Chaque robot possède des statistiques personnalisées
et deux capacités spéciales selon son type.

INSTALLATION
------------
1. Assurez-vous d'avoir Python 3.12 installé.
2. Créez un environnement virtuel (optionnel mais recommandé) :
     python -m venv .venv
     .venv\Scripts\activate          (Windows)
     source .venv/bin/activate       (Linux/macOS)
3. Installez les dépendances :
     pip install -r requirements.txt
4. Lancez le jeu :
     python main.py

LANCER LES TESTS
----------------
     python -m pytest tests/ -v

STRUCTURE DU PROJET
-------------------
  main.py              — Point d'entrée
  requirements.txt     — Dépendances
  robots.json          — Sauvegarde des robots (créé automatiquement)
  impl/
    Robot/             — Classe Robot, RobotType, RobotFactory, RobotBuff
    Capacity/          — 8 capacités spéciales (Assaut, Défenseur, Agile, Équilibré)
    Combat/            — Moteur de combat (Combat, IA)
    exceptions.py      — Exceptions personnalisées
    config.py          — Mapping type → capacités
    sauvegarde.py      — Sauvegarde / chargement JSON
  ui/
    RobotUI.py         — Boucle principale pygame
    ui_helpers.py      — Composants graphiques partagés
    Window/
      Menu.py          — Menu principal
      CreateRobotMenu.py — Création de robot
      RobotListMenu.py   — Liste des robots
      CombatMenu.py      — Écran de combat
  tests/
    test_robot.py      — Tests unitaires Robot / RobotFactory
    test_combat.py     — Tests unitaires Combat
    test_sauvegarde.py — Tests unitaires Sauvegarde

TYPES DE ROBOTS
---------------
  Assaut    — Dégâts élevés. Capacités : Tir de Barrage (x1.5), Rage de Combat (+20 ATK)
  Défenseur — Robuste. Capacités : Bouclier Renforcé (+15 DEF), Régénération (+30 PV)
  Agile     — Rapide. Capacités : Attaque Rapide (2 coups), Esquive (évite 1 attaque)
  Équilibré — Polyvalent. Capacités : Frappe Puissante (x1.3), Recharge Rapide (+40 énergie)

CONTRAINTE DE STATS
-------------------
  PV + Attaque + Défense + Vitesse = 100 exactement
  PV : 50–150   |   Attaque : 10–50   |   Défense : 5–40   |   Vitesse : 5–40

MODES DE COMBAT
---------------
  Manuel  — Vous choisissez l'action de votre robot à chaque tour.
  Auto IA — Les deux robots sont contrôlés par l'IA.
  Rapide  — Identique à Auto mais à vitesse accélérée.

CONTRÔLES EN COMBAT (mode Manuel)
----------------------------------
  Attaque     — Attaque normale (gratuite)
  Cap 1 (XE)  — Capacité spéciale 1 (coût en énergie indiqué)
  Cap 2 (XE)  — Capacité spéciale 2 (coût en énergie indiqué)
  Défense     — Réduit les dégâts reçus de 50 % ce tour (gratuit)

  L'énergie se régénère de +20 par tour (max 100).
  Le combat se termine au bout de 50 tours sans vainqueur (match nul).

================================================================================
