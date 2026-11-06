# Strand 3: US tariff scenarios (first results, 2026-11-06)

Model: Caliendo and Parro (2015), static, in changes (`gravity_ge.cp_solve`),
OECD ICIO 2025, base year 2022, 81 economies, 50 sectors; US applied tariffs from
CEPII (Guimbard 2026) aggregated to ICIO sectors with 2024 US import weights;
tariff revenue rebated, deficits fixed, no retaliation, tariffs of other
countries zero in the baseline. Scripts 33 and 34. Runtime about 25 seconds.

## Main results (central case: ProTEE sector elasticities)

| Scenario (US tariffs at) | Germany real income | Germany exports to US | EU27 real income | US real income |
|---|---|---|---|---|
| 10 Apr 2025 (peak) | -0.09 % | -14.7 % | -0.05 % | -0.58 % |
| 5 Sep 2025 (EU deal) | -0.07 % | -9.0 % | -0.03 % | -0.42 % |
| 22 Aug 2026 (current) | -0.07 % | -9.2 % | -0.06 % | -0.16 % |

German sectors hit hardest at the current level: motor vehicles, machinery,
electrical equipment and electronics, each about -17 to -22 % in US sales and
-1.5 to -2.6 % in output.

## Check 1: rise of EU exports to the US in the September 2025 scenario

EU exports to the US rise by 2.9 % (USD 718 to 739 bn) although German exports
fall by 9 %. Decomposition by sector:
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
| US tariff revenue | USD 183 to 280 bn a year, 6 to 9 % of imports | USD 195 bn in FY2025 (CRFB from Monthly Treasury Statement), tariffs only partly in force that year | right order of magnitude |
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
