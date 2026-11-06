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

  searoute data     maritime network and port list from the searoute-py package
                    (Apache 2.0), only the two GeoJSON files are extracted
  WITS concordances HS 2022 -> HS 2007 -> ISIC Rev. 3 (folder conc)
  BACI HS22         import weights for the US tariffs (about 0.3 GB)
Not downloadable by script: OECD ICIO 2025 (www.oecd.org blocks automated
requests); put 2016-2022_SML.zip into the folder icio by hand.

Usage: python 30_scenario_download.py
"""
import shutil
import tarfile
import urllib.request
import zipfile

from config import load_config

FILES = {
    "ITPD_E_R2025.zip": "https://www.usitc.gov/data/gravity/itpd_e/r2025/ITPD_E_R2025.zip",
    "rta_20260111_csv.zip": "https://www.ewf.uni-bayreuth.de/pool/dokumente/rta_20260111_csv.zip",
    "usa_tariffs_20260907.zip": "https://www.cepii.fr/DATA_DOWNLOAD/usa_tariffs/usa_tariffs_20260907.zip",
    "ProTEE_0_1.csv": "https://www.cepii.fr/DATA_DOWNLOAD/ProTEE/ProTEE_0_1.csv",
    "CERDI-seadistance_V1.1.dta":
        "https://zenodo.org/api/records/240493/files/CERDI-seadistance_V1.1.dta/content",
    "BACI_HS22_V202601.zip": "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS22_V202601.zip",
    "conc/Concordance_H6_to_H3.zip": "https://wits.worldbank.org/data/public/concordance/Concordance_H6_to_H3.zip",
    "conc/Concordance_H3_to_I3.zip": "https://wits.worldbank.org/data/public/concordance/Concordance_H3_to_I3.zip",
    # MAcMap-HS6 2001-2019 (ITC-CEPII), 2.7 GB, link from the CEPII MAcMap page (Dropbox)
    "macmap/Tariffs_2001_2019.zip": "https://dl.dropboxusercontent.com/scl/fi/rfow5essm4b5kt30o0gdx/"
                                    "Tariffs_2001_2019.zip?rlkey=yd3d66fegws2yv58ng0kmlryl&dl=1",
}
SEAROUTE = "https://files.pythonhosted.org/packages/source/s/searoute/searoute-1.6.0.tar.gz"
# Application files of Yotov et al. (2016), as shipped with the R package tradepolicy
# (Pacha), pinned to the commit used for 32_validate_yotov.py
YOTOV = "https://codeload.github.com/pachadotdev/tradepolicy/zip/577bfde7bd770f61a0e686d346ec1f2ac6656247"


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
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            print(f"exists   {name}")
            continue
        print(f"download {name} ...", flush=True)
        fetch(url, target)
        print(f"         {target.stat().st_size / 1e6:.0f} MB")
        if name.startswith("conc/"):
            with zipfile.ZipFile(target) as z:
                for m in z.namelist():
                    if m.upper().endswith(".CSV"):
                        z.extract(m, target.parent)
    sea = folder / "searoute"
    if not (sea / "marnet_searoute.geojson").exists():
        sea.mkdir(exist_ok=True)
        tgz = sea / "searoute.tar.gz"
        fetch(SEAROUTE, tgz)
        with tarfile.open(tgz) as tf:              # data files only, no code
            for m in tf.getmembers():
                base = m.name.rsplit("/", 1)[-1]
                if base in ("marnet_searoute.geojson", "ports.geojson") and m.isfile():
                    with tf.extractfile(m) as src, (sea / base).open("wb") as dst:
                        shutil.copyfileobj(src, dst)
        tgz.unlink()
        print("searoute network and ports extracted")
    guide = folder / "yotov_guide"
    if not (guide / "Chapter2").exists():
        guide.mkdir(exist_ok=True)
        zf = guide / "tradepolicy.zip"
        fetch(YOTOV, zf)
        with zipfile.ZipFile(zf) as z:                # Stata data and results of chapter 2 only
            for m in z.namelist():
                if "/00-application-files/Chapter2/" in m and not m.endswith("/"):
                    rel = m.split("/00-application-files/", 1)[1]
                    (guide / rel).parent.mkdir(parents=True, exist_ok=True)
                    with z.open(m) as src, (guide / rel).open("wb") as dst:
                        shutil.copyfileobj(src, dst)
        zf.unlink()
        print("Yotov et al. (2016) chapter 2 files extracted")


if __name__ == "__main__":
    main()
