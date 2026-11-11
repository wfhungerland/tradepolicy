"""Critical raw materials under Chinese export controls: Germany's import dependence.

Data: CEPII BACI HS22 V202601 (2022-2024, import values CIF in thousand USD as reported
by the importer, reconciled). Product groups (HS 2022, six digits) for the materials China put
under export licensing since 2023 (MOFCOM announcements: gallium and germanium August 2023,
graphite December 2023, antimony September 2024, tungsten, tellurium, bismuth, molybdenum and
indium February 2025, seven rare earths and permanent magnets April 2025). Codes are approximate:
some six-digit codes mix the controlled element with others (811292/811299: gallium, germanium,
indium, niobium, vanadium).
Per group: German imports 2024, share from China (2022-2024), three largest suppliers, Herfindahl
index of supplier shares; China's share of world exports of the group.
Writes <output>/supply/critical_materials.csv and site data critical_materials.json.
Usage: python 83_critical_materials.py [site_data_folder]
"""
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

from config import load_config

GROUPS = {
    "rare_earths": ("Seltene Erden (Metalle und Verbindungen)", "Rare earths (metals and compounds)", "04/2025", ["280530", "284610", "284690"]),
    "magnets": ("Permanentmagnete aus Metall", "Permanent magnets of metal", "04/2025", ["850511"]),
    "ga_ge_in": ("Gallium, Germanium, Indium (mit Niob, Vanadium)", "Gallium, germanium, indium (with niobium, vanadium)", "08/2023", ["811292", "811299"]),
    "graphite": ("Graphit, natürlich und synthetisch", "Graphite, natural and synthetic", "12/2023", ["250410", "250490", "380110"]),
    "antimony": ("Antimon", "Antimony", "09/2024", ["261710", "282580", "811010", "811020", "811090"]),
    "tungsten": ("Wolfram", "Tungsten", "02/2025", ["261100", "720280", "810110", "810194", "810196", "810197", "810199"]),
    "molybdenum": ("Molybdän", "Molybdenum", "02/2025", ["261310", "261390", "282570", "720270", "810210", "810294", "810295", "810296", "810297", "810299"]),
    "bismuth": ("Bismut", "Bismuth", "02/2025", ["810610", "810690"]),
    "tellurium": ("Tellur", "Tellurium", "02/2025", ["280450"]),
}
DEU, CHN = 276, 156


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "supply"
    out.mkdir(parents=True, exist_ok=True)
    codes = {c: g for g, v in GROUPS.items() for c in v[3]}
    frames = []
    with zipfile.ZipFile(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip") as z:
        cc = pd.read_csv(z.open("country_codes_V202601.csv"))
        for y in (2022, 2023, 2024):
            for ch in pd.read_csv(z.open(f"BACI_HS22_Y{y}_V202601.csv"), dtype={"k": str}, chunksize=3_000_000):
                ch = ch[ch.k.str.zfill(6).isin(codes)]
                frames.append(ch.assign(k=ch.k.str.zfill(6)))
    d = pd.concat(frames)
    d["g"] = d.k.map(codes)
    name = cc.set_index("country_code").country_name
    rows = []
    for g, (de, en, ctrl, _) in GROUPS.items():
        x = d[d.g == g]
        de_imp = x[x.j == DEU]
        r = {"g": g, "de": de, "en": en, "control": ctrl}
        for y in (2022, 2023, 2024):
            v = de_imp[de_imp.t == y].groupby("i").v.sum()
            r[f"cn_{y}"] = float(100 * v.get(CHN, 0) / v.sum()) if v.sum() else None
        v = de_imp[de_imp.t == 2024].groupby("i").v.sum().sort_values(ascending=False)
        r["imp_mio_usd"] = float(v.sum() / 1000)
        sh = v / v.sum()
        r["hhi"] = float((sh ** 2).sum())
        r["top"] = [[str(name.get(i, i)), round(float(100 * s), 1)] for i, s in sh.head(3).items()]
        w = x[x.t == 2024].groupby("i").v.sum()
        r["cn_world"] = float(100 * w.get(CHN, 0) / w.sum())
        rows.append(r)
    t = pd.DataFrame(rows)
    t.drop(columns=["top"]).round(2).to_csv(out / "critical_materials.csv", index=False)
    print(t[["g", "imp_mio_usd", "cn_2022", "cn_2024", "cn_world", "hhi"]].round(1).to_string(index=False))
    for r in rows:
        print(r["g"], r["top"])
    if site:
        p = Path(site) / "critical_materials.json"
        txt = json.dumps({"groups": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()} for r in rows]}, ensure_ascii=False, separators=(",", ":"))
        assert "NaN" not in txt
        p.write_text(txt, encoding="utf-8")
        print(p.name, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
