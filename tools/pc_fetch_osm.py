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


def fetch(q):
    """Ask the chosen server first; on errors rotate through all public servers and keep
    trying (up to 40 attempts, waits growing to 5 minutes), because single servers are
    often overloaded for a while."""
    data = urllib.parse.urlencode({"data": q}).encode()
    order = [URL] + [u for u in SERVERS.values() if u != URL]
    for attempt in range(40):
        url = order[attempt % len(order)]
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "tradepolicy-research/1.0 (BMWE IC1)"})
        try:
            with urllib.request.urlopen(req, timeout=1200) as r:
                return json.load(r)
        except Exception as e:                       # busy server (429/502/504) or timeout
            wait = min(300, 30 * (attempt // len(order) + 1))
            name = next(k for k, v in SERVERS.items() if v == url)
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
            if target.exists():
                print("skip", target.name)
                continue
            body, mode, keep = QUERIES[cat]
            q = f'[out:json][timeout:1100];area["ISO3166-2"="{land}"]->.a;({body});out {mode};'
            print(f"{land} {cat} ...", flush=True)
            res = fetch(q)
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
