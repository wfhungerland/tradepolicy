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
| Eurostat Comext, German exports by SITC, monthly and annual 1996-2019 | Eurostat | Strand 1 benchmarks | `comext` |

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

Results (tables, figures, intermediate files) are written to the `output` folder set in `config.yaml`, outside the repository.

## Status

- [x] Repository and configuration
- [ ] Strand 1: literature review
- [ ] Strand 2: method review, RCA, ECI/PCI, proximity, density, COI, Germany analysis
- [ ] Strand 1: gravity forecasts against benchmarks
