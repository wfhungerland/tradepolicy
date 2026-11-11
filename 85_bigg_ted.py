"""'Big G' facts for Germany from TED contract award notices (pilot).

Replicates, where the data allow, the stylised facts of Cox, Müller, Pasten, Schoenle
and Weber ("Big G", JPE 2024) for German public procurement above EU thresholds:
  F1 volatility of central-government purchases relative to all purchases,
  F2 granularity (concentration across firms and contracts),
  F3 competition (number of bids),
  F4 persistence of suppliers,
  F5 composition by CPV division (works, supplies, services).

Inputs (raw, not in the repository):
  data/ted_legacy/YYYY-MM.jsonl  from tools/ted_legacy_packages.py (legacy XML, 2016-2023)
  data/ted_eforms/YYYY.json      from tools/ted_eforms_api.py (eForms, late 2023 onwards)
Output: output/bigg_ted_awards.parquet, output/bigg_ted.json, optional site JSON.

Units: award values in EUR as published (mostly net of VAT), one row per award (lot);
values of multi-winner awards are split equally across winners. Awards above 5 bn EUR
are treated as errors and dropped.
"""
import json, glob, re, sys, math
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent
CENTRAL_LEGACY = {"MINISTRY", "NATIONAL_AGENCY"}
CENTRAL_EF = {"cga", "body-pl-cga", "pub-undert-cga"}
REGIONAL_LEGACY = {"REGIONAL_AUTHORITY", "REGIONAL_AGENCY"}
LEGAL = r"\b(gmbh|mbh|ag|kg|co|ohg|gbr|ug|se|e\.?\s?k|e\.?\s?v|kgaa|haftungsbeschr\w*|ltd|bv|nv|sa|sarl|srl|inc|llc|plc|und|&|niederlassung\s+\S+|zweigniederlassung\s+\S+)\b"
MAXV = 5e9
CPV2 = {"03": ("Land- und Forstwirtschaft", "Agriculture and forestry"), "09": ("Energie und Brennstoffe", "Energy and fuels"),
        "14": ("Bergbau, Steine", "Mining, stone"), "15": ("Nahrungsmittel", "Food"), "18": ("Bekleidung", "Clothing"),
        "22": ("Druckerzeugnisse", "Printed matter"), "24": ("Chemische Erzeugnisse", "Chemicals"),
        "30": ("Büro- und Rechenmaschinen", "Office and computing machinery"), "31": ("Elektrische Maschinen", "Electrical machinery"),
        "32": ("Funk, Telekommunikation", "Radio, telecommunications"), "33": ("Medizinische Geräte, Arzneimittel", "Medical equipment, pharmaceuticals"),
        "34": ("Fahrzeuge", "Transport equipment"), "35": ("Sicherheit, Verteidigung", "Security, defence"),
        "38": ("Labor- und Messgeräte", "Laboratory and measuring equipment"), "39": ("Möbel, Haushalt", "Furniture, household"),
        "42": ("Industriemaschinen", "Industrial machinery"), "43": ("Bergbau- und Baumaschinen", "Mining and construction machinery"),
        "44": ("Baumaterial", "Construction materials"), "45": ("Bauarbeiten", "Construction work"),
        "48": ("Software", "Software"), "50": ("Reparatur, Wartung", "Repair and maintenance"),
        "55": ("Gastgewerbe", "Hotel and catering"), "60": ("Verkehrsdienste", "Transport services"),
        "63": ("Logistik, Reisebüros", "Logistics, travel agencies"), "64": ("Post, Telekommunikation", "Postal and telecom services"),
        "65": ("Versorgung", "Utilities"), "66": ("Finanz- und Versicherungsdienste", "Financial and insurance services"),
        "70": ("Immobilien", "Real estate"), "71": ("Architektur, Ingenieurleistungen", "Architecture, engineering"),
        "72": ("IT-Dienste", "IT services"), "73": ("Forschung und Entwicklung", "Research and development"),
        "75": ("Verwaltung, Verteidigung, Sozialversicherung", "Administration, defence, social security"),
        "76": ("Öl- und Gasdienste", "Oil and gas services"), "77": ("Land- und Forstwirtschaftsdienste", "Agricultural and forestry services"),
        "79": ("Unternehmensdienste", "Business services"), "80": ("Bildung", "Education"),
        "85": ("Gesundheit und Soziales", "Health and social work"), "90": ("Abwasser, Abfall, Reinigung", "Sewage, waste, cleaning"),
        "92": ("Kultur, Sport", "Recreation, culture"), "98": ("Sonstige Dienste", "Other services")}

def norm_firm(s):
    if not s: return None
    s = s.lower().replace("ß", "ss")
    s = re.sub(r"[\"'`´.,;:()/\-+]", " ", s)
    s = re.sub(LEGAL, " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None

def fnum(x):
    if x in (None, ""): return None
    if isinstance(x, list): x = x[0] if x else None
    try:
        v = float(str(x).replace(" ", "").replace(",", "."))
        return v if 0 < v < MAXV else None
    except Exception: return None

def level_legacy(t, form):
    if "DEFENCE" in form: return "central"
    if t in CENTRAL_LEGACY: return "central"
    if t in REGIONAL_LEGACY: return "regional_local"
    if t is None and "UTILITIES" in form or form.startswith("F06") or form.startswith("F21"):
        return "utilities_other"
    if t == "BODY_PUBLIC": return "public_body"
    return "utilities_other"

def level_ef(types):
    types = set(types or [])
    if types & CENTRAL_EF: return "central"
    if types & {"ra", "la"}: return "regional_local"
    if types & {"body-pl", "body-pl-ra", "body-pl-la"}: return "public_body"
    return "utilities_other"

def load_legacy():
    rows = []
    for f in sorted(glob.glob(str(ROOT / "data/ted_legacy/*.jsonl"))):
        for line in open(f, encoding="utf8"):
            r = json.loads(line)
            v = fnum(r.get("value")) if r.get("cur") in ("EUR", None) else None
            nt = fnum(r.get("n_tenders"))
            date = r.get("date_conclusion") or (r["pub"][:4] + "-" + r["pub"][4:6] + "-" + r["pub"][6:8])
            wins = [w for w in r.get("winners", []) if w.get("name")]
            base = dict(pub_no=int(r["nd"].split("-")[0]), pub_year=int(r["pub"][:4]),
                        date=date, pub=r["pub"][:4] + "-" + r["pub"][4:6] + "-" + r["pub"][6:8],
                        buyer=r.get("buyer"), level=level_legacy(r.get("ca_type"), r.get("form", "")),
                        cpv=(r.get("cpv") or "")[:8], ctype=(r.get("ctype") or "").lower(),
                        n_tenders=nt, source="legacy", nuts=r.get("buyer_nuts"))
            if not wins:
                rows.append({**base, "value": v, "winner": None, "winner_country": None})
            for w in wins:
                rows.append({**base, "value": v / len(wins) if v else None,
                             "winner": norm_firm(w["name"]), "winner_country": w.get("country")})
    return pd.DataFrame(rows)

def first_lang(d):
    if isinstance(d, dict):
        for k in ("deu", "eng"):
            if d.get(k): return d[k]
        for v in d.values(): return v
    return d or []

def load_eforms(legacy_keys):
    rows = []
    for f in sorted(glob.glob(str(ROOT / "data/ted_eforms/*.json"))):
        for r in json.load(open(f, encoding="utf8")):
            no = r["publication-number"]; key = (int(no.split("-")[0]), int(no.split("-")[1]))
            if key in legacy_keys: continue
            wins = first_lang(r.get("winner-name"))
            bl = r.get("buyer-legal-type") or []
            if not wins and set(bl) & {"8", "1", "3", "4", "5", "6", "N", "R", "Z"}:
                continue  # legacy notice mirrored by the API, already in the packages
            v = fnum(r.get("total-value")) if (r.get("total-value-cur") or ["EUR"])[0] == "EUR" else None
            subs = [fnum(x) for x in (r.get("received-submissions-type-val") or [])]
            subs = [s for s in subs if s]
            nt = float(np.median(subs)) if subs else None
            pd_ = r["publication-date"][:10]
            nature = first_lang(r.get("contract-nature")) if isinstance(r.get("contract-nature"), dict) else (r.get("contract-nature") or [None])
            ctype = (nature[0] if nature else "") or ""
            cpv = (r.get("classification-cpv") or [""])[0]
            wins = list(dict.fromkeys(w for w in wins if w))
            base = dict(pub_no=key[0], pub_year=key[1], date=(r.get("contract-conclusion-date") or [pd_])[0][:10] if isinstance(r.get("contract-conclusion-date"), list) else pd_,
                        pub=pd_, buyer=(first_lang(r.get("buyer-name")) or [None])[0], level=level_ef(bl),
                        cpv=cpv[:8], ctype={"works": "works", "supplies": "supplies", "services": "services"}.get(ctype, ctype),
                        n_tenders=nt, source="eforms", nuts=(r.get("place-of-performance") or [None])[0])
            wc = r.get("winner-country") or []
            if not wins:
                rows.append({**base, "value": v, "winner": None, "winner_country": None})
            for i, w in enumerate(wins):
                rows.append({**base, "value": v / len(wins) if v else None, "winner": norm_firm(w),
                             "winner_country": wc[i] if i < len(wc) else None})
    return pd.DataFrame(rows)

def topshare(s, n):
    s = s.sort_values(ascending=False); return float(s.head(n).sum() / s.sum())

def main(site=None):
    leg = load_legacy()
    keys = set(zip(leg.pub_no, leg.pub_year))
    ef = load_eforms(keys)
    d = pd.concat([leg, ef], ignore_index=True)
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    d["pubd"] = pd.to_datetime(d["pub"], errors="coerce")
    # award year: conclusion date if plausible, else publication date
    ok = d.date.notna() & (d.date <= d.pubd) & (d.date >= d.pubd - pd.Timedelta(days=730))
    d["adate"] = d.date.where(ok, d.pubd)
    d["year"] = d.adate.dt.year; d["q"] = d.adate.dt.to_period("Q").astype(str)
    d = d[(d.year >= 2016) & (d.year <= 2025)]
    d["cpv2"] = d.cpv.str[:2]
    (ROOT / "output").mkdir(exist_ok=True)
    d.to_parquet(ROOT / "output/bigg_ted_awards.parquet")
    res = {"_meta": {"source": "TED (Publications Office of the EU), contract award notices with buyer in Germany",
                     "years": [2016, 2025], "n_rows": int(len(d)), "n_notices": int(d.drop_duplicates(["pub_no", "pub_year"]).shape[0])}}
    yrs = sorted(d.year.unique())
    # coverage
    cov = []
    for y in yrs:
        x = d[d.year == y]; nn = x.drop_duplicates(["pub_no", "pub_year"])
        cov.append(dict(year=int(y), notices=int(len(nn)), awards=int(len(x)), value_bn=round(x.value.sum() / 1e9, 1),
                        share_with_value=round(x.value.notna().mean(), 3), share_with_winner=round(x.winner.notna().mean(), 3),
                        share_with_bids=round(x.n_tenders.notna().mean(), 3)))
    res["coverage"] = cov
    # F1 volatility by buyer level (quarterly, value-weighted)
    qv = d.pivot_table(index="q", columns="level", values="value", aggfunc="sum").fillna(0)
    qv = qv[(qv.index >= "2017Q1") & (qv.index <= "2025Q2")]
    tot = qv.sum(axis=1)
    yoy = qv.diff(4).dropna(); ytot = yoy.sum(axis=1)
    lev = {}
    for c in qv.columns:
        lev[c] = dict(share=round(float(qv[c].sum() / tot.sum()), 3),
                      var_share=round(float(np.cov(yoy[c], ytot)[0, 1] / np.var(ytot, ddof=1)), 3),
                      cv_yoy=round(float((qv[c].pct_change(4).replace([np.inf, -np.inf], np.nan)).std()), 3))
    res["f1_levels"] = lev
    res["f1_quarterly"] = {"q": list(qv.index), **{c: [round(v / 1e9, 2) for v in qv[c]] for c in qv.columns}}
    # F2 granularity
    w = d[d.winner.notna() & d.value.notna()]
    f2 = []
    for y in yrs:
        x = w[w.year == y]; fs = x.groupby("winner").value.sum(); cs = x.groupby(["pub_no", "pub_year", "winner"]).value.sum()
        if len(fs) < 100: continue
        f2.append(dict(year=int(y), firms=int(len(fs)), top10=round(topshare(fs, 10), 3), top100=round(topshare(fs, 100), 3),
                       top1pct_firms=round(topshare(fs, max(1, len(fs) // 100)), 3),
                       top1pct_awards=round(topshare(cs, max(1, len(cs) // 100)), 3),
                       hhi=round(float(((fs / fs.sum()) ** 2).sum()), 4)))
    res["f2_concentration"] = f2
    # granular contribution: share of annual change in total explained by the 100 largest firms' changes
    fy = w.pivot_table(index="winner", columns="year", values="value", aggfunc="sum").fillna(0)
    gran = []
    for a, b in zip(yrs[:-1], yrs[1:]):
        if a not in fy or b not in fy: continue
        dlt = fy[b] - fy[a]; big = (fy[a] + fy[b]).sort_values(ascending=False).head(100).index
        gran.append(dict(year=int(b), change_bn=round(dlt.sum() / 1e9, 1), top100_change_bn=round(dlt[big].sum() / 1e9, 1),
                         abs_share_top100=round(float(dlt[big].abs().sum() / dlt.abs().sum()), 3)))
    res["f2_granular"] = gran
    # F3 competition
    t = d.drop_duplicates(["pub_no", "pub_year", "cpv", "n_tenders", "value"])
    t = t[t.n_tenders.notna()]
    f3 = []
    for y in yrs:
        x = t[t.year == y]
        if len(x) < 100: continue
        f3.append(dict(year=int(y), n=int(len(x)), median_bids=float(x.n_tenders.median()),
                       single_bid=round(float((x.n_tenders == 1).mean()), 3),
                       single_bid_value=round(float(x.loc[x.n_tenders == 1, "value"].sum() / x.value.sum()), 3)))
    res["f3_competition"] = f3
    res["f3_by_type"] = {c: dict(median_bids=float(g.n_tenders.median()), single_bid=round(float((g.n_tenders == 1).mean()), 3), n=int(len(g)))
                         for c, g in t.groupby("ctype") if c in ("works", "supplies", "services")}
    res["f3_by_level"] = {c: dict(median_bids=float(g.n_tenders.median()), single_bid=round(float((g.n_tenders == 1).mean()), 3), n=int(len(g)))
                          for c, g in t.groupby("level")}
    # F4 persistence of suppliers
    f4 = []
    firms_by_year = {y: set(w.loc[w.year == y, "winner"]) for y in yrs}
    pairs_by_year = {y: set(zip(w.loc[w.year == y, "buyer"], w.loc[w.year == y, "winner"])) for y in yrs}
    for i, y in enumerate(yrs):
        if i < 1: continue
        x = w[w.year == y]
        prev = set().union(*[firms_by_year[z] for z in yrs[max(0, i - 3):i]])
        prevp = set().union(*[pairs_by_year[z] for z in yrs[max(0, i - 3):i]])
        inc = x.winner.isin(prev); incp = pd.Series(list(zip(x.buyer, x.winner)), index=x.index).isin(prevp)
        f4.append(dict(year=int(y), lookback=min(3, i), value_incumbent_firm=round(float(x.loc[inc, "value"].sum() / x.value.sum()), 3),
                       value_repeat_pair=round(float(x.loc[incp, "value"].sum() / x.value.sum()), 3),
                       awards_incumbent_firm=round(float(inc.mean()), 3)))
    res["f4_persistence"] = f4
    # F5 composition
    v = d[d.value.notna()]
    res["f5_type"] = {c: round(float(g.value.sum() / v.value.sum()), 3) for c, g in v.groupby("ctype") if c}
    top = v.groupby("cpv2").value.sum().sort_values(ascending=False)
    res["f5_cpv2"] = [dict(cpv2=k, de=CPV2.get(k, (k, k))[0], en=CPV2.get(k, (k, k))[1], share=round(float(s / v.value.sum()), 3)) for k, s in top.head(15).items()]
    res["foreign_winners"] = {int(y): round(float(g.loc[g.winner_country.notna() & ~g.winner_country.isin(["DE", "DEU"]), "value"].sum() / g.loc[g.winner_country.notna(), "value"].sum()), 3)
                              for y, g in w.groupby("year")}
    def clean(o):
        if isinstance(o, dict): return {str(k): clean(x) for k, x in o.items()}
        if isinstance(o, list): return [clean(x) for x in o]
        if isinstance(o, float): return None if math.isnan(o) else o
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return None if np.isnan(o) else float(o)
        return o
    res = clean(res)
    json.dump(res, open(ROOT / "output/bigg_ted.json", "w"), indent=1, ensure_ascii=False)
    if site:
        json.dump(res, open(Path(site) / "bigg_ted.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({k: res[k] for k in ("coverage", "f1_levels", "f2_concentration", "f3_competition", "f4_persistence")}, indent=0)[:4000])

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
