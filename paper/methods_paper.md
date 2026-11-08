---
title: "Complexity, Gravity and Scenarios: An Open Monitor of Germany's Trade Position"
subtitle: "Methods, data and validation of the Produktraum-Monitor"
author: "Wolf-Fabian Hungerland"
date: "Draft, 8 November 2026"
abstract: |
  This paper documents an open, reproducible monitor of Germany's position in world trade. It combines four strands. First, economic complexity measures from bilateral trade data for 130 countries and 1,203 products, 1995 to 2024, show that Germany fell from second to fifth place in the Economic Complexity Index while the complexity of its export basket on a fixed yardstick stayed constant; others caught up. Second, an out-of-sample test shows that gravity models with three-way fixed effects do not beat univariate benchmarks in forecasting monthly or quarterly trade. Third, a multi-sector general equilibrium model with input-output links, solved in changes on the OECD inter-country input-output tables for 2022, quantifies scenarios: the US tariffs in force in August 2026 lower German real income by 0.07 % in the long run, the loss of the EU single market would cost 1.5 %, rerouting around Africa as in 2024 costs 0.06 %, and a Chinese supply stop for goods on which the EU depends costs at least 0.09 %, or 0.93 % with short-run elasticities estimated good by good. Fourth, a dependency analysis following the European Commission's criteria finds 497 dependent goods for the EU and 593 for Germany, about half supplied mainly by China; German and Chinese exports have become more similar, and 21 % of German exports are in goods under Chinese price pressure. Each result is checked against published replications, observed data or the literature; an ex-post comparison with US imports in 2025 and 2026 shows that the model is a long-run benchmark, not a short-run forecast. Code, data and an interactive website are public.
---

**Disclaimer.** The views expressed are the author's own and do not necessarily reflect those of any institution. All errors are the author's.

**Availability.** Interactive monitor: <https://wfhungerland.github.io/tradepolicy-site/> (German and English). Scenario code and data: <https://github.com/wfhungerland/tradepolicy-site>. Results files and analysis scripts are referred to by name below.

# 1 Introduction

Trade policy questions reach economic ministries faster than models can be built for them: what a new round of US tariffs costs, what the single market is worth, what a closed shipping lane means, where Europe depends on single suppliers. Answers need to be quick, transparent about uncertainty and grounded in methods that the academic literature accepts. This paper documents a monitor built to meet these needs for Germany. It assembles established methods rather than proposing new ones, and puts the emphasis on data choices, validation and the limits of each result.

The monitor has four strands. The first measures economic complexity (Hidalgo and Hausmann 2009; Hausmann et al. 2014): which products a country exports with comparative advantage, how sophisticated they are, and which related products are within reach. The second asks whether structural gravity, the workhorse of trade policy analysis (Head and Mayer 2014), can forecast trade at short horizons. The third quantifies counterfactual scenarios in a multi-sector model with input-output links (Caliendo and Parro 2015), solved in changes (Dekle, Eaton and Kortum 2008). The fourth identifies strategic dependencies with the criteria of the European Commission (2021) and links them to supply chains and shipping routes.

Four results stand out. Germany's fall in the complexity ranking is relative: the complexity of its basket on a fixed yardstick did not change, while Korea, Taiwan and China caught up. Gravity models do not help in short-run forecasting; their value lies in scenario analysis. In the scenarios, the single market matters about twenty times more for German real income than the US tariffs of 2026, and the costs of shipping disruptions and of a Chinese supply stop for dependent goods are of the same small order as the tariffs in the long run. Finally, an ex-post comparison with observed US imports confirms the direction of the model's predictions for China but not the diversion of trade via South-East Asia; the model is a benchmark for incidence, not a forecast.

# 2 Data

| Source | Content | Use |
|---|---|---|
| CEPII BACI HS92 V202601 (Gaulier and Zignago 2010) | Bilateral trade, HS6, 1995-2024 | Complexity, product space |
| CEPII BACI HS22 V202601 | Bilateral trade, HS6, 2022-2024 | Tariff weights, dependencies |
| Eurostat Comext | Monthly exports of EU members by partner, 2002-2026 | Forecast test, Germany |
| IMF IMTS | Monthly bilateral trade, 2002-2026 | Forecast test, world; ex-post check |
| OECD ICIO 2025 | Inter-country input-output tables, 2022, 81 economies, 50 sectors | Baseline of the scenario model |
| USITC ITPD-E R2025 (Borchert et al. 2021) | Trade and domestic sales by industry | EU border effects |
| CEPII US import tariffs (Guimbard 2026) | US applied tariffs by origin, HS6 and date, 2025-2026 | US tariff scenarios |
| MAcMap-HS6 2019 (ITC and CEPII) | Applied tariffs of all countries | Baseline tariffs |
| ProTEE 0.1 (Fontagné, Guimbard and Orefice 2022) | Trade elasticities by HS6 | Sector elasticities |
| searoute network (Eurostat SeaRoute) | Maritime network with passages | Sea routes |
| Harvard Growth Lab | HS4 product names, Atlas rankings | Labels, benchmark |

All sources are public; licences are listed on the website. Derived results only are published.

# 3 Economic complexity

**Method.** Exports are summed over destinations and aggregated to HS4. The panel is fixed over time: 130 countries with at least one million inhabitants and mean exports of at least USD 1 billion, and 1,203 products with positive world exports in every year and mean world exports of at least USD 40 million. Exports are smoothed with a centred three-year moving average. A country has revealed comparative advantage (RCA) in a product if its Balassa index is at least one. The Economic Complexity Index (ECI) and the Product Complexity Index (PCI) are the eigenvectors associated with the second largest eigenvalue of the country and product similarity matrices, which is the limit of the method of reflections (Hidalgo and Hausmann 2009; Mealy, Farmer and Teytelboym 2019). Proximity between products is the minimum of the two conditional probabilities of joint advantage (Hidalgo et al. 2007); density, the Complexity Outlook Index and the Complexity Outlook Gain follow Hausmann et al. (2014).

Because the ECI is standardised each year, it measures position, not level. A fixed yardstick complements it: each product's PCI is averaged over 1995-2024 ("pooled PCI"), and a country's basket is valued at these fixed complexities each year.

**Results.** Germany ranks second in 1995 and fifth in 2024. On the fixed yardstick, the mean pooled PCI of its products with advantage moved from 1.98 to 1.94, and the export-weighted complexity of its basket from 2.12 to 2.13. Korea's value more than doubled (0.86 to 2.02) and China's tripled (0.40 to 1.24). Germany's world market share fell in every sector except aircraft and other transport. It kept advantage in the connected core of machinery, chemicals, metals and vehicles and lost it at the periphery: mean proximity to all other products is 0.206 for kept products and 0.169 for lost ones. Relatedness predicts entry: the probability of gaining advantage within five years rises from 1.9 % in the lowest density decile to 11.6 % in the highest.

**Robustness and validation.** The decline in rank holds for RCA thresholds from 0.75 to 2, without smoothing and with a five-year window, without re-export hubs, at HS6, and with two alternative algorithms, Fitness-Complexity (Tacchella et al. 2012) and GENEPY (Sciarra et al. 2020). Rank correlations with the Atlas of Economic Complexity are 0.95 to 0.97 for countries and 0.91 for products; the Atlas also shows Germany falling, from fourth to sixth.

# 4 Gravity for short-run forecasts

**Design.** A PPML gravity model with exporter-month, importer-month and pair fixed effects is estimated on rolling 60-month windows at each forecast origin from December 2014. Exporter and importer effects are forecast with the same autoregressive model as the benchmark and combined with the pair effects. Benchmarks are an unchanged year-on-year growth rate, a direct AR model with lag length chosen by BIC, and a bottom-up AR model by destination. Forecasts are evaluated at horizons of one to six months and as quarterly nowcasts, with Diebold-Mariano tests (Diebold and Mariano 1995) and the Harvey, Leybourne and Newbold (1997) correction.

**Results.** For German exports, gravity has 19 to 27 % higher root mean squared errors than the AR model, significantly so at six months and in the quarterly nowcast with one month known. For world exports it is close to AR at short horizons and 18 % worse at six months. Disaggregation by destination helps marginally; the gravity structure does not. The reason is structural: with exporter-time and importer-time effects, all time variation sits in effects that must themselves be forecast. Gravity belongs in scenario analysis, where its structure is the point.

# 5 The scenario model

## 5.1 Model

The model is the static multi-sector Ricardian model of Caliendo and Parro (2015) with input-output links, sector-specific trade elasticities and tariff revenue rebated to households, solved in changes. With $\hat{x} = x'/x$, cost changes of sector $j$ in country $i$ are
$$\hat{c}_i^j = \hat{w}_i^{\beta_i^j} \prod_k \left(\hat{P}_i^k\right)^{\gamma_i^{k,j}},$$
price indices and trade shares change as
$$\hat{P}_n^j = \Big[\sum_i \pi_{ni}^j \big(\hat{\kappa}_{ni}^j \hat{c}_i^j\big)^{-\theta^j}\Big]^{-1/\theta^j}, \qquad \pi_{ni}^{j\prime} = \pi_{ni}^j \left(\frac{\hat{\kappa}_{ni}^j \hat{c}_i^j}{\hat{P}_n^j}\right)^{-\theta^j},$$
where $\kappa_{ni}^j$ includes tariffs $(1+\tau_{ni}^j)$ and iceberg costs. Expenditure satisfies
$$X_n^{j\prime} = \sum_k \gamma_n^{j,k} Y_n^{k\prime} + \alpha_n^j I_n', \qquad I_n' = \hat{w}_n w_n L_n + R_n' + D_n,$$
with tariff revenue $R_n'$ and trade deficits $D_n$ held fixed. Labour market clearing $\hat{w}_n w_n L_n = \sum_j \beta_n^j Y_n^{j\prime}$ closes the model; world value added is the numeraire. Welfare is real income, $\hat{I}_n / \hat{P}_n$ with the consumer price index $\hat{P}_n = \prod_j (\hat{P}_n^j)^{\alpha_n^j}$.

The baseline is the OECD inter-country input-output table for 2022 (80 economies plus the rest of the world, 50 sectors). Baseline tariffs are MAcMap-HS6 2019 for all importers, aggregated to sectors with 2024 bilateral trade weights, and the CEPII schedule of 1 January 2025 for the US. Trade elasticities are sector medians of the ProTEE HS6 estimates, capped at 15 because product-level medians overstate sector-level substitution in a few sectors (refined petroleum 66, electricity 45); services take 5. The range reported for every result spans four variants: capped and uncapped ProTEE and uniform elasticities of 4 and 8.

## 5.2 Validation of the solver

The solver reproduces the baseline exactly without a shock; with one sector and no intermediates it coincides with the one-sector tariff model; and in the one-sector case without tariffs it satisfies the welfare formula of Arkolakis, Costinot and Rodríguez-Clare (2012). A one-sector version reproduces the NAFTA application of Yotov et al. (2016): the same RTA coefficient (0.557) and export effects within 0.75 percentage points of the published results, whose own solution is less tightly converged.

## 5.3 US tariffs and retaliation

US applied tariffs from the CEPII file (Guimbard 2026) are aggregated from origin and HS6 to origin and ICIO sector with 2024 US import weights.

| Real income, % (range) | Germany | EU27 | USA | China |
|---|---|---|---|---|
| Peak, 10 April 2025 | -0.10 | -0.05 | -0.53 | -0.26 |
| After the deals, 5 September 2025 | -0.08 | -0.04 | -0.35 | -0.21 |
| August 2026 | -0.07 (-0.08 to -0.07) | -0.06 | -0.12 (-0.16 to +0.04) | -0.11 |
| August 2026, EU mirror retaliation | -0.07 | -0.06 | -0.13 | -0.11 |
| August 2026, all countries retaliate | -0.05 | -0.05 | -0.25 | -0.10 |

German exports to the US fall by 7.4 % at the August 2026 tariffs; motor vehicles, machinery and electrical equipment lose about a fifth of their US sales. Mirror retaliation leaves the EU almost unaffected, as tariff revenue offsets dearer US goods; retaliation by all countries doubles the US loss and makes it negative under every elasticity, in line with the direction found by Ignatenko et al. (2025). Ireland, Mexico and Vietnam lose most.

## 5.4 The EU single market

Following Head and Mayer (2021), border effects are estimated with flows to self: PPML on import shares with pair, exporter-year and importer-year effects and year-specific dummies for EU-to-EU, non-EU-to-EU and non-EU-destination border flows (ITPD-E, 2000-2019, balanced panels with domestic flows, China, Japan and Taiwan excluded for breaks in domestic data). In manufacturing, trade costs between EU members fall by 11.6 points relative to the 2000 benchmark, and those of outsiders' access to the EU fall as well; there is no "fortress Europe". This matches Figure 1 of Head and Mayer (2021). For services the estimation does not converge on ITPD-E; their effect is taken from the literature.

| Scenario | Shock | Germany | EU27 | Intra-EU trade |
|---|---|---|---|---|
| No single market | Goods coefficient -1.1 (Head and Mayer 2021), services -0.18 (Mayer, Vicard and Zignago 2019) | -1.45 % | -1.87 % | -40 % |
| Integration to 2030 | Ten more years of the 2000-2019 trend | +0.75 % | +0.93 % | +18 % |
| Deeper services market | Services coefficient +0.14 | +0.22 % | +0.29 % | +5 % |

Shocks are set as changes in the gravity coefficient on intra-EU flows and translated into iceberg costs $\hat{\kappa} = \exp(-\Delta\beta/\theta^j)$. Small open members depend most on the single market (Luxembourg -6.5 %, Slovakia and Hungary -4.5 %).

## 5.5 Shipping routes

Shortest routes between the main ports of the 80 economies are computed on the searoute maritime network, with Arctic passages closed, with and without the Red Sea or the Panama Canal. Without the Red Sea, routes between Europe and Asia get 12 days longer on average (10 to 14 days for Germany). The shock is calibrated to the natural experiment of the Suez closure in 1967 to 1975: trade falls with sea distance with an elasticity of about 0.5 (Feyrer 2021), so $\hat{\kappa} = (d_1/d_0)^{\delta/\theta^j}$ with $\delta = 0.5$ (upper variant 1.0). In general equilibrium the model reproduces 0.43. A first version with time costs of 0.6 to 2.1 % per day (Hummels and Schaur 2013) implied an elasticity of 2.5 and was rejected. The 2024 case scales the shock by one half, as Suez transits fell by about 49 %.

| Real income, % | Germany | EU27 | China | India |
|---|---|---|---|---|
| Red Sea, rerouting as in 2024 | -0.06 | -0.07 | -0.03 | -0.14 |
| Red Sea closed | -0.11 | -0.12 | -0.07 | -0.25 |
| Panama Canal closed | 0.00 | 0.00 | -0.02 | 0.00 |

## 5.6 Strategic dependencies and a Chinese supply stop

A good (HS 2022, six digits) is a dependency if, following the European Commission (2021), the Herfindahl index of extra-EU import sources exceeds 0.4, extra-EU imports exceed half of total imports, and extra-EU imports exceed own exports. On BACI 2024 the EU depends on 497 of 5,605 goods (USD 230 billion of imports), Germany on 593. China is the main supplier for 220 of the EU's dependent goods (USD 157 billion), led by laptops, lithium-ion batteries and solar cells. About three quarters of these imports reach Hamburg through the Red Sea. The Commission's own count of 137 goods is restricted to sensitive ecosystems, a mapping that is not public.

Through the global Leontief inverse, Chinese value added accounts for 1.6 % of German output, half of it arriving via third countries or other German industries (Johnson and Noguera 2012). Dependent inputs from China, including indirect routes, reach 2.7 % of output in electronics and 2.1 % in electrical equipment, and below 1 % elsewhere.

A scenario in which China stops supplying the EU with these goods, implemented as an iceberg cost that removes the dependent share of China-EU flows in each sector, lowers German real income by 0.09 % (range 0.09 to 0.17 %) and EU income by 0.07 %. This is a lower bound: the model lets buyers switch suppliers along CES demand curves, while short-run bottlenecks without substitutes cost much more.

To gauge the short run, elasticities of substitution between supplier countries are estimated good by good (HS 1992, six digits) on BACI unit values for 2012 to 2024, for EU imports from outside the EU and for German imports. The estimator follows Feenstra (1994) and Broda and Weinstein (2006), with the limited-information maximum likelihood refinement and constrained fallback of Soderbery (2015); a simulation test recovers known elasticities. The median is 2.5 for both levels, and 57 % of goods have an elasticity below 3. Aggregated to ICIO goods sectors, these short-run values are unrelated to the long-run ProTEE elasticities (rank correlation 0.08), as expected from the different identification. Used in the supply-stop scenario (sector elasticity minus one, floor 0.5), they raise the loss to 0.93 % for Germany and 0.63 % for the EU, about ten times the long-run case. Against the estimates of ESCAP and the World Bank with the same method (base year 2012), levels agree (German median 2.55 here, 2.75 there), but rankings across goods do not (rank correlation 0.00 for Germany). Single-good values are therefore noisy; the monitor flags a dependent good as hard to replace only when both sources put it below 2, which holds for 40 EU and 91 German dependent goods. Quality adjustment after Feenstra and Romalis (2014) would need separate exporter and importer unit values, which BACI reconciles into one.

## 5.7 Chinese competition in third markets

German and Chinese exports to all other countries are compared good by good (BACI HS 1992). The export similarity index of Finger and Kreinin (1979) rose from 0.37 in 2012 to 0.40 in 2018 and 0.45 in 2024. For the same good and destination, the Chinese unit value is at the median 61 % of the German one, weighted by German exports, in line with the low relative unit values of Chinese exports documented by Schott (2008). Quality-ladder length is proxied by the spread between the 90th and 10th percentile of log unit values across suppliers to the EU, a simplification of Khandelwal (2010). As his framework implies, the Chinese discount is larger on long ladders (rank correlation -0.49), and across goods China's share gains go with German share losses (-0.26), consistent with Chowdhry, Erhardt and Hinz (2026).

Goods under price pressure are defined by German exports of at least USD 100 million, a rise in China's world market share of at least five points since 2012, a Chinese unit value at least half the German one, and a ladder shorter than the median. They comprise 256 goods and USD 302 billion, 21 % of German exports; about half are vehicles and parts, where China's export-weighted world market share rose from 4 % to 10 %. Unit values per ton mix quality, model mix and weight, so values for single goods are rough.

# 6 Ex-post check

Observed US imports by partner from August 2025 to July 2026 are compared with 2024 (IMF IMTS), relative to total US imports, and set against the model's predicted changes in exports to the US. Across 67 partners weighted by imports, the correlation is 0.43 for the September 2025 tariffs and 0.73 without South-East Asia, Switzerland and Ireland. The model captures the fall of imports from China (model -32, observed -48 log points relative to the average partner). It misses the strong gains of Vietnam, Thailand and Malaysia, which reflect relocation and transshipment out of China that a model on the 2022 production structure cannot produce, as well as Swiss gold flows and the reversal of Irish pharmaceutical front-loading. The slope of observed on predicted changes is 0.42, consistent with short-run trade elasticities well below long-run ones (Boehm, Levchenko and Pandalai-Nayar 2023).

# 7 Other checks

| Check | Result |
|---|---|
| US imports from China | Model -23 % at current tariffs; observed 2025 about -30 % |
| US tariff revenue | Model USD 192 to 256 billion a year; observed USD 195 billion in fiscal year 2025, when tariffs were only partly in force |
| US welfare without retaliation | Ignatenko et al. (2025) find a small gain; here only with low elasticities. Recorded as a deviation |
| Complexity rankings | Rank correlation with the Atlas 0.95 to 0.97 |
| Forecast evaluation | pyfixest reproduces the PPML estimates |
| Import elasticities against ESCAP and World Bank | Medians agree (2.55 and 2.75 for Germany); rankings across goods do not (0.00) |
| Chinese price discount and ladder length | Larger discount on long ladders (rank correlation -0.49), as in Khandelwal (2010) |

# 8 The monitor

The results are presented on a static website in German and English, designed in the same family as the Konjunkturmonitor of the author. Each view starts with a question and an answer sentence computed from the data; each figure carries a number, a sub-question, an explanatory note, a source line and downloads in XLSX, PPTX, PNG and CSV. Country profiles bring together complexity, sectors, export opportunities and scenario effects for 130 countries. The US tariff scenarios are recomputed automatically each month when CEPII publishes new tariff data. All analysis scripts run from public data; a reference file of 82 key values allows a check that a local run reproduces the published results.

# 9 Limitations

- The scenario model is static and long-run: no capital accumulation, no adjustment costs, fixed trade balances, fixed technologies. Its numbers measure incidence, not timing.
- Elasticities drive the size of effects outside Germany; the German results are robust across the variants, those for the US are not.
- Services integration is taken from the literature; the estimation on ITPD-E did not converge.
- Shipping shocks treat all goods on longer routes as seaborne and leave out canal revenues, freight rate spikes and capacity limits.
- Dependency criteria follow the Commission but count all goods; the indirect dependence uses a multiplier approximation.
- Good-level elasticities are noisy and not quality-adjusted; the short-run scenario uses sector medians.
- Product names in German are own translations of the Harvard Growth Lab labels; product examples are illustrative.

# References

Arkolakis, C., Costinot, A. and Rodríguez-Clare, A. (2012). New Trade Models, Same Old Gains? *American Economic Review* 102(1), 94-130.

Boehm, C.E., Levchenko, A.A. and Pandalai-Nayar, N. (2023). The Long and Short (Run) of Trade Elasticities. *American Economic Review* 113(4), 861-905.

Borchert, I., Larch, M., Shikher, S. and Yotov, Y.V. (2021). The International Trade and Production Database for Estimation (ITPD-E). *International Economics* 166, 140-166.

Broda, C. and Weinstein, D.E. (2006). Globalization and the Gains from Variety. *Quarterly Journal of Economics* 121(2), 541-585.

Caliendo, L. and Parro, F. (2015). Estimates of the Trade and Welfare Effects of NAFTA. *Review of Economic Studies* 82(1), 1-44.

Chowdhry, S., Erhardt, K. and Hinz, J. (2026). Kiel Policy Brief, Kiel Institute for the World Economy (EconStor 341641; title to be verified).

Dekle, R., Eaton, J. and Kortum, S. (2008). Global Rebalancing with Gravity: Measuring the Burden of Adjustment. *IMF Staff Papers* 55(3), 511-540.

Diebold, F.X. and Mariano, R.S. (1995). Comparing Predictive Accuracy. *Journal of Business and Economic Statistics* 13(3), 253-263.

European Commission (2021). Strategic dependencies and capacities. Commission Staff Working Document SWD(2021) 352.

Feenstra, R.C. (1994). New Product Varieties and the Measurement of International Prices. *American Economic Review* 84(1), 157-177.

Feenstra, R.C. and Romalis, J. (2014). International Prices and Endogenous Quality. *Quarterly Journal of Economics* 129(2), 477-527.

Feyrer, J. (2021). Distance, Trade, and Income: The 1967 to 1975 Closing of the Suez Canal as a Natural Experiment. *Journal of Development Economics* 153, 102708.

Finger, J.M. and Kreinin, M.E. (1979). A Measure of 'Export Similarity' and Its Possible Uses. *Economic Journal* 89(356), 905-912.

Fontagné, L., Guimbard, H. and Orefice, G. (2022). Tariff-Based Product-Level Trade Elasticities. *Journal of International Economics* 137, 103593.

Gaulier, G. and Zignago, S. (2010). BACI: International Trade Database at the Product-Level. The 1994-2007 Version. CEPII Working Paper 2010-23.

Guimbard, H. (2026). Trade Policy Shocks under the Second Trump Administration. CEPII Working Paper 2026-07.

Harvey, D., Leybourne, S. and Newbold, P. (1997). Testing the Equality of Prediction Mean Squared Errors. *International Journal of Forecasting* 13(2), 281-291.

Hausmann, R., Hidalgo, C.A., Bustos, S., Coscia, M., Simoes, A. and Yildirim, M.A. (2014). *The Atlas of Economic Complexity: Mapping Paths to Prosperity*. MIT Press.

Head, K. and Mayer, T. (2014). Gravity Equations: Workhorse, Toolkit, and Cookbook. In Gopinath, G., Helpman, E. and Rogoff, K. (eds), *Handbook of International Economics* Vol. 4, 131-195. Elsevier.

Head, K. and Mayer, T. (2021). The United States of Europe: A Gravity Model Evaluation of the Four Freedoms. *Journal of Economic Perspectives* 35(2), 23-48.

Hidalgo, C.A. and Hausmann, R. (2009). The Building Blocks of Economic Complexity. *Proceedings of the National Academy of Sciences* 106(26), 10570-10575.

Hidalgo, C.A., Klinger, B., Barabási, A.-L. and Hausmann, R. (2007). The Product Space Conditions the Development of Nations. *Science* 317(5837), 482-487.

Hummels, D.L. and Schaur, G. (2013). Time as a Trade Barrier. *American Economic Review* 103(7), 2935-2959.

Ignatenko, A., Lashkaripour, A., Macedoni, L. and Simonovska, I. (2025). Making America Great Again? The Economic Impacts of Liberation Day Tariffs. *Journal of International Economics* 157, 104138.

Johnson, R.C. and Noguera, G. (2012). Accounting for Intermediates: Production Sharing and Trade in Value Added. *Journal of International Economics* 86(2), 224-236.

Khandelwal, A. (2010). The Long and Short (of) Quality Ladders. *Review of Economic Studies* 77(4), 1450-1476.

Mayer, T., Vicard, V. and Zignago, S. (2019). The Cost of Non-Europe, Revisited. *Economic Policy* 34(98), 145-199.

Mealy, P., Farmer, J.D. and Teytelboym, A. (2019). Interpreting Economic Complexity. *Science Advances* 5(1), eaau1705.

Schott, P.K. (2008). The Relative Sophistication of Chinese Exports. *Economic Policy* 23(53), 5-49.

Sciarra, C., Chiarotti, G., Ridolfi, L. and Laio, F. (2020). Reconciling Contrasting Views on Economic Complexity. *Nature Communications* 11, 3352.

Soderbery, A. (2015). Estimating Import Supply and Demand Elasticities: Analysis and Implications. *Journal of International Economics* 96(1), 1-17.

Tacchella, A., Cristelli, M., Caldarelli, G., Gabrielli, A. and Pietronero, L. (2012). A New Metrics for Countries' Fitness and Products' Complexity. *Scientific Reports* 2, 723.

Yotov, Y.V., Piermartini, R., Monteiro, J.-A. and Larch, M. (2016). *An Advanced Guide to Trade Policy Analysis: The Structural Gravity Model*. Geneva: WTO and UNCTAD.
