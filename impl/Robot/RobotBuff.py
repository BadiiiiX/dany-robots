from typing import TypedDict, Dict

class BuffData(TypedDict):
    stat: str
    value: int
    turns: int

Buffs = Dict[str, BuffData]