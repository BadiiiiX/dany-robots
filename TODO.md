# TODO — Combat de Robots

État au 25/02/2026. Deadline : **27/02/2026 à 19h00**.

Légende : [ ] à faire  [~] partiel  [x] terminé

---

## IMPL — Logique métier

### Robot
- [x] Classe `Robot` avec tous les attributs (hp, attack, defense, speed, energy, capacities, active_buffs)
- [x] `is_alive()` et `tick_buffs()`
- [x] `RobotType` enum (Assaut, Défenseur, Agile, Équilibré)
- [x] `RobotFactory.build()` + `assign_capacities()` via config
- [x] `impl/config.py` — mapping type → capacités
- [ ] `StatsInvalidesException` (fichier dédié ou dans robot.py)
- [ ] `valider_stats(pv, attaque, defense, vitesse)` — vérifier plages + somme == 100
- [ ] `creer_robot_manuel(nom, type, pv, attaque, defense, vitesse)` — valide nom (3-20 cars, unique) + stats, retourne Robot
- [ ] `creer_robot_aleatoire(nom, type)` — génère stats aléatoires dont la somme == 100 en respectant les plages

### Capacités
- [x] Classe abstraite `Capacity` — `execute(source, target)`, `energy_cost`, `_calc_damage()`
- [x] Assaut   : `HeavyStrike` (Tir de Barrage, ×1.5), `CombatRage` (Rage de Combat, +20 ATT/2 tours)
- [x] Défenseur: `ReinforcedShield` (Bouclier Renforcé, +15 DEF/3 tours), `Regeneration` (+30 PV)
- [x] Agile    : `QuickAttack` (Attaque Rapide, ×2 attaques), `Dodge` (Esquive, évite 1 attaque)
- [x] Équilibré: `PowerfulStrike` (Frappe Puissante, ×1.3), `QuickRecharge` (Recharge Rapide, +40 énergie)

### Combat  ← fichier impl/combat.py à créer
- [ ] `CombatImpossibleException`
- [ ] `EnergieInsuffisanteException`
- [ ] Classe `Combat(robot1, robot2, mode)` — attributs : tour, journal, vainqueur
- [ ] `determiner_premier_attaquant()` — vitesse ; égalité → aléatoire
- [ ] `calculer_degats(attaquant, defenseur)` — formule normale (min 5, ±10%, crit 10%)
- [ ] Action **attaque normale** — applique calculer_degats, gratuite
- [ ] Action **capacité 1 / 2** — vérifie énergie, appelle execute(), lève EnergieInsuffisanteException
- [ ] Action **défense** — ajoute buff `defense_active` (dégâts reçus ×0.5 tour suivant)
- [ ] Régénération d'énergie : +20 par tour (plafonné à 100)
- [ ] `verifier_fin_combat()` — pv ≤ 0 → vainqueur ; 50 tours → match nul
- [ ] Boucle de tour complète : tick_buffs, regen énergie, action, vérif fin
- [ ] Mode **manuel** — attend l'action du joueur humain
- [ ] Mode **auto** — les deux robots sont gérés par l'IA
- [ ] Mode **rapide** — idem auto mais sans délai d'affichage

### IA  ← dans impl/combat.py ou impl/ai.py
- [ ] `decider_action_ia(robot, adversaire)` :
  - énergie < 30  → défense
  - énergie ≥ 60 et capacité dispo → capacité aléatoire
  - pv < 30% et possède Régénération → Régénération
  - sinon → attaque normale

### Sauvegarde  ← fichier impl/sauvegarde.py à créer
- [ ] `sauvegarder_robots(liste_robots, fichier="robots.json")` — sérialise en JSON, try/except, retourne bool
- [ ] `charger_robots(fichier="robots.json")` — désérialise, recrée les objets Robot, retourne [] si absent/corrompu
- [ ] Gérer la contrainte d'unicité des noms au chargement

### Player  ← impl/Player/ (tous vides)
- [ ] Classe abstraite `Player` — attribut `robot`, méthode abstraite `choisir_action(combat)`
- [ ] `HumanPlayer` — délègue à l'interface (attend l'input du joueur)
- [ ] `AIPlayer` — appelle `decider_action_ia()`

---

## UI — Interface pygame

### Menu principal  ← ui/Window/Menu.py (stub coloré)
- [ ] Titre du jeu (grande police, centré)
- [ ] 4 boutons centrés : Créer Robot | Mes Robots | Combat | Quitter
- [ ] Navigation : chaque bouton appelle `ui.set_window(...)`

### Écran Création  ← ui/Window/CreateRobotMenu.py (stub cassé)
- [ ] Champ texte pour le nom (3-20 caractères)
- [ ] Menu déroulant pour le type (4 valeurs)
- [ ] 4 sliders : PV (50-80), Attaque (10-50), Défense (5-40), Vitesse (5-40)
- [ ] Affichage du total en temps réel (vert si == 100, rouge sinon)
- [ ] Affichage des 2 capacités du type sélectionné
- [ ] Bouton **Créer Aléatoire** — appelle creer_robot_aleatoire()
- [ ] Bouton **Créer Robot** — actif seulement si total == 100, appelle creer_robot_manuel()
- [ ] Bouton **Retour**

### Écran Liste Robots  ← ui/Window/RobotListMenu.py à créer
- [ ] Grille de cartes (Nom, Type, PV, ATT, DEF, VIT)
- [ ] Bouton **Supprimer** sur chaque carte avec confirmation
- [ ] Message « Aucun robot disponible » si liste vide
- [ ] Chargement depuis robots.json au on_enter()
- [ ] Bouton **Retour**

### Écran Combat  ← ui/Window/CombatMenu.py à créer
- [ ] **Sélection pré-combat** : 2 menus déroulants (robots différents requis), 3 boutons de mode, bouton Lancer
- [ ] Zone robot gauche : barre PV animée, barre énergie animée, stats, icônes buffs
- [ ] Zone robot droite : idem
- [ ] 4 boutons d'action : Attaque | Capacité 1 | Capacité 2 | Défense
  - Afficher le coût en énergie sur les boutons de capacités
  - Désactiver si énergie insuffisante
  - Masquer en mode auto/rapide
- [ ] Journal de combat scrollable
- [ ] Écran de fin : annonce du vainqueur (ou match nul), bouton Rejouer / Menu

---

## Qualité & Livraison

- [ ] Tests unitaires pytest — `valider_stats`, `creer_robot_manuel`, `calculer_degats`, `sauvegarder/charger`
- [ ] Gestion des erreurs complète (try/except sur toutes les entrées utilisateur et I/O fichiers)
- [ ] Commentaires PEP 8 sur tous les fichiers
- [ ] `requirements.txt` à jour
- [ ] `README.txt` — description, installation, lancement, règles du jeu
- [ ] Vérification : aucun crash sur cas limites (robot sans énergie, fichier JSON absent, nom dupliqué...)
