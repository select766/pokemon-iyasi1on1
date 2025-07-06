"""
自分のポケモンを固定して、相手のポケモンとその型によるダメージ予測テーブルを生成
"""

"""
いくつかのケースでバトルのシミュレーションを行う
モンテカルロ版と有限マルコフ連鎖版の比較用
"""

import csv
import random
import sys

from pokemon_iyasi1on1.damage import calc_damage, calc_status, optimize_hb
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


def main():
    my_poke = calc_status(
        PokeBreeding(
            no=get_species_by_name("ヤドラン(ガラルのすがた)").no,
            level=POKE_LEVEL,
            ev_hp=4,
            ev_a=EV_MAX,
            ev_b=EV_MAX,
            ev_s=0,
            iv_hp=IV_MAX,
            iv_a=IV_MAX,
            iv_b=IV_MAX,
            iv_s=0,
            nature_up=NatureTarget.A,
            nature_down=NatureTarget.S,
            strategy=PokeStrategy.VEST,
        )
    )
    rows = []
    for poke_name in [
        "ピクシー",
        "プクリン",
        "ヤドン",  # 最終進化ではないが最遅
        "ヤドラン",
        "ヤドラン(ガラルのすがた)",
        "メガニウム",
        "ヤドキング",
        "ヤドキング(ガラルのすがた)",
        "ドーブル",
        "ハピナス",
        "サーナイト",
        "チリーン",
        "ラティアス",
        "ラティオス",
        "ルカリオ",
        "エルレイド",
        "ゴチルゼル",
        "ブロスター",
        "ブリムオン",
        "イエッサン♀",
    ]:
        row = {"enemy": poke_name}
        poke = get_species_by_name(poke_name)
        # 自分→相手のダメージ
        for column, hb_total, nature_b_up in [
            ("attack_0", 0, False),
            ("attack_256", 508 - 252, False),
            ("attack_504", 504, False),
            ("attack_504_up", 504, True),
        ]:
            ev_hp, ev_b = optimize_hb(
                poke.base_hp, IV_MAX, poke.base_b, IV_MAX, hb_total
            )
            enemy = calc_status(
                PokeBreeding(
                    no=poke.no,
                    level=POKE_LEVEL,
                    ev_hp=ev_hp,
                    ev_a=0,
                    ev_b=ev_b,
                    ev_s=0,
                    iv_hp=IV_MAX,
                    iv_a=IV_MAX,
                    iv_b=IV_MAX,
                    iv_s=IV_MAX,
                    nature_up=NatureTarget.B if nature_b_up else NatureTarget.NONE,
                    nature_down=NatureTarget.NONE,
                    strategy=PokeStrategy.VEST,
                )
            )
            damage_min = calc_damage(my_poke.level, 50, my_poke.a, enemy.b, False, 0)
            damage_max = calc_damage(my_poke.level, 50, my_poke.a, enemy.b, False, 15)
            row[column] = (
                f"{damage_min}-{damage_max}({round(damage_min / enemy.max_hp * 100, 1):.1f}-{round(damage_max / enemy.max_hp * 100, 1):.1f})"
            )
        # 相手→自分のダメージ
        for column, ev_a, nature_a_up in [
            ("defend_0", 0, False),
            ("defend_252", 252, False),
            ("defend_252_up", 252, True),
        ]:
            enemy = calc_status(
                PokeBreeding(
                    no=poke.no,
                    level=POKE_LEVEL,
                    ev_hp=0,
                    ev_a=ev_a,
                    ev_b=0,
                    ev_s=0,
                    iv_hp=IV_MAX,
                    iv_a=IV_MAX,
                    iv_b=IV_MAX,
                    iv_s=IV_MAX,
                    nature_up=NatureTarget.A if nature_a_up else NatureTarget.NONE,
                    nature_down=NatureTarget.NONE,
                    strategy=PokeStrategy.VEST,
                )
            )
            damage_min = calc_damage(enemy.level, 50, enemy.a, my_poke.b, False, 0)
            damage_max = calc_damage(enemy.level, 50, enemy.a, my_poke.b, False, 15)
            row[column] = (
                f"{damage_min}-{damage_max}({round(damage_min / my_poke.max_hp * 100, 1):.1f}-{round(damage_max / my_poke.max_hp * 100, 1):.1f})"
            )
        rows.append(row)

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "enemy",
            "attack_0",
            "attack_256",
            "attack_504",
            "attack_504_up",
            "defend_0",
            "defend_252",
            "defend_252_up",
        ],
    )
    writer.writerow(
        {
            "enemy": "",
            "attack_0": "自分→相手",
            "attack_256": "",
            "attack_504": "",
            "attack_504_up": "",
            "defend_0": "相手→自分",
            "defend_252": "",
            "defend_252_up": "",
        }
    )
    writer.writerow(
        {
            "enemy": "相手",
            "attack_0": "H0B0",
            "attack_256": "H+B=256",
            "attack_504": "H252B252",
            "attack_504_up": "H252B252↑",
            "defend_0": "A0",
            "defend_252": "A252",
            "defend_252_up": "A252↑",
        }
    )
    writer.writerows(rows)


if __name__ == "__main__":
    main()
