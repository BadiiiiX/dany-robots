"""
Exceptions métier du jeu Combat de Robots.
Chaque exception correspond à une règle du cahier des charges.
"""


class StatsInvalidesException(Exception):
    """
    Levée lorsque les statistiques d'un robot ne respectent pas les contraintes :
    - pv ∈ [50, 150], attaque ∈ [10, 50], défense ∈ [5, 40], vitesse ∈ [5, 40]
    - pv + attaque + défense + vitesse == 100
    """


class CombatImpossibleException(Exception):
    """
    Levée lorsqu'un combat ne peut pas être lancé :
    - les deux robots sont identiques (même nom)
    - un ou les deux robots sont invalides / None
    """


class EnergieInsuffisanteException(Exception):
    """
    Levée lorsqu'un robot tente d'utiliser une capacité
    alors qu'il n'a pas assez d'énergie.
    """


class NomInvalideException(Exception):
    """
    Levée lorsque le nom d'un robot est invalide :
    - moins de 3 ou plus de 20 caractères
    - déjà utilisé par un autre robot
    """
