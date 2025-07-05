"""
いくつかのケースでバトルのシミュレーションを行う
モンテカルロ版と有限マルコフ連鎖版の比較用
"""

import random

from pokemon_iyasi1on1.damage import calc_status
from pokemon_iyasi1on1.db import get_species_by_name
from pokemon_iyasi1on1.model import NatureTarget, Poke, PokeBreeding, PokeStrategy
from pokemon_iyasi1on1.regulation import EV_MAX, EV_MIN, IV_MAX, IV_MIN, POKE_LEVEL
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
    rng = random.Random(151)
    poke0 = calc_status(
        PokeBreeding(
            no=get_species_by_name("エルレイド").no,
            level=POKE_LEVEL,
            ev_hp=EV_MIN,
            ev_a=EV_MAX,
            ev_b=EV_MIN,
            ev_s=EV_MAX,
            iv_hp=IV_MAX,
            iv_a=IV_MAX,
            iv_b=IV_MAX,
            iv_s=IV_MAX,
            nature_up=NatureTarget.A,
            nature_down=NatureTarget.NONE,
            strategy=PokeStrategy.VEST,
        )
    )
    poke1 = calc_status(
        PokeBreeding(
            no=get_species_by_name("ルカリオ").no,
            level=POKE_LEVEL,
            ev_hp=EV_MIN,
            ev_a=EV_MAX,
            ev_b=EV_MIN,
            ev_s=EV_MAX,
            iv_hp=IV_MAX,
            iv_a=IV_MAX,
            iv_b=IV_MAX,
            iv_s=IV_MAX,
            nature_up=NatureTarget.A,
            nature_down=NatureTarget.NONE,
            strategy=PokeStrategy.VEST,
        )
    )
    print(poke0, poke1)
    print(monte_carlo((poke0, poke1), rng, 100000))
    poke0 = calc_status(
        PokeBreeding(
            no=get_species_by_name("ラティオス").no,
            level=POKE_LEVEL,
            ev_hp=EV_MIN,
            ev_a=EV_MAX,
            ev_b=EV_MIN,
            ev_s=EV_MAX,
            iv_hp=IV_MAX,
            iv_a=IV_MAX,
            iv_b=IV_MAX,
            iv_s=IV_MAX,
            nature_up=NatureTarget.A,
            nature_down=NatureTarget.NONE,
            strategy=PokeStrategy.VEST,
        )
    )
    poke1 = calc_status(
        PokeBreeding(
            no=get_species_by_name("ヤドラン").no,
            level=POKE_LEVEL,
            ev_hp=EV_MAX,
            ev_a=EV_MIN,
            ev_b=EV_MAX,
            ev_s=EV_MIN,
            iv_hp=IV_MAX,
            iv_a=IV_MAX,
            iv_b=IV_MAX,
            iv_s=IV_MIN,
            nature_up=NatureTarget.B,
            nature_down=NatureTarget.S,
            strategy=PokeStrategy.LEFTOVER,
        )
    )
    print(poke0, poke1)
    print(monte_carlo((poke0, poke1), rng, 100000))


if __name__ == "__main__":
    main()
