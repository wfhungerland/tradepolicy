"""Download infrastructure lines and points from OpenStreetMap (Overpass API) for Germany.

Runs on the user's Windows PC (the cloud sessions cannot reach the Overpass API). Queries
each Land separately, waits between queries as the Overpass usage policy asks, and writes
one compact gzipped JSON file per category and Land into the output folder:
  power_line   power=line with a voltage tag (transmission and high-voltage grid)
  substation   power=substation (centre point) with a voltage tag
  rail         railway=rail without service tag (main and branch lines, not sidings)
  motorway     highway=motorway
Each feature: {"tags": {selected tags}, "g": [[lon, lat], ...]} (points: one pair).
Data © OpenStreetMap contributors, Open Database License 1.0.

Usage (Anaconda Prompt, environment tradepolicy):
  python pc_fetch_osm.py --out X:\\osm
If the main server keeps answering 502/504 (overloaded), add --server kumi or
--server coffee to use another public Overpass instance. Takes about 20 to 60 minutes. Already downloaded files are skipped, so a broken run can
simply be started again.
"""
import argparse
import gzip
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVERS = {"main": "https://overpass-api.de/api/interpreter",
           "kumi": "https://overpass.kumi.systems/api/interpreter",
           "coffee": "https://overpass.private.coffee/api/interpreter"}
URL = SERVERS["main"]
LAENDER = ["DE-BW", "DE-BY", "DE-BE", "DE-BB", "DE-HB", "DE-HH", "DE-HE", "DE-MV", "DE-NI", "DE-NW", "DE-RP", "DE-SL",
           "DE-SN", "DE-ST", "DE-SH", "DE-TH"]
QUERIES = {
    "power_line": ('way["power"="line"]["voltage"](area.a);', "geom", ["voltage", "operator", "cables", "frequency"]),
    "substation": ('nwr["power"="substation"]["voltage"](area.a);', "center", ["voltage", "operator", "substation"]),
    "rail": ('way["railway"="rail"][!"service"](area.a);', "geom", ["usage", "electrified", "maxspeed", "gauge", "highspeed", "operator"]),
    "motorway": ('way["highway"="motorway"](area.a);', "geom", ["ref", "lanes", "maxspeed"]),
}


# rough bounding boxes (south, west, north, east) per Land: fallback for servers whose area
# index is missing (they answer area queries with zero features). Features outside the Land
# do no harm: the analysis de-duplicates and clips to districts.
BBOX = {"DE-BW": (47.5, 7.5, 49.8, 10.5), "DE-BY": (47.2, 8.9, 50.6, 13.9), "DE-BE": (52.3, 13.0, 52.7, 13.8),
        "DE-BB": (51.3, 11.2, 53.6, 14.8), "DE-HB": (53.0, 8.4, 53.6, 9.0), "DE-HH": (53.3, 9.7, 53.8, 10.4),
        "DE-HE": (49.3, 7.7, 51.7, 10.3), "DE-MV": (53.1, 10.5, 54.7, 14.5), "DE-NI": (51.2, 6.6, 54.0, 11.6),
        "DE-NW": (50.3, 5.8, 52.6, 9.5), "DE-RP": (48.9, 6.1, 50.95, 8.6), "DE-SL": (49.1, 6.3, 49.7, 7.5),
        "DE-SN": (50.1, 11.8, 51.7, 15.1), "DE-ST": (50.9, 10.5, 53.1, 13.2), "DE-SH": (53.3, 8.2, 55.1, 11.4),
        "DE-TH": (50.2, 9.8, 51.7, 12.7)}


def fetch(q_area, q_bbox):
    """Ask the chosen server first; on errors rotate through all public servers and keep
    trying (up to 40 attempts, waits growing to 5 minutes). An answer without any feature
    counts as an error (overloaded server or missing area index); from the second round on
    the bounding-box query is used instead of the area query."""
    order = [URL] + [u for u in SERVERS.values() if u != URL]
    for attempt in range(40):
        url = order[attempt % len(order)]
        q = q_area if attempt < len(order) else q_bbox
        data = urllib.parse.urlencode({"data": q}).encode()
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "tradepolicy-research/1.0 (BMWE IC1)"})
        name = next(k for k, v in SERVERS.items() if v == url)
        try:
            with urllib.request.urlopen(req, timeout=1200) as r:
                res = json.load(r)
            if not res.get("elements"):
                raise RuntimeError("answer without features " + (res.get("remark") or "")[:100])
            return res
        except Exception as e:                       # busy server (429/502/504), timeout, empty answer
            wait = min(300, 30 * (attempt // len(order) + 1))
            print(f"   {name}: {e}; next try in {wait} s", flush=True)
            time.sleep(wait)
    raise RuntimeError("no Overpass server answered after 40 attempts; start the script again later")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--out", default=r"X:\osm")
    a.add_argument("--only", nargs="*", help="categories to fetch (default: all)")
    a.add_argument("--server", default="main", choices=list(SERVERS), help="Overpass instance (if one is overloaded)")
    x = a.parse_args()
    global URL
    URL = SERVERS[x.server]
    out = Path(x.out)
    out.mkdir(parents=True, exist_ok=True)
    cats = x.only or list(QUERIES)
    for land in LAENDER:
        for cat in cats:
            target = out / f"{cat}_{land}.json.gz"
            if target.exists() and target.stat().st_size < 200:
                print("re-fetch empty file", target.name)
                target.unlink()
            if target.exists():
                print("skip", target.name)
                continue
            body, mode, keep = QUERIES[cat]
            q = f'[out:json][timeout:1100];area["ISO3166-2"="{land}"]->.a;({body});out {mode};'
            sw, ww, nn, ee = BBOX[land]
            qb = f'[out:json][timeout:1100][bbox:{sw},{ww},{nn},{ee}];({body.replace("(area.a)", "")});out {mode};'
            print(f"{land} {cat} ...", flush=True)
            res = fetch(q, qb)
            feats = []
            for el in res.get("elements", []):
                tags = {k: v for k, v in (el.get("tags") or {}).items() if k in keep}
                if mode == "geom" and "geometry" in el:
                    g = [[round(p["lon"], 5), round(p["lat"], 5)] for p in el["geometry"]]
                elif mode == "center":
                    c = el.get("center") or ({"lon": el["lon"], "lat": el["lat"]} if "lon" in el else None)
                    if not c:
                        continue
                    g = [[round(c["lon"], 5), round(c["lat"], 5)]]
                else:
                    continue
                feats.append({"tags": tags, "g": g})
            with gzip.open(target, "wt", encoding="utf-8") as f:
                json.dump({"land": land, "category": cat, "features": feats}, f, separators=(",", ":"))
            print(f"   {len(feats):,} features -> {target.name}")
            time.sleep(20)
    print("done")


if __name__ == "__main__":
    main()
