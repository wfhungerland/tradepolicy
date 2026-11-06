"""Download the datasets for strand 3 (structural gravity scenarios).

Files go to cfg["data"]["scenarios"] (see config.example.yaml). Existing files
are skipped, so the script can be re-run after an interruption. Sources and
licences: data_inventory_gravity.md and literature_gravity_scenarios.md.

  ITPD-E R2025      USITC, bilateral trade incl. domestic flows, 170 industries,
                    1986-2023 (about 0.8 GB zipped, 8.7 GB unzipped; kept zipped)
  RTA 2026-01-11    Larch regional trade agreements database, 1950-2025
  US tariffs        CEPII (Guimbard 2026), US applied tariffs 2025-26, HS6 x origin
                    x date, CC BY-NC 4.0
  ProTEE 0.1        CEPII trade elasticities by HS6 (Fontagne, Guimbard, Orefice 2022)
  CERDI seadistance Sea distances between countries, V1.1 (Zenodo)

Usage: python 30_scenario_download.py
"""
import shutil
import urllib.request

from config import load_config

FILES = {
    "ITPD_E_R2025.zip": "https://www.usitc.gov/data/gravity/itpd_e/r2025/ITPD_E_R2025.zip",
    "rta_20260111_csv.zip": "https://www.ewf.uni-bayreuth.de/pool/dokumente/rta_20260111_csv.zip",
    "usa_tariffs_20260907.zip": "https://www.cepii.fr/DATA_DOWNLOAD/usa_tariffs/usa_tariffs_20260907.zip",
    "ProTEE_0_1.csv": "https://www.cepii.fr/DATA_DOWNLOAD/ProTEE/ProTEE_0_1.csv",
    "CERDI-seadistance_V1.1.dta":
        "https://zenodo.org/api/records/240493/files/CERDI-seadistance_V1.1.dta/content",
}


def fetch(url, target):
    # usitc.gov refuses browser user agents; the Python default works.
    tmp = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as r, tmp.open("wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    tmp.rename(target)


def main():
    cfg = load_config()
    folder = cfg["data"]["scenarios"]
    folder.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        target = folder / name
        if target.exists():
            print(f"exists   {name}")
            continue
        print(f"download {name} ...", flush=True)
        fetch(url, target)
        print(f"         {target.stat().st_size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
