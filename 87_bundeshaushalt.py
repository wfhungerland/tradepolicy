"""Federal budget by function (Funktionenplan), for the site tab "Staatsausgaben".

Inputs (folder given as argument, on the server X:\\Haushalt):
  HH_<year>_ALL.csv  budget (Soll; HH_<year>_RegE_ALL.csv = government draft) by title with function code, bundeshaushalt.de download,
                     amounts in 1,000 EUR; chapters "Anlage ..." are the business plans of special
                     funds and the EU own resources and are kept apart from the core budget
  HR<year>.xlsx      budget outturn (Ist) by title, Haushaltsrechnung, EUR
  Gesamtplan und Uebersichten.pdf  function names (Funktionenübersicht), read with pdftotext
Function codes: 1 digit main function, 2 digits upper function, 3 digits function.

Usage: python 87_bundeshaushalt.py <input_dir> [site_data_dir]
"""
import csv, json, re, subprocess, sys, warnings
from collections import defaultdict
from pathlib import Path
import openpyxl

warnings.filterwarnings("ignore")
HAUPT_SHORT = {"0": "Allgemeine Dienste", "1": "Bildung, Forschung, Kultur", "2": "Soziale Sicherung, Familie, Arbeitsmarkt",
               "3": "Gesundheit, Umwelt, Sport", "4": "Wohnen, Städtebau, Raumordnung", "5": "Ernährung, Landwirtschaft",
               "6": "Energie, Wasser, Gewerbe", "7": "Verkehr, Nachrichtenwesen", "8": "Finanzwirtschaft"}
# Upper functions that the function plan defines as one range (11-12, 18-19): drawn as one block
MERGE = {"12": "11", "19": "18"}
# Outdated or very long names of the function plan, replaced for display
RENAME = {"251": "Bürgergeld nach dem SGB II (bis 2022 Arbeitslosengeld II)",
          "259": "Sonstige Leistungen der Grundsicherung nach dem SGB II",
          "018": "Versorgung und Beihilfen (ohne Bundeswehr und Finanzverwaltung)",
          "038": "Versorgung und Beihilfen, Bundeswehrverwaltung",
          "039": "Versorgung und Beihilfen der Soldatinnen und Soldaten",
          "068": "Versorgung und Beihilfen, Finanzverwaltung",
          "033": "Lasten durch ausländische Streitkräfte",
          "114": "Weiterführende allgemeinbildende Schulen",
          "14": "Förderung von Schülern, Studierenden und Weiterbildung",
          "16": "Forschung und Entwicklung außerhalb der Hochschulen",
          "167": "Internationale Forschungsorganisationen",
          "22": "Sozialversicherung einschließlich Arbeitslosenversicherung",
          "23": "Familienhilfe, Wohlfahrtspflege",
          "24": "Soziale Entschädigung, Folgen von Krieg und politischen Ereignissen",
          "249": "Sonstige Folgen von Krieg und politischen Ereignissen",
          "26": "Kinder- und Jugendhilfe (ohne Kindertagesbetreuung)",
          "28": "Sozialhilfe, Asylbewerberleistungen, Eingliederungshilfe"}

def labels(pdf):
    """Function names from the Funktionenübersicht: code, name (possibly over several lines), then amounts."""
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    part = txt[txt.find("Gliederung der Einnahmen und Ausgaben nach Funktionen"):]
    part = part[:part.find("Teil III")] if "Teil III" in part else part
    out, cur, buf = {}, None, ""
    def close(code, text):
        name = re.split(r"\.{2,}|\s{3,}[\d-]", text)[0].strip().rstrip(".").strip()
        name = re.sub(r"(\w)- (?!und\b|oder\b|sowie\b)([a-zäöü])", r"\1\2", re.sub(r"\s+", " ", name))  # undo line-break hyphens only
        codes = [str(c) for c in range(int(code.split("-")[0]), int(code.split("-")[1]) + 1)] if "-" in code else [code]
        for c in codes: out.setdefault(c, name)
    for line in part.splitlines():
        m = re.match(r"^\s{0,12}(\d{1,3}(?:-\d{2})?)\s+([A-ZÄÖÜa-zäöü].*)$", line)
        if m:
            cur, buf = m.group(1), m.group(2)
        elif cur and re.match(r"^\s{6,}\S", line):
            buf += " " + line.strip()
        else:
            continue
        if re.search(r"\.{2,}|\s{3,}[\d-]", buf):
            close(cur, buf); cur, buf = None, ""
    return out

# Special funds (Sondervermögen) whose spending the site can add to the core budget. Other "Anlage"
# chapters stay out: EU own resources (6090) and EU market funds (1090) pass through, the NATO
# programme (1490) and the agency budgets of BfR and BLE (1091, 1092) are financed from the core budget.
FUNDS = {"1491": "Sondervermögen Bundeswehr", "6092": "Klima- und Transformationsfonds",
         "6093": "Sondervermögen Infrastruktur und Klimaneutralität", "6097": "Sondervermögen Digitale Infrastruktur",
         "6098": "Sondervermögen Aufbauhilfe 2021", "6095": "Sondervermögen Aufbauhilfe",
         "1790": "Sondervermögen Kinderbetreuungsausbau", "1791": "Sondervermögen Ganztagsausbau",
         "6096": "Kommunalinvestitionsförderungsfonds", "6091": "Investitions- und Tilgungsfonds",
         "6094": "Mauergrundstücksfonds"}
# Versorgungsrücklage and Versorgungsfonds (0690, 0691) invest pension reserves; their outflows are
# purchases of securities, not spending, and stay out like the core-budget payments into them.
# payments from the core budget or one fund to another fund: dropped when funds are added (no double counting)
TRANSFER = re.compile(r"Zuweisung\w* an (das Sondervermögen|den Klima- und Transformationsfonds)", re.I)

def read_soll(path):
    with open(path, encoding="utf-8-sig") as f:
        r = csv.reader(f, delimiter=";"); head = [h.strip() for h in next(r)]
        rows = [dict(zip(head, x[:len(head)])) for x in r]
    return [x for x in rows if x["einahmen-ausgaben"] == "A"]

def main(src, site=None):
    src = Path(src)
    lab = {}
    for pdf in sorted(src.glob("Gesamtplan*.pdf")) + sorted(src.glob("Vorspann*.pdf")):
        if pdf.stat().st_size > 100000:
            for k, v in labels(pdf).items(): lab.setdefault(k, v)
    soll, fmap, special, spkap = {}, {}, {}, set()
    funds, transfer, trf = {}, {}, {}  # funds[y][kapitel][function]; transfer[y][function] = core-budget payments to funds
    draft = set()
    for y in range(2024, 2031):
        p = src / f"HH_{y}_ALL.csv"
        if not p.exists():
            p = src / f"HH_{y}_RegE_ALL.csv"  # government draft (Regierungsentwurf)
            if not p.exists(): continue
            draft.add(y)
        rows = read_soll(p)
        core = defaultdict(float); sv = defaultdict(float)
        fd = defaultdict(lambda: defaultdict(float)); tr = defaultdict(float)
        for x in rows:
            v = float(x["soll"] or 0) / 1e6  # 1,000 EUR -> bn EUR
            fmap.setdefault(y, {})[(x["kapitel"], x["titel"])] = x["funktion"]
            sp = x["kapitel-text"].startswith("Anlage")
            if sp: spkap.add(x["kapitel"])
            (sv if sp else core)[x["funktion"]] += v
            if TRANSFER.search(x["titel-text"]):
                if not sp: tr[x["funktion"]] += v
                elif x["kapitel"] in FUNDS: trf[y] = trf.get(y, 0) + v
            elif x["kapitel"] in FUNDS: fd[x["kapitel"]][x["funktion"]] += v
        soll[y] = core; special[y] = sv; funds[y] = fd; transfer[y] = tr
    ist, unmatched = {}, {}
    for y in (2024, 2025, 2026):
        p = src / f"HR{y}.xlsx"
        if not p.exists(): continue
        ws = openpyxl.load_workbook(p).worksheets[0]
        agg = defaultdict(float); agg_sp = defaultdict(float); miss = 0.0; tot = 0.0
        fd = defaultdict(lambda: defaultdict(float)); tr = defaultdict(float); trf[y] = 0.0  # outturn replaces plan
        for e, k, t, z, v, _ in ws.iter_rows(min_row=2, values_only=True):
            if not t or v is None or not str(t).strip(): continue
            t = int(float(t))
            if t // 10000 < 4: continue  # titles of group 0-3 are revenue
            key = (f"{int(float(e)):02d}{int(float(k)):02d}", f"{t:05d}")
            fn = fmap.get(y, {}).get(key) or next((fmap[z2][key] for z2 in sorted(fmap) if key in fmap[z2]), None)
            v = float(v) / 1e9
            isTr = bool(TRANSFER.search(str(z or "")))
            if key[0] in spkap and key[0] in FUNDS and isTr: trf[y] = trf.get(y, 0) + v
            if key[0] in spkap:  # special funds, EU own resources: kept apart
                if fn: agg_sp[fn] += v
                if fn and key[0] in FUNDS and not isTr: fd[key[0]][fn] += v
                continue
            if fn and isTr: tr[fn] += v
            tot += v
            if fn: agg[fn] += v
            else: miss += v
        ist[y] = agg; unmatched[y] = (miss, tot); special[y] = agg_sp; funds[y] = fd; transfer[y] = tr
    years = sorted(set(ist) | set(soll))
    out = {"_meta": {"source": "bundeshaushalt.de (Haushaltsplan, Haushaltsrechnung)", "unit": "bn EUR"},
           "years": [], "labels": {}, "haupt_short": HAUPT_SHORT, "merge": MERGE, "fund_names": FUNDS}
    for y in years:
        kind = "Ist" if y in ist else ("Entwurf" if y in draft else "Soll")
        vals = ist[y] if y in ist else soll[y]
        out["years"].append({"year": y, "kind": kind, "values": {k: round(v, 4) for k, v in sorted(vals.items()) if abs(v) > 1e-4},
                             "special": {k: round(v, 4) for k, v in sorted(special.get(y, {}).items()) if abs(v) > 1e-4},
                             "total": round(sum(vals.values()), 2), "special_total": round(sum(special.get(y, {}).values()), 2),
                             "funds": {k: {f: round(v, 4) for f, v in sorted(d.items()) if abs(v) > 1e-4} for k, d in sorted(funds.get(y, {}).items()) if sum(d.values()) > 1e-3},
                             "transfer": {k: round(v, 4) for k, v in sorted(transfer.get(y, {}).items()) if abs(v) > 1e-4}})
        if y in unmatched:
            m, t = unmatched[y]; print(y, kind, f"total {t:.1f} bn, without function {m:.2f} bn ({100*m/t:.2f} %)")
        else:
            pass
        print(y, kind, f"core {sum(vals.values()):.1f} bn; special funds and EU own resources {sum(special.get(y, {}).values()):.1f} bn")
    codes = {c for yy in out["years"] for c in yy["values"]} | {c for yy in out["years"] for c in yy["special"]}
    for yy in out["years"]:
        fsum = sum(v for d in yy["funds"].values() for v in d.values()); tsum = sum(yy["transfer"].values())
        yy["funds_total"] = round(fsum, 2); yy["transfer_total"] = round(tsum, 2); yy["transfer_funds"] = round(trf.get(yy["year"], 0), 2)
        print(yy["year"], "special funds", {k: round(sum(d.values()), 1) for k, d in yy["funds"].items()}, "transfers to funds", round(tsum, 2))
    need = codes | {c[:2] for c in codes} | {c[:1] for c in codes}
    out["labels"] = {c: RENAME.get(c) or lab.get(c) or lab.get(c[:2]) or lab.get(c[:1]) or c for c in sorted(need)}
    missing = [c for c in sorted(need) if not lab.get(c)]
    print("labels missing:", missing)
    txt = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    assert "NaN" not in txt
    Path("output").mkdir(exist_ok=True); open("output/bund.json", "w").write(txt)
    if site: open(Path(site) / "bund.json", "w").write(txt)
    y0 = out["years"][-1]
    top = sorted(y0["values"].items(), key=lambda x: -x[1])[:8]
    print("largest functions", y0["year"], [(c, out["labels"][c][:30], round(v, 1)) for c, v in top])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
