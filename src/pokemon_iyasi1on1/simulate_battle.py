"""
わるあがきバトルをシミュレートする
"""

import math
import random

from pokemon_iyasi1on1.damage import calc_damage
from pokemon_iyasi1on1.model import Poke, PokeStrategy


def simulate(pokes: tuple[Poke, Poke], rng: random.Random) -> int:
    """
    バトルをシミュレートし、勝者(0 or 1)を返す
    PokeのHPは変化するため、事前にreset()を呼んでおくこと。
    """

    while True:
        if pokes[0].s > pokes[1].s:
            move_order = [0, 1]
        elif pokes[1].s > pokes[0].s:
            move_order = [1, 0]
        else:
            # 同速なのでランダムに先攻を決める
            move_first = rng.randint(0, 1)
            move_order = [move_first, 1 - move_first]
        for attacker_idx in move_order:
            attacker = pokes[attacker_idx]
            defender = pokes[1 - attacker_idx]
            if attacker.heal_pulse_pp > 0:
                # いやしのはどうが発動
                attacker.heal_pulse_pp -= 1
                # 回復量は切り上げ
                # メガランチャーは考慮していない
                defender.current_hp = min(
                    defender.max_hp,
                    defender.current_hp + math.ceil(defender.max_hp / 2),
                )
            else:
                # わるあがきが発動
                damage = calc_damage(
                    attacker.level,
                    50,  # わるあがきの威力
                    attacker.a,
                    defender.b,
                    rng.randrange(0, 24) == 0,  # 急所は1/24
                    rng.randrange(0, 16),  # ダメージ乱数は16段階
                )
                defender.current_hp = max(0, defender.current_hp - damage)
                if defender.current_hp == 0:
                    return attacker_idx

                # 反動
                recoil = attacker.max_hp // 4
                attacker.current_hp = max(0, attacker.current_hp - recoil)

                if attacker.current_hp == 0:
                    return 1 - attacker_idx

        # ターン終了処理
        for attacker_idx in move_order:
            attacker = pokes[attacker_idx]
            if attacker.strategy == PokeStrategy.LEFTOVER:
                # たべのこしが発動
                # 回復量は切り捨て(切り捨てて0になるケースは1になるが、LV50戦では発生しないため未実装)
                attacker.current_hp = min(
                    attacker.max_hp,
                    attacker.current_hp + math.floor(attacker.max_hp / 16),
                )
