"""Helpers for regional (NUTS) analyses: Eurostat TSV reader, NUTS geometries, maps.

Geometries: Eurostat GISCO NUTS 2021, 1:20 million (NUTS 2) and 1:10 million (NUTS 3),
projection ETRS89-LAEA (EPSG:3035). Maps are drawn with matplotlib (no GIS libraries)
and, for the site, written as SVG paths.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Polygon

# map window for continental Europe (EPSG:3035 metres): excludes overseas regions
EXTENT_EU = (2500000, 7400000, 1350000, 5450000)
EXTENT_DE = (4020000, 4700000, 2650000, 3580000)


def read_eurostat(path):
    d = pd.read_csv(path, sep="\t")
    k = d.columns[0]
    dims = k.split("\\")[0].split(",")
    s = d[k].str.split(",", expand=True)
    s.columns = dims
    v = d.drop(columns=k)
    v.columns = [c.strip() for c in v.columns]
    v = v.apply(lambda c: pd.to_numeric(c.astype(str).str.extract(r"([-\d.]+)")[0], errors="coerce"))
    out = pd.concat([s.drop(columns="freq"), v], axis=1).melt(id_vars=[c for c in dims if c != "freq"], var_name="year", value_name="value")
    out["year"] = out.year.astype(int)
    return out.dropna(subset=["value"])


def load_nuts(path):
    """Dict NUTS_ID -> list of rings (arrays of x, y), plus names."""
    g = json.load(open(path))
    shapes, names = {}, {}
    for f in g["features"]:
        p = f["properties"]
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        shapes[p["NUTS_ID"]] = [np.array(poly[0]) for poly in polys]
        names[p["NUTS_ID"]] = p.get("NAME_LATN") or p.get("NUTS_NAME")
    return shapes, names


def choropleth(ax, shapes, values, bins, colors, extent=EXTENT_EU, missing="#bfbfbf", edge="#ffffff", lw=0.15):
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bins, cmap.N)
    patches, vals, miss = [], [], []
    for nid, rings in shapes.items():
        for r in rings:
            x0, x1, y0, y1 = extent
            if r[:, 0].max() < x0 or r[:, 0].min() > x1 or r[:, 1].max() < y0 or r[:, 1].min() > y1:
                continue
            v = values.get(nid, np.nan)
            (miss if pd.isna(v) else patches).append(Polygon(r, closed=True))
            if not pd.isna(v):
                vals.append(v)
    ax.add_collection(PatchCollection(miss, facecolor=missing, edgecolor=edge, linewidth=lw))
    pc = PatchCollection(patches, cmap=cmap, norm=norm, edgecolor=edge, linewidth=lw)
    pc.set_array(np.array(vals))
    ax.add_collection(pc)
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal"); ax.axis("off")
    return pc


def legend_bins(ax, bins, colors, fmt="{:.1f}", title="", loc="upper left"):
    from matplotlib.patches import Patch
    labels = [f"{fmt.format(bins[k])} bis {fmt.format(bins[k + 1])}" for k in range(len(colors))]
    labels[0] = f"unter {fmt.format(bins[1])}"
    labels[-1] = f"{fmt.format(bins[-2])} und mehr"
    ax.legend(handles=[Patch(color=c) for c in colors], labels=labels, title=title, frameon=False, fontsize=7,
              title_fontsize=8, loc=loc)


def svg_paths(shapes, extent=EXTENT_EU, width=600, tol=2500):
    """NUTS_ID -> SVG path string in a width-wide viewbox (y flipped), simplified by
    dropping vertices closer than tol metres to the previous kept vertex."""
    x0, x1, y0, y1 = extent
    k = width / (x1 - x0)
    out = {}
    for nid, rings in shapes.items():
        parts = []
        for r in rings:
            if r[:, 0].max() < x0 or r[:, 0].min() > x1 or r[:, 1].max() < y0 or r[:, 1].min() > y1:
                continue
            keep = [r[0]]
            for p in r[1:]:
                if abs(p[0] - keep[-1][0]) + abs(p[1] - keep[-1][1]) > tol:
                    keep.append(p)
            if len(keep) < 3:
                continue
            pts = [(round((p[0] - x0) * k, 1), round((y1 - p[1]) * k, 1)) for p in keep]
            parts.append("M" + "L".join(f"{a},{b}" for a, b in pts) + "Z")
        if parts:
            out[nid] = "".join(parts)
    return out, round((y1 - y0) * k)


def kreis_names(names, types):
    """District names made unique: Bavarian and other cities share their name with the
    surrounding Landkreis (Regensburg, Schweinfurt, ...); add 'Stadt' or 'Landkreis'."""
    names, types = list(names), list(types)
    dup = {n for n in names if names.count(n) > 1}
    return [f"{n}, {'Stadt' if str(t).startswith('Kreisfreie') else 'Landkreis'}" if n in dup else n for n, t in zip(names, types)]


def rdb_kreise(path):
    """Regionaldatenbank 42111 flat CSV -> district panel (index ags, year; columns umsatz, ausl in EUR thousand)."""
    d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    d = d[d["1_variable_code"] == "KREISE"]
    d["v"] = pd.to_numeric(d.value, errors="coerce")
    p = d.pivot_table(index=["1_variable_attribute_code", "time"], columns="value_variable_label", values="v")
    p = p.rename(columns={"Umsatz": "umsatz", "Auslandsumsatz": "ausl"})[["umsatz", "ausl"]]
    p.index = p.index.set_names(["ags", "year"])
    return p.rename(index=int, level="year")
