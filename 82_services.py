"""German trade in services: types, partners, the US balance and digital dependence.

Data: OECD, Trade in services by partner economy (BPM6, dataflow OECD.SDD.TPS DSD_BOP@DF_TIS),
Germany as reporter, all partners and EBOPS 2010 service types, 2010-2024, EUR and USD;
goods trade with partners from IMF IMTS (exports FOB, imports CIF, USD; customs basis).
Measures: exports (credit) and imports (debit) by service type; balance with the US in goods and
in services; "digital" imports = telecommunications, computer and information services (SI) plus
charges for the use of intellectual property (SH): share supplied from the US, and from the US
and Ireland together (US firms often book European sales through Irish subsidiaries).
Writes <output>/services/services_*.csv and site data services.json.
Usage: python 82_services.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config

TYPES = {"SA": ("Lohnveredelung", "Manufacturing services"), "SB": ("Wartung und Reparatur", "Maintenance and repair"),
         "SC": ("Transport", "Transport"), "SD": ("Reiseverkehr", "Travel"), "SE": ("Bau", "Construction"), "SF": ("Versicherungen", "Insurance"),
         "SG": ("Finanzdienste", "Financial services"), "SH": ("Lizenzen und Patente", "Charges for intellectual property"),
         "SI": ("Telekommunikation, IT, Information", "Telecom, computer and information"), "SJ": ("Unternehmensdienste", "Other business services"),
         "SK": ("Kultur und Freizeit", "Personal, cultural, recreational"), "SL": ("Staat", "Government")}


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "services"
    out = cfg["output"] / "services"
    out.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(raw / "tis.csv", usecols=["COUNTERPART_AREA", "MEASURE", "ACCOUNTING_ENTRY", "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE"])
    d = d.rename(columns={"COUNTERPART_AREA": "p", "MEASURE": "m", "ACCOUNTING_ENTRY": "f", "UNIT_MEASURE": "u", "TIME_PERIOD": "y", "OBS_VALUE": "v"})
    eur = d[d.u == "EUR_EXC"]
    last = int(eur[(eur.p == "W") & (eur.m == "S")].y.max())
    tot = eur[(eur.p == "W") & (eur.m == "S")].pivot_table(index="y", columns="f", values="v") / 1000
    print(f"services {last}: exports {tot.loc[last, 'C']:.0f}, imports {tot.loc[last, 'D']:.0f} bn EUR")
    ty = eur[(eur.p == "W") & (eur.y == last) & eur.m.isin(TYPES)].pivot_table(index="m", columns="f", values="v") / 1000
    ty.round(2).to_csv(out / "services_types.csv")
    # partners (single economies)
    pa = eur[(eur.m == "S") & (eur.y == last) & (eur.p.str.len() == 3)].pivot_table(index="p", columns="f", values="v") / 1000
    pa = pa.sort_values("C", ascending=False)
    pa.round(2).to_csv(out / "services_partners.csv")
    print("top export partners:", pa.C.head(6).round(1).to_dict())
    # US balance: goods (IMF, USD) and services (OECD, USD)
    usd = d[(d.u == "USD_EXC") & (d.m == "S") & (d.p == "USA")].pivot_table(index="y", columns="f", values="v") / 1000
    g = {}
    for ind, col in (("XG_FOB_USD", "x"), ("MG_CIF_USD", "m")):
        t = pd.read_csv(raw / f"imts_{ind}.csv")
        t = t[t.COUNTERPART_COUNTRY == "USA"].set_index("TIME_PERIOD").OBS_VALUE / 1e9
        g[col] = t
    us = pd.DataFrame({"goods": g["x"] - g["m"], "services": usd["C"] - usd["D"]}).dropna()
    us.round(2).to_csv(out / "services_us_balance.csv")
    print("US balance bn USD:", us.loc[[2010, 2019, last]].round(1).to_dict("index"))
    # digital imports: SI + SH, share from US and from US + IE
    dig = eur[eur.m.isin(["SI", "SH"]) & (eur.f == "D")].pivot_table(index="y", columns="p", values="v", aggfunc="sum")
    sh = pd.DataFrame({"total_bn": dig["W"] / 1000, "us": 100 * dig["USA"] / dig["W"], "us_ie": 100 * (dig["USA"] + dig["IRL"]) / dig["W"]})
    sh = sh.dropna(subset=["us"])                      # years with a confidential value for Ireland keep a gap
    sh.round(2).to_csv(out / "services_digital.csv")
    print("digital imports:", sh.loc[[2010, last]].round(1).to_dict("index"))
    if site:
        j = {"year": last, "years": [int(y) for y in tot.index], "exp": tot.C.round(1).tolist(), "imp": tot.D.round(1).tolist(),
             "types": [{"k": k, "de": TYPES[k][0], "en": TYPES[k][1], "x": round(float(ty.loc[k, "C"]), 1), "m": round(float(ty.loc[k, "D"]), 1)} for k in TYPES if k in ty.index],
             "partners": [{"p": p, "x": round(float(r.C), 1), "m": round(float(r.D), 1)} for p, r in pa.head(12).iterrows()],
             "us": {"years": [int(y) for y in us.index], "goods": us.goods.round(1).tolist(), "services": us.services.round(1).tolist()},
             "digital": {"years": [int(y) for y in sh.index], "total": sh.total_bn.round(1).tolist(), "us": sh.us.round(1).tolist(),
                         "us_ie": [None if pd.isna(v) else round(float(v), 1) for v in sh.us_ie]}}
        p = Path(site) / "services.json"
        txt = json.dumps(j, ensure_ascii=False, separators=(",", ":"))
        assert "NaN" not in txt, "NaN in site data"
        p.write_text(txt, encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
