from dataclasses import dataclass
from enum import Enum


@dataclass
class Poke:
    level: int
    max_hp: int
    a: int
    b: int
    s: int
    current_hp: int


@dataclass
class PokeSpecies:
    no: int  # 図鑑No
    name: str  # 名前
    base_hp: int  # HP
    base_a: int  # 攻撃
    base_b: int  # 防御
    base_s: int  # 素早さ


class NatureTarget(Enum):
    NONE = 0
    A = 1
    B = 2
    S = 3


@dataclass
class PokeBreeding:
    """
    育成に関わる値
    """

    no: int
    level: int
    ev_hp: int
    ev_a: int
    ev_b: int
    ev_s: int
    iv_hp: int
    iv_a: int
    iv_b: int
    iv_s: int
    nature_up: NatureTarget  # 性格上昇補正のパラメータ
    nature_down: NatureTarget  # 性格下降補正のパラメータ
