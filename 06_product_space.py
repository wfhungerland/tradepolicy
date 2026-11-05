"""Step 6: product space network with Germany's position, first vs last year.

Builds the product space as in Hidalgo et al. (2007): the maximum spanning tree
of the proximity matrix plus all links with proximity above a cut-off. The
proximity matrix is the last year's (HS4 main run). Node positions come from a
force-directed layout with a fixed seed, so the map is the same in every run.

The left panel colours nodes by eight product groups; the right panel by Germany's status between the first and last year:
kept RCA, gained RCA, lost RCA, never had RCA. Node size reflects world exports.
Writes to <output>/product_space/:
  product_space_deu.png   the map
  nodes.csv               product, sector, x, y, status, PCI, world exports
Requires 02_complexity.py (hs4). Usage: python 06_product_space.py
"""
import importlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from config import load_config

sectors = importlib.import_module("05_sectors")

LINK_CUTOFF = 0.55  # Hidalgo et al. (2007) keep links with proximity >= 0.55
SEED = 7

STATUS_STYLE = {  # label, colour, draw order
    "never": ("no RCA in either year", "#d9d8d2", 0),
    "kept": ("RCA in both years", "#184f95", 1),
    "lost": ("RCA lost", "#e34948", 2),
    "entry": ("RCA gained", "#1baf7a", 3),
}
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
EDGE = "#c9c8c1"


# Eight product groups for the reference panel (one categorical colour each)
GROUPS = {
    "Food and agriculture": "Food and agriculture",
    "Minerals and fuels": "Minerals, metals, stone",
    "Metals": "Minerals, metals, stone",
    "Stone, glass, precious metals": "Minerals, metals, stone",
    "Basic chemicals": "Chemicals and pharma",
    "Pharmaceuticals": "Chemicals and pharma",
    "Other chemicals": "Chemicals and pharma",
    "Plastics and rubber": "Plastics, wood, paper",
    "Leather, wood, paper": "Plastics, wood, paper",
    "Textiles, apparel, footwear": "Textiles and apparel",
    "Machinery": "Machinery",
    "Electrical and electronics": "Electrical and electronics",
    "Motor vehicles": "Vehicles, instruments, other",
    "Other transport": "Vehicles, instruments, other",
    "Instruments and medical": "Vehicles, instruments, other",
    "Other manufactures": "Vehicles, instruments, other",
}
GROUP_COLORS = {  # validated default categorical order (dataviz palette)
    "Machinery": "#2a78d6",
    "Chemicals and pharma": "#eb6834",
    "Food and agriculture": "#1baf7a",
    "Minerals, metals, stone": "#eda100",
    "Textiles and apparel": "#e87ba4",
    "Plastics, wood, paper": "#008300",
    "Electrical and electronics": "#6250d6",
    "Vehicles, instruments, other": "#e34948",
}


def build_graph(phi: pd.DataFrame):
    """Return (tree, graph): the maximum spanning tree and tree plus strong links."""
    phi = phi.fillna(0.0)
    names = list(phi.index)
    a = phi.to_numpy()
    full = nx.Graph()
    iu = np.triu_indices_from(a, k=1)
    for i, j in zip(*iu):
        if a[i, j] > 0:
            full.add_edge(names[i], names[j], weight=a[i, j])
    tree = nx.maximum_spanning_tree(full, weight="weight")
    g = tree.copy()
    for i, j in zip(*np.where(np.triu(a, k=1) >= LINK_CUTOFF)):
        g.add_edge(names[i], names[j], weight=a[i, j])
    return tree, g


def main():
    cfg = load_config()
    focus = cfg["complexity"]["focus"]
    src = cfg["output"] / "complexity_hs4"
    out = cfg["output"] / "product_space"
    out.mkdir(exist_ok=True)

    phi = pd.read_parquet(src / "proximity_last_year.parquet")
    phi.index = phi.index.astype(str)
    phi.columns = phi.columns.astype(str)
    products = pd.read_parquet(src / "products.parquet")
    cp = pd.read_parquet(src / "country_products.parquet")
    y0, y1 = cp.year.min(), cp.year.max()

    tree, g = build_graph(phi)
    # Layout from the spanning tree only (spreads the dense core), refined by a
    # few spring steps on the tree; the extra strong links are drawn on top.
    init = nx.kamada_kawai_layout(tree, weight=None)
    pos = nx.spring_layout(tree, pos=init, seed=SEED, iterations=20, k=1.0 / np.sqrt(len(tree)))

    d = cp[(cp.iso3 == focus) & cp.year.isin([y0, y1])].pivot(index="prod", columns="year", values="mcp")
    status = np.select([(d[y0] == 1) & (d[y1] == 1), (d[y0] == 0) & (d[y1] == 1),
                        (d[y0] == 1) & (d[y1] == 0)], ["kept", "entry", "lost"], "never")
    status = pd.Series(status, index=d.index)
    world = products[products.year == y1].set_index("prod")["world_exports"]
    pci = products.groupby("prod")["pci"].mean()

    nodes = pd.DataFrame({"prod": list(g.nodes)})
    nodes["x"] = [pos[p][0] for p in nodes["prod"]]
    nodes["y"] = [pos[p][1] for p in nodes["prod"]]
    nodes["sector"] = nodes["prod"].map(sectors.sector_of)
    nodes["status"] = nodes["prod"].map(status).fillna("never")
    nodes["world_exports"] = nodes["prod"].map(world)
    nodes["pci"] = nodes["prod"].map(pci)
    nodes.to_csv(out / "nodes.csv", index=False)

    nodes["group"] = nodes["sector"].map(GROUPS)
    from matplotlib.collections import LineCollection
    tree_segs = np.array([[pos[u], pos[v]] for u, v in tree.edges])
    extra = [(u, v) for u, v in g.edges if not tree.has_edge(u, v)]
    extra_segs = np.array([[pos[u], pos[v]] for u, v in extra])
    size = 6 + 90 * np.sqrt(nodes.world_exports / nodes.world_exports.max())

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    for ax in axes:
        ax.add_collection(LineCollection(extra_segs, colors=EDGE, linewidths=0.25, alpha=0.25, zorder=0))
        ax.add_collection(LineCollection(tree_segs, colors="#a9a8a1", linewidths=0.6, zorder=0))
        ax.set_axis_off()
        ax.set_aspect("equal")

    ax = axes[0]
    for grp, colour in GROUP_COLORS.items():
        m = nodes.group == grp
        ax.scatter(nodes.x[m], nodes.y[m], s=size[m], c=colour, edgecolors="#fcfcfb",
                   linewidths=0.4, zorder=2, label=f"{grp} ({int(m.sum())})")
    ax.set_title("Product groups", loc="left", color=TEXT, fontsize=13)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.02), ncol=2, frameon=False, fontsize=10,
              markerscale=1.3)

    ax = axes[1]
    for key, (label, colour, order) in sorted(STATUS_STYLE.items(), key=lambda kv: kv[1][2]):
        m = nodes.status == key
        ax.scatter(nodes.x[m], nodes.y[m], s=size[m], c=colour, edgecolors="#fcfcfb",
                   linewidths=0.4, zorder=order + 1, label=f"{label} ({int(m.sum())})")
    ax.set_title(f"{focus}: revealed comparative advantage, {y0} vs {y1}",
                 loc="left", color=TEXT, fontsize=13)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.02), ncol=2, frameon=False, fontsize=10,
              markerscale=1.3)

    fig.suptitle(f"The product space (HS4, proximity {y1}). Dark lines: maximum spanning tree; "
                 f"light lines: proximity >= {LINK_CUTOFF}. Node size: world exports {y1}.",
                 x=0.01, ha="left", color=TEXT2, fontsize=11)
    fig.savefig(out / "product_space_deu.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)
    print(nodes.status.value_counts().to_string())
    print(f"{g.number_of_nodes()} nodes, {g.number_of_edges()} links -> {out}")


if __name__ == "__main__":
    main()
