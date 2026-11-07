# Strand 3: US tariff scenarios (first results, 2026-11-06)

Model: Caliendo and Parro (2015), static, in changes (`gravity_ge.cp_solve`),
OECD ICIO 2025, base year 2022, 81 economies, 50 sectors; US applied tariffs from
CEPII (Guimbard 2026) aggregated to ICIO sectors with 2024 US import weights;
tariff revenue rebated, deficits fixed, no retaliation, tariffs of other
countries zero in the baseline. Scripts 33 and 34. Runtime about 25 seconds.

## Main results (central case: ProTEE sector elasticities, capped at 15)

| Scenario (US tariffs at) | Germany real income | Germany exports to US | EU27 real income | US real income |
|---|---|---|---|---|
| 10 Apr 2025 (peak) | -0.10 % | -12.8 % | -0.05 % | -0.53 % |
| 5 Sep 2025 (EU deal) | -0.08 % | -6.8 % | -0.04 % | -0.35 % |
| 22 Aug 2026 (current) | -0.07 % | -7.4 % | -0.06 % | -0.12 % |

German sectors hit hardest at the current level: motor vehicles, machinery,
electrical equipment and electronics, each about -15 to -22 % in US sales and
-1.6 to -2.8 % in output.

Elasticity cap: ProTEE HS6 medians are product-level elasticities; sector values
above 15 (refined petroleum 66, electricity 45, metal ores 37, coal 35, other
transport 23, pharmaceuticals 21 and others) are capped at 15 (decision of
2026-11-06). Uncapped ProTEE, uniform 4 and uniform 8 are reported as sensitivity.

## Check 1: rise of EU exports to the US in the September 2025 scenario

EU exports to the US rise by 1.4 % in the central case (2.9 % with uncapped
elasticities, USD 718 to 739 bn) although German exports fall by 6.8 % (9.0 %
uncapped). Decomposition by sector (uncapped run, where the effect is largest):
- falls where EU goods face tariffs: motor vehicles (-24 bn), chemicals (-22 bn),
  food (-12 bn), machinery (-9 bn);
- rises where EU goods are nearly tariff-free while competitors (China at 44 %,
  India at 38 %) are not: pharmaceuticals (+29 bn, US tariff 0.5 %), refined
  petroleum (+31 bn, 0.4 %), aircraft and other transport (+15 bn, 1 %),
  professional services (+20 bn, no tariffs).

By country, Ireland (+13 bn), France (+11 bn) and Belgium (+6 bn) gain, Germany
(-14 bn), Austria and Italy lose. The rise is trade diversion, not a coding
error. It is amplified by high ProTEE elasticities in some sectors (refined
petroleum 66, pharmaceuticals 21, other transport 23), but it survives all
elasticity variants: +0.8 % (uniform 8) to +2.1 % (uniform 4); with ProTEE
capped at 15 it is +1.4 %. At the current tariff level (pharmaceuticals now
taxed at 5 %) EU exports to the US fall in every variant (-1.4 to -5.3 %).

## Check 2: plausibility against observed data and literature

| Check | Model | Reference | Verdict |
|---|---|---|---|
| No-shock run reproduces baseline | exact | | passes (tests) |
| One-sector limit equals one-sector tariff model | exact | | passes (tests) |
| NAFTA example of Yotov et al. (2016) | RTA coefficient 0.5572, effects within 0.75 pp | book | passes |
| US imports from China | -24 % (current), -59 % (Sep 2025 tariffs) | -30 % in 2025 (Census, as reported by news and PIIE) | plausible: model is long-run, 2025 mixed tariff levels over the year |
| US tariff revenue | USD 183 to 280 bn a year before the MAcMap baseline, 192 to 256 bn after | USD 195 bn in FY2025 (CRFB from Monthly Treasury Statement), tariffs only partly in force that year | right order of magnitude |
| Sign of US welfare without retaliation | -0.6 to +0.04 %, positive only with low elasticity | small gain without retaliation (Ignatenko et al. 2025, JIE) | consistent in direction for low elasticities; our central case is more negative because of high sector elasticities |
| Germany | -0.07 to -0.09 %, robust to elasticity | | small, as expected for a 6 to 9 % average tariff on about 4 % of German output |

Sensitivity of the German result to the elasticity is small (-0.068 to -0.091 %),
the US result is not (-0.42 to -0.11 % in Sep 2025). Elasticity choice matters
mainly for the US and China.

## Known limits

- Baseline tariffs of all countries other than the US are zero (MAcMap not yet used).
- No retaliation, no deficit adjustment, static (no capital, no dynamics).
- 2022 trade structure; ICIO country coverage puts small exporters into ROW.
- ProTEE HS6 medians are product-level elasticities; at sector level they are
  likely too high for some sectors (refined petroleum, mining, electricity).


# EU integration (2026-11-06)

## Border effects with flows to self (Head and Mayer 2021 method)

Script 35: PPML on import shares, pair, exporter-year and importer-year fixed
effects, year-specific dummies for EU-to-EU, non-EU-to-EU and non-EU-destination
border flows; ITPD-E R2025, 2000-2019, balanced countries with domestic flows,
China, Japan and Taiwan excluded (domestic-flow breaks); eps = 5.

| Sector (countries) | EU to EU | non-EU to EU | to non-EU |
|---|---|---|---|
| Manufacturing (52) | -2.9 % (2000) to -14.5 % (2019) | 0 to -9.5 % | 0 to -6.7 % |
| Agriculture (86) | -18.4 % to -28.2 % | -11.4 % to -15.7 % | 0 to -14.5 % |
| Mining and energy (34) | noisy, no clear trend | | |
| Services (45) | not estimated: fixed-effect demeaning does not converge | | |

Changes in trade costs relative to non-EU destinations in 2000. Check against
Head and Mayer (2021, Figure 1, goods): over 2000-2018 their EU-to-EU costs fall
by roughly 8 to 10 points (read off the figure), ours by 11.6 points in
manufacturing; outsiders' access to the EU also improves in both ("no Fortress
Europe"). Our levels start from 2000 and are identified only from accessions
since then, so they do not measure the full EU effect.

## Scenarios (script 36, same Caliendo-Parro model, ICIO 2022, EU27)

| Scenario | Shock | Germany | EU27 | Intra-EU trade |
|---|---|---|---|---|
| No single market | intra-EU gravity coefficient -1.1 for goods (Head and Mayer 2021), -0.18 for services (Mayer, Vicard and Zignago 2019) | -1.48 % | -1.91 % | -40 % |
| Trend to 2030 | ten more years of the 2000-2019 trend in intra-EU goods integration (+0.04 a year) | +0.77 % | +0.95 % | +18.5 % |
| Deeper services market | services EU effect up to the goods level on a comparable sample (+0.14) | +0.22 % | +0.29 % | +5.4 % |

Real income changes. Smaller, more open members gain or lose most (Ireland,
Poland, Netherlands); third countries barely move (US within 0.01 %).
Limits: services effect from the literature, not estimated here; the trend
scenario extrapolates a linear path.


# Transport cost shocks (2026-11-06)

Script 38 with sea_routes.py. Shortest sea routes between the main ports of the
80 ICIO economies in the marnet network (searoute data, Arctic passages closed),
with and without the Red Sea (Suez and Bab el-Mandeb) or the Panama Canal.
Europe-Asia routes get 12 days longer on average when the Red Sea is closed
(Germany 10 to 14 days, Mediterranean ports up to 25 days); Hamburg-Ningbo
grows from 19,868 to 25,584 km (+29 %).

Calibration. Goods trade on longer routes falls with an elasticity of 0.5 with
respect to sea distance (Feyrer 2021, JDE, closure of the Suez Canal 1967-75:
about half the cross-sectional estimate; the 0.5 figure is from the working
paper summary, search snippet only), upper variant 1.0. In general equilibrium
the model gives 0.43. A first version with time costs of 0.6 to 2.1 % per day
(Hummels and Schaur 2013) implied 2.5, five times Feyrer, and was dropped: it
treats all goods as seaborne and as time-sensitive as parts.
Red Sea 2024: half of the full shock; Suez transits fell from about 26,000 ships
(2023) to about 13,200 (2024), -49 % (AP data as reported by PortNews), Suez oil
flows -51 % (S&P Global). IMF PortWatch could not be queried (API quota).

| Real income, central (range) | Red Sea as 2024 | Red Sea closed | Panama closed |
|---|---|---|---|
| DEU | -0.050 % (-0.097 to -0.044) | -0.097 % (-0.182 to -0.086) | +0.003 % (+0.002 to +0.005) |
| EU27 | -0.055 % (-0.104 to -0.048) | -0.104 % (-0.192 to -0.091) | +0.002 % (+0.002 to +0.004) |
| CHN | -0.023 % (-0.047 to -0.022) | -0.045 % (-0.091 to -0.043) | -0.018 % (-0.036 to -0.017) |
| IND | -0.081 % (-0.164 to -0.076) | -0.152 % (-0.307 to -0.143) | +0.004 % (+0.003 to +0.007) |
| EGY | -0.112 % (-0.215 to -0.107) | -0.203 % (-0.390 to -0.194) | +0.000 % (-0.001 to +0.000) |
| USA | -0.009 % (-0.017 to -0.007) | -0.017 % (-0.031 to -0.014) | -0.034 % (-0.064 to -0.030) |
| JPN | -0.007 % (-0.017 to -0.006) | -0.014 % (-0.033 to -0.013) | -0.047 % (-0.092 to -0.044) |

Germany: exports on the longer routes fall by about 4 % (2024 case), most in
electronics, chemicals, electrical equipment and machinery (about -6 to -7 %).
Mediterranean and Gulf economies lose most. Not modelled: Suez Canal fees for
Egypt, freight rate spikes and capacity shortages, air freight substitution.


# Retaliation and full tariff baseline (2026-11-06)

Baseline tariffs of all importers now from MAcMap-HS6 2019 (script 39; ITC-CEPII,
HS 2007, aggregated to ICIO sectors with 2024 BACI bilateral weights; trade-weighted
averages: US 1.3 %, China 2.3 %, India 7.3 %, Brazil 8.8 %, Germany 0.8 % incl.
duty-free intra-EU trade); US row from the CEPII schedule of 1 January 2025.
All scenarios re-run: results change by at most 0.02 points for Germany and the EU
(e.g. Red Sea 2024: Germany -0.058 % instead of -0.050 %).

Retaliation (script 34): partners add, sector by sector, the increase in the US
tariff on their goods since January 2025 to their own tariff on US goods
(mirror retaliation). The EU list of July 2025 (Implementing Regulation
2025/1564, about EUR 93 bn) is suspended and not coded.

| Real income, central (range over elasticities) | US tariffs Aug 2026 | + EU mirror tariffs | + all countries mirror |
|---|---|---|---|
| Germany | -0.07 % | -0.07 % | -0.05 % |
| EU27 | -0.06 % | -0.06 % | -0.05 % |
| USA | -0.12 % (-0.16 to +0.04) | -0.13 % (-0.17 to +0.02) | -0.25 % (-0.28 to -0.14) |
| China | -0.11 % | -0.11 % | -0.10 % |

EU mirror retaliation barely changes EU welfare (tariff revenue offsets higher
prices of US goods) and costs the US about 0.01 points; global retaliation
doubles the US loss and turns its result negative under every elasticity, in line
with the direction found by Ignatenko et al. (2025). EU exports to the US fall
more with retaliation (-6.0 % instead of -4.6 %) because trade balances are held
fixed: when US exports fall, US imports must fall too.


# Ex-post check against observed US imports (2026-11-07)

Script 43. Observed US imports by partner (IMF IMTS, CIF, USD), August 2025 to July
2026 against calendar 2024, relative to total US imports (+5.2 %); model: change in
exports to the US in the scenarios of 5 Sep 2025 and 22 Aug 2026, also relative to
all partners. 67 partners, weighted by 2024 imports.

| Model scenario | Weighted correlation | Slope | Without CHE, IRL |
|---|---|---|---|
| 5 Sep 2025 | 0.43 | 0.42 | corr 0.50, slope 0.49 |
| 22 Aug 2026 | 0.11 | 0.20 | corr 0.14, slope 0.26 |
| mean of both | 0.33 | 0.48 | corr 0.39, slope 0.57 |

Without South-East Asia (VNM, THA, MYS, KHM, IDN, PHL), Switzerland and Ireland the
correlation is 0.73. Weighted sign agreement is only 0.42, as many partners sit near zero.

What the model gets: the fall of imports from China (model -32, observed -48 log points
relative), the rise of Taiwan (+60 vs +82, partly the AI server boom, not tariffs).
What it misses: strong gains of Vietnam, Thailand, Malaysia and Korea (observed +10 to
+69, model -12 to -26): relocation and transshipment out of China ("China plus one"),
which a model on the 2022 input-output structure with fixed technologies cannot
produce; Swiss gold flows and the reversal of Irish pharmaceutical front-loading; EU
countries slightly below the US total rather than above it.

Reading: the model is a long-run benchmark for the incidence of tariffs, not a forecast
of bilateral trade one year out. The slope of about 0.4 to 0.5 fits short-run trade
elasticities being well below long-run ones (Boehm, Levchenko and Pandalai-Nayar 2023).
Added to the checks on the site as "teilweise".


# Strategic dependencies (2026-11-07)

Script 44, criteria of the European Commission (2021) as summarised in CEPII Policy
Brief 2023-41: HHI of extra-EU import sources > 0.4, extra-EU imports > 50 % of all
imports, extra-EU imports > own exports. BACI HS22, 2024, HS6 (5,605 lines).

| Level | Dependent goods | Imports from outside the EU | China main supplier | via Red Sea | via Malacca |
|---|---|---|---|---|---|
| EU27 | 497 | USD 230 bn (8.3 % of extra-EU imports) | 220 goods, USD 157 bn | 74 % | 70 % |
| Germany | 593 | USD 102 bn (17.6 %) | 253 goods, USD 61 bn | 63 % | 59 % |

Check: the Commission found 137 goods in its sensitive ecosystems (2018 data); CEPII
reproduces 134 with seven sectors (2019). Our 497 cover all goods; chemicals (101),
textiles (81), machinery and electronics (41), metals (40) lead. The largest by value
are laptops, lithium-ion batteries and solar cells, all from China (85 to 98 %).

Scenario (script 45): China stops supplying the EU with these goods, implemented per
ICIO sector as an iceberg cost cutting China-EU flows by the dependent share f_j
(electrical equipment 40 %, electronics 32 %, metal ores 61 %; goods sectors only).
Real income: Germany -0.09 % (range -0.17 to -0.09), EU27 -0.07 %, China -0.04 %, US
+0.004 %. German electronics and electrical equipment expand (+2 to +5 % output) as
domestic and other suppliers replace China in the long run. The CES model lets buyers
switch; hard short-run bottlenecks cost much more, so this is a lower bound.
Criticality: dependent inputs from China are at most 2 % of costs in any German
industry (electronics 2.0 %, electrical equipment 1.4 %), direct use only.


## Indirect dependence (script 47, 2026-11-07)

Global Leontief inverse of ICIO 2022 (81 x 50 country-sectors). Chinese value added in
German output over all supply-chain stages (Johnson and Noguera 2012): 1.58 % of output
on average; 0.78 % reaches German industries through their direct purchases from China,
so about half arrives via third countries or other German industries. Highest:
electronics 7.1 %, ships 5.7 %, electrical equipment 5.4 %, textiles 4.4 %; motor
vehicles 3.3 %, of which half indirectly.

Dependent goods, including indirect supply chains (direct cost share times the
industry's ratio of total to direct-route Chinese value added): electronics 2.7 %
(direct 2.1 %), electrical equipment 2.1 % (1.5 %), ships 1.0 %, machinery 0.8 % (0.5 %),
motor vehicles 0.7 % (0.4 %); economy-wide 0.32 % instead of 0.17 % direct. The
multiplier approach assumes that the indirect Chinese inputs have the same dependent
share as the direct ones; it is an approximation.

## Import demand elasticities (script 48, 2026-11-07)

Own estimates of the elasticity of substitution between supplier countries, HS6 good by
good, after Feenstra (1994) and Broda and Weinstein (2006), with the LIML refinement of
Soderbery (2015). Data: BACI HS92 V202601, 2012-2024, unit values in USD per ton. EU27:
imports from outside the EU; Germany: imports from all suppliers.

| Level | Goods estimated | Median sigma | Import-weighted median | Share sigma < 3 | LIML feasible |
|---|---|---|---|---|---|
| Germany | 4,472 | 2.53 | 2.22 | 56 % | 73 % |
| EU27 | 4,521 | 2.46 | 2.44 | 57 % | 76 % |

Comparison with ProTEE: rank correlation across ICIO goods sectors 0.08. The concepts
differ: Feenstra-type estimates measure short-run substitution between varieties from
year-to-year unit-value and share changes; ProTEE identifies the long-run trade
elasticity from tariff variation. Low own values are in line with Broda and Weinstein
(2006) and Soderbery (2015), who report medians of about 3 for detailed US import goods.
Comparison with the ESCAP-World Bank estimates (script 49; Soderbery method, HS 2012, base
year 2012; one-to-one HS 2012 -> HS92 links only): levels agree (Germany median 2.55 own
vs 2.75 ESCAP, 4,126 goods; EU27 2.44 vs 3.03, ESCAP EU value = median of members), but
product rankings do not (Spearman 0.00 for Germany, 0.06 for EU27; HS2 chapter medians
0.22 and 0.34). Single-good estimates are therefore noisy; statements about groups of
goods (shares, medians, sector values) are more reliable than the value for one good.
The site says so in the table note.

Uses:
- Dependent goods: 218 of 488 EU dependent goods with an estimate have sigma < 2
  (Germany: 244 of 565), among them laptops (847130, at the grid floor 1.05), lithium-ion
  batteries (850760, 1.44) and solar modules (854143, at the floor).
- China supply-stop scenario, short-run variant (own sector values sigma - 1, floor 0.5,
  services 5): real income Germany -0.93 %, EU27 -0.63 %, about ten times the long-run
  central case (-0.09 %, EU27 -0.07 %). Reported separately, not part of the range.
