"""
様々なパラメータでモンテカルロシミュレーションを行い、勝率の表を作成する
"""

import itertools
import multiprocessing
import pickle
import random
from typing import Generator

from tqdm import tqdm

from pokemon_iyasi1on1.damage import calc_status, optimize_hb
from pokemon_iyasi1on1.db import get_species_by_name
from pokemon_iyasi1on1.model import NatureTarget, Poke, PokeBreeding, PokeStrategy
from pokemon_iyasi1on1.regulation import (
    AVAILABLE_POKEMONS,
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


def enumerate_breeding() -> Generator[PokeBreeding, None, None]:
    for poke_name in AVAILABLE_POKEMONS:
        poke = get_species_by_name(poke_name)
        for strategy in PokeStrategy:
            # 19タイプの極振りパターンを網羅
            # AS252 or A252 or S252 残り耐久
            for ev_a, ev_s in [(EV_MAX, EV_MAX), (EV_MAX, EV_MIN), (EV_MIN, EV_MAX)]:
                ev_hp, ev_b = optimize_hb(
                    poke.base_hp, IV_MAX, poke.base_b, IV_MAX, EV_TOTAL - ev_a - ev_s
                )
                for nature_up in [NatureTarget.A, NatureTarget.B, NatureTarget.S]:
                    yield PokeBreeding(
                        no=poke.no,
                        level=POKE_LEVEL,
                        ev_hp=ev_hp,
                        ev_a=ev_a,
                        ev_b=ev_b,
                        ev_s=ev_s,
                        iv_hp=IV_MAX,
                        iv_a=IV_MAX,
                        iv_b=IV_MAX,
                        iv_s=IV_MAX,
                        nature_up=nature_up,
                        nature_down=NatureTarget.NONE,
                        strategy=strategy,
                    )
            # 耐久最大、残りA or S
            ev_hp = EV_MAX
            ev_b = EV_MAX
            remain = EV_TOTAL - ev_hp - ev_b
            for ev_a, ev_s in [(remain, 0), (0, remain)]:
                for nature_up in [NatureTarget.A, NatureTarget.B, NatureTarget.S]:
                    yield PokeBreeding(
                        no=poke.no,
                        level=POKE_LEVEL,
                        ev_hp=ev_hp,
                        ev_a=ev_a,
                        ev_b=ev_b,
                        ev_s=ev_s,
                        iv_hp=IV_MAX,
                        iv_a=IV_MAX,
                        iv_b=IV_MAX,
                        iv_s=IV_MAX,
                        nature_up=nature_up,
                        nature_down=NatureTarget.NONE,
                        strategy=strategy,
                    )
            # 最遅ケース
            ev_s = 0
            # 最遅、A252
            ev_a = 252
            ev_hp, ev_b = optimize_hb(
                poke.base_hp, IV_MAX, poke.base_b, IV_MAX, EV_TOTAL - ev_a - ev_s
            )
            for nature_up in [NatureTarget.A, NatureTarget.B]:
                yield PokeBreeding(
                    no=poke.no,
                    level=POKE_LEVEL,
                    ev_hp=ev_hp,
                    ev_a=ev_a,
                    ev_b=ev_b,
                    ev_s=ev_s,
                    iv_hp=IV_MAX,
                    iv_a=IV_MAX,
                    iv_b=IV_MAX,
                    iv_s=IV_MIN,
                    nature_up=nature_up,
                    nature_down=NatureTarget.S,
                    strategy=strategy,
                )
            # 最遅、耐久最大、残りA
            ev_hp = EV_MAX
            ev_b = EV_MAX
            ev_a = EV_TOTAL - ev_hp - ev_b - ev_s
            for nature_up in [NatureTarget.A, NatureTarget.B]:
                yield PokeBreeding(
                    no=poke.no,
                    level=POKE_LEVEL,
                    ev_hp=ev_hp,
                    ev_a=ev_a,
                    ev_b=ev_b,
                    ev_s=ev_s,
                    iv_hp=IV_MAX,
                    iv_a=IV_MAX,
                    iv_b=IV_MAX,
                    iv_s=IV_MIN,
                    nature_up=nature_up,
                    nature_down=NatureTarget.S,
                    strategy=strategy,
                )


breedings = list(enumerate_breeding())
N_MATCHES = 1000


def match_breedings(match: tuple[int, int]) -> tuple[tuple[int, int], float]:
    rng = random.Random(151)
    pokes = tuple(calc_status(breedings[idx]) for idx in match)
    return (match, monte_carlo(pokes, rng, N_MATCHES))


def main():
    # 対戦ペア
    matches = list(itertools.combinations(range(len(breedings)), 2))
    results = []
    with multiprocessing.Pool() as pool:
        with tqdm(total=len(matches)) as t:
            for result in pool.imap_unordered(match_breedings, matches):
                results.append(result)
                t.update(1)
    with open("data/monte_carlo_win_table.pkl", "wb") as f:
        pickle.dump(
            {"breedings": breedings, "results": results, "n_matches": N_MATCHES}, f
        )


if __name__ == "__main__":
    main()
