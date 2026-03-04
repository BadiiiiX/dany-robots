from typing import TypedDict, Dict

class BuffData(TypedDict, total=False):
    """
    Données d'un buff actif sur un robot.
    - 'turns'         (obligatoire) : nombre de tours restants.
    - 'stat' + 'value' (optionnels) : stat modifiée et valeur à annuler à l'expiration.
      Absents pour les buffs non-stat (ex. evasion, defense_active).
    """
    turns: int   # obligatoire dans les faits, mais total=False simplifie les sous-types
    stat: str
    value: int

Buffs = Dict[str, BuffData]