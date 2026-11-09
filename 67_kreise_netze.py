"""Digital networks and coverage along transport routes by German district.

Source: Breitbandatlas / Gigabit-Grundbuch of the Federal Network Agency (file
bba_06_2026.xlsx, data as of June 2026; district rows, "3 - Kreis"):
  households and industrial estates (Gewerbegebiete) with >= 1000 Mbit/s fixed broadband,
  of which fibre to the building/home (FTTB/H);
  mobile coverage in the vehicle along railways and motorways: 4G and 5G share of route
  length for the best of the three network operators with own networks (Telekom,
  Vodafone, Telefónica). The best operator is a lower bound for coverage by any operator.
District key -> NUTS 3 from the Destatis district list (66_kreise_energy.py).
Writes <output>/kreise/netze_kreise.csv, netze_maps.png and site data kreise_netze.json.
Usage: python 67_kreise_netze.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import regional as rg
from config import load_config


def sheet(path, name):
    d = pd.read_excel(path, sheet_name=name, header=None)
    h = d.iloc[:4].ffill(axis=1)
    d.columns = [" | ".join(str(v) for v in h.iloc[1:4, c]) if c >= 6 else ["ags", "name", "level", "land", "kreis", "raum"][c] for c in range(d.shape[1])]
    d = d[d.level.astype(str).str.startswith("3")].copy()
    d["ags"] = d.ags.astype(str).str.zfill(5)
    return d.set_index("ags")


def col(d, *parts):
    c = [x for x in d.columns if all(p in x for p in parts[:-1]) and x.endswith(parts[-1])]
    assert len(c) == 1, (parts, c)
    return pd.to_numeric(d[c[0]], errors="coerce")


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "kreise"
    out.mkdir(parents=True, exist_ok=True)
    f = raw / "netze" / "bba.xlsx"
    hh, gw, rail, bab = (sheet(f, s) for s in ("Privathaushalte", "Gewerbegebiete", "Schienenwege", "Autobahnen"))
    r = pd.DataFrame({
        "hh_gigabit": col(hh, "alle Technologien", "≥ 1000 Mbit/s"), "hh_ftth": col(hh, "FTTB/H", "≥ 1000 Mbit/s"),
        "gw_gigabit": col(gw, "alle Technologien", "≥ 1000 Mbit/s"), "gw_ftth": col(gw, "FTTB/H", "≥ 1000 Mbit/s")})
    for d, k in ((rail, "rail"), (bab, "bab")):
        for g in ("4G", "5G"):
            ops = [col(d, op, f"| {g}") for op in ("| Telekom |", "| Vodafone |", "| Telefónica |")]
            r[f"{k}_{g.lower()}"] = pd.concat(ops, axis=1).max(axis=1)
    r["name"] = hh.name
    k = pd.read_excel(raw / "kreise" / "kreise.xlsx", sheet_name=1, header=None, skiprows=3).iloc[:, [0, 3]]
    k.columns = ["ags", "nuts3"]
    k = k[k.ags.astype(str).str.len() == 5]
    r = r.join(k.assign(ags=k.ags.astype(str)).set_index("ags"))
    r.round(2).to_csv(out / "netze_kreise.csv")
    print(f"{len(r)} districts, NUTS matched {r.nuts3.notna().sum()}")
    print(r[["hh_gigabit", "hh_ftth", "gw_gigabit", "gw_ftth", "rail_4g", "rail_5g", "bab_4g", "bab_5g"]].describe().round(1).loc[["mean", "min", "50%", "max"]])
    for c in ("gw_ftth", "rail_4g", "bab_5g"):
        lo = r.sort_values(c).head(3)
        print(f"lowest {c}:", list(zip(lo.name, lo[c].round(1))))
    y = r.dropna(subset=["nuts3"]).set_index("nuts3")
    shapes, _ = rg.load_nuts(raw / "regional" / "nuts3_2024_10m.geojson")
    de = {g: s for g, s in shapes.items() if g.startswith("DE")}
    bins = [0, 25, 50, 75, 90, 95, 101]
    cols = ["#c00000", "#f4b183", "#deebf7", "#9dc3e6", "#2e75b6", "#002060"]
    specs = [("hh_gigabit", "Haushalte mit ≥ 1000 Mbit/s, %"), ("gw_ftth", "Gewerbegebiete mit Glasfaser (FTTB/H), %"),
             ("rail_4g", "4G entlang der Schienenwege, bester Netzbetreiber, %"), ("bab_5g", "5G entlang der Autobahnen, bester Netzbetreiber, %")]
    fig, axes = plt.subplots(1, 4, figsize=(22, 8))
    for a, (c, t) in zip(axes, specs):
        rg.choropleth(a, de, y[c].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        a.set_title(t, fontsize=10, loc="left")
    rg.legend_bins(axes[0], bins, cols, fmt="{:.0f}", loc="lower left")
    fig.suptitle("Digitale Netze und Mobilfunk entlang der Verkehrswege nach Kreisen, Juni 2026", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis des Breitbandatlas (Gigabit-Grundbuch, Bundesnetzagentur, Stand 06.2026) und Destatis. "
             "Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "netze_maps.png", dpi=150); plt.close(fig)
    if site:
        data = {g: {c: (None if pd.isna(v) else round(float(v), 1)) for c, v in row.items() if c not in ("name",)} for g, row in y.iterrows()}
        p = Path(site) / "kreise_netze.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
