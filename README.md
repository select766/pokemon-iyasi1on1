# ポケモンバトル仲間大会「いやしのはどう1on1」の考察プログラム

参加者の一人として、シミュレーションを用いた最適なパーティ構築を検討した際のコードです。

検討結果のブログ https://select766.hatenablog.com/entry/2025/07/12/230137

大会運営の記事 https://tetspond.hatenablog.com/entry/2025/06/29/135840

# 環境構築

WSL環境を想定。uvが必要。

```
uv sync
```

# 実行

様々な構築(1292通り)の全組み合わせについてモンテカルロシミュレーション(1000回)を行い、勝率を計算する。16スレッド環境で40分程度かかる。

```
python -m pokemon_iyasi1on1.generate_win_table
```

出力: `data/monte_carlo_win_table.pkl`

シミュレーション結果を用いて、混合戦略ナッシュ均衡を求めるnotebookを実行。

```
jupyter nbconvert --to notebook --execute compute_nash.ipynb
```

# データ
種族値リスト `src/pokemon_iyasi1on1/base_stats.csv` はポケモンWikiより。
https://wiki.xn--rckteqa2e.com/wiki/%E7%A8%AE%E6%97%8F%E5%80%A4%E4%B8%80%E8%A6%A7_(%E7%AC%AC%E4%B9%9D%E4%B8%96%E4%BB%A3)
