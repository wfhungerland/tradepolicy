"""Fetch district-level (Kreis) data on the user's own server and write compact files.

Runs on the Hetzner server (Python 3.10+, pandas). Two parts:

1. Marktstammdatenregister (MaStR, Bundesnetzagentur, Datenlizenz Deutschland 2.0):
   downloads the full export (about 3.3 GB), streams the unit XML files without unpacking
   them and aggregates electrical units to districts (first five digits of the municipal
   key): capacity in operation at the end of each year by energy source, plus counts.
   Output: mastr_kreis_jahr.csv (kreis, jahr, energietraeger, anzahl, brutto_mw).
   Storage units (batteries) are included as energy source "Speicher".

2. Regionaldatenbank Deutschland (GENESIS web service): needs a free account. Put the
   credentials into the environment variables RDB_USER and RDB_PASSWORD (or an API token
   into RDB_USER and leave RDB_PASSWORD empty) on the server; they never leave the server.
   With --search TERM the script lists matching tables; with --tables CODE ... it downloads
   each table for all districts as flat CSV (ffcsv).

Usage on the server:
  python3 server_fetch_kreise.py --out /srv/daten/claude-daten/kreise --mastr
  RDB_USER=... RDB_PASSWORD=... python3 server_fetch_kreise.py --search Auslandsumsatz
  RDB_USER=... RDB_PASSWORD=... python3 server_fetch_kreise.py --out /srv/daten/claude-daten/kreise --tables 42111-... 13111-...
"""
import argparse
import io
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

MASTR_PAGE = "https://www.marktstammdatenregister.de/MaStR/Datendownload"
RDB = "https://www.regionalstatistik.de/genesisws/rest/2020/"
UNIT_FILES = re.compile(r"^Einheiten(Solar|Wind|Biomasse|Wasser|Verbrennung|Kernkraft|GeoSolarthermieGrubenKlaerschlammDruckentspannung|Stromspeicher)(_\d+)?\.xml$")
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
            storage = "Stromspeicher" in fn
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


def rdb_post(path, data):
    user, pw = os.environ.get("RDB_USER"), os.environ.get("RDB_PASSWORD", "")
    if not user:
        sys.exit("set RDB_USER (and RDB_PASSWORD) on the server first")
    req = urllib.request.Request(RDB + path, data=urllib.parse.urlencode(data).encode(), method="POST",
                                 headers={"username": user, "password": pw, "Content-Type": "application/x-www-form-urlencoded"})
    return urllib.request.urlopen(req, timeout=600).read()


def rdb_search(term):
    r = rdb_post("find/find", {"term": term, "category": "tables", "pagelength": "50", "language": "de"})
    import json
    for t in json.loads(r).get("Tables") or []:
        print(t.get("Code"), "|", t.get("Content"))


def rdb_tables(out, codes):
    out.mkdir(parents=True, exist_ok=True)
    for c in codes:
        r = rdb_post("data/tablefile", {"name": c, "area": "all", "format": "ffcsv", "compress": "false", "language": "de"})
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
    a.add_argument("--tables", nargs="*")
    x = a.parse_args()
    out, work = Path(x.out), Path(x.work)
    work.mkdir(parents=True, exist_ok=True)
    if x.mastr:
        mastr(out, work)
    if x.search:
        rdb_search(x.search)
    if x.tables:
        rdb_tables(out, x.tables)


if __name__ == "__main__":
    main()
