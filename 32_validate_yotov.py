"""Validate gravity_ge.py against the NAFTA application in Yotov, Piermartini,
Monteiro and Larch (2016), An Advanced Guide to Trade Policy Analysis, ch. 2,
application 2 ("Impact of regional trade agreements").

Needs the book's application files (Stata). They ship with the R replication
package tradepolicy (github.com/pachadotdev/tradepolicy, folder
00-application-files/Chapter2). Set cfg["data"]["yotov_guide"] to that
Chapter2 folder.

Steps follow RTAsEffects.do:
  1. Panel PPML 1986-2006 (every 4 years) with pair, exporter-year and
     importer-year fixed effects and an RTA dummy.
  2. Pair effects of 1994; missing ones (pairs never trading) predicted by a
     cross-section PPML on distance, contiguity, language and colony.
  3. Baseline 1994 flows consistent with these costs; counterfactual removes
     NAFTA; sigma = 7; GE solved with gravity_ge.ge_solve.
  4. Compare with the book's results file 2_RTAsEffects_FULL_PROD.dta.
Usage: python 32_validate_yotov.py
"""
import numpy as np
import pandas as pd

import gravity_ge as gg
from config import load_config

YEARS = [1986, 1990, 1994, 1998, 2002, 2006]
NAFTA = {"CAN", "USA", "MEX"}
SIGMA = 7.0


def main():
    cfg = load_config()
    root = cfg["data"]["yotov_guide"]
    d = pd.read_stata(root / "Datasets" / "Chapter2Application2.dta")
    d = d[d.year.isin(YEARS)].copy()
    d["year"] = d.year.astype(int)
    d["ln_DIST"] = np.log(d.DIST)
    # as in the book: symmetric pair effects (pair_id is the same for ij and
    # ji) and one common effect for all domestic pairs
    d["pair"] = np.where(d.exporter == d.importer, "domestic", d.pair_id.astype(int).astype(str))
    d["exp_year"] = d.exporter + d.year.astype(str)
    d["imp_year"] = d.importer + d.year.astype(str)

    # 1. panel PPML
    m = gg.fepois(d, "trade ~ RTA | pair + exp_year + imp_year")
    b_rta = float(m.coef()["RTA"])
    print(f"RTA coefficient {b_rta:.4f} (book 0.5572)")
    fe = m.fixef()
    pair_fe = {k: v for k, v in fe["C(pair)"].items()}

    # 2. pair costs in 1994
    c = d[d.year == 1994].copy()
    c["gamma"] = c.pair.map(pair_fe) - pair_fe["domestic"]   # domestic pairs = 0
    c["tij"] = np.exp(c.gamma)
    foreign = c[(c.exporter != c.importer) & c.tij.notna()]
    m2 = gg.fepois(foreign, "tij ~ ln_DIST + CNTG + LANG + CLNY | exporter + importer")
    c["tij_hat"] = np.exp(m2.predict(newdata=c, type="link"))
    c["tij_bar"] = np.where(c.exporter == c.importer, 1.0, c.tij.fillna(c.tij_hat))
    n_missing = int((c.exporter != c.importer).sum() - len(foreign))
    print(f"pairs without own estimate, predicted: {n_missing}")

    countries = sorted(c.exporter.unique())
    k = len(countries)
    pos = {x: i for i, x in enumerate(countries)}
    ii, jj = c.exporter.map(pos).to_numpy(), c.importer.map(pos).to_numpy()
    grid = lambda v: np.bincount(ii * k + jj, weights=v, minlength=k * k).reshape(k, k)
    rta = grid(c.RTA.to_numpy())
    t_bln = grid(c.tij_bar.to_numpy()) * np.exp(b_rta * rta)
    trade = grid(c.trade.to_numpy())
    X = gg.sinkhorn(t_bln, trade.sum(axis=1), trade.sum(axis=0))

    # 3. counterfactual: no NAFTA
    nafta = np.array([x in NAFTA for x in countries])
    rta_cfl = rta.copy()
    rta_cfl[np.ix_(nafta, nafta)] = 0
    np.fill_diagonal(rta_cfl, np.diag(rta))
    T_hat = np.exp(b_rta * (rta_cfl - rta))
    res = gg.ge_solve(X, T_hat, SIGMA, ref=pos["DEU"])
    cdl = gg.ge_solve(X, T_hat, SIGMA, conditional=True)

    # book reports the NAFTA effect: baseline relative to counterfactual
    ours = pd.DataFrame({
        "country": countries,
        "Xi_CDL": (1 / cdl["exports_hat"] - 1) * 100,
        "Xi_FULL": (1 / res["exports_hat"] - 1) * 100,
        "rGDP_FULL": (1 / res["W_hat"] - 1) * 100,
    }).set_index("country")
    res_dir = root / "Applications" / "2_RTAsEffects" / "Results"
    prod = pd.read_stata(res_dir / "2_RTAsEffects_FULL_PROD.dta").set_index("country")
    cons = pd.read_stata(res_dir / "2_RTAsEffects_FULL_CONS.dta").set_index("country")
    book = pd.DataFrame({
        "Xi_CDL": prod.change_Xi_CDL, "Xi_FULL": prod.change_Xi_FULL,
        "rGDP_FULL": ((prod.Y_BLN / cons.IMR_BLN ** (1 / (1 - SIGMA)))
                      / (prod.Y_FULL / cons.IMR_FULL ** (1 / (1 - SIGMA))) - 1) * 100,
    })
    cmp = ours.join(book, lsuffix="_ours", rsuffix="_book")
    show = ["CAN", "MEX", "USA", "DEU", "CHN", "JPN"]
    pd.set_option("display.width", 140)
    print(cmp.loc[show].round(3))
    for v in ("Xi_CDL", "Xi_FULL", "rGDP_FULL"):
        diff = (cmp[f"{v}_ours"] - cmp[f"{v}_book"]).abs()
        print(f"{v:10s} max abs diff {diff.max():.4f} pp, corr "
              f"{cmp[f'{v}_ours'].corr(cmp[f'{v}_book']):.5f}")


if __name__ == "__main__":
    main()
