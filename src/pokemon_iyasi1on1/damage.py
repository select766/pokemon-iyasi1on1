import math

from pokemon_iyasi1on1.db import get_species
from pokemon_iyasi1on1.model import NatureTarget, Poke, PokeBreeding


def calc_damage(
    level: int, power: int, attack: int, defend: int, critical: bool, random_: int
) -> int:
    """
    ダメージ計算を行う
    level: 攻撃側のレベル
    random_: 乱数補正(0 <= random_ <= 15)
    """
    return (
        (((level * 2 // 5 + 2) * power * attack // defend) // 50 + 2)
        * (int(critical) + 2)
        // 2
        * (random_ + 85)
        // 100
    )


def status_hp(bv: int, iv: int, ev: int, level: int) -> int:
    return (bv * 2 + iv + ev // 4) * level // 100 + level + 10


def status_non_hp(bv: int, iv: int, ev: int, level: int, nature: float) -> int:
    return math.floor(((bv * 2 + iv + ev // 4) * level // 100 + 5) * nature)


def calc_status(breeding: PokeBreeding) -> Poke:
    species = get_species(breeding.no)
    hp = status_hp(species.base_hp, breeding.iv_hp, breeding.ev_hp, breeding.level)
    return Poke(
        level=breeding.level,
        max_hp=hp,
        a=status_non_hp(
            species.base_a,
            breeding.iv_a,
            breeding.ev_a,
            breeding.level,
            1.1
            if breeding.nature_up == NatureTarget.A
            else 0.9
            if breeding.nature_down == NatureTarget.A
            else 1.0,
        ),
        b=status_non_hp(
            species.base_b,
            breeding.iv_b,
            breeding.ev_b,
            breeding.level,
            1.1
            if breeding.nature_up == NatureTarget.B
            else 0.9
            if breeding.nature_down == NatureTarget.B
            else 1.0,
        ),
        s=status_non_hp(
            species.base_s,
            breeding.iv_s,
            breeding.ev_s,
            breeding.level,
            1.1
            if breeding.nature_up == NatureTarget.S
            else 0.9
            if breeding.nature_down == NatureTarget.S
            else 1.0,
        ),
        current_hp=hp,
    )
