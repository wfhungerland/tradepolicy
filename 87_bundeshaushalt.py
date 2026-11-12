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

def labels(pdf, part="fn"):
    """Names from an overview of the budget: code, name (possibly over several lines), then amounts.
    part "fn": Funktionenübersicht; part "grp": Gruppierungsübersicht (expenditure groups 4-9).
    Returns names by code and merges: codes of a two-digit range such as 11-12 or 51-54 -> first code."""
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    if part == "fn":
        part = txt[txt.find("Gliederung der Einnahmen und Ausgaben nach Funktionen"):]
        part = part[:part.find("Teil III")] if "Teil III" in part else part
    else:
        hits = [m.start() for m in re.finditer(r"Teil I:\s+Gruppierungsübersicht", txt)]
        if len(hits) < 2: return {}, {}
        part = txt[hits[1]:]
        part = part[part.find("Personalausgaben") - 40:]
        end = part.find("ökonomischen Arten)")
        part = part[:end] if end > 0 else part
    out, merges, cur, buf = {}, {}, None, ""
    def close(code, text):
        name = re.split(r"\.{2,}|\s{3,}[\d-]", text)[0].strip().rstrip(".").strip()
        name = re.sub(r"(\w)[-\u00ad] (?!und\b|oder\b|sowie\b)([a-zäöü])", r"\1\2", re.sub(r"\s+", " ", name))  # undo line-break hyphens only
        name = name.replace("\u00ad", "")
        if "-" in code:
            a, b = code.split("-")
            codes = [str(c).zfill(len(a)) for c in range(int(a), int(b) + 1)]
            if len(a) == 2:
                for c in codes[1:]: merges.setdefault(c, codes[0])
        else:
            codes = [code]
        for c in codes: out.setdefault(c, name)
    for line in part.splitlines():
        m = re.match(r"^\s{0,12}(\d{1,3}(?:-\d{2,3})?)\s+([A-ZÄÖÜa-zäöü].*)$", line)
        if m:
            cur, buf = m.group(1), m.group(2)
        elif cur and re.match(r"^\s{6,}\S", line):
            buf += " " + line.strip()
        else:
            continue
        if re.search(r"\.{2,}|\s{3,}[\d-]", buf):
            close(cur, buf); cur, buf = None, ""
    return out, merges

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

GRP_SHORT = {"4": "Personal", "5": "Sachausgaben, militärische Beschaffung, Zinsen", "6": "Zuweisungen und Zuschüsse (ohne Investitionen)",
             "7": "Baumaßnahmen", "8": "Sonstige Investitionen und Investitionsförderung", "9": "Besondere Finanzierungsausgaben"}
GRP_RENAME = {"57": "Zinsen am Kreditmarkt", "681": "Renten und sonstige Geldleistungen an Personen", "688": "Abführung der Eigenmittel an die EU",
              "636": "Zuweisungen an die Sozialversicherung und die Bundesagentur für Arbeit", "55": "Militärische Beschaffungen, Materialerhaltung, Wehrforschung",
              "45": "Sonstige personalbezogene Ausgaben", "51": "Sächliche Verwaltungsausgaben",
              "56": "Zinsausgaben an öffentlichen Bereich", "58": "Tilgungsausgaben an öffentlichen Bereich",
              "61": "Allgemeine Zuweisungen an öffentlichen Bereich"}
VIEWS = {"fn": "Funktion", "grp": "Ausgabenart", "epl": "Ressort"}

def short_epl(t):
    """Ministry without the common prefix: "Bundesministerium für Arbeit und Soziales" -> "Arbeit und Soziales"."""
    m = re.match(r"^Bundesministerium (?:für |der |des )?(.*)$", t)
    if not m: return t
    r = m.group(1).replace(" und für ", " und ")
    return {"Innern": "Inneres"}.get(r, r[0].upper() + r[1:])

def clean(t):
    t = re.sub(r'"+', '', t or "").strip()
    return re.sub(r"\s*\(\d{4}\)$", "", t)

def main(src, site=None):
    src = Path(src)
    lab, glab, gmerge, fmerge = {}, {}, {}, {}
    for pdf in sorted(src.glob("Gesamtplan*.pdf")) + sorted(src.glob("Vorspann*.pdf")):
        if pdf.stat().st_size > 100000:
            a, m = labels(pdf, "fn")
            for k, v in a.items(): lab.setdefault(k, v)
            fmerge.update(m)
            a, m = labels(pdf, "grp")
            for k, v in a.items(): glab.setdefault(k, v)
            gmerge.update(m)
    fmerge = fmerge or MERGE
    # records per year: kapitel, titel, function, value (bn EUR), category
    #   core, fund (special fund in FUNDS), tcore (core payment to a fund), tfund (payment between funds), other (other "Anlage")
    rec, kinds, fmap, eplname, kapname, spkap = {}, {}, {}, {}, {}, set()
    for y in range(2024, 2031):
        p = src / f"HH_{y}_ALL.csv"
        kinds[y] = "Soll"
        if not p.exists():
            p = src / f"HH_{y}_RegE_ALL.csv"  # government draft (Regierungsentwurf)
            if not p.exists(): kinds.pop(y); continue
            kinds[y] = "Entwurf"
        rows = read_soll(p); r = []
        for x in rows:
            k, t, fn = x["kapitel"], x["titel"], x["funktion"]
            fmap.setdefault(y, {})[(k, t)] = fn
            eplname[k[:2]] = x["einzelplan-text"].strip(); kapname[k] = clean(x["kapitel-text"])
            sp = x["kapitel-text"].startswith("Anlage")
            if sp: spkap.add(k)
            tr = bool(TRANSFER.search(x["titel-text"]))
            cat = ("tfund" if tr else "fund") if k in FUNDS else ("other" if sp else ("tcore" if tr else "core"))
            r.append((k, t, fn, float(x["soll"] or 0) / 1e6, cat))
        rec[y] = r
    unmatched = {}
    for y in (2024, 2025, 2026):
        p = src / f"HR{y}.xlsx"
        if not p.exists(): continue
        ws = openpyxl.load_workbook(p).worksheets[0]
        r, miss, tot = [], 0.0, 0.0
        for e, k, t, z, v, _ in ws.iter_rows(min_row=2, values_only=True):
            if not t or v is None or not str(t).strip(): continue
            t = int(float(t))
            if t // 10000 < 4: continue  # titles of group 0-3 are revenue
            key = (f"{int(float(e)):02d}{int(float(k)):02d}", f"{t:05d}")
            fn = fmap.get(y, {}).get(key) or next((fmap[z2][key] for z2 in sorted(fmap) if key in fmap[z2]), None)
            v = float(v) / 1e9
            tr = bool(TRANSFER.search(str(z or "")))
            kk = key[0]
            cat = ("tfund" if tr else "fund") if kk in FUNDS else ("other" if kk in spkap else ("tcore" if tr else "core"))
            if cat in ("core", "tcore"):
                tot += v
                if not fn: miss += v
            r.append((kk, key[1], fn or "999", v, cat))
        rec[y] = r; kinds[y] = "Ist"; unmatched[y] = (miss, tot)
    # one aggregation per view
    def code(view, k, t, fn):
        return fn if view == "fn" else (t[:3] if view == "grp" else k)
    out = {"_meta": {"source": "bundeshaushalt.de (Haushaltsplan, Haushaltsrechnung)", "unit": "bn EUR"},
           "fund_names": FUNDS, "views": {}, "years": []}
    used = {v: set() for v in VIEWS}
    for y in sorted(rec):
        has_f = any(c == "fund" for *_, c in rec[y])
        Y = {"year": y, "kind": kinds[y], "v": {}, "alt": {} if has_f else None, "part": {} if has_f else None}
        for view in VIEWS:
            core, alt, part = defaultdict(float), defaultdict(float), defaultdict(float)
            for k, t, fn, v, c in rec[y]:
                cd = code(view, k, t, fn)
                if c in ("core", "tcore"): core[cd] += v
                if c in ("core", "fund"): alt[cd] += v
                if c == "fund": part[cd] += v
            r4 = lambda d: {a: round(b, 4) for a, b in sorted(d.items()) if abs(b) > 1e-4}
            Y["v"][view] = r4(core); used[view] |= set(core)
            if has_f:
                Y["alt"][view] = r4(alt); Y["part"][view] = r4(part); used[view] |= set(alt)
        tot = lambda cats: round(sum(v for *_, v, c in rec[y] if c in cats), 2)
        Y.update(total=tot(("core", "tcore")), special_total=tot(("fund", "tfund", "other")),
                 funds_total=tot(("fund",)) if has_f else 0, netted=round(tot(("tcore",)) + tot(("tfund",)), 2) if has_f else 0,
                 negative=round(sum(v for v in Y["v"]["fn"].values() if v < 0), 2),
                 funds={FUNDS[k]: round(s_, 2) for k in FUNDS if (s_ := sum(v for kk, _, _, v, c in rec[y] if kk == k and c == "fund")) >= 0.05} if has_f else {})
        out["years"].append(Y)
        if y in unmatched:
            m, t_ = unmatched[y]; print(y, Y["kind"], f"total {t_:.1f} bn, without function {m:.2f} bn ({100*m/t_:.2f} %)")
        print(y, Y["kind"], f"core {Y['total']:.1f} bn; special funds {Y['funds_total']:.1f} bn; netted {Y['netted']:.1f} bn; all Anlage chapters {Y['special_total']:.1f} bn")
    # trees: parent and labels per view
    fnp, fnl = {}, {}
    for c in used["fn"]:
        up = fmerge.get(c[:2], c[:2]); fnp[c], fnp[up], fnp[c[0]] = up, c[0], ""
    for c in fnp:
        fnl[c] = HAUPT_SHORT.get(c) if len(c) == 1 else (RENAME.get(c) or lab.get(c) or lab.get(c[:2]) or lab.get(c[:1]) or c)
    fnl["999"] = "ohne Zuordnung"; fnp["999"] = "99"; fnp["99"] = "9"; fnp["9"] = ""; fnl["99"] = fnl["9"] = "ohne Zuordnung"
    gp, gl = {}, {}
    for c in used["grp"]:
        up = gmerge.get(c[:2], c[:2]); gp[c], gp[up], gp[c[0]] = up, c[0], ""
    for c in gp:
        gl[c] = GRP_SHORT.get(c) if len(c) == 1 else (GRP_RENAME.get(c) or glab.get(c) or (glab.get(gp[c]) or GRP_RENAME.get(gp[c]) or GRP_SHORT.get(c[0], c)) + f" (Gruppe {c})" * (len(c) == 3))
    ep, el = {}, {}
    for c in used["epl"]:
        ep[c], ep[c[:2]] = c[:2], ""
    for c in ep:
        el[c] = short_epl(eplname.get(c, c)) if len(c) == 2 else (FUNDS.get(c) or kapname.get(c, c))
    out["views"] = {"fn": {"label": VIEWS["fn"], "parent": fnp, "labels": fnl},
                    "grp": {"label": VIEWS["grp"], "parent": gp, "labels": gl},
                    "epl": {"label": VIEWS["epl"], "parent": ep, "labels": el}}
    print("group names missing:", sorted(c for c in gp if len(c) > 1 and not glab.get(c) and c not in GRP_RENAME))
    print("function names missing:", sorted(c for c in fnp if len(c) > 1 and not lab.get(c) and c not in RENAME))
    txt = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    assert "NaN" not in txt
    Path("output").mkdir(exist_ok=True); open("output/bund.json", "w").write(txt)
    if site: open(Path(site) / "bund.json", "w").write(txt)
    y0 = out["years"][-1]
    for view in VIEWS:
        top = sorted(y0["v"][view].items(), key=lambda x: -x[1])[:6]
        print(view, y0["year"], [(c, out["views"][view]["labels"].get(c, c)[:28], round(v, 1)) for c, v in top])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
