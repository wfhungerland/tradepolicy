"""Robustness of the district US tariff exposure (74) to the downscaling assumptions.

Baseline (74): dm_k = m_r x q_k / q_r, loss_k = -dm_k x U_k, with m_r the NUTS 2 manufacturing-mix
shock, q the export ratio and U manufacturing sales (Regionaldatenbank 42111-04-02-4, 2024).
Variants (one assumption changed at a time):
  q2019      export ratios and sales of 2019 (before Covid and the 2025 tariffs)
  q2224      export ratios and sales averaged over 2022-2024 (smooths single-year swings)
  no_q       no within-region scaling: every district takes its region's shock (dm_k = m_r)
  half_q     half of the shock via exports, half proportional to output: m_r x (0.5 + 0.5 q_k / q_r)
  emp        regional loss allocated by industry employment x export ratio instead of sales x export
             ratio (INKAR Industriequote 2023 x working-age population); removes productivity differences
  deal       sector shock of the September 2025 framework deals (scenario deal_2025_09)
  retal      sector shock with EU retaliation (scenario retaliation_eu)
For each variant: total loss, rank correlation with the baseline loss per inhabitant, overlap of the
top fifth, Spearman correlations with the INKAR profile (industry employment, GDP per head, earnings,
unemployment), share of the loss in GRW C and C/D areas, local business tax per inhabitant in the top
versus bottom fifth, number of double-risk districts and overlap with the baseline list (79, 80).
Writes <output>/kreise/robustness_kreise.csv (variants x metrics), robustness_districts.csv
(loss per inhabitant by district and variant) and site data kreise_robust.json.
Usage: python 86_kreise_robustness.py [site_data_folder]
"""
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import regional as rg
from config import load_config

k74 = importlib.import_module("74_kreise_us_tariffs")
i79 = importlib.import_module("79_inkar_analyses")

LABELS = {"base": ("Basis (Exportquote 2024)", "Baseline (export ratio 2024)"),
          "q2019": ("Exportquote und Umsatz 2019", "Export ratio and sales 2019"),
          "q2224": ("Exportquote und Umsatz 2022-2024", "Export ratio and sales 2022-2024"),
          "no_q": ("ohne Exportquote (nur NUTS-2-Mix)", "No export ratio (NUTS 2 mix only)"),
          "half_q": ("halb Export, halb Produktion", "Half exports, half output"),
          "emp": ("Beschäftigte statt Umsatz", "Employment instead of sales"),
          "deal": ("Szenario Rahmenabkommen Sept. 2025", "Scenario framework deals Sept 2025"),
          "retal": ("Szenario mit EU-Gegenzöllen", "Scenario with EU retaliation")}


def downscale(k, m, q, u, mode="ratio"):
    """District output change (%) and loss (EUR million) from NUTS 2 shock m, export ratio q, sales u."""
    a = q * u
    pub = pd.DataFrame({"nuts2": k.nuts2, "a": a, "u": u}).dropna()
    qr = pub.groupby("nuts2").a.sum() / pub.groupby("nuts2").u.sum()
    mr, qr = k.nuts2.map(m), k.nuts2.map(qr)
    rel = {"ratio": q / qr, "none": q * 0 + 1, "half": 0.5 + 0.5 * q / qr}[mode]
    dm = mr * rel
    return dm, -dm / 100 * u


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    p = rg.rdb_kreise(cfg["data"]["scenarios"] / "kreise" / "rdb_42111-04-02-4.csv")
    u = p.umsatz.unstack() / 1000                          # EUR million
    q = (p.ausl / p.umsatz).unstack()
    base = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    k = base[["name", "nuts3", "nuts2", "pop"]].copy()
    m0 = k74.mix_shock(cfg)
    v = {}
    v["base"] = downscale(k, m0, q[2024].reindex(k.index), u[2024].reindex(k.index))
    v["q2019"] = downscale(k, m0, q[2019].reindex(k.index), u[2019].reindex(k.index))
    u3 = u[[2022, 2023, 2024]].mean(axis=1, skipna=False)
    a3 = (q * u)[[2022, 2023, 2024]].mean(axis=1, skipna=False)
    v["q2224"] = downscale(k, m0, (a3 / u3).reindex(k.index), u3.reindex(k.index))
    v["no_q"] = downscale(k, m0, q[2024].reindex(k.index), u[2024].reindex(k.index), "none")
    v["half_q"] = downscale(k, m0, q[2024].reindex(k.index), u[2024].reindex(k.index), "half")
    d = i79.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    g = lambda n, y=None: i79.get(d, n, y).reindex(k.index)
    emp = g("Industriequote", 2023) / 100 * g("Erwerbsfähige Bevölkerung (15 bis unter 65 Jahre)", 2023)
    # employment variant: regional loss of the baseline, shared by employment x export ratio
    dm_b, l_b = v["base"]
    w = (emp * q[2024].reindex(k.index)).where(l_b.notna())
    lr = l_b.groupby(k.nuts2).sum()
    l_e = k.nuts2.map(lr) * w / w.groupby(k.nuts2).transform("sum")
    v["emp"] = (-100 * l_e / u[2024].reindex(k.index), l_e)
    for key, sc in (("deal", "deal_2025_09"), ("retal", "retaliation_eu")):
        v[key] = downscale(k, k74.mix_shock(cfg, sc), q[2024].reindex(k.index), u[2024].reindex(k.index))
    lpc = pd.DataFrame({key: l * 1e6 / k["pop"] for key, (_, l) in v.items()})
    assert abs(v["base"][1].sum() - base.loss_mio.sum()) < 1, "baseline differs from 74"

    prof = pd.DataFrame({"iq": g("Industriequote"), "bip": g("Bruttoinlandsprodukt je Einwohner"),
                         "inc": g("Medianeinkommen"), "alq": g("Arbeitslosenquote"), "gwst": g("Gewerbesteuer"),
                         "prog": g("Prognostizierte Bevölkerungsentwicklung (2022-2045)"), "sgb2": g("SGB II - Quote")})
    grw = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags").reindex(k.index)
    thr = prof.sgb2.quantile(0.8)
    rows, dbl = [], {}
    for key in v:
        x = lpc[key].dropna()
        lm = v[key][1].reindex(x.index)
        qq = pd.qcut(x, 5, labels=False) + 1
        top = set(x[qq == 5].index)
        dbl[key] = {a for a in top if prof.prog.get(a, np.nan) < -5 or prof.sgb2.get(a, np.nan) >= thr}
        pw = lambda s: float(np.average(prof.gwst[s].dropna(), weights=k["pop"][s][prof.gwst[s].notna()]))
        r = {"variant": key, "label": LABELS[key][0], "label_en": LABELS[key][1], "n": len(x),
             "total_bn": lm.sum() / 1000, "rho_base": x.corr(lpc["base"], method="spearman"),
             "top_overlap": len(top & set(lpc["base"].dropna()[pd.qcut(lpc["base"].dropna(), 5, labels=False) == 4].index)) / len(top),
             **{f"rho_{c}": x.corr(prof[c].reindex(x.index), method="spearman") for c in ("iq", "bip", "inc", "alq")},
             "loss_c": float((lm * grw.share_c.reindex(x.index)).sum() / lm.sum()),
             "loss_cd": float((lm * grw.share_cd.reindex(x.index)).sum() / lm.sum()),
             "gwst_top": pw(x[qq == 5].index), "gwst_bottom": pw(x[qq == 1].index),
             "double_n": len(dbl[key]), "double_overlap": len(dbl[key] & dbl["base"])}
        rows.append(r)
    res = pd.DataFrame(rows).set_index("variant")
    pd.set_option("display.width", 220)
    print(res.drop(columns=["label", "label_en"]).round(3).to_string())
    print("double risk only in variants:", {kk: sorted(k.name[list(s - dbl["base"])]) for kk, s in dbl.items() if s - dbl["base"]})
    res.round(4).to_csv(out / "robustness_kreise.csv")
    lpc.join(k[["name", "nuts3"]]).round(1).to_csv(out / "robustness_districts.csv")
    # districts in the top fifth under every sales-based variant (robust core)
    core = [c for c in ("base", "q2019", "q2224", "half_q", "emp", "deal", "retal")]
    rk = lpc[core].rank(pct=True)
    always = rk[(rk > 0.8).all(axis=1)].index
    print(f"in the top fifth under all {len(core)} variants: {len(always)} districts, e.g.", list(k.name[always][:12]))
    if site:
        js = {"variants": res.reset_index().round(4).to_dict("records"), "core_n": len(always),
              "core": sorted(k.name[always].tolist()),
              "range": {a: [round(float(lpc.loc[a, core].min())), round(float(lpc.loc[a, core].max()))] for a in lpc.index if lpc.loc[a, core].notna().all()}}
        js["range"] = {k.nuts3[a]: r for a, r in js["range"].items() if pd.notna(k.nuts3[a])}
        pth = Path(site) / "kreise_robust.json"
        pth.write_text(json.dumps(js, ensure_ascii=False, separators=(",", ":"), default=float), encoding="utf-8")
        print(pth.name, pth.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
