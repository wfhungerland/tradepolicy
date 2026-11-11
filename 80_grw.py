"""GRW regional aid areas (Fördergebietskarte 2022-2027) for the districts hit by US tariffs.

Data: BBSR, Raumgliederungen Referenz 2023 (in the INKAR 2025 download), sheet "Gemeindereferenz
(inkl. Kreise)": GRW status of every municipality (GRW2023/GRW_NAME: C, C+, D, mixed, N, none) and
population 2023. C areas = predefined and non-predefined C areas (C+ = C with higher rates),
D areas = de-minimis areas; "N" marks municipalities outside the aid map within a mixed area.
Per district: population share living in C areas and in D areas.
Combined with the US tariff exposure (74) and the double risks of 79.
Writes <output>/kreise/grw_kreise.csv, grw_summary.json; site data kreise_grw.json (map layer).
Usage: python 80_grw.py [site_data_folder]
"""
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "inkar"
    out = cfg["output"] / "kreise"
    ref = raw / "BBSR_Raumgliederungen_Referenz_2023.xlsx"
    if not ref.exists():
        with zipfile.ZipFile(raw / "inkar_2025.zip") as z:
            z.extract("BBSR_Raumgliederungen_Referenz_2023.xlsx", raw)
    g = pd.read_excel(ref, sheet_name="Gemeindereferenz (inkl. Kreise)", dtype={"GEM2023": str})
    g["bev23"] = pd.to_numeric(g.bev23, errors="coerce")
    g = g[g.GRW_NAME.notna() & g.bev23.notna() & g.GEM2023.str.fullmatch(r"\d+")].copy()   # second header row in the sheet
    g["ags"] = g.GEM2023.str.zfill(8).str[:5]
    lab = g.GRW_NAME.astype(str)
    print(lab.value_counts().to_dict())
    # municipalities split between categories (e.g. "C/D", "D/N") count with equal parts, an approximation
    parts = lab.str.replace(" -Förderung", "", regex=False).str.replace("+", "", regex=False).str.split("/")
    g["c"] = parts.map(lambda p: p.count("C") / len(p) if p != ["keine Förderung"] else 0.0)
    g["d"] = parts.map(lambda p: p.count("D") / len(p) if p != ["keine Förderung"] else 0.0)
    g["pc"], g["pd"] = g.bev23 * g.c, g.bev23 * g.d
    a = g.groupby("ags")[["bev23", "pc", "pd"]].sum()
    k = pd.DataFrame({"pop": a.bev23, "share_c": a.pc / a.bev23, "share_d": a.pd / a.bev23})
    k["share_cd"] = k.share_c + k.share_d
    k["status"] = np.select([k.share_c >= 0.5, k.share_cd >= 0.5, k.share_cd > 0], ["C", "D", "teilweise"], "keine")
    m = pd.read_csv(out / "inkar_analyses_kreise.csv", dtype={"ags": str}).set_index("ags")
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    k = k.join(m[["name", "loss", "q", "prog", "sgb2"]], how="left").join(u[["nuts3", "loss_mio"]], how="left")
    thr = m.sgb2.quantile(0.8)
    k["double"] = (k.q == 5) & ((k.prog < -5) | (k.sgb2 >= thr))
    k.round(4).to_csv(out / "grw_kreise.csv")
    w = lambda x, c: float(np.average(x[c], weights=x["pop"]))
    v = k.dropna(subset=["q"])
    summ = {"by_quintile": [{"q": int(q), "n": len(x), "share_c": w(x, "share_c"), "share_cd": w(x, "share_cd")} for q, x in v.groupby("q")],
            "germany": {"share_c": w(k, "share_c"), "share_cd": w(k, "share_cd")},
            "loss_share_in_c": float((v.loss_mio * v.share_c).sum() / v.loss_mio.sum()),
            "loss_share_in_cd": float((v.loss_mio * v.share_cd).sum() / v.loss_mio.sum()),
            "double": [[r["name"], round(r.loss), round(100 * r.share_c), round(100 * r.share_d), r.status] for _, r in k[k.double].sort_values("loss", ascending=False).iterrows()],
            "top": [[r["name"], round(r.loss), round(100 * r.share_c), round(100 * r.share_d), r.status] for _, r in v.sort_values("loss", ascending=False).head(12).iterrows()]}
    (out / "grw_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k2: v2 for k2, v2 in summ.items() if k2 not in ("double", "top")}, indent=1))
    print("double risk:", summ["double"])
    print("top loss:", summ["top"])
    if site:
        code = {"C": 3, "D": 2, "teilweise": 1, "keine": 0}
        d = {r.nuts3: {"grw": code[r.status], "c": round(100 * r.share_c), "d": round(100 * r.share_d)} for _, r in k.dropna(subset=["nuts3"]).iterrows()}
        p = Path(site) / "kreise_grw.json"
        p.write_text(json.dumps({"kreise": d, "summary": {kk: summ[kk] for kk in ("by_quintile", "germany", "loss_share_in_c", "loss_share_in_cd")}}, separators=(",", ":")), encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
