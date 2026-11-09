"""Transmission grid expansion (EnLAG and BBPlG projects): status and planned commissioning.

Data: Bundesnetzagentur, "Monitoring des Stromnetzausbaus", second quarter 2026 (PDF in
Monitoring-Archiv_2026.zip from data.netzausbau.de). Read from the PDF text:
  status of all 128 projects in km (summary page),
  length and planned commissioning year per project (progress tables, EnLAG pp. 62-63,
  BBPlG pp. 368-373); projects without a date ("-", "> 2030") are counted as "ohne Termin".
Writes <output>/netzausbau/status.csv, plan_jahre.csv and netzausbau.png.
"""
import re
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import load_config

PDF = "Monitoringbericht_Q2-26.pdf"
STATUS = [("vor dem Genehmigungsverfahren", "noch nicht im Verfahren"), ("im Bundesfachplanungs", "Bundesfachplanung/Raumordnung"),
          ("vor dem oder im Planfeststellungs", "vor/im Planfeststellungsverfahren"), ("genehmigt und vor dem oder im Bau", "genehmigt, vor/im Bau"),
          ("fertiggestellt aber noch nicht in Betrieb", "fertig, noch nicht in Betrieb"), ("vollständig in Betrieb", "in Betrieb")]


def text(path, a, b):
    return subprocess.run(["pdftotext", "-layout", "-f", str(a), "-l", str(b), str(path), "-"], capture_output=True, text=True, check=True).stdout


def main():
    cfg = load_config()
    pdf = cfg["data"]["scenarios"] / "netzausbau" / PDF
    out = cfg["output"] / "netzausbau"
    out.mkdir(parents=True, exist_ok=True)
    t = re.sub(r"\s+", " ", text(pdf, 6, 6))
    st = []
    for key, label in STATUS:
        m = re.search(r"(\d[\d.]*) km [^•]*?" + re.escape(key.split()[0]) + r"[^•]*?" + re.escape(key.split()[-1]), t)
        st.append({"status": label, "km": int(m.group(1).replace(".", ""))})
    st = pd.DataFrame(st)
    total = int(re.search(r"Gesamtlänge von ([\d.]+) km", t).group(1).replace(".", ""))
    print(st.to_string(index=False), "\nsum", st.km.sum(), "reported total", total)
    st.to_csv(out / "status.csv", index=False)
    rows = []
    for law, (a, b) in {"EnLAG": (62, 63), "BBPlG": (368, 373)}.items():
        for line in text(pdf, a, b).splitlines():
            m = re.search(r"~?\s*([\d.]+) km\s+(\S.*?)\s*$", line)
            if m and "Länge" not in line:
                y = re.fullmatch(r"(\d{4})", m.group(2))
                rows.append({"gesetz": law, "km": float(m.group(1).replace(".", "")), "jahr": int(y.group(1)) if y else None})
    v = pd.DataFrame(rows)
    print(f"projects parsed: {len(v)}, km {v.km.sum():,.0f}; without date: {v.jahr.isna().sum()} ({v[v.jahr.isna()].km.sum():,.0f} km)")
    plan = v.dropna(subset=["jahr"]).groupby("jahr").km.sum().sort_index().cumsum()
    plan.to_csv(out / "plan_jahre.csv")
    print("planned cumulative km 2025/2030/2035:", plan.reindex(range(2009, 2039)).ffill().loc[[2025, 2030, 2035]].to_dict())

    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1, 1.2]})
    cols = ["#d9d9d9", "#bfbfbf", "#9dc3e6", "#5b9bd5", "#2e75b6", "#002060"]
    a.barh(st.status[::-1], st.km[::-1], color=cols[::-1])
    for i, k in enumerate(st.km[::-1]):
        a.text(k + 80, i, f"{k:,}".replace(",", "."), va="center", fontsize=8)
    a.set_title("Stand der Vorhaben, km (gesamt " + f"{total:,}".replace(",", ".") + " km)", loc="left", fontsize=10)
    a.spines[["top", "right"]].set_visible(False)
    b.step(plan.index, plan.values, where="post", color="#002060")
    b.axvline(2026.5, color="#c00000", lw=0.8, ls="--"); b.text(2026.7, plan.max() * 0.05, "Stichtag 30.06.2026", color="#c00000", fontsize=8)
    b.set_title("Geplante Inbetriebnahme nach Vorhaben, kumulierte km", loc="left", fontsize=10)
    b.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Ausbau des Übertragungsnetzes (EnLAG und BBPlG), Stand zweites Quartal 2026", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, f"Quelle: eigene Berechnungen auf Basis des Monitorings des Stromnetzausbaus der Bundesnetzagentur (Q2/2026). Rechts ohne "
             f"{v.jahr.isna().sum()} Vorhaben ohne Termin (" + f"{v[v.jahr.isna()].km.sum():,.0f}".replace(",", ".") + " km); Termin = geplante Gesamtinbetriebnahme des Vorhabens.", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out / "netzausbau.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
