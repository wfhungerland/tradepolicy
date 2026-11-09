"""Line and point layers of the German power, rail and motorway networks for the site map.

Data: OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0), files from tools/pc_fetch_osm.py.
Coordinates are projected (sinusoidal, central meridian 10.5 E, as in 68_kreise_infra.py),
simplified with a tolerance of 60 m, de-duplicated across Länder and written as integer
coordinates in units of 100 m. District outlines (GISCO NUTS 2024, 1:1 million) as background.
Writes <site>/netz_<layer>.json, one file per layer, loaded on demand by the site.
Usage: python 71_netz_lines.py site_data_folder
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, shape
from shapely.ops import transform

from config import load_config

R, LON0, UNIT = 6371.0088, 10.5, 0.1     # km; output unit 0.1 km


def proj(lon, lat):
    la = np.radians(lat)
    return R * np.radians(np.asarray(lon) - LON0) * np.cos(la), R * la


def volt(t):
    v = [int(x) for x in str(t.get("voltage", "")).replace(",", ";").split(";") if x.strip().isdigit()]
    return max(v) if v else 0


def feats(raw, cat):
    seen = set()
    for f in sorted((raw / "osm").glob(f"{cat}_DE-*.json.gz")):
        for ft in json.load(gzip.open(f))["features"]:
            g = ft["g"]
            key = (tuple(g[0]), tuple(g[-1]), len(g))
            if key not in seen:
                seen.add(key)
                yield ft


def enc(geom, y_top):
    """Line -> flat list of ints (x, y_down) in 0.1 km."""
    c = np.asarray(geom.coords)
    return [int(v) for xy in zip(np.round(c[:, 0] / UNIT), np.round((y_top - c[:, 1]) / UNIT)) for v in xy]


def main(site):
    raw = load_config()["data"]["scenarios"]
    site = Path(site)
    gj = json.load(open(raw / "regional" / "nuts3_2024_01m.geojson"))
    kreise = {f["properties"]["NUTS_ID"]: transform(proj, shape(f["geometry"])) for f in gj["features"] if f["properties"]["NUTS_ID"].startswith("DE")}
    minx = min(p.bounds[0] for p in kreise.values()); maxx = max(p.bounds[2] for p in kreise.values())
    miny = min(p.bounds[1] for p in kreise.values()); maxy = max(p.bounds[3] for p in kreise.values())
    x0 = minx
    shift = lambda g: transform(lambda x, y: (np.asarray(x) - x0, y), g)
    meta = {"w": round((maxx - minx) / UNIT), "h": round((maxy - miny) / UNIT), "unit_km": UNIT}
    out = {}
    # background: district outlines
    rings = []
    for g in kreise.values():
        for poly in getattr(g, "geoms", [g]):
            s = shift(poly.exterior).simplify(0.3)
            rings.append(enc(s, maxy))
    out["kreise"] = rings
    layers = {"ehv380": [], "ehv220": [], "hv110": [], "rail_el": [], "rail_nel": [], "bab": [], "sub": []}
    for ft in feats(raw, "power_line"):
        v = volt(ft["tags"])
        k = "ehv380" if v >= 380000 else "ehv220" if v >= 220000 else "hv110" if v >= 110000 else None
        if k and len(ft["g"]) > 1:
            layers[k].append(LineString(np.c_[proj(*np.array(ft["g"]).T)]))
    for ft in feats(raw, "rail"):
        if len(ft["g"]) > 1:
            k = "rail_nel" if str(ft["tags"].get("electrified", "no")) in ("no", "") else "rail_el"
            layers[k].append(LineString(np.c_[proj(*np.array(ft["g"]).T)]))
    for ft in feats(raw, "motorway"):
        if len(ft["g"]) > 1:
            layers["bab"].append(LineString(np.c_[proj(*np.array(ft["g"]).T)]))
    subs = []
    for ft in feats(raw, "substation"):
        v = volt(ft["tags"])
        if v >= 110000 and ft["tags"].get("substation") != "minor_distribution":
            x, y = proj(*ft["g"][0])
            subs += [int(round((x - x0) / UNIT)), int(round((maxy - y) / UNIT)), 380 if v >= 380000 else 220 if v >= 220000 else 110]
    for k, ls in layers.items():
        if k == "sub":
            continue
        out[k] = [e for e in (enc(shift(l).simplify(0.06), maxy) for l in ls) if len(e) >= 4]
    out["sub"] = subs
    for k, v in out.items():
        p = site / f"netz_{k}.json"
        p.write_text(json.dumps({**meta, "d": v}, separators=(",", ":")))
        print(f"{p.name}: {len(v):,} items, {p.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1])
