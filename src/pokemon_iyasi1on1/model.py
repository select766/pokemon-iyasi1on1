from dataclasses import dataclass
from enum import Enum

HEAL_PULSE_MAX_PP = 10  # いやしのはどうの最大PP


class PokeStrategy(Enum):
    """
    ポケモンの戦略型
    """

    VEST = 0  # とつげきチョッキ
    LEFTOVER = 1  # たべのこし


@dataclass
class Poke:
    level: int
    max_hp: int
    a: int
    b: int
    s: int
    current_hp: int
    strategy: PokeStrategy
    heal_pulse_pp: int  # いやしのはどうの残りPP

    def reset(self):
        """
        戦闘中に変化する状態をリセットする
        """
        self.current_hp = self.max_hp
        match self.strategy:
            case PokeStrategy.VEST:
                self.heal_pulse_pp = 0
            case _:
                self.heal_pulse_pp = HEAL_PULSE_MAX_PP


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
    strategy: PokeStrategy
