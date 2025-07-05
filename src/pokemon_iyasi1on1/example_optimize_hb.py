"""
いくつかのケースでバトルのシミュレーションを行う
モンテカルロ版と有限マルコフ連鎖版の比較用
"""

import random

from pokemon_iyasi1on1.damage import calc_status, optimize_hb
from pokemon_iyasi1on1.db import get_species_by_name
from pokemon_iyasi1on1.model import NatureTarget, Poke, PokeBreeding, PokeStrategy
from pokemon_iyasi1on1.regulation import (
    EV_MAX,
    EV_MIN,
    EV_TOTAL,
    IV_MAX,
    IV_MIN,
    POKE_LEVEL,
)
from pokemon_iyasi1on1.simulate_battle import simulate


def monte_carlo(pokes: tuple[Poke, Poke], rng: random.Random, count: int):
    """
    モンテカルロシミュレーションを行い、pokes[0]の勝率を返す
    """
    lhs_wins = 0
    for _ in range(count):
        [poke.reset() for poke in pokes]
        winner = simulate(pokes, rng)
        if winner == 0:
            lhs_wins += 1
    return lhs_wins / count


def main():
    for poke_name in [
        "エルレイド",
        "ブリムオン",
        "ハピナス",
        "ヤドラン",
    ]:
        print(poke_name)
        poke = get_species_by_name(poke_name)
        for total in [4, 252, 508]:
            print(
                "total",
                total,
                "hb",
                optimize_hb(poke.base_hp, IV_MAX, poke.base_b, IV_MAX, total),
            )


if __name__ == "__main__":
    main()
