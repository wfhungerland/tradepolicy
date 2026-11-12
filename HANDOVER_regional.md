# Handover: regional exposure work (districts, Kreise)

State as of 2026-11-11 (updated after robustness and Gewerbesteuer work), for a new chat that deepens the regional exposure analysis.
Read this file first, then the section "Regions" onward in results_strand3.md and HANDOVER.md
(general working style, data locations, pitfalls).

## Owner and working style (short)

- Wolf-Fabian Hungerland, economist, BMWE unit IC1. No git or command-line background:
  step-by-step instructions, one command per code block.
- Chat in German, short, result first, no long dashes; code and repository docs in English.
- Open decisions as clickable questions; larger tasks start with a short plan.
- Never ask for or print passwords or tokens. Credentials (Regionaldatenbank/Destatis GENESIS,
  GTA) are typed only on his PC (environment variables GENESIS_USER, GENESIS_PASSWORD).
- KRITIS restriction lifted by the owner: public OSM infrastructure may be shown as lines.

## Core result

US tariffs hit prosperous industrial districts, not structurally weak ones. The modelled
manufacturing output loss (about 34 bn EUR a year, median district -1.5 %) correlates with
industry employment per working-age inhabitant (Spearman 0.67), GDP per head (0.47) and
earnings (0.42), not with unemployment (-0.10). Regional aid (GRW) targets other places:
only 13 % of the loss falls in GRW C areas, 32 % in C or D areas. Local business tax
(Gewerbesteuer) is the main fiscal channel: 1,269 EUR per inhabitant in the most exposed
fifth versus 599 in the least. 26 "double-risk" districts combine high loss with population
decline or high SGB II rates.

## Method

1. Caliendo-Parro scenario (strand 3) gives output changes by country and sector.
2. NUTS 2 shift-share: m_r = sum_s (L_rs / L_r) * dY_s with Eurostat sbs_r_nuts2021
   manufacturing mix (scripts 64, 65).
3. Districts (script 74): dY_k = m_r * q_k / q_r, with q = manufacturing export ratio
   (Regionaldatenbank 42111-04-02-4, establishments with 20+ employees, script 73); loss
   V_k = -dY_k * U_k (U = manufacturing turnover). The district industry mix is confidential,
   so each district inherits its NUTS 2 mix. This is the main weakness.
4. Profiles and associations with INKAR 2025 (scripts 78, 79): quintiles of loss per
   inhabitant, OLS with Land effects, robust s.e., standardised regressors. Associations only.
5. GRW status (script 80): BBSR Raumgliederungen Referenz 2023, municipality status, split
   municipalities counted in equal parts, population-weighted to districts.

## Scripts (repo wfhungerland/tradepolicy, branch main)

| Script | Content |
|---|---|
| 64_regional_exposure.py, 65_regional_history_cohesion.py | NUTS 2/3 exposure, ARDECO history, cohesion RDD |
| 66_kreise_energy.py | MaStR capacities by district |
| 67_kreise_netze.py, 68_kreise_infra.py, 71_netz_lines.py | broadband, OSM infrastructure densities and line layers |
| 69_h2_kernnetz.py, 70_netzausbau.py, 72_export_energienetze.py | hydrogen core network, grid expansion |
| 73_kreise_export.py | export ratio by district 1999-2024 |
| 74_kreise_us_tariffs.py | US tariff loss by district |
| 77_roses_wolf.py | Rosés-Wolf regional GDP 1900-2021 |
| 78_kreise_profile.py | INKAR profile of exposed districts |
| 79_inkar_analyses.py | ten INKAR analyses (skilled labour, demography, municipal finances, votes, broadband, industrial decline, accessibility, migration, land use, poverty) and kreise_inkar_map.json |
| 80_grw.py | GRW aid areas versus exposure |
| 81_kreis_steckbrief.py | district profile, 31 indicators with median and rank |
| 86_kreise_robustness.py | seven downscaling and scenario variants versus the baseline (kreise_robust.json) |
| 87_kreise_gewerbesteuer.py | Gewerbesteuer elasticity (district panel) and tax loss by district (kreise_gewst.json) |
| 88_regional_paper_figures.py | four figures of the working paper (paper/figures_regional) |
| 89_kreise_impute.py | imputes the 14 suppressed districts from Regierungsbezirk residuals (variant, not on the site) |
| 90_amr.py | losses by BBSR labour market region (223), fig5, site data kreise_amr.json |
| 91_decomposition.py | loss = manufacturing intensity x tariff intensity; uniform benchmark shock (fig6, table 7) |
| tools/build_regional_paper.py | fills paper/regional_paper_template.md with result tables, builds md, HTML and PDF |
| tools/scenario_from_site.py | rebuilds German scenario outputs from site/data/scenarios.json when the model cannot run |
| regional.py | shared helpers, kreis_names() disambiguates duplicate names, rdb_kreise() reads 42111 panels |
| tools/server_fetch_kreise.py | Regionaldatenbank/Destatis downloads (run on the PC, --start, --destatis) |
| tools/pc_fetch_osm.py | Overpass downloads (run on the PC) |

Data: X:\kreise (MaStR, Regionaldatenbank), X:\osm, X:\Regionen (INKAR 2021-2025,
Rosés-Wolf v7, BBSR Raumgliederungen). INKAR zip uses Deflate64: read with `unzip -p`;
Kennziffer has 8 digits, district AGS = first 5.

## Site (wfhungerland/tradepolicy-site, public)

- https://wfhungerland.github.io/tradepolicy-site/ tabs "Regionen" (EU maps, network map,
  hydrogen, grid), "Kreise" (11 analysis blocks, 20 stacked map cards, no dropdown, by
  owner's wish) and the district profile, route #steckbrief/<NUTS3> (click on any map).
- Data in site/data/kreise_*.json, netz_*.json, regional_*.json, roses_wolf.json.
- Quarterly update: .github/workflows/update-kreise.yml (cron 15 Jan/Apr/Jul/Oct, parts
  mastr, osm, netzausbau, steckbrief; own concurrency group, only deploy in group "pages").
  The second GitHub run was still to be checked (MaStR and OSM parts).
- app.js is loaded as app.js?v=...; raise the version after every change.

## Memo

Wirtschaftsdienst-style analysis "US-Zölle: Getroffen sind die starken Industrieregionen"
(Claude Docs): https://claude.ai/artifact/UjmiSFCwCP58NFK9YvxoEu. Sections: regional
effects, method and data (formula), who loses (figure 1), rich industrial districts (table 1),
local business tax channel (table 2), double risks (table 3, 26 districts), little overlap with
regional aid (table 4), limits, policy conclusions, references, English abstract
(JEL F13, F14, R12, H71).

## Done in the deepening chat (2026-11-11)

- Robustness (86): results hold. Rank correlation with the baseline 0.87 to 1.00; 42 districts in the
  top fifth under all seven variants; GRW, profile and Gewerbesteuer gaps barely move.
- Gewerbesteuer (87): elasticity to district manufacturing sales about 0.2 (0.43 in the most industrial
  third); tax loss 0.3 bn EUR a year (1.2 bn with elasticity 1), concentrated in rich places.
- Working paper (English): paper/regional_paper.md/.html/.pdf, 14 pages, built from the template;
  adds a 95 % band for the tax loss (0.19 to 0.42 bn EUR) and a placebo with next year's sales (0.08, n.s.).
  The 14 suppressed districts (Wolfsburg, Ingolstadt, Dingolfing-Landau, Böblingen ...) are imputed in 89:
  loss 38.1 instead of 34.0 bn EUR; Wolfsburg 13,600 EUR per inhabitant, first. Used as variant 8.
- Site JSON files kreise_robust.json and kreise_gewst.json are written but not yet shown on the site.
- Cloud rebuild without the model: WITS concordances answer 403 to cloud sessions, so
  tools/scenario_from_site.py rebuilds the German sector outputs; 74 then reproduces 34.0 bn EUR.
  Data for a fresh session: X:\kreise (rdb, mastr), X:\Regionen\inkar_2025.zip (district rows
  extracted to inkar/inkar_2025_kreise.parquet, read as latin1), Eurostat sbs_r_nuts2021, GISCO NUTS 2021/2024,
  Destatis 04-kreise.xlsx.

- Panel review (/review, 2026-11-11) priorities still open: validation with 2025/26 data, US share by Land,
  net tax loss after fiscal equalisation by Land, firm layer for the top ten (labour market regions done: 90).

- Overleaf: tools/build_regional_paper.py also writes paper/overleaf (main.tex, tables/*.tex, figures, latexmkrc for
  XeLaTeX); compiled locally without errors (16 pages). To be pushed to a separate paper repo for Overleaf GitHub sync.

## Waiting for the owner

- PC downloads: 42111-04-02-4 again (2025 values), search "Gewerbesteuer" in the Regionaldatenbank,
  Destatis 51000-0034 with --start 2008 (US share by Land, robustness variant and Länder section).
- BA request (DATA_REQUESTS.md, section 1, plus short-time work by district 2025/26).

## Known limits (candidates for deepening)

1. District industry mix inherited from NUTS 2; within-region variation comes only from the
   export ratio. Options: BA employment by WZ and district (request via BA statistics service,
   cloud sessions get 429), Destatis Unternehmensregister, or firm data (Orbis/Bureau van Dijk
   via the ministry).
2. Export ratio covers establishments with 20+ employees only; 14 districts missing in 2024.
3. No direct US export share by district; the shock assumes the national destination mix.
4. Static first-round effect; no input-output spillovers across districts, no labour mobility.
5. Associations, not causal effects (votes, finances); exposure proxies car-industry sites.
6. Double-risk list depends on thresholds (top fifth loss; -5 % population to 2045;
   SGB II >= 10.2 %).

## Open ideas

- Validation: compare the district loss with actual 2025/26 developments (industry turnover
  from Regionaldatenbank 42111, short-time work, Gewerbesteuer receipts).
- Robustness: alternative downscaling weights (employment instead of turnover; US share by
  Land from Destatis 51000-0034 once the owner downloads it with --start 2008 to X:\kreise).
- Bundesländer trade section (waits for that Destatis download).
- Municipal finance scenario: Gewerbesteuer loss per district under the tariff shock.
- Labour market: commuting zones (BBSR Arbeitsmarktregionen) instead of districts.
- Paper version of the memo (methods appendix, robustness tables).
