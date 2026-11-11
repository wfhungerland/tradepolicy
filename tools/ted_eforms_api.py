"""Download German eForms result notices (late 2023 onwards) from the TED search API.

Usage: python tools/ted_eforms_api.py 2023 2025 data/ted_eforms
Writes one JSON file per year with the raw API records.
"""
import sys, os, json, time, urllib.request

FIELDS = ["publication-number", "publication-date", "notice-type", "procedure-type",
          "buyer-name", "buyer-legal-type", "buyer-city", "place-of-performance",
          "classification-cpv", "contract-nature", "total-value", "total-value-cur",
          "result-value-notice", "winner-name", "winner-identifier", "winner-country",
          "winner-size", "received-submissions-type-val", "contract-duration-period-lot",
          "contract-conclusion-date"]
URL = "https://api.ted.europa.eu/v3/notices/search"

def post(body):
    for a in range(6):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            if e.code == 400: raise RuntimeError(e.read()[:400])
            err = e
        except Exception as e:
            err = e
        time.sleep(5 * (a + 1))
    raise err

def year(y, outdir, fields):
    path = os.path.join(outdir, f"{y}.json")
    if os.path.exists(path): return
    q = (f"buyer-country=DEU AND form-type=result AND publication-date>={y}0101 "
         f"AND publication-date<{y+1}0101")
    tok, out = None, []
    while True:
        b = {"query": q, "fields": fields, "limit": 250, "paginationMode": "ITERATION"}
        if tok: b["iterationNextToken"] = tok
        r = post(b); out += r["notices"]; tok = r.get("iterationNextToken")
        if not tok or not r["notices"]: break
    # keep eForms notices only; legacy ones come from the monthly packages
    out = [x for x in out if x.get("notice-type") not in (None, [], "")]
    json.dump(out, open(path, "w"), ensure_ascii=False); print(y, len(out), flush=True)

if __name__ == "__main__":
    a, b, outdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    fields = list(FIELDS)
    # drop fields the API rejects
    while True:
        try:
            post({"query": "buyer-country=DEU AND form-type=result AND publication-date>=20240102 AND publication-date<20240103",
                  "fields": fields, "limit": 1, "page": 1, "paginationMode": "PAGE_NUMBER"}); break
        except RuntimeError as e:
            bad = [f for f in fields if f"'{f}'" in str(e) or f in str(e).split("supported")[0]]
            if not bad: raise
            print("drop", bad); fields = [f for f in fields if f not in bad]
    for y in range(a, b + 1): year(y, outdir, fields)
