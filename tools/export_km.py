"""Export the spending treemaps for the Konjunkturmonitor (KM, repo wfhungerland/konjunkturmonitor).

Reads the site data written by 86_cofog.py (cofog.json) and 87_bundeshaushalt.py (bund.json) and writes
two files in the KM treemap format to the KM folder data/static:
  staat_cofog_tree.json  general government spending by function and group (COFOG), real, bn EUR
  bund_tree.json         federal budget by function plan, bn EUR, with special funds as alternative view

Format (one renderer in the KM draws both): steps (one per year, with values per leaf code and optional
alt values and alt part), parent (code -> parent code, "" for the top), labels and labels_en, hue per top code.

Usage: python tools/export_km.py <tradepolicy-site/site/data> <konjunkturmonitor/data/static>
"""
import json, sys
from pathlib import Path

DIV_HUE = {"GF10": "#002060", "GF07": "#0070C0", "GF01": "#00B0F0", "GF04": "#51154A", "GF09": "#7030A0",
           "GF03": "#D86DCD", "GF02": "#C00000", "GF08": "#47D359", "GF05": "#2E7D32", "GF06": "#595959"}
HF_HUE = {"0": "#00B0F0", "1": "#7030A0", "2": "#002060", "3": "#0070C0", "4": "#595959", "5": "#47D359",
          "6": "#D86DCD", "7": "#51154A", "8": "#C00000"}
HAUPT_EN = {"9": "Not assigned", "0": "General services", "1": "Education, research, culture", "2": "Social security, family, labour market",
            "3": "Health, environment, sport", "4": "Housing, urban development, regional planning", "5": "Food, agriculture",
            "6": "Energy, water, trade and industry", "7": "Transport, communications", "8": "Public finance"}


def cofog(C):
    years, pi = C["years"], C["price_index"]
    labels = {d["code"]: d["de"] for d in C["divisions"]}
    labels_en = {d["code"]: d["en"] for d in C["divisions"]}
    parent = {d["code"]: "" for d in C["divisions"]}
    for g, o in C["groups"].items():
        labels[g], labels_en[g], parent[g] = o["de"], o["en"], g[:4]
    steps = []
    for i, y in enumerate(years):
        vals = {g: round(o["values"][i] / pi[i] / 1000, 3) for g, o in C["groups"].items()
                if o["values"][i] is not None and o["values"][i] > 0}
        if len(vals) < len(C["groups"]) * 0.8:  # groups start in 2000
            continue
        steps.append({"key": str(y), "label": str(y), "values": vals})
    return {"title": "Grundriss der Staatsausgaben", "unit": "Mrd. EUR", "unit_en": "EUR bn",
            "price_base": C["price_base"], "updated": C["_meta"].get("updated", "")[:10],
            "scale_area": True, "slider": True, "steps": steps, "parent": parent,
            "labels": labels, "labels_en": labels_en, "hue": DIV_HUE}


GRP_HUE = {"4": "#00B0F0", "5": "#C00000", "6": "#002060", "7": "#51154A", "8": "#47D359", "9": "#595959"}
EPL_HUE = {"11": "#002060", "14": "#C00000", "60": "#595959", "32": "#7F7F7F", "12": "#51154A", "30": "#7030A0",
           "15": "#0070C0", "17": "#D86DCD", "09": "#47D359", "23": "#2E7D32", "16": "#00B0F0"}
GRP_EN = {"4": "Personnel", "5": "Material spending, military procurement, interest", "6": "Grants and subsidies (excluding investment)",
          "7": "Construction", "8": "Other investment and investment grants", "9": "Special financing items"}
VIEW_EN = {"fn": "Function", "grp": "Economic type", "epl": "Ministry"}


def bund(B):
    views = []
    for key, VW in B["views"].items():
        steps = []
        for Y in B["years"]:
            kind = Y["kind"]
            st = {"key": str(Y["year"]), "group": "Ist" if kind == "Ist" else "Soll", "kind": kind,
                  "label": f"{Y['year']}" + (" Entwurf" if kind == "Entwurf" else ""),
                  "label_en": f"{Y['year']}" + (" draft" if kind == "Entwurf" else ""),
                  "values": {c: v for c, v in Y["v"][key].items() if v > 0}}
            if Y.get("alt"):
                st["alt"] = {"values": {c: v for c, v in Y["alt"][key].items() if v > 0}, "part": Y["part"][key],
                             "funds": Y["funds"], "netted": Y["netted"]}
            steps.append(st)
        labels = dict(VW["labels"])
        en = dict(labels)
        if key == "fn": en.update({c: HAUPT_EN.get(c, labels[c]) for c in labels if len(c) == 1})
        if key == "grp": en.update({c: GRP_EN.get(c, labels[c]) for c in labels if len(c) == 1})
        hue = HF_HUE if key == "fn" else GRP_HUE if key == "grp" else EPL_HUE
        views.append({"key": key, "label": VW["label"], "label_en": VIEW_EN[key], "steps": steps, "parent": VW["parent"],
                      "labels": labels, "labels_en": en, "hue": hue, "light_rest": key == "epl"})
    return {"title": "Grundriss des Bundeshaushalts", "unit": "Mrd. EUR", "unit_en": "EUR bn",
            "scale_area": False, "slider": False, "views": views,
            "alt_label": "mit Sondervermögen", "alt_label_en": "with special funds",
            "part_label": "Sondervermögen", "part_label_en": "special funds"}


def main(site, km):
    site, km = Path(site), Path(km)
    for name, f, data in (("staat_cofog_tree.json", cofog, "cofog.json"), ("bund_tree.json", bund, "bund.json")):
        out = f(json.loads((site / data).read_text(encoding="utf-8")))
        txt = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
        assert "NaN" not in txt
        (km / name).write_text(txt, encoding="utf-8")
        print(name, f"{len(txt) / 1000:.0f} kB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
