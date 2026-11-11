"""German foreign direct investment: the US and China.

Data: OECD FDI statistics by partner country (BMD4, directional principle), dataflows
OECD.DAF.INV DSD_FDI@DF_FDI_POS_CTRY (positions) and DF_FDI_FLOW_CTRY (financial flows),
reporter Germany, all resident units, total direct investment, EUR (reporting currency).
Outward (DO) by immediate counterpart; inward (DI) also by ultimate investing country, which
assigns investment routed through holdings in the Netherlands or Luxembourg to its origin.
Writes <output>/fdi/fdi_*.csv and site data fdi.json.
Usage: python 84_fdi.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "fdi"
    out = cfg["output"] / "fdi"
    out.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(raw / "DF_FDI_POS_CTRY.csv", low_memory=False)
    f = pd.read_csv(raw / "DF_FDI_FLOW_CTRY.csv", low_memory=False)
    base = lambda d, m: d[(d.MEASURE == m) & (d.UNIT_MEASURE == "RC") & (d.TYPE_ENTITY == "ALL") & (d.ACCOUNTING_ENTRY == "NET_FDI")]
    pos = base(p, "LE_FA_F")
    imc = pos[pos.LEVEL_COUNTERPART == "IMC"].pivot_table(index=["MEASURE_PRINCIPLE", "TIME_PERIOD"], columns="COUNTERPART_AREA", values="OBS_VALUE") / 1000
    ult = pos[pos.LEVEL_COUNTERPART == "ULT"].pivot_table(index=["MEASURE_PRINCIPLE", "TIME_PERIOD"], columns="COUNTERPART_AREA", values="OBS_VALUE") / 1000
    fl = base(f, "T_FA_F").pivot_table(index=["MEASURE_PRINCIPLE", "TIME_PERIOD"], columns="COUNTERPART_AREA", values="OBS_VALUE") / 1000
    do, di, dof = imc.loc["DO"], imc.loc["DI"], fl.loc["DO"]
    last = int(do.index.max())
    out_ser = pd.DataFrame({"world": do["W"], "usa": do["USA"], "chn": do["CHN"]})
    out_ser.round(2).to_csv(out / "fdi_outward_stocks.csv")
    flows = pd.DataFrame({"usa": dof["USA"], "chn": dof["CHN"], "world": dof["W"]})
    flows.round(2).to_csv(out / "fdi_outward_flows.csv")
    top = do.loc[last].drop(labels=[c for c in do.columns if len(str(c)) != 3], errors="ignore").sort_values(ascending=False).head(10)
    uy = int(ult.loc["DI"].index.max()) if "DI" in ult.index.get_level_values(0) else None
    inward = {c: {"imc": float(di.loc[uy, c]) if uy and c in di.columns and pd.notna(di.loc[uy, c]) else None,
                  "ult": float(ult.loc[("DI", uy), c]) if uy and c in ult.columns and pd.notna(ult.loc[("DI", uy), c]) else None}
              for c in ("USA", "CHN", "GBR", "CHE", "FRA", "JPN", "NLD", "LUX")}
    print("outward stock", last, out_ser.loc[last].round(0).to_dict(), "| share US %.1f %%, CN %.1f %%" % (100 * do.loc[last, "USA"] / do.loc[last, "W"], 100 * do.loc[last, "CHN"] / do.loc[last, "W"]))
    print("flows to US/CN 2013-24 sum", flows[["usa", "chn"]].sum().round(0).to_dict())
    print("inward", uy, {k: {kk: (None if vv is None else round(vv, 1)) for kk, vv in v.items()} for k, v in inward.items()})
    if site:
        j = {"year": last, "years": [int(y) for y in out_ser.index],
             "out": {k: [None if pd.isna(v) else round(float(v), 1) for v in out_ser[k]] for k in out_ser},
             "flows": {"years": [int(y) for y in flows.index], **{k: [None if pd.isna(v) else round(float(v), 1) for v in flows[k]] for k in flows}},
             "top": [[c, round(float(v), 1)] for c, v in top.items()], "inward_year": uy,
             "inward": {k: {kk: (None if vv is None else round(vv, 1)) for kk, vv in v.items()} for k, v in inward.items()}}
        txt = json.dumps(j, ensure_ascii=False, separators=(",", ":"))
        assert "NaN" not in txt
        pth = Path(site) / "fdi.json"
        pth.write_text(txt, encoding="utf-8")
        print(pth.name, pth.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
