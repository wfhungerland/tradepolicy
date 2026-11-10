"""Export orientation of manufacturing by German district, 1999-2024.

Data: Regionaldatenbank Deutschland, table 42111-04-02-4 (Verarbeitendes Gewerbe, Umsatz and
Auslandsumsatz, annual, districts, 2009-2024, WZ 2008) and 42111-04-01-4 (same up to 2008,
WZ 2003; not comparable at the break), downloaded with tools/server_fetch_kreise.py.
Scope: establishments of manufacturing and mining with 20 and more employees, at the
location of the establishment. Auslandsumsatz = sales to customers abroad (direct exports,
and deliveries to German exporters are not included).
Suppressed values ("." secret, "-" none) stay missing.
Indicators per district: export ratio (foreign / total sales) 2024 and change since 2012 (after the district reform in Mecklenburg-Vorpommern 2011)
in percentage points; foreign sales per inhabitant 2024.
Writes <output>/kreise/export_kreise.csv, export_maps.png and site data kreise_export.json.
Usage: python 73_kreise_export.py [site_data_folder]
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


def read(path):
    d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    d["v"] = pd.to_numeric(d.value, errors="coerce")
    d["time"] = d.time.astype(int)
    return d


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "kreise"
    out = cfg["output"] / "kreise"
    out.mkdir(parents=True, exist_ok=True)
    new, old = read(raw / "rdb_42111-04-02-4.csv"), read(raw / "rdb_42111-04-01-4.csv")
    k = pd.read_excel(raw / "kreise.xlsx", sheet_name=1, header=None, skiprows=3).iloc[:, [0, 1, 2, 3, 5]]
    k.columns = ["ags", "typ", "name", "nuts3", "pop"]
    k = k[k.ags.astype(str).str.len() == 5]
    k["name"] = rg.kreis_names(k.name, k.typ)
    k = k[k.ags.astype(str).str.len() == 5].dropna(subset=["nuts3"]).assign(ags=lambda x: x.ags.astype(str)).set_index("ags")
    # Germany series (both classifications, break 2008/2009)
    de = pd.concat([x[x["1_variable_code"] == "DINSG"].pivot_table(index="time", columns="value_variable_label", values="v").assign(wz=w)
                    for x, w in ((old, "WZ2003"), (new, "WZ2008"))])
    de["quote"] = de.Auslandsumsatz / de.Umsatz
    print("Germany export ratio:", de.quote.round(3).loc[[1999, 2008, 2009, 2019, 2024]].to_dict())
    kr = new[new["1_variable_code"] == "KREISE"].pivot_table(index=["1_variable_attribute_code", "time"], columns="value_variable_label", values="v")
    kr["quote"] = kr.Auslandsumsatz / kr.Umsatz
    q = kr.quote.unstack()
    r = pd.DataFrame({"quote_2024": q[2024], "quote_2012": q[2012], "quote_2019": q[2019],
                      "ausl_mio_2024": kr.Auslandsumsatz.unstack()[2024] / 1000, "umsatz_mio_2024": kr.Umsatz.unstack()[2024] / 1000}).reindex(k.index)
    r["d_2012"] = 100 * (r.quote_2024 - r.quote_2012)
    r["ausl_pc"] = r.ausl_mio_2024 * 1e6 / k["pop"]
    r = r.join(k)
    r.round(4).to_csv(out / "export_kreise.csv")
    print(f"districts with 2024 ratio: {r.quote_2024.notna().sum()} of {len(r)}; with change since 2012: {r.d_2012.notna().sum()}")
    print("median ratio 2024 %.1f %%" % (100 * r.quote_2024.median()))
    for c in ("quote_2024", "d_2012", "ausl_pc"):
        s = r.dropna(subset=[c]).sort_values(c)
        print(c, "top:", list(zip(s.name.tail(5), s[c].tail(5).round(3))), "bottom:", list(zip(s.name.head(3), s[c].head(3).round(3))))
    y = r.dropna(subset=["nuts3"]).set_index("nuts3")
    shapes, _ = rg.load_nuts(cfg["data"]["scenarios"] / "regional" / "nuts3_2024_10m.geojson")
    dsh = {g: s for g, s in shapes.items() if g.startswith("DE")}
    seq = ["#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#1f4e79", "#002060"]
    div = ["#c00000", "#f4b183", "#f2f2f2", "#deebf7", "#5b9bd5", "#002060"]
    specs = [("quote_2024", [0, 0.2, 0.3, 0.4, 0.5, 0.6, 1.01], seq, "Exportquote der Industrie 2024, %", lambda v: f"{100 * v:.0f}"),
             ("d_2012", [-99, -10, -3, 0, 3, 10, 99], div, "Veränderung der Exportquote 2012 bis 2024, Prozentpunkte", lambda v: f"{v:.0f}"),
             ("ausl_pc", [0, 2000, 5000, 10000, 20000, 40000, 1e9], seq, "Auslandsumsatz je Einwohner 2024, EUR", lambda v: f"{v:,.0f}".replace(",", "."))]
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    for a, (c, bins, cols, t, f) in zip(axes, specs):
        rg.choropleth(a, dsh, y[c].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        rg.legend_bins(a, bins, cols, fmt="{:.0f}", loc="lower left")
        for i, tx in enumerate(a.get_legend().get_texts()):
            lo, hi = bins[i], bins[i + 1]
            tx.set_text(f"unter {f(hi)}" if i == 0 else f"{f(lo)} und mehr" if i == len(cols) - 1 else f"{f(lo)} bis {f(hi)}")
        a.set_title(t, fontsize=10, loc="left")
    fig.suptitle("Exportorientierung der Industrie nach Kreisen", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis der Regionaldatenbank Deutschland (Tabelle 42111-04-02-4: Betriebe des Verarbeitenden Gewerbes "
             "mit 20 und mehr Beschäftigten) und Destatis. Grau: geheim gehalten. Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "export_maps.png", dpi=150); plt.close(fig)
    if site:
        data = {"kreise": {g: {c: (None if pd.isna(row[c]) else round(float(row[c]), 4)) for c in ("quote_2024", "d_2012", "ausl_pc", "ausl_mio_2024")} for g, row in y.iterrows()},
                "germany": {"years": de.index.tolist(), "quote": de.quote.round(4).tolist(), "wz": de.wz.tolist()}}
        p = Path(site) / "kreise_export.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
