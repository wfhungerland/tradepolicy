# Germany in the product space, 1995-2024

Results of strand 2 (economic complexity). Methods and specification choices are in `complexity_methods.md`; the code is `01_exports.py` to `04_robustness.py`. Tables and figures referred to below are written to the `output` folder set in `config.yaml` (`germany_hs4/`, `germany_hs6/`, `robustness/`).

## Bottom line

Germany fell from 2nd to 5th place in the Economic Complexity Index (ECI) between 1995 and 2024. The fall is relative. Measured on a fixed yardstick, the complexity of Germany's export basket barely changed (HS4) or rose (HS6). Germany lost rank because others caught up, above all South Korea, Taiwan and China. The decline in rank survives every robustness check; whether Germany lost more complex products than it gained does not.

## Data and specification

- BACI HS92 V202601, exports summed over destinations, 1995-2024.
- Fixed panel of 130 countries (population at least 1 million, mean exports at least USD 1 billion, positive exports in every year) and 1,203 HS4 products (positive world exports in every year, mean world exports at least USD 40 million). The HS6 run keeps 130 countries.
- Three-year centred moving average of exports, Balassa RCA, binary M with RCA >= 1.
- ECI and PCI from the eigenvector of the second largest eigenvalue; proximity as the minimum of conditional probabilities; density, COI and COG as in Hausmann et al. (2014).
- Peers: CHN, USA, JPN, KOR, ITA, FRA, GBR, NLD, CHE, MEX.

Because ECI is standardised every year, it measures position relative to the other countries in that year. Two measures add a fixed yardstick: the mean pooled PCI of products a country exports with RCA >= 1 ("fixed-PCI ECI"), and the export-weighted mean pooled PCI of its basket. Pooled PCI is each product's PCI averaged over 1995-2024.

## Findings

### 1. Rank: Germany slips, Asia rises

ECI rank among 130 countries (HS4, main run):

| | 1995 | 2000 | 2005 | 2010 | 2015 | 2020 | 2024 |
|---|---|---|---|---|---|---|---|
| JPN | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CHE | 4 | 3 | 3 | 2 | 2 | 3 | 2 |
| DEU | 2 | 2 | 2 | 3 | 3 | 5 | 5 |
| KOR | 23 | 24 | 11 | 11 | 5 | 4 | 4 |
| USA | 8 | 7 | 8 | 12 | 10 | 13 | 12 |
| GBR | 7 | 6 | 7 | 8 | 9 | 11 | 10 |
| FRA | 9 | 9 | 13 | 14 | 15 | 15 | 17 |
| CHN | 49 | 43 | 36 | 30 | 23 | 20 | 19 |

Top five in 1995: JPN, DEU, SWE, CHE, FIN. In 2024: JPN, CHE, TWN, KOR, DEU. Germany's ECI fell from 2.22 to 1.79 standard deviations above the mean.

### 2. On a fixed yardstick Germany holds its level

| | Fixed-PCI ECI 1995 | 2024 | Diversity 1995 | 2024 |
|---|---|---|---|---|
| DEU | 1.98 | 1.94 | 561 | 536 |
| JPN | 2.32 | 2.23 | 293 | 340 |
| CHE | 1.99 | 2.14 | 344 | 176 |
| KOR | 0.86 | 2.02 | 267 | 225 |
| CHN | 0.40 | 1.24 | 421 | 580 |
| USA | 1.57 | 1.60 | 448 | 376 |
| FRA | 1.47 | 1.39 | 488 | 444 |

The export-weighted complexity of Germany's basket was 2.12 in 1995 and 2.13 in 2024. The share of the most complex quintile of products in German exports rose from 48% to 50%. Korea's fixed-PCI ECI more than doubled and China's tripled. Germany remains the most diversified of the large exporters except China.

### 3. Products gained and lost

Between 1995 and 2024 (smoothed endpoints), at HS4 Germany gained RCA in 89 products and lost it in 114. Lost products are more complex on average (pooled PCI 1.31 against 0.89). Losses include speciality chemicals (2933, 2934), doped semiconductor materials (3818) and stainless steel (7219); gains include aircraft (8802), engines (8407), medical devices (9021) and transformers (8504). By value the gains dominate: USD 126 billion of 2024 exports against USD 36 billion.

At HS6 the pattern reverses: 399 gains with mean PCI 1.37 against 546 losses with mean PCI 1.25. This finding therefore depends on aggregation and should not be reported as robust.

### 4. Relatedness predicts entry

For Germany and the peers, the probability that a product without RCA gains RCA within five years rises with density, from 1.9% in the lowest density decile to 11.6% in the highest. The product space has predictive content for this group, which supports reading density as a measure of feasible diversification.

### 5. Opportunities

Products without German RCA in 2024 that combine high complexity with high density (top by Complexity Outlook Gain) include glass products (7006), doped semiconductor materials (3818), integrated circuits (8542), telecom equipment (8517), recording media (8523) and stainless steel bars (7221). Several are products Germany held in 1995 and lost.

## Robustness

| Variant | Countries | DEU ECI rank 1995 | 2024 | DEU fitness rank 1995 | 2024 | Spearman ECI vs main | Spearman ECI vs fitness |
|---|---|---|---|---|---|---|---|
| Main (HS4, RCA >= 1, 3-year window) | 130 | 2 | 5 | 1 | 2 | 1.000 | 0.88 |
| RCA >= 0.75 | 130 | 3 | 6 | 1 | 2 | 0.994 | 0.90 |
| RCA >= 1.25 | 130 | 2 | 4 | 1 | 2 | 0.995 | 0.87 |
| RCA >= 2 | 130 | 1 | 2 | 3 | 3 | 0.973 | 0.81 |
| No smoothing | 130 | 2 | 5 | 1 | 2 | 0.988 | 0.88 |
| 5-year window | 130 | 2 | 5 | 1 | 2 | 0.993 | 0.89 |
| Without NLD, BEL, SGP, HKG | 126 | 2 | 5 | 1 | 2 | 0.998 | 0.89 |
| HS6 | 130 | 2 | 6 | 1 | 2 | 0.961 | 0.79 |

Spearman correlations are averages over years. Korea rises from places 21-37 to places 4-6 in every variant. Fitness-Complexity, which rewards diversification more, places Germany higher (1st or 2nd in most variants) and shows a smaller decline.

## Caveats

- ECI rank is relative and depends on the country sample; the fixed-PCI measures should accompany any statement about rank.
- Some product complexity values are implausible because rich countries happen to export the product (for example pig meat, 0203, pooled PCI 2.3). Product-level statements need a plausibility check.
- Taiwan enters BACI under a non-standard code (mapped to TWN for population). Singapore is a re-export hub; dropping hubs does not change Germany's rank.
- BACI values are in current USD. Exchange-rate swings affect RCA only through relative shares, but they move the value comparisons in finding 3.
- The Atlas of Economic Complexity switched to a continuous method in 2026; its current rankings are not directly comparable.

## Next steps

- Sector view: chemicals, vehicles, machinery and electronics separately.
- Product space network figure for Germany 1995 and 2024.
- GENEPY as a further algorithm check (not yet implemented).
