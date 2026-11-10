# Handover

State of the project as of 2026-11-10, for a new chat session. Read this first, then
README.md and the results reports (results_strand1.md, results_strand2.md, results_strand3.md).

## Owner and working style

- Wolf-Fabian Hungerland, economist (BMWE, unit IC1). No git or command-line background:
  give step-by-step instructions ("Anleitung für dumme"), one command per code block.
- Chat in German, short, result first, no long dashes. Code and repository docs in English.
- Offer open decisions as clickable questions. Larger tasks: short plan first.
- Local runs on his Windows PC: Anaconda Prompt, `conda activate tradepolicy`, `cd C:\Daten`
  (scripts he downloads from GitHub via "Download raw file") or the repo folder with config.yaml.
- Never ask for or repeat passwords or tokens in chat. Credentials (Regionaldatenbank, GTA)
  are typed only on his machine.
- KRITIS restriction lifted on 2026-11-09 at his request: public OSM infrastructure may be
  shown as lines and points.

## Repositories

| Repo | Visibility | Content |
|---|---|---|
| wfhungerland/tradepolicy | private | analysis code and reports (this repo), branch main |
| wfhungerland/tradepolicy-site | public | static site "Produktraum-Monitor", GitHub Pages: https://wfhungerland.github.io/tradepolicy-site/ |
| wfhungerland/space | private | SPACE paper (German product space 1880-1913); has its own HANDOVER.md, continued in a separate chat |
| wfhungerland/konjunkturmonitor | | footer link to the Produktraum-Monitor (merged) |

Commit author: Wolf-Fabian Hungerland. Pages deploys: check the Actions run "Seite veröffentlichen";
a failed run with "No artifacts named github-pages" is a GitHub glitch, re-run with workflow_dispatch.

## Data locations

- Local PC: raw data under `C:\Daten` (BACI HS92 V202601, CEPII Gravity, Comext, IMF IMTS);
  outputs in `C:\Daten\tradepolicy_output`.
- Hetzner server, mapped on the PC as drive X: (rclone mount, task "Laufwerk X Daten"); X:\ equals
  `/srv/daten/claude-daten` = `https://newswolf.eu/claude-daten/` for cloud sessions (basic auth
  via the environment secret; never print it). Upload rule: files appear as `*.partial` while copying.
- On the server: `scenarios/icio` (OECD ICIO 2016-2022 small), `kreise/` (MaStR, Regionaldatenbank
  tables 42111-04-01/02-4), `osm/` (64 files, power/rail/motorway/substations per Land), `gta/`
  (full GTA export, interventions.csv), `Regionen/` (Rosés-Wolf v7, INKAR 2021/2022/2024/2025).
- Cloud session copies: raw in /home/user/scen_raw, outputs in /home/user/scen_out (ephemeral).

## Done (main results in results_strand3.md)

1. Strand 1 gravity nowcasting, strand 2 economic complexity (results_strand1/2.md).
2. Strand 3 Caliendo-Parro scenarios: US tariffs, EU single market, transport, China dependencies,
   import elasticities and ESCAP comparison, China competition (Schott), zero trade (HMR), trade by
   regime type, Mittelstand, migration, defence alliances, business systems (Witt et al.).
3. Regional modules (scripts 64-78): NUTS 2 exposure, ARDECO history and cohesion RDD, ports;
   districts: MaStR energy, broadband/mobile, OSM infrastructure densities and zoomable line map,
   export ratios (Regionaldatenbank), US tariff exposure by district, INKAR profile of exposed
   districts (exposed districts are rich industrial ones); hydrogen core network and grid expansion
   (BNetzA); Rosés-Wolf regional GDP 1900-2021.
4. Subsidies (75, 76): GTA full export; raw finding (Chinese subsidies concentrate on goods where
   Germany faces Chinese price pressure) is a size effect and disappears within HS chapters.
5. Site views: Überblick, Länder, Länderprofil, Produktraum, Branchen, Abhängigkeiten,
   China-Wettbewerb (with subsidies), Null-Handel, Regierungsform, Mittelstand, Regionen
   (EU and district maps, network map, hydrogen and grid charts, INKAR table), Szenarien,
   Prognosetest, Methodik; DE and EN. Monthly US tariff update via tradepolicy-site/.github/workflows/update-tariffs.yml.
6. KM handover prompt (HANDOVER_KM_extensions.md), data requests (DATA_REQUESTS.md).

## Open

- Local reproduction of strand 3 on the owner's PC (guide given in chat on 2026-11-10):
  `python run_strand3.py`, about 6 GB free on C:, ICIO copied from X:\scenarios\icio to
  C:\Daten\scenarios\icio, config.yaml keys `scenarios` and `yotov_guide`; success = "82 of 82
  values reproduced" (still 82 of 82 in the cloud on 2026-11-10).
- Publication permission for the methods paper: decision of the ministry, not ours.
- Ideas for INKAR (10 proposals in chat of 2026-11-10), none started.

## Not pursued or blocked

- Quality-adjusted elasticities (Feenstra-Romalis data): stopped by the owner.
- BA statistics (statistik.arbeitsagentur.de) answer 429 to cloud sessions; HU Berlin and INKAR
  pages block automated access; Overpass blocked from the cloud (use the PC script).
- Hydrogen core network and grid expansion projects have no public line geometry (BNetzA lists only).
- District industry mix within manufacturing is confidential; districts take their NUTS 2 mix.

## Known pitfalls

- Run scripts in the `tradepolicy` conda env, not `base`.
- Adding a `.fig` card to the site renumbers all later figures (links #abb-N shift).
- OSM Overpass: empty answers can come with HTTP 200; tools/pc_fetch_osm.py now retries them.
- INKAR CSV is UTF-8 inside a Deflate64 zip: read via `unzip -p`, not Python's zipfile.
- Comext month 202608 is incomplete (no intra-EU flows). IMF IMTS: keep three-letter ISO codes only.
