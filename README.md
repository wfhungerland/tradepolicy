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
| `50_china_competition.py` | competition of German and Chinese exports by HS6 good: export similarity, unit-value gap, quality-ladder length (BACI HS92) |
| `51_export_china_competition.py` | exports the competition analysis as competition.json for the site |
| `52_zero_trade.py` | zero-trade matrices (Helpman, Melitz and Rubinstein 2008): country level (IMF IMTS 1990-2024) and HS sections, HS2, HS4, HS6 (BACI HS92 1995-2024) |
| `53_zero_trade_figures.py` | matrix pages (median, mean, five periods), Germany bars, XLSX; copies in `figures/zero_trade/` |
| `55_zero_trade_compare.py` | trade breadth of every country plus EU27 and euro-area member means, comparison figures |
| `56_trade_by_regime.py` | trade, trade breadth and dependencies by partner regime (V-Dem v16) and UN voting alignment (Bailey, Strezhnev and Voeten); figures in `figures/regime/` |
| `57_export_regime.py` | exports trade by regime for the site (regime.json) |
| `58_mittelstand.py` | SMEs in trade (Eurostat TEC): shares by partner and activity, exposure to US tariffs, Chinese price pressure and imports from China |
| `59_export_mittelstand.py` | exports the SME analysis for the site (mittelstand.json) |
| `60_world_shares.py` | yearly world export shares of China and Germany by HS6 (BACI HS92) |
| `61_migration_gravity.py` | migrant networks in structural gravity (UN DESA migrant stocks, ITPD-E, PPML with pair effects) |
| `62_defense_alliances.py` | defence procurement by supplier origin (Kiel tracker) and friend-shoring test with UN alignment and alliances (ATOP, NATO) |
| `63_business_systems.py` | trade by business system and institutional distance (Witt et al. 2018, 61 economies), gravity with institutional distance |
| `regional.py` | helpers for NUTS maps (GISCO geometries, Eurostat TSV reader, choropleths, SVG paths) |
| `64_regional_exposure.py` | regional exposure (NUTS 2) to US tariffs, a Chinese supply stop and Red Sea rerouting (shift-share), energy-intensive employment |
| `65_regional_history_cohesion.py` | regional GDP per head 1980-2024 (ARDECO, NUTS 2/3), EU cohesion payments and the 75 % threshold (RDD), seaports |
| `tools/server_fetch_kreise.py` | runs on the user's server: Marktstammdatenregister aggregated to districts, Regionaldatenbank tables via the GENESIS web service (credentials stay on the server) |
| `66_kreise_energy.py` | electricity capacity by German district 1990-2026 (Marktstammdatenregister via the server script), maps |
| `67_kreise_netze.py` | gigabit broadband (households, industrial estates) and mobile coverage along railways and motorways by district (Breitbandatlas) |
| `68_kreise_infra.py` | extra-high-voltage and 110 kV lines, substations, electrified rail share and motorway density by district (OpenStreetMap, fetched with `tools/pc_fetch_osm.py`; aggregates only) |
| `69_h2_kernnetz.py` | hydrogen core network (BNetzA approval 2024): new-build and conversion km by Land and planned commissioning year |
| `70_netzausbau.py` | transmission grid expansion (EnLAG, BBPlG): km by status and planned commissioning, BNetzA monitoring Q2/2026 |
| `71_netz_lines.py` | OSM line and point layers (power lines by voltage, substations, rail, motorways) for the zoomable site map |
| `72_export_energienetze.py` | site data for the hydrogen core network and grid expansion charts |
| `73_kreise_export.py` | manufacturing export ratio and foreign sales per inhabitant by district, 1999-2024 (Regionaldatenbank 42111-04-01/02-4) |
| `74_kreise_us_tariffs.py` | US tariff exposure of manufacturing by district: NUTS 2 industry mix scaled by the district export ratio |
| `75_subsidies.py` | harmful subsidies (Global Trade Alert, MAST L and P) by implementer and year; targeted Chinese subsidies on goods under Chinese price pressure |
| `76_subsidies_regression.py` | PPML: targeted Chinese subsidies on goods under price pressure, with HS chapter/heading effects and size controls |
| `77_roses_wolf.py` | regional GDP per head in Western Europe 1900-2021 (Rosés-Wolf database v7): index, sigma and beta convergence, rank persistence, maps |
| `78_kreise_profile.py` | INKAR 2025 profile of districts by quintile of US tariff loss per inhabitant (income, unemployment, industry share, age, education, votes) |
| `79_inkar_analyses.py` | ten INKAR district analyses (skilled labour, demography, municipal finances, AfD vote change, broadband, industrial decline, accessibility, migration, land use, poverty) for the site tab Kreise |
| `80_grw.py` | GRW regional aid areas 2022-2027 (BBSR municipal reference 2023) for the tariff-exposed and double-risk districts |
| `81_kreis_steckbrief.py` | district profile for the site tab Kreis-Steckbrief: 31 indicators with German median and rank |
| `82_services.py` | German trade in services (OECD TiS): types, partners, goods and services balance with the US, digital imports from the US and Ireland |
| `83_critical_materials.py` | raw materials under Chinese export controls (2023-2025): German imports, China share, suppliers (BACI HS22) |
| `84_fdi.py` | German FDI with the US and China (OECD FDI statistics): outward stocks and flows, inward by ultimate investor |
| `tools/pc_fetch_osm.py` | runs on the user's PC: power lines, substations, rail lines and motorways from OpenStreetMap (Overpass) per Land |
| `54_export_zero_trade.py` | exports the matrices for the site (zerotrade_*.json) |
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
