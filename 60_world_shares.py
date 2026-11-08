"""Yearly world export shares of China and Germany by HS6 good (BACI HS92, 1995-2024).
World exports exclude flows to China and Germany themselves, as in 50_china_competition.py.
Writes <output>/subsidies/world_shares.parquet (hs92, year, world, chn, deu in thousand USD).
Usage: python 60_world_shares.py
"""
import zipfile

import pandas as pd

from config import load_config


def main():
    cfg = load_config()
    out = cfg["output"] / "subsidies"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with zipfile.ZipFile(cfg["data"]["scenarios"] / "baci92" / "BACI_HS92_V202601.zip") as z:
        for nm in sorted(n for n in z.namelist() if "_Y" in n):
            y = int(nm.split("_Y")[1][:4])
            b = pd.read_csv(z.open(nm), usecols=["i", "j", "k", "v"], dtype={"k": str})
            b = b[~b.j.isin([156, 276])]
            g = pd.DataFrame({"world": b.groupby("k").v.sum(), "chn": b[b.i == 156].groupby("k").v.sum(),
                              "deu": b[b.i.isin([276, 280])].groupby("k").v.sum()}).fillna(0)
            g["year"] = y
            rows.append(g.reset_index().rename(columns={"k": "hs92"}))
            print(y, end=" ", flush=True)
    print()
    d = pd.concat(rows, ignore_index=True)
    d.to_parquet(out / "world_shares.parquet", index=False)
    print(len(d), d.hs92.nunique())


if __name__ == "__main__":
    main()
