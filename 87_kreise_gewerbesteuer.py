"""Local business tax (Gewerbesteuer) under the US tariff shock, by district.

Step 1, elasticity: how strongly does a district's Gewerbesteuer react to its own manufacturing
sales? District panel 2009-2023: Gewerbesteuer per inhabitant (INKAR 2025, q_gewst_bev, EUR) and
manufacturing sales per inhabitant (Regionaldatenbank 42111-04-02-4, establishments 20+).
  levels   ln G_kt = b ln U_kt + district FE + year FE (s.e. clustered by district; all models also by NUTS 2)
  lags     d ln G_kt = sum_j b_j d ln U_k,t-j (j = 0, 1, 2) + year FE (prepayments adjust with a lag)
  longdiff change 2010-12 -> 2021-23 with Land FE
  terciles levels model by tercile of the industry employment rate 2013 (INKAR Industriequote)
  placebo  levels model with next year's sales added (lead); a large lead coefficient would point to
           reverse timing or common trends rather than a response of the tax to sales
Year effects absorb the national cycle, so b measures the response to a district-specific sales
shock, the kind of shock that the regional allocation of the tariff loss creates. Apportionment
(Zerlegung) of the tax base by payroll to municipalities with plants is part of the reduced form.
Step 2, scenario: dG_k = b_t(k) x dm_k x G_k (2023), with dm_k the manufacturing output change of 74
and b_t the tercile elasticity; variants with the uniform levels elasticity and with b = 1 (upper
bound: the national Gewerbesteuer fell 21 % in 2009 while manufacturing sales fell about 20 %).
Shown per inhabitant, in % of Gewerbesteuer and of tax capacity (Steuerkraft), by tariff quintile,
and for GRW areas. A first-round estimate: no second-round effects via suppliers or incomes.
Writes <output>/kreise/gewerbesteuer_elasticity.csv, gewerbesteuer_kreise.csv, site data kreise_gewst.json.
Usage: python 87_kreise_gewerbesteuer.py [site_data_folder]
"""
import importlib
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf

import regional as rg
from config import load_config

i79 = importlib.import_module("79_inkar_analyses")
warnings.filterwarnings("ignore", message=".*singleton.*")


def panel(d, rdb):
    s = lambda n, c: d[d.I == n].groupby(["ags", "Zeitbezug"]).Wert.first().rename(c)
    p = pd.concat([s("Gewerbesteuer", "g"), s("Bevölkerung gesamt", "pop")], axis=1)
    p.index = p.index.set_names(["ags", "year"])
    p = p.join(rdb.umsatz, how="left").reset_index()
    p["lg"] = np.log(p.g.where(p.g > 0))
    p["lu"] = np.log(p.umsatz / p["pop"])
    p = p.sort_values(["ags", "year"])
    for c in ("lg", "lu"):
        p["d_" + c] = p.groupby("ags")[c].diff()
    for j in (1, 2):
        p[f"d_lu_{j}"] = p.groupby("ags").d_lu.shift(j)
    p["land"] = p.ags.str[:2]
    return p[(p.year >= 2009) & (p.year <= 2023)]


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    d = i79.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    p = panel(d, rg.rdb_kreise(cfg["data"]["scenarios"] / "kreise" / "rdb_42111-04-02-4.csv"))
    iq = i79.get(d, "Industriequote", 2013)
    p["t"] = p.ags.map(pd.qcut(iq, 3, labels=[1, 2, 3]).astype(float))
    nuts2 = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags").nuts2
    p["nuts2"] = p.ags.map(nuts2)
    lev = p.dropna(subset=["lg", "lu", "nuts2"])
    dl = p.dropna(subset=["d_lg", "d_lu", "d_lu_1", "d_lu_2", "nuts2"])
    dl = dl[(dl.d_lg.abs() < 1.5) & (dl.d_lu.abs() < 1)]               # drop extreme swings (reclassification, single plants)
    a = lev[lev.year.between(2010, 2012)].groupby("ags")[["lg", "lu"]].mean()
    z = lev[lev.year.between(2021, 2023)].groupby("ags")[["lg", "lu"]].mean()
    ld = (z - a).dropna().reset_index().assign(land=lambda x: x.ags.str[:2], nuts2=lambda x: x.ags.map(nuts2)).dropna(subset=["nuts2"])
    p["lu_lead"] = p.groupby("ags").lu.shift(-1)
    pl = p.dropna(subset=["lg", "lu", "lu_lead", "nuts2"])
    # (model, formula, data, weights, own-district clustering); every model is also run with clusters by NUTS 2 region
    specs = [("levels", "lg ~ lu | ags + year", lev, None, {"CRV1": "ags"}),
             ("levels_popweighted", "lg ~ lu | ags + year", lev, "pop", {"CRV1": "ags"}),
             ("lags_sum", "d_lg ~ d_lu + d_lu_1 + d_lu_2 | year", dl, None, {"CRV1": "ags"}),
             ("longdiff", "lg ~ lu | land", ld, None, "hetero"),
             ("placebo_lead", "lg ~ lu + lu_lead | ags + year", pl, None, {"CRV1": "ags"})]
    specs += [(f"tercile_{t}", "lg ~ lu | ags + year", lev[lev.t == t], None, {"CRV1": "ags"}) for t in (1, 2, 3)]
    est, bt, st = [], {}, {}
    for name, f, data, w, vc in specs:
        r1 = pf.feols(f, data=data, weights=w, vcov=vc)
        r2 = pf.feols(f, data=data, weights=w, vcov={"CRV1": "nuts2"})
        if name == "lags_sum":
            row = {"b": float(r1.coef().sum()), "se": float(np.sqrt(r1._vcov.sum())), "se_nuts2": float(np.sqrt(r2._vcov.sum())),
                   "b0": float(r1.coef().d_lu), "b1": float(r1.coef().d_lu_1), "b2": float(r1.coef().d_lu_2)}
        else:
            row = {"b": float(r1.coef().lu), "se": float(r1.se().lu), "se_nuts2": float(r2.se().lu)}
        if name == "placebo_lead":
            row.update(b_lead=float(r1.coef().lu_lead), se_lead=float(r1.se().lu_lead), se_lead_nuts2=float(r2.se().lu_lead))
        if name.startswith("tercile"):
            t = int(name[-1])
            bt[t], st[t] = row["b"], max(row["se"], row["se_nuts2"])      # band uses the larger standard error
            row["iq_mean"] = float(iq[iq.index.isin(data.ags)].mean())
        est.append({"model": name, **row, "n": int(r1._N)})
    e = pd.DataFrame(est)
    print(e.round(3).to_string(index=False))
    e.round(4).to_csv(out / "gewerbesteuer_elasticity.csv", index=False)
    nat = (lev.g * lev["pop"]).groupby(lev.year).sum() / 1e9
    print("Gewerbesteuer, EUR bn (sum over districts):", nat.round(1).loc[[2009, 2019, 2023]].to_dict())

    # scenario
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    grw = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags")
    k = u[["name", "nuts3", "pop", "dm", "loss_pc"]].copy()
    k["gwst_pc"] = i79.get(d, "Gewerbesteuer", 2023).reindex(k.index)
    k["stk_pc"] = i79.get(d, "Steuerkraft", 2023).reindex(k.index)
    k["t"] = pd.qcut(iq, 3, labels=[1, 2, 3]).astype(float).reindex(k.index)
    b_lev = float(e.set_index("model").b["levels"])
    k["el"] = k.t.map(bt)
    for c, el in (("central", k.el), ("uniform", b_lev), ("upper", 1.0)):
        k[f"dg_pc_{c}"] = el * k.dm / 100 * k.gwst_pc                 # EUR per inhabitant (negative = loss)
        k[f"dg_mio_{c}"] = k[f"dg_pc_{c}"] * k["pop"] / 1e6
    imp = out / "us_tariffs_kreise_imputed.csv"
    if imp.exists():                                   # tax loss including the 14 imputed districts (89)
        x = pd.read_csv(imp, dtype={"ags": str}).set_index("ags").reindex(k.index)
        k["dg_mio_imputed"] = k.el * x.dm / 100 * k.gwst_pc * k["pop"] / 1e6
        print(f"tax loss with imputed districts: {k.dg_mio_imputed.sum():,.0f} EUR million;",
              k.assign(n=u.name).dropna(subset=["dg_mio_imputed"])[x.imputed.reindex(k.index).fillna(False).astype(bool)]
              .assign(pc=lambda z: z.dg_mio_imputed * 1e6 / z["pop"]).sort_values("pc")[["n", "pc"]].head(4).round(1).values.tolist())
    k["dg_pct"] = 100 * k.dg_pc_central / k.gwst_pc
    k["dg_stk_pct"] = 100 * k.dg_pc_central / k.stk_pc
    k = k.join(grw[["share_c", "share_cd", "double"]])
    v = k.dropna(subset=["dg_pc_central"]).copy()
    v["q"] = pd.qcut(v.loss_pc, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    w = lambda x, c: float(np.average(x[c], weights=x["pop"]))
    tot = {c: float(v[f"dg_mio_{c}"].sum()) for c in ("central", "uniform", "upper")}
    if "dg_mio_imputed" in k:
        tot["imputed"] = float(k.dg_mio_imputed.sum())
    # 95 % band of the central total from the tercile standard errors (larger of district and NUTS 2 clustering;
    # tercile regressions on disjoint samples)
    part = v.groupby("t").apply(lambda x: (x.dm / 100 * x.gwst_pc * x["pop"] / 1e6).sum())
    se_tot = float(np.sqrt(sum((part[t] * st[t]) ** 2 for t in part.index)))
    tot["central_lo"], tot["central_hi"] = tot["central"] - 1.96 * se_tot, tot["central"] + 1.96 * se_tot
    quint = [{"q": q, "n": len(x), "dg_pc": w(x, "dg_pc_central"), "dg_pct": w(x, "dg_pct"), "dg_stk_pct": w(x, "dg_stk_pct"),
              "gwst_pc": w(x, "gwst_pc")} for q, x in v.groupby("q")]
    summ = {"elasticity": e.round(4).to_dict("records"), "total_mio": tot, "gwst_total_mio": float((v.gwst_pc * v["pop"]).sum() / 1e6),
            "by_quintile": quint,
            "loss_share_c": float((v.dg_mio_central * v.share_c).sum() / v.dg_mio_central.sum()),
            "loss_share_cd": float((v.dg_mio_central * v.share_cd).sum() / v.dg_mio_central.sum()),
            "top_pc": [[r["name"], round(r.dg_pc_central), round(r.dg_pct, 1), round(r.dg_stk_pct, 1)] for _, r in v.sort_values("dg_pc_central").head(15).iterrows()],
            "top_stk": [[r["name"], round(r.dg_pc_central), round(r.dg_pct, 1), round(r.dg_stk_pct, 1)] for _, r in v.sort_values("dg_stk_pct").head(15).iterrows()],
            "double": [[r["name"], round(r.dg_pc_central), round(r.dg_stk_pct, 1)] for _, r in v[v.double == True].sort_values("dg_pc_central").iterrows()]}
    print(f"Gewerbesteuer loss, EUR million a year: central {tot['central']:,.0f} (95 % band {tot['central_hi']:,.0f} to {tot['central_lo']:,.0f}), uniform {tot['uniform']:,.0f}, upper {tot['upper']:,.0f}"
          f" (of {summ['gwst_total_mio']:,.0f}); in C areas {summ['loss_share_c']:.0%}, C or D {summ['loss_share_cd']:.0%}")
    print(pd.DataFrame(quint).round(2).to_string(index=False))
    print("largest per inhabitant:", summ["top_pc"][:10])
    print("largest relative to tax capacity:", summ["top_stk"][:10])
    k.round(4).to_csv(out / "gewerbesteuer_kreise.csv")
    (out / "gewerbesteuer_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    if site:
        mp = {r.nuts3: {"pc": round(float(r.dg_pc_central), 1), "pct": round(float(r.dg_pct), 2), "stk": round(float(r.dg_stk_pct), 2)}
              for _, r in v.dropna(subset=["nuts3"]).iterrows()}
        pth = Path(site) / "kreise_gewst.json"
        pth.write_text(json.dumps({"kreise": mp, "summary": summ}, ensure_ascii=False, separators=(",", ":"), default=float), encoding="utf-8")
        print(pth.name, pth.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
