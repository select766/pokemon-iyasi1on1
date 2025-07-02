"""
わるあがきバトルをシミュレートする
"""

import random

from pokemon_iyasi1on1.damage import calc_damage
from pokemon_iyasi1on1.model import Poke


def simulate(pokes: tuple[Poke, Poke], rng: random.Random) -> int:
    """
    わるあがきバトルをシミュレートし、勝者を返す
    PokeのHPは変化することに注意
    """

    while True:
        if pokes[0].s > pokes[1].s:
            move_order = [0, 1]
        elif pokes[0].s > pokes[1].s:
            move_order = [1, 0]
        else:
            # 同速なのでランダムに先攻を決める
            move_first = rng.randint(0, 1)
            move_order = [move_first, 1 - move_first]
        for attacker_idx in move_order:
            attacker = pokes[attacker_idx]
            defender = pokes[1 - attacker_idx]
            damage = calc_damage(
                attacker.level,
                50,  # わるあがきの威力
                attacker.a,
                defender.b,
                rng.randint(0, 23) == 0,  # 急所は1/24
                rng.randint(0, 15),  # ダメージ乱数は16段階
            )
            defender.current_hp = max(0, defender.current_hp - damage)
            if defender.current_hp == 0:
                return attacker_idx
            recoil = attacker.max_hp // 4
            attacker.current_hp = max(0, attacker.current_hp - recoil)

            if attacker.current_hp == 0:
                return 1 - attacker_idx
