"""Foreign trade of the German Länder (Destatis GENESIS-Online 51000-0032, 51000-0034).

51000-0032: exports and imports by Land and partner country, 2008 onward (1,000 EUR).
51000-0034: exports and imports by Land and product group (GP 2019, two digits).
Länder trade assigns exports to the Land where the goods were produced; "Ausland" are goods of
foreign origin and "Restposition" unassigned trade: both are shown only in the national total.
Land GDP: Eurostat nama_10r_2gdp (NUTS 1).

Usage: python 88_laender_trade.py <input_dir with rdb_51000-0032.csv, rdb_51000-0034.csv> [site_data_dir]
"""
import json, sys, urllib.request
from pathlib import Path
import pandas as pd

LAND = {"01": ("Schleswig-Holstein", "DEF"), "02": ("Hamburg", "DE6"), "03": ("Niedersachsen", "DE9"), "04": ("Bremen", "DE5"),
        "05": ("Nordrhein-Westfalen", "DEA"), "06": ("Hessen", "DE7"), "07": ("Rheinland-Pfalz", "DEB"), "08": ("Baden-Württemberg", "DE1"),
        "09": ("Bayern", "DE2"), "10": ("Saarland", "DEC"), "11": ("Berlin", "DE3"), "12": ("Brandenburg", "DE4"),
        "13": ("Mecklenburg-Vorpommern", "DE8"), "14": ("Sachsen", "DED"), "15": ("Sachsen-Anhalt", "DEE"), "16": ("Thüringen", "DEG")}
EU = {"Belgien (ab 1999)", "Bulgarien", "Dänemark", "Estland (ab 1992)", "Finnland", "Frankreich", "Griechenland", "Irland", "Italien",
      "Kroatien (ab 05/1992)", "Lettland (ab 1992)", "Litauen (ab 1992)", "Luxemburg (ab 1999)", "Malta", "Niederlande", "Österreich",
      "Polen", "Portugal", "Rumänien", "Schweden", "Slowakei (ab 1993)", "Slowenien (ab 05/1992)", "Spanien", "Tschechien (ab 1993)",
      "Ungarn", "Zypern"}
PARTNER = {"USA": lambda s: s == "Vereinigte Staaten von Amerika", "CHN": lambda s: s == "China",
           "GBR": lambda s: s == "Vereinigtes Königreich", "EU": lambda s: s in EU}

def load(p):
    d = pd.read_csv(p, sep=";", dtype=str, encoding="utf-8-sig")
    d = d[d.value_variable_code.isin(["WERTA", "WERTE"])].copy()
    d["v"] = pd.to_numeric(d.value.str.replace(",", "."), errors="coerce").fillna(0) / 1e6   # 1,000 EUR -> bn EUR
    d["year"] = d.time.astype(int); d["land"] = d["1_variable_attribute_code"]
    return d

def gdp():
    u = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10r_2gdp?unit=MIO_EUR&"
         + "&".join("geo=" + v[1] for v in LAND.values()))
    d = json.load(urllib.request.urlopen(u, timeout=180))
    t = {v: k for k, v in d["dimension"]["time"]["category"]["index"].items()}
    g = {v: k for k, v in d["dimension"]["geo"]["category"]["index"].items()}
    nt = len(t); out = {}
    for k, v in d["value"].items():
        k = int(k); out.setdefault(g[k // nt], {})[int(t[k % nt])] = v / 1000
    return out

def main(src, site=None):
    src = Path(src)
    a = load(src / "rdb_51000-0032.csv"); b = load(src / "rdb_51000-0034.csv")
    years = sorted(a.year.unique()); codes = sorted(LAND)
    def series(df, flow, mask=None, land=None):
        x = df[(df.value_variable_code == flow)]
        if mask is not None: x = x[x["2_variable_attribute_label"].map(mask)]
        s = x.groupby(["land", "year"]).v.sum()
        return {l: [round(float(s.get((l, y), 0)), 4) for y in years] for l in (land or codes + ["17", "18"])}
    out = {"_meta": {"source": "Destatis GENESIS-Online 51000-0032, 51000-0034; Eurostat nama_10r_2gdp", "unit": "bn EUR"},
           "years": [int(y) for y in years],
           "laender": [{"code": c, "name": LAND[c][0], "nuts": LAND[c][1]} for c in codes],
           "exp": series(a, "WERTA"), "imp": series(a, "WERTE"),
           "exp_p": {p: series(a, "WERTA", m) for p, m in PARTNER.items()},
           "imp_p": {p: series(a, "WERTE", m) for p, m in PARTNER.items()}}
    G = gdp(); out["gdp"] = {c: {str(y): round(v, 3) for y, v in G.get(LAND[c][1], {}).items() if y >= years[0]} for c in codes}
    # product mix of exports, latest year
    yl = int(years[-1]); x = b[(b.value_variable_code == "WERTA") & (b.year == yl)]
    prod = x.groupby(["land", "2_variable_attribute_code", "2_variable_attribute_label"]).v.sum().reset_index()
    tot = prod[prod.land.isin(codes)].groupby(["2_variable_attribute_code", "2_variable_attribute_label"]).v.sum().sort_values(ascending=False)
    out["products"] = {"year": yl, "groups": [{"code": c, "label": l, "total": round(float(v), 3)} for (c, l), v in tot.items()],
                       "values": {l: {r["2_variable_attribute_code"]: round(float(r.v), 4) for _, r in prod[prod.land == l].iterrows()} for l in codes}}
    txt = json.dumps(out, ensure_ascii=False, separators=(",", ":")); assert "NaN" not in txt
    Path("output").mkdir(exist_ok=True); open("output/laender_trade.json", "w").write(txt)
    if site: open(Path(site) / "laender_trade.json", "w").write(txt)
    # summary
    i = years.index(yl); i19 = years.index(2019)
    tot_de = sum(out["exp"][c][i] for c in codes + ["17", "18"])
    print(f"exports {yl}: Germany {tot_de:.0f} bn, of which Länder {sum(out['exp'][c][i] for c in codes):.0f}, foreign origin {out['exp']['17'][i]:.0f}")
    gy = max(int(y) for y in out["gdp"]["08"])
    rows = []
    for c in codes:
        e = out["exp"][c][i]; us = out["exp_p"]["USA"][c][i]; cn = out["exp_p"]["CHN"][c][i]
        g = out["gdp"][c].get(str(gy)); egy = out["exp"][c][years.index(gy)]
        rows.append((LAND[c][0], e, 100 * us / e, 100 * cn / e, 100 * egy / g, 100 * out["exp_p"]["USA"][c][years.index(gy)] / g, 100 * (e / out["exp"][c][i19] - 1)))
    for r in sorted(rows, key=lambda r: -r[5]):
        print(f"{r[0]:24s} exp {r[1]:6.1f}  US {r[2]:5.1f} %  CN {r[3]:5.1f} %  exp/GDP {r[4]:5.1f} %  US/GDP {r[5]:4.1f} %  since 2019 {r[6]:+5.1f} %")
    print("top product groups", [(g["label"][:28], round(g["total"])) for g in out["products"]["groups"][:6]])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
