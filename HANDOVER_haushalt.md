# Handover: public spending and federal budget (tab "Staatsausgaben")

State as of 2026-11-12, for a new chat that continues the work on government spending.
Read this file first, then results_public_spending.md and HANDOVER.md (working style, data
locations, pitfalls).

## Owner and working style (short)

- Wolf-Fabian Hungerland, economist, BMWE unit IC1. No git or command-line background:
  step-by-step instructions, one command per code block.
- Chat in German, short, result first, no long dashes; code and repository docs in English.
- Open decisions as clickable questions; larger tasks start with a short plan.
- Never ask for or print passwords or tokens.
- Design wishes stated by the owner: sober, Bauhaus-like, "form follows function", clarity of
  the Konjunkturmonitor; nothing playful; Tufte principles (direct labels, no legends where
  avoidable, little non-data ink, finding in the title). Colour must carry meaning and stay
  consistent across charts.

## Where things are

- Repo wfhungerland/tradepolicy (private, branch main):
  - 86_cofog.py: Eurostat COFOG (gov_10a_exp) for general government and the four
    subsectors, 1995-2024; groups (second level) for general government from 2000;
    population demo_gind; deflator of government final consumption (nama_10_gdp P3_S13),
    prices of the latest year. Writes site/data/cofog.json.
  - 87_bundeshaushalt.py: federal budget by function plan. Input folder X:\Haushalt
    (server path /srv/daten/claude-daten/Haushalt, cloud: https://newswolf.eu/claude-daten/Haushalt/):
    HH_<year>_ALL.csv (Soll by title with function code, 1,000 EUR; HH_2027_RegE_ALL.csv is
    the government draft), HR<year>.xlsx (Ist by title, EUR), "Gesamtplan und
    Uebersichten*.pdf" and Vorspann_2026.pdf (function names from the Funktionenübersicht,
    pdftotext). Writes site/data/bund.json.
  - results_public_spending.md: findings and method notes.
- Repo wfhungerland/tradepolicy-site (public, GitHub Pages):
  https://wfhungerland.github.io/tradepolicy-site/#staat
  - site/app.js: renderState() and helpers slopegraph, sparkTable, squarify, nestedTreemap,
    barMatrix, lineDirect, bundTree; colours DIV_HUE (COFOG functions) and HF_HUE (federal
    main functions); tint() for group shades.
  - site/index.html and site/en/index.html: section view-staat (DE and EN).
  - update/update_cofog.py + .github/workflows/update-kreise.yml: quarterly Eurostat refresh.
  - Raise app.js?v=... (and style.css?v=...) after every change, or browsers keep old files.

## What the tab shows (figure numbers as on the site)

1. Abb. 28 slopegraph of shares of general government spending, columns 2000, 2019, 2024 on a
   time scale, axis break between about 17 and 40 %. 2019 is the last pre-crisis year, not a
   peak (peaks: social protection 43.6 % in 2005, health 17.0 % in 2022).
2. Abb. 29 table with sparklines: EUR per head 2024, index 2000 = 100 on one scale, change since
   2019, share.
3. Abb. 30 "Grundriss der Staatsausgaben": nested treemap (10 functions, 69 groups), one hue per
   function, fixed tints per group by COFOG code; click to zoom; click a group in the zoom view
   to pin it top left (black frame); year slider 2000-2024; play button with smooth
   interpolation; total area grows with real spending (dashed frame = peak).
4. Abb. 31 bar matrix: functions x levels (federal, Länder, municipalities, social security),
   one scale; values by level include transfers between levels (sum exceeds the consolidated
   total by 14-24 %).
5. Abb. 32 federal spending per head by function (COFOG), direct labels.
6. Abb. 33 "Grundriss des Bundeshaushalts": treemap by function plan, three levels (main,
   upper, function), buttons 2024 Ist, 2025 Ist, 2026 Soll, 2027 Entwurf. Core budget only:
   474.8 / 495.7 / 524.5 / 555.4 bn EUR. Special funds (climate and transformation fund,
   Bundeswehr fund and others) and EU own resources are excluded and named in the source line
   (2025: 133.6 bn, 2026: 169.7 bn, 2027: 177.6 bn). Negative plan items (global spending cuts)
   are not drawn and named in the source line.

## Known limits and open ideas

1. bundeshaushalt.de blocks automated downloads (bot protection); new budget years must be
   downloaded by the owner into X:\Haushalt. Several PDFs arrived broken (*.part, 0 bytes);
   the CSV and XLSX files were intact and are all the script needs.
2. Done 2026-11-12: Abb. 33 selector split into "Ergebnis (Ist)" and "Plan (Soll)"; source line
   says outturn and plan are only partly comparable.
3. Federal history is short (2024-2027). Older budget years (CSV and Haushaltsrechnung) would
   allow a federal time series and a film like Abb. 30.
4. Done 2026-11-12: checkbox "mit Sondervermögen" in Abb. 33 adds the special funds in FUNDS
   (87_bundeshaushalt.py), hatched; payments into funds and between them (10 bn a year from the
   infrastructure fund to the climate fund) are netted out. EU own resources, EU pass-through funds,
   NATO programme, agency budgets and pension reserves stay out. HR2024.xlsx has no fund chapters,
   so 2024 has no funds.
5. Other cuts: by Einzelplan (ministry) or by economic type (Gruppierungsplan: personnel,
   investment, transfers); comparison plan versus outturn per function.
6. Done 2026-11-12: RENAME in 87_bundeshaushalt.py updates outdated names (251 Bürgergeld) and
   shortens long ones; MERGE draws the range upper functions 11-12 and 18-19 as one block (bund.json
   key "merge", used by bundTree). Functions without own name still take the upper function's name.
7. COFOG is updated by Eurostat once a year; the quarterly workflow refreshes it.
