"""Shortest sea routes between countries, with and without chokepoints.

Uses the maritime network (marnet) and port list shipped as data with the
searoute-py package (Apache License 2.0; network derived from the Eurostat
SeaRoute / ORNL data), read here as plain GeoJSON. Only the two data files are
used, none of the package code: 30_scenario_download.py extracts
marnet_searoute.geojson and ports.geojson into cfg["data"]["scenarios"]/searoute.

Edges carry a "passage" tag (suez, babalmandab, panama, malacca, gibraltar, ...).
A scenario closes passages by dropping the tagged edges.

Country ports: for every ISO2 code the port flagged as main (t = 1) with the most
connected destination countries; countries without a port get the best
connected foreign port that lists them among its hinterland countries.
"""
import heapq
import json
import math
from collections import defaultdict

EARTH_KM = 6371.0088
ALWAYS_CLOSED = ("northwest", "bering")   # Arctic routes, not used by regular container lines


def _norm(lon):
    return ((lon + 180.0) % 360.0) - 180.0


def _key(lon, lat):
    return (round(_norm(lon), 4), round(lat, 4))


def haversine(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(h))


class SeaNetwork:
    def __init__(self, marnet_path):
        g = json.load(open(marnet_path, encoding="utf-8"))
        self.adj = defaultdict(list)          # node -> [(node, km, passage)]
        for f in g["features"]:
            passage = (f.get("properties") or {}).get("passage")
            geom = f["geometry"]
            lines = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
            for line in lines:
                for p, q in zip(line[:-1], line[1:]):
                    a, b = _key(*p[:2]), _key(*q[:2])
                    if a == b:
                        continue
                    d = haversine(a, b)
                    self.adj[a].append((b, d, passage))
                    self.adj[b].append((a, d, passage))
        self.nodes = list(self.adj)

    def nearest(self, lon, lat):
        p = (_norm(lon), lat)
        return min(self.nodes, key=lambda n: haversine(n, p))

    def distances(self, source, closed=()):
        """Dijkstra from one node; returns dict node -> km, avoiding closed passages."""
        closed = set(closed) | set(ALWAYS_CLOSED)
        dist = {source: 0.0}
        heap = [(0.0, source)]
        while heap:
            d, n = heapq.heappop(heap)
            if d > dist.get(n, math.inf):
                continue
            for m, w, passage in self.adj[n]:
                if passage in closed:
                    continue
                nd = d + w
                if nd < dist.get(m, math.inf):
                    dist[m] = nd
                    heapq.heappush(heap, (nd, m))
        return dist


def country_ports(ports_path, iso2_codes):
    """ISO2 -> (lon, lat, port name) for the main port of each country."""
    ports = json.load(open(ports_path, encoding="utf-8"))["features"]
    by_cty = defaultdict(list)
    for f in ports:
        pr = f["properties"]
        by_cty[pr["port"][:2]].append((pr.get("t") or 0.0, len(pr.get("to_cty") or []),
                                       f["geometry"]["coordinates"], pr["name"], pr.get("to_cty") or []))
    out = {}
    for c in iso2_codes:
        own = [p for p in by_cty.get(c, []) if p[0] >= 1]
        if own:
            t, n, xy, name, _ = max(own, key=lambda p: (p[0], p[1]))
            out[c] = (xy[0], xy[1], name)
            continue
        gateways = [(p[1], p[2], p[3], k) for k, lst in by_cty.items() if k != c
                    for p in lst if p[0] >= 1 and c in p[4]]
        if gateways:
            n, xy, name, k = max(gateways)
            out[c] = (xy[0], xy[1], f"{name} ({k}, gateway)")
    return out


def distance_matrix(net, ports, closed=()):
    """Sea distance in km between all countries in ports (dict ISO2 -> lon, lat, name)."""
    codes = sorted(ports)
    node = {c: net.nearest(ports[c][0], ports[c][1]) for c in codes}
    D = {}
    for a in codes:
        dist = net.distances(node[a], closed)
        for b in codes:
            D[(a, b)] = dist.get(node[b], math.inf) if a != b else 0.0
    return D
