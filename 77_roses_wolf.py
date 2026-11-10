"""Regional GDP per head in Europe, 1900-2021 (Rosés and Wolf database, version 7).

Data: Rosés, J. R. and Wolf, N. (2021), "Regional growth and inequality in the long run:
Europe, 1900-2015", Oxford Review of Economic Policy 37(1); database version 7 with 2021
(files RosesWolf_RegionalGDP_v7.dta and the region shapefile, provided by the user).
173 regions (NUTS 2, partly NUTS 1) in 16 countries, benchmark years 1900 to 2021. GDP (series in 2011 international dollars, which alone reaches 2021) in
million 1990 international dollars (Geary-Khamis), population in thousands.
Measures: GDP per head; index relative to the unweighted regional mean of each year (= 100);
sigma convergence (standard deviation of log GDP per head across regions); beta convergence
1900-2021 (growth on initial log level); persistence (Spearman rank correlation 1900 vs 2021).
Writes <output>/regional/roses_wolf.csv, roses_wolf_summary.csv, roses_wolf_maps.png and site
data roses_wolf.json (SVG paths in the projection of the EU maps).
Usage: python 77_roses_wolf.py [site_data_folder]
"""
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapefile

import regional as rg
from config import load_config


def laea(lon, lat):
    """Spherical Lambert azimuthal equal-area, centre 52 N 10 E with the false origin of
    EPSG:3035 (close enough to the GISCO maps for display)."""
    R, l0, p0 = 6371007.0, math.radians(10), math.radians(52)
    lam, phi = np.radians(lon), np.radians(lat)
    k = np.sqrt(2 / (1 + math.sin(p0) * np.sin(phi) + math.cos(p0) * np.cos(phi) * np.cos(lam - l0)))
    x = R * k * np.cos(phi) * np.sin(lam - l0)
    y = R * k * (math.cos(p0) * np.sin(phi) - math.sin(p0) * np.cos(phi) * np.cos(lam - l0))
    return x + 4321000, y + 3210000


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "roses_wolf"
    out = cfg["output"] / "regional"
    d = pd.read_stata(raw / "RosesWolf_RegionalGDP_v7.dta")
    d["pc"] = d.gdp_2011 / d.population * 1000          # gdp_1990 ends in 2015; gdp_2011 covers 2021
    d["lpc"] = np.log(d.pc)
    d["idx"] = 100 * d.pc / d.groupby("year").pc.transform("mean")
    d.round(4).to_csv(out / "roses_wolf.csv", index=False)
    years = sorted(d.year.unique())
    sig = d.groupby("year").lpc.std()
    w = d.pivot(index="nuts", columns="year", values="lpc")
    ww = w[[1900, 2021]].dropna()
    beta = np.polyfit(ww[1900], (ww[2021] - ww[1900]) / (2021 - 1900), 1)[0]
    rho = ww.rank().corr().iloc[0, 1]
    print(f"regions with 1900 and 2021: {len(ww)}")
    de = d[d.country == "Germany"]
    summ = pd.DataFrame({"year": years, "sigma": sig.reindex(years).values,
                         "max_min_ratio": [d[d.year == y].pc.max() / d[d.year == y].pc.min() for y in years],
                         "de_mean_idx": [de[de.year == y].idx.mean() for y in years]})
    summ.round(4).to_csv(out / "roses_wolf_summary.csv", index=False)
    print(summ.round(3).to_string(index=False))
    print(f"beta 1900-2021: {beta:.4f} per year; rank correlation 1900 vs 2021: {rho:.2f}")
    for y in (1900, 1950, 2021):
        t = d[d.year == y].dropna(subset=["idx"]).sort_values("idx")
        print(y, "top:", list(zip(t.region.tail(3), t.idx.tail(3).round(0))), "bottom:", list(zip(t.region.head(3), t.idx.head(3).round(0))))
    # geometry: shapefile polygons (NUTS 2) -> data region with the longest matching code prefix
    rd = shapefile.Reader(str(raw / "shp" / "regions_nuts2"))
    codes = set(d.nuts)
    shapes = {}
    for sr in rd.shapeRecords():
        c = sr.record[0]
        m = next((c[:n] for n in range(len(c), 1, -1) if c[:n] in codes), None)
        if not m:
            continue
        pts, parts = np.array(sr.shape.points), list(sr.shape.parts) + [len(sr.shape.points)]
        for a, b in zip(parts[:-1], parts[1:]):
            x, y = laea(pts[a:b, 0], pts[a:b, 1])
            shapes.setdefault(m, []).append(np.c_[x, y])
    print(f"regions with geometry: {len(shapes)} of {len(codes)}")
    bins = [0, 50, 75, 90, 110, 125, 150, 1e9]
    cols = ["#7f0000", "#e06666", "#fce4d6", "#f2f2f2", "#deebf7", "#5b9bd5", "#002060"]
    ext = (2600000, 5400000, 1400000, 5300000)
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    for a, y in zip(axes, (1900, 1950, 2021)):
        rg.choropleth(a, shapes, d[d.year == y].set_index("nuts").idx.to_dict(), bins, cols, extent=ext, lw=0.2)
        a.set_title(str(y), fontsize=11, loc="left")
    rg.legend_bins(axes[0], bins, cols, fmt="{:.0f}", loc="upper left")
    fig.suptitle("BIP je Einwohner nach Regionen, Mittel aller Regionen = 100", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis der Rosés-Wolf-Datenbank zum regionalen BIP (Version 7), Rosés und Wolf (2021). "
             "Grenzen der heutigen NUTS-Regionen.", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "roses_wolf_maps.png", dpi=150); plt.close(fig)
    if site:
        paths, h = rg.svg_paths(shapes, extent=ext, width=500, tol=6000)
        piv = d.pivot(index="nuts", columns="year", values="idx").round(1)
        j = {"width": 500, "height": h, "paths": paths, "years": [int(y) for y in years],
             "names": d.drop_duplicates("nuts").set_index("nuts").region.to_dict(),
             "idx": {n: [None if pd.isna(v) else float(v) for v in r] for n, r in piv.iterrows()},
             "sigma": summ.sigma.round(3).tolist(), "beta": round(float(beta), 4), "rho": round(float(rho), 2),
             "de_idx": summ.de_mean_idx.round(1).tolist()}
        p = Path(site) / "roses_wolf.json"
        p.write_text(json.dumps(j, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
