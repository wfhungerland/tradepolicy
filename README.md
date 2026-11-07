# tradepolicy

Empirical trade research on two questions:

1. **Gravity for short horizons.** Can gravity models forecast or nowcast German and world trade at monthly or quarterly frequency? Every model must beat naive benchmarks (last value, autoregressive model, bridge equation on Comext monthly data) out of sample. No result counts without an out-of-sample test.
2. **Economic complexity and the product space.** From BACI HS6 data: revealed comparative advantage (RCA), the country-product matrix, Economic Complexity Index (ECI), Product Complexity Index (PCI), product proximity, density/relatedness, diversity, ubiquity and Complexity Outlook Index (COI). Focus: Germany against the large exporters, and how Germany's position in the product space has shifted since 1995.

The repository holds code and documentation only. No data is committed.

## Data

| Dataset | Source | Used in | Config key |
|---|---|---|---|
| BACI HS92 V202601, 1995-2024, HS6 bilateral | CEPII | Strand 1, 2 | `baci_derived`, `baci_raw` |
| Gravity V202211 (distance, contiguity, colony, language) | CEPII | Strand 1 | `gravity` |
| MAcMap-HS6 tariffs 2001-2019 | CEPII / ITC | Strand 1 | `tariffs` |
| TRADHIST 1827-2014, RICardo | CEPII, Sciences Po | historical extensions | `history` |
| Eurostat Comext bulk files, EU27 exports by partner and product, monthly 2002-2026 | Eurostat | Strand 1 | `comext` |
| IMF IMTS (formerly DOTS), bilateral exports, monthly 2000- | IMF, downloaded by `11_imts_download.py` | Strand 1 | none |

Licences and citation notes for each dataset: <https://newswolf.eu/daten>.

Data paths are set in `config.yaml`, which stays on your machine and is never committed. `config.example.yaml` is the template.

## Setup

Requirements: Git, Anaconda (or Miniconda), optionally Stata 17+ with `ppmlhdfe` for cross-checks.

```bash
git clone https://github.com/wfhungerland/tradepolicy.git
cd tradepolicy
conda env create -f environment.yml
conda activate tradepolicy
copy config.example.yaml config.yaml
python config.py
```

`copy` is the Windows command; on macOS/Linux use `cp`. Edit `config.yaml` so the paths point to your data. `python config.py` then lists every data folder as `ok` or `MISSING`.

To update the environment after `environment.yml` changes:

```bash
conda env update -f environment.yml --prune
```

Stata cross-checks need:

```stata
ssc install ftools
ssc install reghdfe
ssc install ppmlhdfe
```

## Layout

Flat structure, at most one folder level. Scripts are numbered in run order.

| File | Purpose |
|---|---|
| `config.example.yaml` | template for local data paths |
| `config.py` | loads `config.yaml`, checks paths |
| `environment.yml` | Python environment |
| `literature_gravity_nowcasting.md` | literature review, strand 1 |
| `complexity.py` | RCA, ECI/PCI (eigenvector), proximity, density, COI/COG, Fitness-Complexity, GENEPY |
| `panel.py` | fixed country-product panel, filters, smoothing, yearly runs |
| `01_exports.py` | BACI raw CSV to country x HS6 x year exports, population from CEPII Gravity |
| `02_complexity.py` | main complexity run (`hs4`, or `hs6` as argument) |
| `03_germany.py` | Germany vs peers: ranks, gaps, complexity quintiles, gained/lost products, opportunities |
| `05_sectors.py` | sector view: world market share, products gained and lost by HS chapter group |
| `06_product_space.py` | product space network map with Germany's gained, kept and lost products |
| `07_atlas_comparison.py` | downloads Atlas rankings and PCI from Harvard Dataverse, compares ECI, ranks and PCI |
| `04_robustness.py` | RCA thresholds, smoothing windows, HS6, without re-export hubs, Fitness-Complexity, GENEPY, GENEPY |
| `forecast.py` | strand 1: benchmarks (naive, AR, bottom-up), PPML gravity with three-way fixed effects, Diebold-Mariano test |
| `10_comext_panel.py` | monthly bilateral export panel from Comext bulk files (EU27 x partners, 2002-) |
| `11_imts_download.py` | monthly bilateral exports of all countries from IMF IMTS |
| `12_forecast_germany.py` | out-of-sample test: German exports, total and by partner, monthly and quarterly |
| `13_forecast_world.py` | out-of-sample test: world exports |
| `test_forecast.py` | checks gravity estimates against pyfixest, AR and DM test |
| `20_export_site.py` | exports derived results as JSON for the public site (repo tradepolicy-site) |
| `30_scenario_download.py` | strand 3: downloads ITPD-E, Larch RTA, CEPII US tariffs, ProTEE, CERDI sea distances |
| `31_itpd_panel.py` | strand 3: converts ITPD-E to compact Parquet (industry and broad-sector panels) |
| `32_validate_yotov.py` | strand 3: reproduces the NAFTA example of Yotov et al. (2016) with gravity_ge.py |
| `33_tariff_inputs.py` | strand 3: US tariffs 2025-26 and ProTEE elasticities by ICIO sector |
| `34_scenario_us_tariffs.py` | strand 3: US tariff scenarios in a Caliendo-Parro model on ICIO 2022 |
| `gravity_ge.py` | strand 3: structural gravity GE solver (exact hat algebra, with tariff revenue option) |
| `test_gravity_ge.py` | checks the GE solver (market clearing, ACR welfare formula, tariff solver) |
| `test_elasticities.py` | simulation test of the elasticity estimator |
| `test_complexity.py` | checks against py-ecomplexity formulas and the method of reflections |
| `complexity_methods.md` | methods review and specification, strand 2 |
| `paper/` | methods paper (Markdown source, PDF built with pandoc and Chromium) |
| `HANDOVER.md` | project state and open items for a new session |
| `literature_gravity_scenarios.md` | literature review for strand 3 (tariff, integration and transport scenarios) |
| `data_inventory_gravity.md` | inventory of datasets for gravity scenario analysis (tariffs, RTAs, transport costs) |
| `results_strand3.md` | results report, strand 3 (US tariffs, EU integration, plausibility checks) |
| `35_eu_border_effects.py` | strand 3: time-varying EU border effects with flows to self (Head and Mayer 2021) |
| `36_scenario_eu.py` | strand 3: EU single market scenarios in the Caliendo-Parro model |
| `38_scenario_transport.py` | strand 3: Red Sea and Panama closure scenarios (sea routes, Feyrer calibration) |
| `sea_routes.py` | sea routing between main ports on the marnet network, passages can be closed |
| `39_macmap_baseline.py` | strand 3: baseline tariffs of all countries from MAcMap-HS6 2019 by ICIO sector |
| `run_strand3.py` | runs strand 3 end to end in the right order |
| `40_check_reproduction.py` | compares local results with the cloud reference (`reference_results.csv`) |
| `44_dependencies.py` | strategic dependencies of the EU and Germany at HS6 (Commission criteria) |
| `45_scenario_china_dependencies.py` | scenario: China stops supplying dependent goods |
| `47_indirect_dependence.py` | direct and indirect dependence of German industries on China (global Leontief inverse) |
| `48_import_elasticities.py` | import demand elasticities by HS6 good for the EU and Germany (BACI HS92 2012-2024), aggregated to ICIO sectors |
| `49_compare_escap.py` | compares own elasticities with the ESCAP-World Bank estimates (HS 2012) |
| `elasticities.py` | Feenstra (1994) / Broda-Weinstein (2006) estimator with Soderbery (2015) LIML and constrained-LIML fallback |
| `46_export_dependencies.py` | exports dependencies.json for the site |
| `43_expost_check.py` | ex-post check: modelled vs observed US imports by partner (IMF IMTS) |
| `41_update_assets.py` | builds the fixed inputs for the monthly tariff update (copied to tradepolicy-site/update/assets) |
| `42_update_us_scenarios.py` | monthly update of the US tariff scenarios (runs in tradepolicy-site via GitHub Actions) |
| `37_export_scenarios.py` | strand 3: exports scenario results as scenarios.json for the site |
| `product_examples_de.csv` | one or two everyday product examples per HS4 heading (German) |
| `results_strand1.md` | results report, strand 1 |
| `results_strand2.md` | results report, strand 2 |

## Running strand 2

In the Anaconda Prompt, inside the project folder, with `conda activate tradepolicy`:

```bash
python -m pytest test_complexity.py
python 01_exports.py
python 02_complexity.py
python 03_germany.py
python 02_complexity.py hs6
python 03_germany.py hs6
python 04_robustness.py
python 05_sectors.py
python 06_product_space.py
python 07_atlas_comparison.py
```

`01_exports.py` reads the BACI CSV files once (roughly 10-20 minutes). Peers, filters and thresholds are set in the `complexity` block of `config.yaml`.

## Running strand 1

```bash
python -m pytest test_forecast.py
python -m pytest test_gravity_ge.py test_elasticities.py
python 10_comext_panel.py
python 11_imts_download.py
python 12_forecast_germany.py
python 13_forecast_world.py
```

`10_comext_panel.py` unpacks about 300 monthly Comext files (one to two hours, resumable). `11_imts_download.py` needs internet access to api.imf.org.

Results (tables, figures, intermediate files) are written to the `output` folder set in `config.yaml`, outside the repository.

## Status

- [x] Repository and configuration
- [x] Strand 1: literature review (verdict: gravity unsuitable for aggregate short-term forecasts; see review)
- [x] Strand 2: method review and code (tested on synthetic data)
- [x] Strand 2: run on BACI and interpret (see results_strand2.md)
- [x] Strand 1: gravity forecasts against benchmarks (done, see results_strand1.md)
