"""US tariffs (August 2026): exposure of manufacturing by German district.

Downscaling of the NUTS 2 shift-share result (64_regional_exposure.py) with district data:
  m_r  manufacturing output change of NUTS 2 region r, employment-weighted over its
       manufacturing industries (Eurostat sbs_r_nuts2021, NACE two-digit) with the
       Caliendo-Parro output change of each industry in Germany (central elasticities);
  q_k  export ratio of district k (foreign / total sales of manufacturing establishments
       with 20+ employees, Regionaldatenbank 42111-04-02-4, 2024), q_r the same for region r
       (sum over its districts with published values);
  dm_k = m_r x q_k / q_r: output change of manufacturing in district k, assuming that within
       a region the tariff loss scales with the share of output sold abroad;
  loss_k = dm_k x sales_k (EUR million) and per inhabitant.
Limits: the industry mix inside a district is not published (secrecy), so districts take
their region's mix; foreign sales include all destinations, not only the US.
Writes <output>/kreise/us_tariffs_kreise.csv, us_tariffs_kreise.png and site data kreise_us.json.
Usage: python 74_kreise_us_tariffs.py [site_data_folder]
"""
import importlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import regional as rg
from config import load_config

ex = importlib.import_module("64_regional_exposure")


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "kreise"
    s = rg.read_eurostat(raw / "regional" / "sbs_r_nuts2021.tsv.gz")
    s = s[(s.indic_sbs == "EMP_LOC_NR") & s.geo.str.match(r"^DE..$") & s.nace_r2.str.startswith("C") & s.nace_r2.isin(ex.NACE_ICIO)]
    s = s.sort_values("year").groupby(["geo", "nace_r2"]).tail(1)
    rows = []
    for _, r in s.iterrows():
        secs = ex.NACE_ICIO[r.nace_r2]
        secs = secs if isinstance(secs, list) else [secs]
        rows += [{"geo": r.geo, "sector": c, "emp": r.value / len(secs)} for c in secs]
    e = pd.DataFrame(rows)
    o = pd.read_csv(cfg["output"] / "scenarios" / "us_tariffs_output_all.csv")
    o = o[(o.scenario == "current_2026_08") & (o.country == "DEU")][["sector", "output_pct"]]
    e = e.merge(o, on="sector", how="left")
    m = (e.emp * e.output_pct).groupby(e.geo).sum() / e.groupby("geo").emp.sum()
    print("manufacturing mix shock by NUTS 2, %:", m.describe().round(2).loc[["min", "50%", "max"]].to_dict())
    k = pd.read_csv(out / "export_kreise.csv", dtype={"ags": str}).dropna(subset=["nuts3"])
    k["nuts2"] = k.nuts3.str[:4]
    pub = k.dropna(subset=["quote_2024", "umsatz_mio_2024"])
    qr = pub.groupby("nuts2").ausl_mio_2024.sum() / pub.groupby("nuts2").umsatz_mio_2024.sum()
    k["m_r"] = k.nuts2.map(m)
    k["q_r"] = k.nuts2.map(qr)
    k["dm"] = k.m_r * k.quote_2024 / k.q_r
    k["loss_mio"] = -k.dm / 100 * k.umsatz_mio_2024
    k["loss_pc"] = k.loss_mio * 1e6 / k["pop"]
    k.round(5).to_csv(out / "us_tariffs_kreise.csv", index=False)
    v = k.dropna(subset=["dm"])
    print(f"districts: {len(v)}; total loss {v.loss_mio.sum():,.0f} EUR million (manufacturing output, establishments 20+)")
    for c in ("dm", "loss_pc"):
        t = v.sort_values(c)
        print(c, "most hit:", list(zip(t.name.head(5) if c == "dm" else t.name.tail(5), (t[c].head(5) if c == "dm" else t[c].tail(5)).round(2))))
    y = v.set_index("nuts3")
    shapes, _ = rg.load_nuts(raw / "regional" / "nuts3_2024_10m.geojson")
    de = {g: s for g, s in shapes.items() if g.startswith("DE")}
    red = ["#7f0000", "#c00000", "#e06666", "#f4b183", "#fce4d6", "#f2f2f2"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 8))
    for a, (c, bins, cols, t) in zip(axes, [("dm", [-99, -3, -2.5, -2, -1.5, -1, 99], red, "Produktion der Industrie, Veränderung in %"),
                                            ("loss_pc", [0, 100, 250, 500, 1000, 2000, 1e9], red[::-1], "Produktionsverlust der Industrie je Einwohner, EUR")]):
        rg.choropleth(a, de, y[c].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        rg.legend_bins(a, bins, cols, fmt="{:.1f}" if c == "dm" else "{:.0f}", loc="lower left")
        a.set_title(t, fontsize=10, loc="left")
    fig.suptitle("US-Zölle (Stand August 2026): Betroffenheit der Industrie nach Kreisen", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen; Caliendo-Parro-Modell, Eurostat (Branchenstruktur NUTS 2), Regionaldatenbank (Exportquote je Kreis). "
             "Kreise übernehmen den Branchenmix ihrer Region. Grau: geheim gehalten. Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "us_tariffs_kreise.png", dpi=150); plt.close(fig)
    if site:
        d = {g: {"dm": round(float(r.dm), 3), "lpc": round(float(r.loss_pc), 1), "lm": round(float(r.loss_mio), 1)} for g, r in y.iterrows()}
        p = Path(site) / "kreise_us.json"
        p.write_text(json.dumps({"kreise": d, "total_mio": round(float(v.loss_mio.sum()))}, separators=(",", ":")), encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
