# Germany in the product space, 1995-2024

Results of strand 2 (economic complexity). Methods and specification choices are in `complexity_methods.md`; the code is `01_exports.py` to `04_robustness.py`. Tables and figures referred to below are written to the `output` folder set in `config.yaml` (`germany_hs4/`, `germany_hs6/`, `robustness/`).

## Bottom line

Germany fell from 2nd to 5th place in the Economic Complexity Index (ECI) between 1995 and 2024. The fall is relative. Measured on a fixed yardstick, the complexity of Germany's export basket barely changed (HS4) or rose (HS6). Germany lost rank because others caught up, above all South Korea, Taiwan and China. The decline in rank survives every robustness check, including the Fitness-Complexity and GENEPY algorithms. Germany's world market share fell in every sector except aircraft and other transport, while the complexity of what it gains and loses within sectors is about the same.

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

At HS6 the pattern reverses: 399 gains with mean PCI 1.37 against 546 losses with mean PCI 1.25. This finding therefore depends on aggregation and should not be reported as robust. The sector view below shows why: the comparison is driven by composition, not by a shift in the complex core.

### 4. Relatedness predicts entry

For Germany and the peers, the probability that a product without RCA gains RCA within five years rises with density, from 1.9% in the lowest density decile to 11.6% in the highest. The product space has predictive content for this group, which supports reading density as a measure of feasible diversification.

### 5. Opportunities

Products without German RCA in 2024 that combine high complexity with high density (top by Complexity Outlook Gain) include glass products (7006), doped semiconductor materials (3818), integrated circuits (8542), telecom equipment (8517), recording media (8523) and stainless steel bars (7221). Several are products Germany held in 1995 and lost.

## Sector view

Products are grouped into 16 sectors by HS chapter (`05_sectors.py`). World market share is Germany's exports in the sector divided by world exports of the panel products in that sector.

| Sector | World share 1995 | 2024 | Share of German exports 2024 | HS6 gained | HS6 lost |
|---|---|---|---|---|---|
| Motor vehicles | 18.1% | 15.3% | 18.5% | 11 | 2 |
| Machinery | 13.0% | 9.6% | 16.7% | 36 | 45 |
| Electrical and electronics | 8.0% | 4.7% | 10.3% | 29 | 31 |
| Metals | 11.7% | 7.9% | 7.7% | 52 | 71 |
| Pharmaceuticals | 14.4% | 13.2% | 7.5% | 4 | 3 |
| Food and agriculture | 5.8% | 5.0% | 6.8% | 73 | 32 |
| Plastics and rubber | 13.4% | 9.8% | 6.2% | 13 | 19 |
| Instruments and medical | 11.7% | 10.8% | 5.2% | 20 | 18 |
| Other chemicals | 14.5% | 9.1% | 4.3% | 23 | 33 |
| Basic chemicals | 11.4% | 6.1% | 2.7% | 42 | 76 |
| Other transport | 7.3% | 10.1% | 2.7% | 8 | 7 |
| Textiles, apparel, footwear | 5.7% | 3.5% | 2.2% | 23 | 130 |

World shares are from the HS4 run; HS6 gives the same values to within 0.2 points.

Three results stand out.

1. **Market share fell almost everywhere.** The steepest falls are in basic chemicals (11.4% to 6.1%), other chemicals, electronics and metals. Only other transport (aircraft) gained. Over the same period China's share rose from 3.5% to 19.0% in basic chemicals, from 2.1% to 22.8% in machinery and from 0.5% to 10.5% in motor vehicles. Japan, the US, France and the UK lost share in the same sectors, mostly by more than Germany.
2. **The entries-exits puzzle is composition.** Germany gained many low-complexity food products and lost many low-complexity textile products. These two sectors decide the sign of the aggregate comparison. Without them, mean pooled PCI is 1.36 for gains and 1.56 for losses at HS4, and 1.65 against 1.69 at HS6: losses are marginally more complex, by a margin too small to matter.
3. **Net losses concentrate in chemicals and metals.** Basic chemicals (42 gained, 76 lost at HS6), metals (52 against 71) and textiles account for most of the net decline in diversity. Motor vehicles, food and instruments show net gains. Machinery and electronics are close to balanced in counts, despite the fall in market share.

Figures: `sectors/sectors_deu.png` (world share by sector) and `sectors/sectors_deu_entries.png` (HS6 products gained and lost).

## Product space map

`06_product_space.py` draws the product space as in Hidalgo et al. (2007): the maximum spanning tree of the 2024 proximity matrix plus all links with proximity >= 0.55 (1,203 HS4 products, 3,420 links). The left panel colours products by eight groups, the right panel by Germany's status between 1995 and 2024 (`product_space/product_space_deu.png`).

The map shows Germany's advantage concentrated in the connected core of machinery, chemicals, metals and vehicles, with little presence in the textile and raw-material branches. Lost products sit further out than kept ones. Measured as mean proximity to all other products, centrality is 0.206 for products Germany kept, 0.190 for products it gained, 0.169 for products it lost and 0.152 for products it never had. Germany shed advantage mainly at the edges of its cluster and kept the core. The layout uses the 2024 proximity matrix only, so it shows today's product space, not that of 1995.

## Robustness

| Variant | Countries | DEU ECI rank 1995 | 2024 | DEU fitness rank 1995 | 2024 | DEU GENEPY rank 1995 | 2024 | Spearman ECI vs main | ECI vs fitness | ECI vs GENEPY |
|---|---|---|---|---|---|---|---|---|---|---|
| Main (HS4, RCA >= 1, 3-year window) | 130 | 2 | 5 | 1 | 2 | 2 | 5 | 1.000 | 0.88 | 0.91 |
| RCA >= 0.75 | 130 | 3 | 6 | 1 | 2 | 2 | 6 | 0.994 | 0.90 | 0.93 |
| RCA >= 1.25 | 130 | 2 | 4 | 1 | 2 | 2 | 3 | 0.995 | 0.87 | 0.89 |
| RCA >= 2 | 130 | 1 | 2 | 3 | 3 | 1 | 2 | 0.973 | 0.81 | 0.82 |
| No smoothing | 130 | 2 | 5 | 1 | 2 | 2 | 6 | 0.988 | 0.88 | 0.90 |
| 5-year window | 130 | 2 | 5 | 1 | 2 | 2 | 6 | 0.993 | 0.89 | 0.91 |
| Without NLD, BEL, SGP, HKG | 126 | 2 | 5 | 1 | 2 | 2 | 5 | 0.998 | 0.89 | 0.91 |
| HS6 | 130 | 2 | 6 | 1 | 2 | 2 | 3 | 0.961 | 0.79 | 0.82 |

Spearman correlations are averages over years. Korea rises from places 21-37 to places 4-6 in every variant. Fitness-Complexity, which rewards diversification more, places Germany higher (1st or 2nd in most variants) and shows a smaller decline.

GENEPY (Sciarra, Chiarotti, Ridolfi and Laio 2020) combines the two views: it uses the first two eigenvectors of a country proximity matrix built from degree-normalised exports, so both diversification and the complexity of products count. It reproduces the ECI result for Germany: 2nd in 1995 in every variant, 2nd to 6th in 2024 (5th in the main run). It differs from ECI for diversified economies with a less exclusive basket. In 2024 China ranks 3rd by GENEPY, 1st by fitness and 19th by ECI; Switzerland ranks 2nd by ECI, 6th by GENEPY and 27th by fitness. Germany's ranks agree across all three methods: 5th by ECI and GENEPY, 2nd by fitness. The implementation follows Eqs. 5 and 15 of the article.

## Comparison with the Atlas of Economic Complexity

`07_atlas_comparison.py` compares the main run with the Growth Lab's published rankings (Growth Projections and Complexity Rankings, doi:10.7910/DVN/XTAQMC, version of February 2026, HS92 ECI) and its HS92 four-digit PCI (doi:10.7910/DVN/T4CHWJ). Ranks are recomputed on the 128 countries in both samples.

- ECI agrees closely: Spearman 0.95 in 1995, 0.97 in 2010 and 2024; Pearson 0.93 to 0.95.
- PCI agrees well: Spearman 0.91 across 1,202 common HS4 products, in 1995 and 2024.
- Germany falls in both: from 2nd to 5th here, from 4th to 6th in the Atlas. The Atlas places Sweden and Switzerland ahead of Germany already in 1995, so its decline is smaller but starts from a lower rank.
- Top 10 in 2024: JPN, CHE, TWN, KOR, DEU, SGP, CZE, SWE, AUT, GBR here; JPN, TWN, KOR, CHE, SGP, DEU, ISR, CZE, SVN, CHN in the Atlas. Seven of ten coincide in both years.
- The largest gaps among the peers: China ranks 10th in the Atlas against 19th here, the US 18th against 12th. Plausible reasons are the Growth Lab's own mirror-data reconciliation and filters, and the Atlas's change of method in 2026 (see caveats); our fixed panel and three-year smoothing also differ.

The comparison supports the main finding: Germany's relative decline and Korea's and Taiwan's rise are not an artefact of this project's data or choices.

## Caveats

- ECI rank is relative and depends on the country sample; the fixed-PCI measures should accompany any statement about rank.
- Some product complexity values are implausible because rich countries happen to export the product (for example pig meat, 0203, pooled PCI 2.3). Product-level statements need a plausibility check.
- Taiwan enters BACI under a non-standard code (mapped to TWN for population). Singapore is a re-export hub; dropping hubs does not change Germany's rank.
- BACI values are in current USD. Exchange-rate swings affect RCA only through relative shares, but they move the value comparisons in finding 3.
- The Atlas of Economic Complexity reportedly switched to a continuous RCA method in 2026 (not verified against Growth Lab documentation); its rankings are therefore a benchmark, not a replication target.
