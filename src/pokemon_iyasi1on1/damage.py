import math

from pokemon_iyasi1on1.db import get_species
from pokemon_iyasi1on1.model import NatureTarget, Poke, PokeBreeding
from pokemon_iyasi1on1.regulation import EV_MAX


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


def _optimal_xy(A: float, B: float, C: float) -> tuple[float, float, float]:
    """
    Maximise  (A + X + 60)*(B + Y + 5)
    subject to
        0 ≤ X ≤ 31.5
        0 ≤ Y ≤ 31.5
        X + Y ≤ C        (A, B, C are given positive constants)
    戻り値: (最適 X, 最適 Y, 最大値)
    """
    CAP = 31.5  # 上限 31.5 を一か所にまとめておくと後で拡張しやすい

    if not (A > 0 and B > 0 and C >= 0):
        raise ValueError("A, B は正、C は非負で与えてください。")

    a = A + 60  # (A+X+60) の定数部分
    b = B + 5  # (B+Y+5) の定数部分

    # まず X+Y が取り得る最大和 T (個別上限を考慮)
    T = min(C, 2 * CAP)

    # X+Y=T と置いたときの (a+X)*(b+T–X) を X で最大化
    # f(X) = (a+X)*(b+T–X) の極値は f'(X)=0 → X0 = (b+T–a)/2
    x0 = (b + T - a) / 2

    # 範囲 [0, T] に切り詰め、その上で個別上限 31.5 も適用
    x0 = max(0.0, min(x0, T))
    x0 = min(x0, CAP)  # X ≤ 31.5
    y0 = T - x0

    # Y も上限を守れているかチェック。超えていれば調整。
    if y0 > CAP:  # 超過分を X に回す
        y0 = CAP
        x0 = T - y0
        x0 = min(x0, CAP)  # 念のためもう一度 X 上限を確認

    # 念のため 0-境界／片方上限／両方上限の点も評価し、
    # 漏れなく最大値を拾う（ほとんどの場合は x0,y0 が最適）
    candidates = {
        (x0, y0),
        (0.0, T),  # X=0
        (CAP, max(0.0, T - CAP)),  # X 上限
        (max(0.0, T - CAP), CAP),  # Y 上限
    }

    best_val = -float("inf")
    best_x = best_y = 0.0

    for x, y in candidates:
        if 0 <= x <= CAP and 0 <= y <= CAP and x + y <= T:
            val = (a + x) * (b + y)
            if val > best_val:
                best_val, best_x, best_y = val, x, y

    return best_x, best_y, best_val


def optimize_hb(
    bv_h: int, iv_h: int, bv_b: int, iv_b: int, ev_total: int
) -> tuple[int, int]:
    """
    耐久値を最適化するような努力値配分を求める
    耐久値: HP実数値*防御実数値
    戻り値: H努力値、B努力値
    前提: LV50
    """

    """
    やること
    HP: (A+X+60) A: (HP種族値*2+個体値)/2, X: 努力値/8
    防御: (B+Y+5) B: (HP種族値*2+個体値)/2, Y: 努力値/8
    として、これらの積を最大化するX,Yを一度実数で求める
    制約として、努力値は0~252かつ、合計をev_total（他のパラメータに振った残り）以下とする

    整数の努力値への割り当て
    努力値/4が奇数になることで実数値が1増える式になっている
    ダメージ計算式上、HPが増えるほうが防御よりちょっとだけ得。
    HP/4が奇数になるように切り上げて、残りを防御に振る
    """
    if ev_total < 4:
        return (0, 0)
    A = (bv_h * 2 + iv_h) / 2
    B = (bv_b * 2 + iv_b) / 2
    X, Y, _ = _optimal_xy(A, B, ev_total / 8)

    if X <= 0:
        ev_h = 0
    else:
        # ev_h: X*8以上の最小の8n+4
        ev_h = math.ceil((X * 8 + 4) / 8) * 8 - 4
        ev_h = min(ev_h, min(ev_total, EV_MAX))
    ev_b = min(ev_total - ev_h, EV_MAX)
    assert ev_b >= 0

    return (ev_h, ev_b)


def calc_status(breeding: PokeBreeding) -> Poke:
    species = get_species(breeding.no)
    hp = status_hp(species.base_hp, breeding.iv_hp, breeding.ev_hp, breeding.level)
    poke = Poke(
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
        current_hp=0,  # resetで適切な値を設定
        strategy=breeding.strategy,
        heal_pulse_pp=0,  # resetで適切な値を設定
    )
    poke.reset()
    return poke
