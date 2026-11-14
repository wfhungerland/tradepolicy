"""Fetch district-level (Kreis) data on the user's own server and write compact files.

Runs on the Hetzner server (Python 3.10+, pandas). Two parts:

1. Marktstammdatenregister (MaStR, Bundesnetzagentur, Datenlizenz Deutschland 2.0):
   downloads the full export (about 3.3 GB), streams the unit XML files without unpacking
   them and aggregates electrical units to districts (first five digits of the municipal
   key): capacity in operation at the end of each year by energy source, plus counts.
   Output: mastr_kreis_jahr.csv (kreis, jahr, energietraeger, anzahl, brutto_mw).
   Storage units (batteries) are included as energy source "Speicher".

2. Regionaldatenbank Deutschland (GENESIS web service): needs a free account. Put the
   credentials into the environment variables GENESIS_USER and GENESIS_PASSWORD (or an API token
   into GENESIS_USER and leave GENESIS_PASSWORD empty) on the server; they never leave the server.
   With --search TERM the script lists matching tables; with --tables CODE ... it downloads
   each table for all districts as flat CSV (ffcsv).

Usage on the server:
  python3 server_fetch_kreise.py --out /srv/daten/claude-daten/kreise --mastr
  GENESIS_USER=... GENESIS_PASSWORD=... python3 server_fetch_kreise.py --search Auslandsumsatz
  GENESIS_USER=... GENESIS_PASSWORD=... python3 server_fetch_kreise.py --out /srv/daten/claude-daten/kreise --tables 42111-04-02-4 --start 1995
  Destatis GENESIS-Online (own account): add --destatis, e.g. --destatis --tables 51000-0032 51000-0034 --start 2008
"""
import argparse
import io
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

MASTR_PAGE = "https://www.marktstammdatenregister.de/MaStR/Datendownload"
RDB = "https://www.regionalstatistik.de/genesisws/rest/2020/"
DESTATIS = "https://genesis.destatis.de/genesisWS/rest/2020/"     # GENESIS-Online of Destatis (own account)
UNIT_FILES = re.compile(r"^Einheiten(Solar|Wind|Biomasse|Wasser|Verbrennung|Kernkraft|GeoSolarthermieGrubenKlaerschlammDruckentspannung|Stromspeicher)(_\d+)?\.xml$", re.IGNORECASE)
FIELDS = {"Gemeindeschluessel", "EinheitBetriebsstatus", "Inbetriebnahmedatum", "DatumEndgueltigeStilllegung",
          "Bruttoleistung", "Energietraeger"}


def latest_export_url():
    html = urllib.request.urlopen(urllib.request.Request(MASTR_PAGE, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read().decode("utf-8", "ignore")
    m = re.search(r'href="(https://download\.marktstammdatenregister\.de/Gesamtdatenexport_\d{8}_[\d.]+\.zip)"', html)
    if not m:
        sys.exit("export link not found on " + MASTR_PAGE)
    return m.group(1)


def download(url, target):
    if target.exists() and target.stat().st_size > 1e9:
        print("using existing", target)
        return
    print("downloading", url)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=600) as r, open(target, "wb") as f:
        while True:
            b = r.read(1 << 22)
            if not b:
                break
            f.write(b)


def catalog(z):
    """Energy-source codes -> names from Katalogwerte.xml."""
    names = {}
    name = next(n for n in z.namelist() if n.lower().startswith("katalogwerte"))
    for _, el in ET.iterparse(z.open(name)):
        if el.tag == "Katalogwert":
            i, w = el.findtext("Id"), el.findtext("Wert")
            if i and w:
                names[i] = w
            el.clear()
    return names


def mastr(out, work):
    zpath = work / "mastr_export.zip"
    download(latest_export_url(), zpath)
    agg = defaultdict(lambda: [0, 0.0])          # (kreis, energietraeger, start, end) -> [count, MW]
    with zipfile.ZipFile(zpath) as z:
        names = catalog(z)
        files = sorted(n for n in z.namelist() if UNIT_FILES.match(n))
        for fn in files:
            storage = "stromspeicher" in fn.lower()
            n = 0
            for _, el in ET.iterparse(z.open(fn)):
                # unit records: <EinheitSolar>, <EinheitWind>, ... with child fields; skip the
                # child fields themselves and the root <EinheitenSolar>
                if len(el) == 0 or not el.tag.startswith("Einheit") or el.tag.startswith("Einheiten"):
                    continue
                rec = {c.tag: c.text for c in el if c.tag in FIELDS}
                el.clear()
                g = rec.get("Gemeindeschluessel")
                if not g or not rec.get("Inbetriebnahmedatum"):
                    continue
                status = rec.get("EinheitBetriebsstatus")
                start = int(rec["Inbetriebnahmedatum"][:4])
                end = int(rec["DatumEndgueltigeStilllegung"][:4]) if rec.get("DatumEndgueltigeStilllegung") else 9999
                if status in ("31",):           # in planning: not built yet
                    continue
                et = "Speicher" if storage else names.get(rec.get("Energietraeger"), rec.get("Energietraeger") or "unbekannt")
                key = (g[:5], et, start, end)
                agg[key][0] += 1
                agg[key][1] += float(rec.get("Bruttoleistung") or 0) / 1000
                n += 1
            print(f"{fn}: {n:,} units")
    # capacity in operation at year end
    years = range(1990, 2027)
    rows = defaultdict(lambda: [0, 0.0])
    for (k, et, s, e), (c, mw) in agg.items():
        for y in years:
            if s <= y < e:
                rows[(k, y, et)][0] += c
                rows[(k, y, et)][1] += mw
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "mastr_kreis_jahr.csv", "w", encoding="utf-8") as f:
        f.write("kreis,jahr,energietraeger,anzahl,brutto_mw\n")
        for (k, y, et), (c, mw) in sorted(rows.items()):
            f.write(f"{k},{y},{et},{c},{mw:.3f}\n")
    print("written", out / "mastr_kreis_jahr.csv")


BASE = RDB


def rdb_post(path, data):
    # GENESIS_USER / GENESIS_PASSWORD: account of the Regionaldatenbank or, with --destatis, of
    # Destatis GENESIS-Online (the old names RDB_USER / RDB_PASSWORD still work)
    user = os.environ.get("GENESIS_USER") or os.environ.get("RDB_USER")
    pw = os.environ.get("GENESIS_PASSWORD") or os.environ.get("RDB_PASSWORD", "")
    if not user:
        sys.exit("set GENESIS_USER (and GENESIS_PASSWORD) first")
    req = urllib.request.Request(BASE + path, data=urllib.parse.urlencode(data).encode(), method="POST",
                                 headers={"username": user, "password": pw, "Content-Type": "application/x-www-form-urlencoded"})
    return urllib.request.urlopen(req, timeout=600).read()


def rdb_search(term):
    import json
    try:
        r = rdb_post("find/find", {"term": term, "category": "tables", "pagelength": "50", "language": "de"})
    except urllib.error.HTTPError as e:            # print the service's answer instead of a traceback
        print("search failed:", e.code, e.read()[:500].decode("utf-8", "replace"))
        return
    d = json.loads(r)
    tables = d.get("Tables") or []
    if not tables:
        print("no tables found; service status:", json.dumps(d.get("Status"), ensure_ascii=False))
    for t in tables:
        print(t.get("Code"), "|", t.get("Content"))


def rdb_catalogue(selection):
    """List tables whose code matches selection (e.g. 51000*), via catalogue/tables."""
    import json
    try:
        r = rdb_post("catalogue/tables", {"selection": selection, "area": "all", "pagelength": "1000", "language": "de"})
    except urllib.error.HTTPError as e:
        print("catalogue failed:", e.code, e.read()[:300].decode("utf-8", "replace"))
        return
    d = json.loads(r)
    rows = d.get("List") or []
    if not rows:
        print("no tables; service status:", json.dumps(d.get("Status"), ensure_ascii=False))
    for t in rows:
        print(t.get("Code"), "|", " ".join(str(t.get("Content", "")).split()))


def rdb_tables(out, codes, start=None, extra=None):
    out.mkdir(parents=True, exist_ok=True)
    for c in codes:
        q = {"name": c, "area": "all", "format": "ffcsv", "compress": "false", "language": "de"}
        if start:
            q["startyear"] = str(start)
        q.update(extra or {})                           # e.g. classifyingvariable1=STLAH classifyingkey1=STLAH400             # otherwise the service returns only recent years
        if BASE == DESTATIS:
            q["job"] = "true"                       # large tables are prepared as a job; fetched below
        r = rdb_post("data/tablefile", q)
        if r[:1] == b"{" and b'"Code":98' in r:      # table too large for a direct call: start a background job
            q["job"] = "true"
            r = rdb_post("data/tablefile", q)
        if r[:1] == b"{" and b'"Code":99' in r:      # job started: poll the result file
            import json, time
            jname = json.loads(r)["Status"]["Content"].split(":")[-1].strip().split()[0]
            for _ in range(90):
                time.sleep(30)
                try:
                    r = rdb_post("data/resultfile", {"name": jname, "area": "all", "format": "ffcsv", "compress": "false", "language": "de"})
                except urllib.error.HTTPError as e:    # 404 while the job is still being prepared
                    if e.code != 404:
                        raise
                    r = b"{"
                if r[:1] != b"{":
                    break
                print("   waiting for job", jname, flush=True)
        if r[:2] == b"PK":
            with zipfile.ZipFile(io.BytesIO(r)) as z:
                r = z.read(z.namelist()[0])
        (out / f"rdb_{c}.csv").write_bytes(r)
        print("written", out / f"rdb_{c}.csv", len(r))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--out", default="/srv/daten/claude-daten/kreise")
    a.add_argument("--work", default="/srv/daten/tmp")
    a.add_argument("--mastr", action="store_true")
    a.add_argument("--search")
    a.add_argument("--catalogue", help="list tables by code pattern, e.g. 51000*")
    a.add_argument("--param", nargs="*", default=[], help="extra service parameters key=value, e.g. classifyingvariable1=STLAH")
    a.add_argument("--tables", nargs="*")
    a.add_argument("--destatis", action="store_true", help="use GENESIS-Online of Destatis instead of the Regionaldatenbank (Destatis account in GENESIS_USER/GENESIS_PASSWORD)")
    a.add_argument("--start", type=int, help="first year for --tables (default: service default, often only recent years)")
    x = a.parse_args()
    out, work = Path(x.out), Path(x.work)
    global BASE
    if x.destatis:
        BASE = DESTATIS
    work.mkdir(parents=True, exist_ok=True)
    if x.mastr:
        mastr(out, work)
    if x.search:
        rdb_search(x.search)
    if x.catalogue:
        rdb_catalogue(x.catalogue)
    if x.tables:
        rdb_tables(out, x.tables, x.start, dict(p.split("=", 1) for p in x.param))


if __name__ == "__main__":
    main()
