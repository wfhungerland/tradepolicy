"""Build the working paper on US tariffs and German districts.

Fills the result tables of paper/regional_paper_template.md from the output files of scripts
74 and 78-88 (placeholders {{NAME}}), writes paper/regional_paper.md, and converts it with pandoc
to paper/regional_paper.html (and to PDF with Chromium, if Playwright is installed).
Usage: python tools/build_regional_paper.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import load_config

PAPER = ROOT / "paper"


def fmt(x, d=1, sign=False):
    if pd.isna(x):
        return ""
    s = f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}"
    return s.replace("-", "−")


def md(df):
    cols = list(df.columns)
    al = ["---"] + ["---:"] * (len(cols) - 1)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(al) + " |"]
    rows += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


def short(n):
    n = re.sub(r", (Stadt|Stadtkreis|kreisfreie Stadt|Landeshauptstadt|Wissenschaftsstadt|Freie und Hansestadt)$", r" (\1)", n)
    return n.replace(" (Stadtkreis)", " (city)").replace(" (Stadt)", " (city)").replace(" (kreisfreie Stadt)", " (city)") \
            .replace(" (Landeshauptstadt)", " (city)").replace(" (Wissenschaftsstadt)", " (city)").replace(" (Freie und Hansestadt)", "")


def tables(out, site):
    t = {}
    p = pd.read_csv(out / "profile_us_tariffs.csv")
    ind = [("loss_pc_mean", "Output loss per inhabitant, EUR", 0), ("Bruttoinlandsprodukt je Einwohner", "GDP per head, EUR thousand (2022)", 1),
           ("Medianeinkommen", "Median full-time earnings, EUR per month", 0), ("Industriequote", "Industry employees per 100 aged 15-64", 1),
           ("Beschäftigte am AO mit akademischem Berufsabschluss", "Employees with university degree, %", 1),
           ("Arbeitslosenquote", "Unemployment rate, %", 1), ("Durchschnittsalter der Bevölkerung", "Mean age, years", 1),
           ("pop_growth", "Population change 2013-2023, %", 1)]
    t["T_PROFILE"] = md(pd.DataFrame([[lab] + [fmt(v, d) for v in p[c]] for c, lab, d in ind],
                                     columns=["Indicator (population-weighted mean)"] + [f"Q{q}" for q in p.quintile]))
    e = pd.read_csv(out / "gewerbesteuer_elasticity.csv")
    lab = {"levels": "Levels, district and year effects", "levels_popweighted": "Levels, population-weighted",
           "lags_sum": "First differences, sum of lags 0 to 2", "longdiff": "Long difference 2010-12 to 2021-23, Land effects",
           "placebo_lead": "Levels with next year's sales: current year", "tercile_1": "Levels, least industrial third",
           "tercile_2": "Levels, middle third", "tercile_3": "Levels, most industrial third"}
    rows = []
    for r in e.itertuples():
        rows.append([lab[r.model], fmt(r.b, 3), fmt(r.se, 3), fmt(r.se_nuts2, 3), f"{r.n:,}"])
        if r.model == "placebo_lead":
            rows.append(["Levels with next year's sales: next year (placebo)", fmt(r.b_lead, 3), fmt(r.se_lead, 3), fmt(r.se_lead_nuts2, 3), f"{r.n:,}"])
    t["T_ELAST"] = md(pd.DataFrame(rows, columns=["Model", "Elasticity", "Std. error, district clusters", "Std. error, NUTS 2 clusters", "Observations"]))
    g = json.load(open(out / "gewerbesteuer_summary.json", encoding="utf-8"))
    q = pd.DataFrame(g["by_quintile"])
    t["T_TAX"] = md(pd.DataFrame({"Quintile": q.q, "Gewerbesteuer 2023, EUR per inhabitant": [fmt(x, 0) for x in q.gwst_pc],
                                  "Tax loss, EUR per inhabitant": [fmt(x, 1) for x in q.dg_pc],
                                  "Tax loss, % of Gewerbesteuer": [fmt(x, 2) for x in q.dg_pct],
                                  "Tax loss, % of tax capacity": [fmt(x, 2) for x in q.dg_stk_pct]}))
    s = json.load(open(out / "grw_summary.json", encoding="utf-8"))
    b = pd.DataFrame(s["by_quintile"])
    t["T_GRW"] = md(pd.DataFrame({"Quintile": b.q, "Districts": b.n, "Population in C areas, %": [fmt(100 * x, 0) for x in b.share_c],
                                  "Population in C or D areas, %": [fmt(100 * x, 0) for x in b.share_cd]}))
    r = pd.read_csv(out / "robustness_kreise.csv")
    t["T_ROBUST"] = md(pd.DataFrame({"Variant": r.label_en, "Districts": r.n, "Loss, EUR bn": [fmt(x, 1) for x in r.total_bn],
                                     "Rank corr. with baseline": [fmt(x, 2) for x in r.rho_base],
                                     "Top fifth kept, %": [fmt(100 * x, 0) for x in r.top_overlap],
                                     "Rank corr. with industry employment": [fmt(x, 2) for x in r.rho_iq],
                                     "Loss in C areas, %": [fmt(100 * x, 0) for x in r.loss_c],
                                     "Gewerbesteuer Q5/Q1": [fmt(a / b_, 2) for a, b_ in zip(r.gwst_top, r.gwst_bottom)],
                                     "Double-risk districts (in baseline)": [f"{a} ({b_})" for a, b_ in zip(r.double_n, r.double_overlap)]}))
    k = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags")
    gk = pd.read_csv(out / "gewerbesteuer_kreise.csv", dtype={"ags": str}).set_index("ags")
    d = k[k.double == True].join(gk[["dg_pc_central"]]).sort_values("loss", ascending=False)
    risk = lambda x: " and ".join([w for w, c in (("shrinking", x.prog < -5), ("poverty", x.sgb2 >= 10.172)) if c])
    t["T_DOUBLE"] = md(pd.DataFrame({"District": [short(n) for n in d.name], "Loss, EUR per inhabitant": [fmt(x, 0) for x in d.loss],
                                     "Population 2022-2045, %": [fmt(x, 1, True) for x in d.prog], "SGB II rate, %": [fmt(x, 1) for x in d.sgb2],
                                     "Second risk": [risk(x) for x in d.itertuples()], "GRW status": d.status.map({"C": "C", "D": "D", "teilweise": "partly", "keine": "none"}),
                                     "Tax loss, EUR per inhabitant": [fmt(x, 1) for x in d.dg_pc_central]}))
    core = json.load(open(Path(site) / "kreise_robust.json", encoding="utf-8"))["core"]
    t["T_CORE"] = ", ".join(short(n) for n in core) + "."
    return t


def main():
    cfg = load_config()
    out = cfg["output"] / "kreise"
    site = sys.argv[1] if len(sys.argv) > 1 else "/home/user/scen_site"
    text = (PAPER / "regional_paper_template.md").read_text(encoding="utf-8")
    for key, val in tables(out, site).items():
        text = text.replace("{{" + key + "}}", val)
    left = re.findall(r"\{\{\w+\}\}", text)
    assert not left, f"unfilled placeholders: {left}"
    (PAPER / "regional_paper.md").write_text(text, encoding="utf-8")
    subprocess.run(["pandoc", "regional_paper.md", "-s", "--css", "paper.css", "--embed-resources", "-o", "regional_paper.html",
                    "--metadata", "lang=en"], cwd=PAPER, check=True)
    print("written", PAPER / "regional_paper.html")
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('{(PAPER / 'regional_paper.html').as_uri()}');"
          f"await p.pdf({{path:'{PAPER / 'regional_paper.pdf'}',format:'A4',preferCSSPageSize:true}});await b.close();}})();")
    r = subprocess.run(["node", "-e", js], cwd=PAPER, capture_output=True, text=True)
    print("written", PAPER / "regional_paper.pdf" if r.returncode == 0 else "no PDF (Node Playwright missing): " + r.stderr[-300:])


if __name__ == "__main__":
    main()
