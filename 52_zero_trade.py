"""Zero-trade matrices: which country pairs trade at all, and in how many products.

Following the presentation of Helpman, Melitz and Rubinstein (2008, QJE), who show that
about half of all country pairs do not trade with each other. For each year and level:

  country level   x[i, j] = 1 if i exports anything to j, else 0
  HS levels       x[i, j] = share of all codes at that level (HS sections, HS2, HS4,
                  HS6 of HS 1992) that i exports to j
  two-way         same, counting only flows that go both ways (i to j and j to i in the
                  same code), i.e. intra-industry trade at that level
The import view is the transpose of x.

Sources: country level from IMF IMTS (bilateral goods trade, annual, 1990-2024; a flow
counts if the exporter reports exports or the importer reports imports, mirror data),
HS levels from CEPII BACI HS92 V202601 (1995-2024, already reconciled). Country set:
countries present in every year of the source (BACI codes merged to ISO3, e.g. Belgium-
Luxembourg before 1999 to BEL, Southern African Customs Union to ZAF); entities that
appear later (e.g. South Sudan) or vanish are left out, so shares refer to a fixed set.
Writes <output>/zero_trade/matrices_<level>.npz (years, countries, x, two) and
germany_<level>.csv. Usage: python 52_zero_trade.py
"""
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd

from config import load_config

SECTIONS = [(1, 5), (6, 14), (15, 15), (16, 24), (25, 27), (28, 38), (39, 40), (41, 43), (44, 46), (47, 49),
            (50, 63), (64, 67), (68, 70), (71, 71), (72, 83), (84, 85), (86, 89), (90, 92), (93, 93), (94, 96),
            (97, 97)]
LEVELS = {"section": None, "hs2": 2, "hs4": 4, "hs6": 6}
FIX_ISO = {"ZA1": "ZAF", "S19": "TWN"}


def section_of(hs2):
    out = np.zeros(100, dtype=np.int16) - 1
    for s, (a, b) in enumerate(SECTIONS):
        out[a:b + 1] = s
    return out[hs2]


def pair_shares(i, j, c, n, n_codes):
    """i, j country indices, c code index (unique triples assumed after np.unique).
    Returns share matrices for all flows and two-way flows."""
    key = np.unique((i.astype(np.int64) * n + j) * n_codes + c)
    rev = (((key // n_codes) % n) * n + (key // n_codes) // n) * n_codes + key % n_codes
    two = np.isin(key, rev, assume_unique=False)
    pair = key // n_codes
    x = np.bincount(pair, minlength=n * n).reshape(n, n) / n_codes
    t = np.bincount(pair[two], minlength=n * n).reshape(n, n) / n_codes
    return x.astype(np.float32), t.astype(np.float32)


def baci(cfg, out):
    path = cfg["data"]["scenarios"] / "baci92" / "BACI_HS92_V202601.zip"
    with zipfile.ZipFile(path) as z:
        names = sorted(n for n in z.namelist() if "_Y" in n)
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str,
                         keep_default_na=False)
        iso = dict(zip(cc.country_code.astype(int), cc.country_iso3.replace(FIX_ISO)))
        prod = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("product_codes"))), dtype=str)
        pc = prod.iloc[:, 0].astype(str)
        k6 = np.unique(pc[pc.str.fullmatch(r"\d+")].astype(int).to_numpy())
        # first pass: countries present in every year
        present, years = None, []
        for nm in names:
            b = pd.read_csv(z.open(nm), usecols=["i", "j"])
            s = {iso[c] for c in np.unique(np.r_[b.i.unique(), b.j.unique()])}
            present = s if present is None else present & s
            years.append(int(nm.split("_Y")[1][:4]))
        countries = sorted(present)
        n, idx = len(countries), {c: k for k, c in enumerate(countries)}
        code_idx = {c: (idx[v] if v in idx else -1) for c, v in iso.items()}
        conv = {"section": lambda k: section_of(k // 10000), "hs2": lambda k: k // 10000,
                "hs4": lambda k: k // 100, "hs6": lambda k: k}
        levels = {lv: {"codes": np.unique(conv[lv](k6)), "x": [], "two": []} for lv in LEVELS}
        for nm in names:
            b = pd.read_csv(z.open(nm), usecols=["i", "j", "k"], dtype={"i": np.int32, "j": np.int32, "k": str})
            b["k"] = pd.to_numeric(b.k, errors="coerce")
            b = b.dropna(subset=["k"]).astype({"k": np.int32})
            i = b.i.map(code_idx).to_numpy()
            j = b.j.map(code_idx).to_numpy()
            ok = (i >= 0) & (j >= 0) & (i != j)
            i, j, k = i[ok], j[ok], b.k.to_numpy()[ok]
            for lv, L in levels.items():
                c = np.searchsorted(L["codes"], conv[lv](k))
                x, t = pair_shares(i, j, c, n, len(L["codes"]))
                L["x"].append(x)
                L["two"].append(t)
            print(nm.split("_Y")[1][:4], end=" ", flush=True)
    print()
    for lv, L in levels.items():
        save(out, lv, years, countries, np.stack(L["x"]), np.stack(L["two"]), len(L["codes"]))
    # BACI also at country level, as a check on the IMF matrices
    x = np.stack([(m > 0).astype(np.float32) for m in levels["section"]["x"]])
    save(out, "country_baci", years, countries, x, (x * np.transpose(x, (0, 2, 1))).astype(np.float32), 1)


def imf(cfg, out):
    raw = cfg["data"]["scenarios"] / "imts"
    rows = []
    for ind, reporter_is_exporter in (("XG_FOB_USD", True), ("MG_CIF_USD", False)):
        for _, el in ET.iterparse(raw / f"{ind}.xml"):
            if el.tag.endswith("Series"):
                a = el.attrib
                rep, cp = a.get("COUNTRY"), a.get("COUNTERPART_COUNTRY")
                for o in el:
                    v = o.attrib.get("OBS_VALUE")
                    if v not in (None, "", "NaN") and float(v) > 0:
                        y = int(o.attrib["TIME_PERIOD"][:4])
                        rows.append((rep, cp, y) if reporter_is_exporter else (cp, rep, y))
                el.clear()
    d = pd.DataFrame(rows, columns=["i", "j", "year"]).drop_duplicates()
    # ISO3 country codes only (drops regional aggregates such as G001, W00)
    d = d[d.i.str.fullmatch(r"[A-Z]{3}") & d.j.str.fullmatch(r"[A-Z]{3}") & (d.i != d.j)]
    years = sorted(y for y in d.year.unique() if 1990 <= y <= 2024)
    present = None
    for y in years:
        s = set(d.loc[d.year == y, "i"]) | set(d.loc[d.year == y, "j"])
        present = s if present is None else present & s
    countries = sorted(present)
    n, idx = len(countries), {c: k for k, c in enumerate(countries)}
    d = d[d.i.isin(idx) & d.j.isin(idx)]
    xs = []
    for y in years:
        g = d[d.year == y]
        m = np.zeros((n, n), dtype=np.float32)
        m[g.i.map(idx).to_numpy(), g.j.map(idx).to_numpy()] = 1
        xs.append(m)
    x = np.stack(xs)
    save(out, "country", years, countries, x, (x * np.transpose(x, (0, 2, 1))).astype(np.float32), 1)


def save(out, lv, years, countries, x, two, n_codes):
    np.savez_compressed(out / f"matrices_{lv}.npz", years=np.array(years), countries=np.array(countries), x=x, two=two,
                        n_codes=n_codes)
    k = list(countries).index("DEU")
    rows = []
    for t, y in enumerate(years):
        e, m, w = np.delete(x[t, k, :], k), np.delete(x[t, :, k], k), np.delete(two[t, k, :], k)
        # shares of all partner x code cells: two-way, export only, import only, none
        both = w.mean()
        rows.append({"year": y, "two_way": both, "export_only": e.mean() - both, "import_only": m.mean() - both,
                     "none": 1 - e.mean() - m.mean() + both})
    g = pd.DataFrame(rows)
    g.round(5).to_csv(out / f"germany_{lv}.csv", index=False)
    print(f"{lv}: {len(countries)} countries, {years[0]}-{years[-1]}, mean share of pairs with any trade "
          f"{(x[-1] > 0).sum() / (len(countries) * (len(countries) - 1)):.0%} in {years[-1]}; Germany {years[-1]}: "
          + ", ".join(f"{c} {g.iloc[-1][c]:.0%}" for c in ("two_way", "export_only", "import_only", "none")))


def main():
    cfg = load_config()
    out = cfg["output"] / "zero_trade"
    out.mkdir(parents=True, exist_ok=True)
    import sys
    if "imf" not in sys.argv[1:]:
        baci(cfg, out)
    if "baci" not in sys.argv[1:]:
        imf(cfg, out)


if __name__ == "__main__":
    main()
