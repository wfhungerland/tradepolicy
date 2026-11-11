"""Stream TED monthly XML packages and keep German contract award notices.

Legacy TED notices (before eForms, ~2016-2023) do not expose winners or bid
counts through the search API, so we read the monthly bulk packages
(https://ted.europa.eu/packages/monthly/YYYY-MM), stream them without saving,
and write one JSON line per award (lot) for buyers located in Germany.

Usage: python tools/ted_legacy_packages.py 2016-01 2023-12 data/ted_legacy
"""
import sys, os, json, tarfile, re, urllib.request, time
import xml.etree.ElementTree as ET

def months(a, b):
    y, m = map(int, a.split("-")); y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield f"{y}-{m:02d}"; m += 1
        if m == 13: y, m = y + 1, 1

def strip(tag): return tag.rsplit("}", 1)[-1]

def first(el, name):
    for e in el.iter():
        if strip(e.tag) == name: return e
    return None

def _oc(form):
    oc = first(form, "OBJECT_CONTRACT")
    return oc if oc is not None else form

def text(e): return (e.text or "").strip() if e is not None else None

def _date(el):
    if el is None: return None
    d = {strip(e.tag): text(e) for e in el}
    try: return f"{d['YEAR']}-{int(d['MONTH']):02d}-{int(d['DAY']):02d}"
    except Exception: return None

def _cost(el):
    """VALUE_COST inside a COSTS_RANGE_AND_CURRENCY... block (old R2.0.8 schema)."""
    if el is None: return None, None
    for c in el.iter():
        if strip(c.tag).startswith("COSTS_RANGE_AND_CURRENCY"):
            v = first(c, "VALUE_COST")
            if v is not None:
                return (v.get("FMTVAL") or text(v).replace(" ", "")), c.get("CURRENCY")
    return None, None

def parse_old(form, nd, pub):
    """Old standard forms (R2.0.8, CONTRACT_AWARD*, until about 2017)."""
    ca = first(form, "NAME_ADDRESSES_CONTACT_CONTRACT_AWARD")
    if ca is None: ca = first(form, "CONTRACTING_AUTHORITY_INFORMATION_CONTRACT_AWARD")
    buyer = text(first(ca, "OFFICIALNAME")) if ca is not None else None
    t = first(form, "TYPE_OF_CONTRACTING_AUTHORITY")
    catype = t.get("VALUE") if t is not None else None
    cpvel = first(form, "CPV_MAIN"); cpv = first(cpvel, "CPV_CODE") if cpvel is not None else None
    cpv = cpv.get("CODE") if cpv is not None else None
    fd = next((e for e in form if strip(e.tag).startswith("FD_")), None)
    ctype = fd.get("CTYPE") if fd is not None else None
    nuts = first(form, "NUTS"); nuts = nuts.get("CODE") if nuts is not None else None
    tv, tcur = _cost(first(form, "TOTAL_FINAL_VALUE"))
    out = []
    for aw in form.iter():
        if strip(aw.tag) != "AWARD_OF_CONTRACT": continue
        v, cur = _cost(first(aw, "CONTRACT_VALUE_INFORMATION"))
        win = []
        for eo in aw.iter():
            if strip(eo.tag) == "ECONOMIC_OPERATOR_NAME_ADDRESS":
                c = first(eo, "COUNTRY")
                win.append({"name": text(first(eo, "OFFICIALNAME")), "id": text(first(eo, "NATIONALID")),
                            "town": text(first(eo, "TOWN")), "country": c.get("VALUE") if c is not None else None,
                            "sme": None})
        out.append({"nd": nd, "pub": pub, "form": strip(form.tag), "buyer": buyer, "buyer_nuts": nuts,
                    "ca_type": catype, "cpv": cpv, "ctype": ctype, "lot": text(first(aw, "LOT_NUMBER")),
                    "date_conclusion": _date(first(aw, "CONTRACT_AWARD_DATE")),
                    "n_tenders": text(first(aw, "OFFERS_RECEIVED_NUMBER")), "n_tenders_sme": None,
                    "value": v, "cur": cur, "winners": win})
    if not out:
        out.append({"nd": nd, "pub": pub, "form": strip(form.tag), "buyer": buyer, "buyer_nuts": nuts,
                    "ca_type": catype, "cpv": cpv, "ctype": ctype, "value": tv, "cur": tcur, "winners": []})
    if len(out) == 1 and out[0].get("value") is None and tv is not None:
        out[0]["value"], out[0]["cur"] = tv, tcur
    return out

def parse(raw):
    if b'<TD_DOCUMENT_TYPE CODE="7"' not in raw and b"CODE='7'" not in raw:
        return []
    root = ET.fromstring(raw)
    coded = first(root, "CODED_DATA_SECTION")
    if coded is None or text(first(coded, "ISO_COUNTRY")) is None: return []
    iso = first(coded, "ISO_COUNTRY").get("VALUE")
    if iso != "DE": return []
    nd = root.get("DOC_ID"); pub = text(first(coded, "DATE_PUB"))
    form = None
    for e in root.iter():
        t = strip(e.tag)
        if t.startswith("F0") or t.startswith("F1") or t.startswith("F2") or t.startswith("F15"):
            if e.get("LG") is not None or e.get("CATEGORY") == "ORIGINAL":
                form = e; break
    if form is None:
        form = next((e for e in root.iter() if strip(e.tag).startswith("CONTRACT_AWARD")
                     and e.get("CATEGORY") == "ORIGINAL"), None)
        if form is None:
            form = next((e for e in root.iter() if strip(e.tag).startswith("CONTRACT_AWARD") and e.get("LG")), None)
        if form is None: return []
        return parse_old(form, nd, pub)
    ca = first(form, "ADDRESS_CONTRACTING_BODY")
    buyer = text(first(ca, "OFFICIALNAME")) if ca is not None else None
    buyer_nuts = None
    if ca is not None:
        n = first(ca, "NUTS"); buyer_nuts = n.get("CODE") if n is not None else None
    catype = first(form, "CA_TYPE"); catype = catype.get("VALUE") if catype is not None else None
    cpv = first(_oc(form), "CPV_CODE")
    cpv = cpv.get("CODE") if cpv is not None else None
    ctype = first(form, "TYPE_CONTRACT"); ctype = ctype.get("CTYPE") if ctype is not None else None
    vt = first(_oc(form), "VAL_TOTAL")
    out = []
    for aw in form.iter():
        if strip(aw.tag) != "AWARD_CONTRACT": continue
        ac = first(aw, "AWARDED_CONTRACT")
        if ac is None: continue
        rec = {"nd": nd, "pub": pub, "form": strip(form.tag), "buyer": buyer,
               "buyer_nuts": buyer_nuts, "ca_type": catype, "cpv": cpv, "ctype": ctype,
               "lot": text(first(aw, "LOT_NO")),
               "date_conclusion": text(first(ac, "DATE_CONCLUSION_CONTRACT")),
               "n_tenders": text(first(ac, "NB_TENDERS_RECEIVED")),
               "n_tenders_sme": text(first(ac, "NB_TENDERS_RECEIVED_SME"))}
        v = first(ac, "VAL_TOTAL")
        rec["value"] = text(v); rec["cur"] = v.get("CURRENCY") if v is not None else None
        rec["winners"] = []
        for c in ac.iter():
            if strip(c.tag) == "CONTRACTOR":
                rec["winners"].append({"name": text(first(c, "OFFICIALNAME")),
                                       "id": text(first(c, "NATIONALID")),
                                       "town": text(first(c, "TOWN")),
                                       "country": (first(c, "COUNTRY").get("VALUE") if first(c, "COUNTRY") is not None else None),
                                       "sme": first(c, "SME") is not None})
        out.append(rec)
    if not out:
        out.append({"nd": nd, "pub": pub, "form": strip(form.tag), "buyer": buyer, "buyer_nuts": buyer_nuts,
                    "ca_type": catype, "cpv": cpv, "ctype": ctype, "value": text(vt),
                    "cur": vt.get("CURRENCY") if vt is not None else None, "winners": []})
    return out

def run_month(ym, outdir):
    path = os.path.join(outdir, f"{ym}.jsonl")
    if os.path.exists(path): return
    for a in range(5):
        try:
            resp = urllib.request.urlopen(f"https://ted.europa.eu/packages/monthly/{ym}", timeout=600)
            n = 0
            with tarfile.open(fileobj=resp, mode="r|gz") as tf, open(path + ".tmp", "w") as f:
                def members(t):
                    # some months hold daily .tar.gz packages instead of XML files
                    for m in t:
                        if not m.isfile(): continue
                        if m.name.endswith(".tar.gz"):
                            with tarfile.open(fileobj=t.extractfile(m), mode="r|gz") as inner:
                                yield from members(inner)
                        elif m.name.endswith(".xml"):
                            yield t.extractfile(m).read()
                for raw in members(tf):
                    try: recs = parse(raw)
                    except ET.ParseError: continue
                    for r in recs:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
            os.replace(path + ".tmp", path); print(ym, n, flush=True); return
        except Exception as e:
            print(ym, "retry", a, e, flush=True); time.sleep(20 * (a + 1))
    print(ym, "FAILED", flush=True)

if __name__ == "__main__":
    a, b, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    for ym in months(a, b): run_month(ym, outdir)
