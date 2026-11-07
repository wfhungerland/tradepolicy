# Handover

State of the project as of 2026-11-05, for a new chat session. Read this first,
then README.md, results_strand1.md, results_strand2.md and data_inventory_gravity.md.

## Owner and working style

- Wolf-Fabian Hungerland, economist (BMWE, unit IC1). No git or command-line
  background: give step-by-step instructions with short explanations.
- Chat in German, short, result first. Code and repository docs in English.
- Offer open decisions as clickable questions. Larger tasks: short plan first, wait for OK.
- Long computations run locally on his Windows PC: Anaconda Prompt, `conda activate tradepolicy`,
  repo folder with `config.yaml` (not in git). Stata is available.
- Never ask for or repeat passwords or tokens in chat.

## Repositories

| Repo | Visibility | Branch | Content |
|---|---|---|---|
| wfhungerland/tradepolicy | private | main | analysis code and reports (this repo) |
| wfhungerland/tradepolicy-site | public | main | static site "Produktraum-Monitor", GitHub Pages: https://wfhungerland.github.io/tradepolicy-site/ |
| wfhungerland/konjunkturmonitor | | PR via branch | footer links to the Produktraum-Monitor (merged) |

Commit author: Wolf-Fabian Hungerland <w.f.hungerland@gmail.com>.

## Data locations

- Local PC: raw data under `C:\Daten` (BACI HS92 V202601, CEPII Gravity V202211 .dta,
  Comext bulk, IMF IMTS). Outputs in `C:\Daten\tradepolicy_output`.
- Hetzner server (mapped as drive X: via rclone): `/srv/daten`. The owner mirrors outputs with
  `robocopy C:\Daten\tradepolicy_output X:\tradepolicy_output /MIR` (run on Windows, not on the server).
- Cloud sessions read the server at `https://newswolf.eu/claude-daten/` (Caddy, basic auth).
  The credential sits in the environment secrets; the proxy adds it. Do not print it.

## Done

1. Strand 1, gravity nowcasting (scripts 10 to 13, forecast.py): three-way FE PPML forecasts
   lose against AR. Germany: RMSE 19 to 27 % above AR at 1 to 6 months. World: about equal
   short term, ratio 1.18 at 6 months. See results_strand1.md.
2. Strand 2, economic complexity (scripts 01 to 07, complexity.py, panel.py): Germany falls
   from ECI rank 2 (1995) to 5 (2024), fixed-PCI complexity roughly flat (1.98 to 1.94),
   robust across specs, GENEPY, HS6, Atlas comparison. See results_strand2.md.
3. Public site built from `20_export_site.py` output (copy `site_data` to `site/data` in
   tradepolicy-site), with imprint and privacy pages, self-hosted fonts, no cookies or localStorage.
4. Shared German summary page of both strands: https://claude.ai/artifact/HgXQY1BwernM86cQz2dEfb
5. Data inventory for gravity scenario analysis (tariffs, trade agreements, transport costs):
   data_inventory_gravity.md. Each fact carries a verification tag.

## Open

1. Data inventory verified on 2026-11-05: 114 of 160 facts checked on official pages, the rest
   mostly blocked by www.oecd.org (refuses automated requests). Download URLs are in the file.
2. Strand 3 built (2026-11-06): US tariff and EU single market scenarios (scripts 30 to 37,
   results_strand3.md), shown on the site under Szenarien. Open: retaliation, MAcMap baseline
   tariffs for non-US countries, transport cost shocks, price convergence (Head and Mayer 2021).
   Policy brief (German, Claude Docs): https://claude.ai/artifact/CRtTJnuC6yZ5VfRja4QLUf
   Former note: structural gravity scenarios (GE-PPML) for tariffs, EU integration and
   transport cost shocks. Likely core data: ITPD-E (with domestic flows), tariffs (Teti GTD,
   WTO IDB), Larch RTA database, OECD ITIC, CEPII ProTEE. Not yet approved.
3. Optional: link back from the Produktraum-Monitor to the Konjunkturmonitor. Not answered.

## Site status (2026-11-07)

- Views: Überblick, Länder, Länderprofil (#profil/ISO), Produktraum, Branchen, Szenarien
  (11 scenarios), Prognosetest, Methodik; German and English (site/en/), one app.js
  (L(de, en) helper, BASE path prefix).
- Look and feel follow the Konjunkturmonitor (ten rules): question headings with answer
  sentences, numbered figures with italic side notes, downloads XLSX/PPTX/PNG/CSV per
  figure (PptxGenJS, SheetJS, self-hosted in site/lib), file names "Produktraum-Monitor
  (date, Abb. NN) short title".
- Monthly update of the US tariff scenarios: tradepolicy-site/.github/workflows/update-tariffs.yml
  (6th of each month), code in tradepolicy-site/update/, assets built here by 41_update_assets.py.
  Rebuild assets after any baseline change (scripts 33, 34, 39) and copy to update/assets.
- Policy brief (Claude Docs) mentions profiles, downloads and the monthly update.

## On hold (Wiedervorlage)

- Local reproduction of strand 3 on the owner's PC: `python run_strand3.py`, needs about
  4.5 GB on C: and 30 to 60 minutes; config.yaml needs the keys `scenarios` and `yotov_guide`
  (see config.example.yaml); success = "82 of 82 values reproduced". Postponed on 2026-11-06
  for lack of time and disk space.

## Known pitfalls

- Run tests and scripts in the `tradepolicy` conda env, not `base`.
- github.io is blocked from cloud sessions; check Pages deploys via the Actions runs.
- Comext month 202608 is incomplete (no intra-EU flows).
- IMF IMTS returns aggregate codes (e.g. TX899): keep only three-letter ISO codes.
