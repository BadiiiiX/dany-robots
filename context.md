# 🤖 Projet Python — Combat de Robots

## Contexte

Plongez dans l'arène des étincelles ! Des robots surpuissants s'affrontent dans des duels stratégiques. Chaque machine est unique : caractéristiques personnalisées, capacités spéciales dévastatrices. Une seule règle : **survivre !**

Concevez un jeu de combat futuriste avec une interface graphique immersive pour vivre chaque coup, esquive et explosion tour par tour.

---

## Exigence technique

- **Langage unique** : Python (léger, polyvalent, compatible tous OS)
- **Version** : Python 3.12
- **Bibliothèque graphique** : [pygame](https://www.pygame.org/docs/)

---

## Livrables

L'archive à remettre doit être nommée : `[1PYTH]-Projet-PYTHON-NOM-Prénom.zip`

Elle doit contenir :

- L'intégralité du **code source** commenté (tous les fichiers + `README.txt`)
- Une **documentation complète** :
  - Schéma des modules et classes, algorithmes en pseudo-code, formules de calcul, maquettes de l'interface
  - Guide de jeu avec captures d'écran, explication des 4 types de robots
  - Description du projet et bibliothèques utilisées
- Une **vidéo de démonstration** présentant une partie vous affrontant un robot

> 📅 **Date limite : 27 février 2026 à 19h00**
> Pénalité : **-2 points/jour** de retard
> Remise via le lien WIMI personnel reçu par mail (non partageable)

---

## Critères d'évaluation

### 📄 Documents (4 pts)

| Critère | Points | Détails |
|---|---|---|
| Spécifications techniques | 2 | Cahier des charges complet, justification des choix algorithmiques et structures de données |
| Clarté et structure | 1 | Document bien organisé, lisible, sans ambiguïté |
| Schémas et diagrammes | 1 | Présence de schémas (diagrammes de flux, UML simplifié) |

### 💻 Code (19 pts)

| Critère | Points | Détails |
|---|---|---|
| Fonctionnalités | 6 | Implémentation complète des fonctionnalités demandées |
| Modularité | 4 | Modules Python, fonctions bien découpées, respect du principe DRY |
| Gestion des fichiers | 2 | Sauvegarde/chargement des données |
| Gestion des erreurs | 3 | Utilisation de try/except, messages d'erreur clairs, validation des entrées |
| Qualité du code | 3 | Respect des conventions PEP 8, noms explicites, commentaires pertinents |
| Recherche & Développement | 1 | Interface graphique ou fonctionnalité avancée non enseignée |

### ▶️ Exécution (4 pts)

| Critère | Points | Détails |
|---|---|---|
| Exécution sans erreur | 2 | Programme robuste, tests de validation |
| Robustesse | 1 | Comportement cohérent face aux cas limites |
| Tests et validation | 1 | Présence de tests unitaires (pytest) |

### ⚠️ Malus

- Programme qui crash : **-5 pts**
- Code non exécutable : **-5 pts**
- Absence de gestion d'erreurs : **-3 pts**
- Copie détectée : **0/20**

---

## Cahier des charges

### Module de création de robots

#### Classe `Robot`

**Attributs obligatoires :**

| Attribut | Type | Contrainte |
|---|---|---|
| `nom` | str | 3-20 caractères, unique |
| `type` | str | Assaut, Défenseur, Agile, Équilibré |
| `pv` | int | 50-150 |
| `pv_max` | int | Valeur initiale des PV |
| `attaque` | int | 10-50 |
| `defense` | int | 5-40 |
| `vitesse` | int | 5-40 |
| `energie` | int | 0-100, commence à 100 |
| `capacites` | list | 2 capacités spéciales selon le type |
| `buffs_actifs` | dict | Effets temporaires en cours |

> ⚠️ **Contrainte importante :** `pv + attaque + defense + vitesse` doit être **exactement égal à 100**

#### Validation des statistiques

```python
def valider_stats(pv, attaque, defense, vitesse):
    # Vérifier que pv est entre 50 et 150
    # Vérifier que attaque est entre 10 et 50
    # Vérifier que defense est entre 5 et 40
    # Vérifier que vitesse est entre 5 et 40
    # Vérifier que pv + attaque + defense + vitesse == 100
    # Lever StatsInvalidesException si une condition n'est pas respectée
```

#### Types de robots et capacités

| Type | Capacité 1 | Capacité 2 |
|---|---|---|
| **Assaut** | Tir de barrage (30 énergie) : 1.5× dégâts | Rage de combat (40 énergie) : +20 ATT pendant 2 tours |
| **Défenseur** | Bouclier renforcé (35 énergie) : +15 DEF pendant 3 tours | Régénération (50 énergie) : +30 PV |
| **Agile** | Attaque rapide (25 énergie) : 2 attaques normales | Esquive (30 énergie) : évite la prochaine attaque (100%) |
| **Équilibré** | Frappe puissante (35 énergie) : 1.3× dégâts | Recharge rapide (20 énergie) : +40 énergie immédiatement |

#### Fonctions de création

```python
def creer_robot_manuel(nom, type, pv, attaque, defense, vitesse):
    # Valider le nom (3-20 caractères, pas de doublons)
    # Valider le type (dans la liste autorisée)
    # Appeler valider_stats()
    # Créer l'objet Robot avec les capacités correspondantes

def creer_robot_aleatoire(nom, type):
    # Générer aléatoirement pv, attaque, defense, vitesse
    # S'assurer que le total == 100
    # Respecter les limites min/max de chaque stat
    # Retourner le robot créé
```

---

### Module de système de combat

#### Classe `Combat`

**Attributs :**

| Attribut | Type | Description |
|---|---|---|
| `robot1` | Robot | Premier combattant |
| `robot2` | Robot | Second combattant |
| `tour` | int | Numéro du tour actuel |
| `journal` | list | Historique des actions |
| `mode` | str | `manuel`, `auto`, `rapide` |
| `vainqueur` | Robot / None | Vainqueur ou None |

> Lever `CombatImpossibleException` si les deux robots sont identiques ou invalides.

#### Ordre d'attaque

```python
def determiner_premier_attaquant(robot1, robot2):
    # Comparer la vitesse des deux robots
    # Le robot le plus rapide attaque en premier
    # En cas d'égalité : choix aléatoire
```

#### Calcul des dégâts

```python
def calculer_degats(attaquant, defenseur, type_attaque):
    degats_base = attaquant.attaque - defenseur.defense
    degats_base = max(5, degats_base)            # minimum 5 dégâts
    degats = degats_base * random(0.9, 1.1)      # variation ±10%
    # 10% de chance de coup critique : degats * 1.5
    # Si capacité : appliquer le multiplicateur correspondant
    return round(degats)
```

#### Actions disponibles par tour

1. **Attaque normale** — formule de dégâts standard, gratuite en énergie
2. **Capacité spéciale 1 ou 2** — déduit l'énergie, lève `EnergieInsuffisanteException` si insuffisant
3. **Défense** — réduit de 50% les dégâts au prochain tour, ajoute le buff `defense_active`, gratuite
4. **Gestion de l'énergie** — +20 énergie par tour (max 100)

#### Condition de victoire

```python
def verifier_fin_combat():
    # Si robot.pv <= 0 : l'adversaire est déclaré vainqueur
    # Limite : 50 tours maximum (match nul si dépassé)
```

---

### Module d'intelligence artificielle

```python
def decider_action_ia(robot, adversaire):
    if robot.energie < 30:
        return "défense"
    elif robot.energie >= 60 and capacite_disponible:
        return capacite_aleatoire()
    elif robot.pv < 30% and possede_regeneration:
        return "régénération"
    else:
        return "attaque normale"
```

---

### Module de sauvegarde et persistance

```python
def sauvegarder_robots(liste_robots, fichier="robots.json"):
    # Convertir chaque robot en dictionnaire
    # Sauvegarder en JSON avec indentation
    # Gérer les erreurs d'écriture (try/except)
    # Retourner True si succès, False sinon

def charger_robots(fichier="robots.json"):
    # Vérifier si le fichier existe
    # Lire et parser le JSON
    # Recréer les objets Robot depuis les dictionnaires
    # Si fichier absent ou corrompu : retourner liste vide
```

---

### Module d'interface graphique (pygame)

#### `MenuPrincipal`

- Titre du jeu (grande police)
- 4 boutons : **Créer Robot** | **Mes Robots** | **Combat** | **Quitter**
- Éléments centrés à l'écran

#### `EcranCreation`

- Champ texte pour le nom (3-20 caractères)
- Menu déroulant pour le type
- 4 sliders : PV, Attaque, Défense, Vitesse
- Affichage en temps réel du total (🟢 vert si = 100, 🔴 rouge sinon)
- Bouton **Créer Aléatoire**
- Bouton **Créer Robot** (actif seulement si total = 100)
- Affichage des capacités du type sélectionné
- Bouton **Retour**

#### `EcranListeRobots`

- Grille de cartes (Nom, Type, PV, ATT, DEF, VIT + icône)
- Bouton **Supprimer** avec confirmation sur chaque carte
- Message si vide : *Aucun robot disponible*
- Bouton **Retour**

#### `EcranCombat`

**Affichage (deux zones côte à côte) :**
- Icône du robot (animation lors d'attaque)
- Barre de vie avec animation progressive + texte `PV: X/Y`
- Barre d'énergie avec animation progressive + texte `ENERGIE: X/100`
- Stats : `ATT: X  DEF: Y  VIT: Z`
- Icônes de buffs actifs

**Actions :**
- 4 boutons : **Attaque** | **Capacité 1** | **Capacité 2** | **Défense**
- Coût en énergie affiché sur les boutons de capacités
- Boutons désactivés si énergie insuffisante
- Masqués en mode `auto` / `rapide`

**Sélection pré-combat :**
- 2 menus déroulants pour choisir les robots
- Vérification : au moins 2 robots, robots différents
- 3 boutons de mode : **Manuel** | **Auto** | **Rapide**
- Bouton **Lancer le combat**

---

## Structure du projet

```
Nom_du_projet/
├── modules/
│   ├── robot.py        # Classe Robot et fonctions de création
│   ├── combat.py       # Classe Combat, calculs, IA
│   ├── sauvegarde.py   # Gestion JSON
│   └── interface.py    # Toutes les classes d'écrans
├── main.py             # Point d'entrée du programme
└── requirements.txt    # Liste des dépendances
```

---

*Bon développement ! 🚀*
