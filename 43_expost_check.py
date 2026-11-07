"""Ex-post check of the US tariff scenarios against observed US imports.

Observed: US goods imports by partner from IMF IMTS (monthly, CIF, USD), the 12 months
August 2025 to July 2026 against calendar 2024. Model: change in each partner's
exports to the US in the scenarios of 5 September 2025 and 22 August 2026 (the tariff
levels in force for most of that window) and their mean.

Both sides are taken relative to the change in total US imports, so that growth,
prices and the US business cycle drop out: for partner i,
  rel_i = ln(M_i,post / M_i,2024) - ln(M_post / M_2024).
The test is the cross-section of partners: correlation and slope of observed on
modelled relative changes, weighted by 2024 imports. A slope below one is expected,
because the model describes long-run adjustment and short-run trade elasticities are
smaller (Boehm, Levchenko and Pandalai-Nayar 2023, AER).

Writes <output>/scenarios/expost_us_imports.csv and expost_us_imports.png.
Usage: python 43_expost_check.py
"""
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from config import load_config

URL = ("https://api.imf.org/external/sdmx/2.1/data/IMF.STA,IMTS/USA.MG_CIF_USD..M"
       "?startPeriod=2024-01&detail=dataonly")
PRE = [f"2024-M{m:02d}" for m in range(1, 13)]
POST = [f"2025-M{m:02d}" for m in range(8, 13)] + [f"2026-M{m:02d}" for m in range(1, 8)]
SCEN = ["deal_2025_09", "current_2026_08"]
# known special cases, reported but kept: gold flows (Switzerland) and pharmaceutical
# front-loading (Ireland) move US import values far beyond tariff effects
SPECIAL = {"CHE": "gold", "IRL": "pharma front-loading"}


def imf_imports(cache):
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=300) as r:
            cache.write_bytes(r.read())
    rows = []
    for s in ET.parse(cache).getroot().iter():
        if s.tag.endswith("Series"):
            cp = s.attrib.get("COUNTERPART_COUNTRY")
            for o in s:
                v = o.attrib.get("OBS_VALUE")
                if v not in (None, "", "NaN"):
                    rows.append((cp, o.attrib.get("TIME_PERIOD"), float(v)))
    return pd.DataFrame(rows, columns=["partner", "period", "value"])


def wcorr(x, y, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return cov / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    obs = imf_imports(cfg["data"]["scenarios"] / "expost" / "imf_usa_imports.xml")
    last = sorted(obs.period.unique())[-1]
    if last < POST[-1]:
        raise SystemExit(f"IMF data end in {last}, need {POST[-1]}")
    pre = obs[obs.period.isin(PRE)].groupby("partner").value.sum()
    post = obs[obs.period.isin(POST)].groupby("partner").value.sum()
    world = obs[obs.partner.isin(["W00", "G001", "W"])]
    if len(world):
        tot_pre, tot_post = world[world.period.isin(PRE)].value.sum(), world[world.period.isin(POST)].value.sum()
    else:
        iso = [p for p in pre.index if len(p) == 3 and p.isalpha()]
        tot_pre, tot_post = pre.reindex(iso).sum(), post.reindex(iso).sum()

    res = pd.read_csv(out / "us_tariffs_results.csv")
    res = res[(res.elasticity == "protee") & res.scenario.isin(SCEN)]
    m = res.pivot(index="country", columns="scenario", values="exports_to_us_pct") / 100 + 1
    m["mean"] = m[SCEN].mean(axis=1)
    d = pd.DataFrame({"imports_2024": pre, "imports_post": post}).join(m, how="inner").dropna()
    d = d[(d.imports_2024 > 1e9 if d.imports_2024.max() > 1e9 else d.imports_2024 > 1e3)]
    d["obs_rel"] = np.log(d.imports_post / d.imports_2024) - np.log(tot_post / tot_pre)
    w = d.imports_2024
    lines = []
    for c in SCEN + ["mean"]:
        mod = np.log(d[c])
        d[f"mod_rel_{c}"] = mod - np.average(mod, weights=w)
        obs_rel = d.obs_rel - np.average(d.obs_rel, weights=w)
        x, y = d[f"mod_rel_{c}"], obs_rel
        slope = np.sum(w * x * y) / np.sum(w * x * x)
        keep = ~d.index.isin(SPECIAL)
        slope_ex = np.sum(w[keep] * x[keep] * y[keep]) / np.sum(w[keep] * x[keep] ** 2)
        lines.append(f"{c:16s} weighted corr {wcorr(x, y, w):.2f}  slope {slope:.2f}  "
                     f"without {', '.join(SPECIAL)}: corr {wcorr(x[keep], y[keep], w[keep]):.2f} slope {slope_ex:.2f}")
    print(f"{len(d)} partners, IMF data to {last}; total US imports {tot_post / tot_pre - 1:+.1%}")
    print("\n".join(lines))
    d["obs_rel_demeaned"] = d.obs_rel - np.average(d.obs_rel, weights=w)
    d.round(4).to_csv(out / "expost_us_imports.csv")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5.5))
    s = 30 + 400 * w / w.max()
    ax.scatter(d["mod_rel_mean"] * 100, d["obs_rel_demeaned"] * 100, s=s, color="#0070C0", alpha=0.6, edgecolor="#002060")
    big = d.sort_values("imports_2024", ascending=False).head(15).index
    for i in big:
        ax.annotate(i, (d.loc[i, "mod_rel_mean"] * 100, d.loc[i, "obs_rel_demeaned"] * 100), fontsize=8,
                    xytext=(4, 3), textcoords="offset points")
    lim = [min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])]
    ax.plot(lim, lim, color="#8c8c8c", lw=0.8, ls="--")
    ax.axhline(0, color="#595959", lw=0.6)
    ax.axvline(0, color="#595959", lw=0.6)
    ax.set_xlabel("Model: change in exports to the US relative to all partners, log points x 100")
    ax.set_ylabel("Observed Aug 2025-Jul 2026 vs 2024, relative, log points x 100")
    ax.set_title("US imports by partner: model and observation")
    fig.tight_layout()
    fig.savefig(out / "expost_us_imports.png", dpi=150)


if __name__ == "__main__":
    main()
