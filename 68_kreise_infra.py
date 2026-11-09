"""Energy and transport infrastructure by German district from OpenStreetMap.

Data: OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0), downloaded per Land with
tools/pc_fetch_osm.py (power lines with voltage tag, substations, railway=rail without
service tag, highway=motorway). District geometry: GISCO NUTS 2024 level 3, 1:1 million.
Ways that cross Land borders appear in two files and are de-duplicated. Lines are clipped
to districts; lengths are computed in a sinusoidal projection (central meridian 10.5 E),
error well below 1 % for Germany.
Indicators per district (aggregates only, no maps of single facilities):
  ehv_km   extra-high-voltage lines (>= 220 kV), route km per 100 km2 (circuit lines along the
           same pylons are mapped as one way in OSM)
  hv_km    110 kV lines, km per 100 km2
  sub_n    substations >= 110 kV (transmission and distribution), count
  rail_km  railway lines (main and branch, without sidings), track-way km per 100 km2
  rail_el  share of that length that is electrified, %
  bab_km   motorway km per 100 km2 (carriageway length / 2, since OSM maps both directions)
OSM completeness varies; power lines in Germany are mapped close to completely, rail and
motorways completely.
Writes <output>/kreise/infra_kreise.csv, infra_maps.png and site data kreise_infra.json.
Usage: python 68_kreise_infra.py [site_data_folder]
"""
import gzip
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import STRtree
from shapely.geometry import LineString, Point, shape
from shapely.ops import transform

import regional as rg
from config import load_config

R = 6371.0088
LON0 = 10.5


def sinus(lon, lat):
    la = np.radians(lat)
    return R * np.radians(np.asarray(lon) - LON0) * np.cos(la), R * la


def volt(tags):
    vs = [int(v) for v in str(tags.get("voltage", "")).replace(",", ";").split(";") if v.strip().isdigit()]
    return max(vs) if vs else 0


def load(raw, cat):
    seen, out = set(), []
    for f in sorted((raw / "osm").glob(f"{cat}_DE-*.json.gz")):
        for ft in json.load(gzip.open(f))["features"]:
            g = ft["g"]
            key = (tuple(g[0]), tuple(g[-1]), len(g))
            if key in seen:
                continue
            seen.add(key)
            out.append(ft)
    return out


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "kreise"
    out.mkdir(parents=True, exist_ok=True)
    gj = json.load(open(raw / "regional" / "nuts3_2024_01m.geojson"))
    polys = {f["properties"]["NUTS_ID"]: transform(sinus, shape(f["geometry"])) for f in gj["features"] if f["properties"]["NUTS_ID"].startswith("DE")}
    ids = list(polys)
    tree = STRtree([polys[i] for i in ids])
    area = pd.Series({i: p.area for i, p in polys.items()})
    print(f"{len(ids)} districts, area {area.sum():,.0f} km2")

    def clip(lines):
        """Sum of clipped length per district for lists of (LineString, group)."""
        acc = {}
        for ln, grp in lines:
            for j in tree.query(ln):
                p = polys[ids[j]]
                l = ln.intersection(p).length
                if l > 0:
                    acc[(ids[j], grp)] = acc.get((ids[j], grp), 0) + l
        return pd.Series(acc, dtype=float)

    res = pd.DataFrame(index=ids)
    pl = []
    for ft in load(raw, "power_line"):
        v = volt(ft["tags"])
        grp = "ehv" if v >= 220000 else "hv" if v >= 110000 else None
        if grp and len(ft["g"]) > 1:
            x, y = sinus(*np.array(ft["g"]).T)
            pl.append((LineString(np.c_[x, y]), grp))
    s = clip(pl).unstack().reindex(ids).fillna(0)
    res["ehv_km"], res["hv_km"] = s.get("ehv", 0) / area * 100, s.get("hv", 0) / area * 100
    rl = []
    for ft in load(raw, "rail"):
        if len(ft["g"]) > 1:
            x, y = sinus(*np.array(ft["g"]).T)
            el = str(ft["tags"].get("electrified", "no")) not in ("no", "")
            rl.append((LineString(np.c_[x, y]), "el" if el else "nel"))
    s = clip(rl).unstack().reindex(ids).fillna(0)
    tot = s.sum(axis=1)
    res["rail_km"], res["rail_el"] = tot / area * 100, 100 * s.get("el", 0) / tot.replace(0, np.nan)
    ml = []
    for ft in load(raw, "motorway"):
        if len(ft["g"]) > 1:
            x, y = sinus(*np.array(ft["g"]).T)
            ml.append((LineString(np.c_[x, y]), "bab"))
    s = clip(ml).unstack().reindex(ids).fillna(0)
    res["bab_km"] = s["bab"] / 2 / area * 100
    cnt = {}
    for ft in load(raw, "substation"):
        if volt(ft["tags"]) >= 110000 and ft["tags"].get("substation") not in ("minor_distribution",):
            pt = Point(*sinus(*ft["g"][0]))
            for j in tree.query(pt):
                if polys[ids[j]].contains(pt):
                    cnt[ids[j]] = cnt.get(ids[j], 0) + 1
                    break
    res["sub_n"] = pd.Series(cnt).reindex(ids).fillna(0).astype(int)
    res["area_km2"] = area
    names = {f["properties"]["NUTS_ID"]: f["properties"]["NAME_LATN"] for f in gj["features"]}
    res["name"] = pd.Series(names)
    res.round(3).to_csv(out / "infra_kreise.csv")
    tot_km = {"ehv": (res.ehv_km * area / 100).sum(), "hv": (res.hv_km * area / 100).sum(), "rail": (res.rail_km * area / 100).sum(),
              "bab": (res.bab_km * area / 100).sum(), "sub": res.sub_n.sum()}
    print("Germany totals:", {k: round(v) for k, v in tot_km.items()}, "electrified %.0f%%" % (100 * ((res.rail_el / 100 * res.rail_km * area).sum() / (res.rail_km * area).sum())))
    print(res.drop(columns=["name", "area_km2"]).describe().round(2).loc[["mean", "min", "50%", "max"]])
    for c in ("ehv_km", "rail_el", "bab_km"):
        lo = res.sort_values(c)
        print(f"lowest {c}:", list(zip(lo.name.head(3), lo[c].head(3).round(1))), "highest:", list(zip(lo.name.tail(3), lo[c].tail(3).round(1))))
    print("districts without extra-high-voltage line:", int((res.ehv_km == 0).sum()), "without motorway:", int((res.bab_km == 0).sum()))

    shapes, _ = rg.load_nuts(raw / "regional" / "nuts3_2024_10m.geojson")
    de = {g: s for g, s in shapes.items() if g.startswith("DE")}
    cols = ["#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#1f4e79", "#002060"]
    specs = {"ehv_km": ([0, 0.01, 2, 4, 6, 9, 99], "Höchstspannungsleitungen (≥ 220 kV), km je 100 km²", "{:.0f}"),
             "hv_km": ([0, 4, 8, 12, 16, 22, 99], "110-kV-Leitungen, km je 100 km²", "{:.0f}"),
             "rail_el": ([0, 25, 50, 65, 80, 90, 101], "Elektrifizierter Anteil der Bahnstrecken, %", "{:.0f}"),
             "bab_km": ([0, 0.01, 2, 4, 6, 9, 99], "Autobahnen, km je 100 km²", "{:.0f}")}
    fig, axes = plt.subplots(1, 4, figsize=(22, 8))
    for a, (c, (bins, t, fmt)) in zip(axes, specs.items()):
        rg.choropleth(a, de, res[c].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        rg.legend_bins(a, bins, cols, fmt=fmt, loc="lower left")
        if bins[1] == 0.01:                         # first class means "none"
            a.get_legend().get_texts()[0].set_text("keine")
            a.get_legend().get_texts()[1].set_text(f"bis {bins[2]}")
        a.set_title(t, fontsize=10, loc="left")
    fig.suptitle("Strom- und Verkehrsnetze nach Kreisen, Stand November 2026", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis von OpenStreetMap (© OpenStreetMap-Mitwirkende, ODbL 1.0). "
             "Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "infra_maps.png", dpi=150); plt.close(fig)
    if site:
        data = {g: {c: (None if pd.isna(v) else round(float(v), 2)) for c, v in row.items() if c not in ("name", "area_km2")} for g, row in res.iterrows()}
        p = Path(site) / "kreise_infra.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
