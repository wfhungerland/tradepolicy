# Gravity Models for Monthly/Quarterly Trade Forecasting and Nowcasting: A Focused Literature Review

*Compiled 4 November 2026. Question: Are gravity models suitable for forecasting or nowcasting German and world trade at monthly or quarterly frequency?*

**How sources were checked.** All sources were located via web search, and bibliographic data were checked against index records (RePEc/EconPapers/IDEAS, EconBiz, publisher or institution pages). Full-text fetching was blocked in this session for arxiv.org, imf.org and cepr.org. So for most entries the claims rest on abstracts and index summaries, not on full texts. Markers used: **[V]** = citation verified on an index or publisher page; **[V-abs]** = verified, but content taken from the abstract only; **[U]** = some element unverified (stated in the entry).

---

## Bottom line

The literature is **thin and points against** using gravity models as the main tool for short-horizon aggregate forecasting.

- Monthly and quarterly forecasting of German and world trade is done almost entirely with time-series and indicator methods. These include bridge equations, MIDAS, dynamic factor models (DFMs), machine-learning regressions on hundreds of indicators, and ship-tracking (AIS) data.
- None of the institutional forecasters reviewed (ECB, OECD, WTO, IMF, CPB, Kiel) uses a gravity equation for short-term projections of the aggregate time path.
- Gravity work at monthly frequency exists, but it is used for **ex-post identification** of shocks (COVID, sanctions, Brexit), not for forecasting.
- The out-of-sample gravity literature (Apfel et al. 2025; Kunst & Nuroglu 2014; Morland et al. 2025; ML comparisons) mostly tests **cross-sectional or counterfactual** prediction on annual data. It does not test real-time time-series forecasting.

The structural reason: in a theory-consistent gravity model with exporter-time and importer-time fixed effects, the whole aggregate time dimension sits inside the fixed effects. The model therefore has nothing to say about next month's German exports unless those fixed effects are forecast by some other model. Gravity can add value only in two places: (i) **bilateral or compositional allocation** of an aggregate forecast, and (ii) **conditional/scenario** nowcasts of policy shocks.

---

## 1. Nowcasting and short-term forecasting of trade

**Keck, A. & Raubold, A. (2006).** *Forecasting trade.* WTO Staff Working Paper ERSD-2006-05. https://ideas.repec.org/p/zbw/wtowps/ersd200605.html **[V-abs]**
Time-series models for short-term trade forecasts 6–18 months ahead. This is the WTO's own methodological starting point.

**Keck, A., Raubold, A. & Truppia, A. (2009/2010).** "Forecasting international trade: A time series approach." *OECD Journal: Journal of Business Cycle Measurement and Analysis*, 2009(2), 157–176. https://ideas.repec.org/a/oec/stdkab/5ks9v44bdj32.html **[V-abs; DOI not verified]**
Time-series model for import growth of major advanced economies in the current and following year. D'Agostino, Modugno & Osbat (ECB WP 1986, 2016; https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1986.en.pdf **[V, listing only]**) cite it as the reference for time-series trade models with good forecasting properties.

**Burgert, M. & Dées, S. (2008/2009).** "Forecasting world trade: direct versus 'bottom-up' approaches." ECB WP 882; *Open Economies Review* 20(3), 385–402. https://ideas.repec.org/p/ecb/ecbwps/2008882.html **[V-abs]**
- Forecasting world trade **directly at the aggregate level** beats aggregating country forecasts bottom-up.
- Factor models summarising large datasets do well.
- This is relevant to gravity: a gravity model is a bilateral bottom-up approach.

**Jakaitiene, A. & Dées, S. (2009/2012).** "Forecasting the world economy in the short term." ECB WP 1059; *The World Economy* 35(3), 331–350. https://econpapers.repec.org/RePEc:ecb:ecbwps:20091059 **[V-abs]**
Compares the accuracy of short-term methods (factor models, time-series models, forecast combinations) for world variables, including trade.

**Guichard, S. & Rusticelli, E. (2011).** "A dynamic factor model for world trade growth." OECD Economics Department WP 874. DOI 10.1787/5kg9zbvvwqq2-en; https://econpapers.repec.org/RePEc:oec:ecoaaa:874-en **[V-abs]**
- Monthly indicators (financial, shipping/transport, orders, IT) feed a DFM.
- The DFM beats bridge models and AR benchmarks, with diminishing returns from adding more indicators.

**Martínez-Martín, J. & Rusticelli, E. (2018).** "Keeping track of global trade in real time." OECD Economics Department WP 1524 (also Banco de España WP); later in the *International Journal of Forecasting*. https://econpapers.repec.org/RePEc:oec:ecoaaa:1524-en ; https://www.bde.es/wbe/en/publicaciones/analisis-economico-investigacion/documentos-trabajo/keeping-track-global-trade-real-time.html **[V-abs; IJF year/volume U - indexes disagree (2019 vs 2021)]**
- Mixed-frequency DFM with Markov switching, built as a real-time world trade-cycle index covering goods and services.
- *Note:* the brief named "Martínez-Martín & Rusinova". No such pairing was found; the co-author is **Rusticelli**.

**Chinn, M. D., Meunier, B. & Stumpner, S. (2023).** "Nowcasting world trade with machine learning: a three-step approach." NBER WP 31419; ECB WP 2836; Banque de France WP 917. https://www.nber.org/papers/w31419 ; https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2836~6b34f0492c.en.pdf **[V-abs]**
- About 600 indicators go through three steps: pre-selection, factor extraction, then ML regression.
- The approach beats PCA-OLS, elastic net and a DFM. Tree-based methods perform poorly.
- The target is the CPB world trade series, which is published about 8 weeks after month end.
- *Note:* "Cantú/Chinn" was not found; this is the Chinn paper that matches.

**Jackson, C. & Rivera Greenwood, D. (2026).** "Nowcasting world trade with a multi-region factor model." IMF WP 26/48. https://econpapers.repec.org/RePEc:imf:imfwpa:2026/048 **[V-abs]**
Block-structured DFM with global plus regional factors. It beats a single-factor DFM in the COVID period.

**Arslanalp, S., Choi, … Verschuur, J. (2025).** "Nowcasting global trade from space." IMF WP 2025/093. https://econpapers.repec.org/RePEc:imf:imfwpa:2025/093 **[V-abs; full author list per index]**
Monthly nowcast of maritime trade from AIS vessel data (IMF PortWatch).
**Arslanalp, S., Exton, … Verschuur, J. (2026).** "Nowcasting country-level trade estimates using IMF PortWatch." IMF WP 2026/099. https://econpapers.repec.org/RePEc:imf:imfwpa:2026/099 **[V-abs]**
Country-level monthly estimates within about 7 working days. The best fit is for advanced economies and large emerging markets.

**Stamer, V. (2021; rev. 2022).** "Thinking outside the container: A machine learning [sparse partial least squares] approach to forecasting trade flows." Kiel Working Paper 2179. https://econpapers.repec.org/RePEc:zbw:ifwkwp:2179 **[V-abs; a journal version is listed on ifw-kiel.de but its outlet was not verified]**
- This is the basis of the **Kiel Trade Indicator**.
- Container-ship positions are mapped by PLS/LASSO to unilateral and bilateral flows for 75–76 economies.
- It beats benchmarks for most countries in current-month and next-month nowcasts.
- Lechthaler & Stamer (SUERF Policy Brief) stress that it is a container-based indicator, "not an all-encompassing forecasting model of trade". https://www.suerf.org/publications/suerf-policy-notes-and-briefs/the-kiel-trade-indicator-a-real-time-indicator-for-trade-flows **[V-abs]**

**CPB Netherlands Bureau for Economic Policy Analysis.** *World Trade Monitor*, technical description (2016; updates 2018, 2020, April 2023). https://cpb.nl/en/node/161098 **[V, landing page only]**
- Monthly compilation, not a forecast. It is the standard **target variable** for world-trade nowcasts.
- Method overhaul in 2012 (Ebregt memo).

**Germany-specific.**
- **Hanslin Grossmann, S. & Scheufele, R. (2019).** "PMIs: Reliable indicators for exports?" *Review of International Economics* 27(2), 711–734. DOI 10.1111/roie.12395 **[V-abs]**
  - MIDAS models with foreign PMIs, weighted by German and Swiss export shares.
  - The forecasts compare favourably with benchmarks for quarterly export growth.
- **Grimme, C. & Lehmann, R. (2019).** "The ifo Export Climate – A leading indicator to forecast German export growth." *CESifo Forum* 20(4), 36–42. https://ideas.repec.org/a/ces/ifofor/v20y2020i04p36-42.html **[V-abs]**
  - Export-share-weighted foreign business climate plus price competitiveness.
  - The best indicator for next-quarter German exports among those tested.
- **No Bundesbank discussion paper specifically on nowcasting German exports was found** (searched; possibly exists but unverified).
- Note that the German indicators *do* use a gravity-like ingredient: **partner weights by export share**. They do not estimate a gravity equation.

**Synthesis, area 1.** The established toolkit is bridge equations, MIDAS, DFMs, ML regressions and AIS data. Benchmarks are AR and random walk. Gravity does not appear in this literature as a forecasting model.

---

## 2. Gravity with high-dimensional fixed effects and out-of-sample prediction

**Estimation tool.** Correia, S., Guimarães, P. & Zylkin, T. (2020). "Fast Poisson estimation with high-dimensional fixed effects." *The Stata Journal* 20(1), 95–115. DOI 10.1177/1536867X20909691 **[V]**

**Apfel, Breinlich, Green, Novy, Santos Silva & Zylkin (2025).** "Out-of-sample gravity predictions and trade policy counterfactuals." arXiv 2509.11271. https://arxiv.org/abs/2509.11271 **[V-abs via search index; full text not accessible; data frequency U - most likely annual]**
- The **3-way model** (exporter-time, importer-time and pair fixed effects) is hard to beat on *average* out-of-sample predictive performance, especially in flexible specifications.
- 2-way models can be beaten by ML methods, and ensemble ML can beat the 3-way model for *individual* bilateral flows.
- The prediction targets are held-out flows and policy counterfactuals, not future aggregate periods.

**Kunst, R. M. & Nuroglu, E. (2014).** "Competing specifications of the gravity equation: a three-way model, bilateral interaction effects, or a dynamic gravity model with time-varying country effects?" *Empirical Economics*. DOI 10.1007/s00181-013-0696-3 **[V-abs]**
- Compares out-of-sample forecast performance of gravity specifications, including time-varying country effects.
- This is one of the few papers that addresses forecasting directly, on annual data.

**Breinlich, H., Corradi, V., Rocha, N., Ruta, M., Santos Silva, J.M.C. & Zylkin, T. (2021/2022).** "Machine learning in international trade research – evaluating the impact of trade agreements." World Bank PRWP 9629; CEP DP 1776; CEPR DP 17325. https://econpapers.repec.org/RePEc:cep:cepdps:dp1776 **[V-abs]**
ML variable selection (lasso variants) within PPML gravity to identify which PTA provisions matter. This is **inference, not forecasting**.

**Gopinath, M., Batarseh, F. A. & Beckman, J. (2020/2021).** "Machine learning in gravity models: An application to agricultural trade." NBER WP 27151 https://econpapers.repec.org/RePEc:nbr:nberwo:27151 ; published as "International agricultural trade forecasting using machine learning," *Data & Policy* (Cambridge). **[V-abs; title of NBER version U]**
- Neural networks fit better than gravity over long horizons for seven agricultural commodities.
- Annual data; no real-time design.

**Wohl, I. & Kennedy, J. (2018).** "Neural network analysis of international trade." USITC Office of Industries WP ID-049. https://www.usitc.gov/publications/332/working_papers/050218_neural.html **[V-abs]**
- Self-described "very preliminary".
- A neural network with country fixed effects gives the lowest out-of-sample RMSE for US bilateral trade.

**Morland, C., Tandetzki, J. & Schier, F. (2025).** "An evaluation of gravity models and artificial neuronal networks on bilateral trade flows in wood markets." *Forest Policy and Economics* 172, 103457. https://www.sciencedirect.com/science/article/pii/S138993412500036X **[V-abs]**
- Neural networks fit better in-sample, but their advantage shrinks with the horizon.
- Gravity gives "stable" long-horizon (annual) forecasts.

**Baxter, M. & Kouparitsas, M. A. (2006).** "What determines bilateral trade flows?" NBER WP 12188 (Chicago Fed WP 2005-11). https://www.nber.org/papers/w12188 **[V-abs]**
- An extreme-bounds style robustness search over gravity regressors. Few variables survive, and currency-union effects are small.
- Relevance: it warns that many gravity covariates are fragile. It is not about forecasting.

**Monthly bilateral gravity (all ex-post identification):**
- **Zajc Kejžar, K., Velić, A. & Damijan, J. P. (2022).** "COVID-19, trade collapse and GVC linkages: European experience." *The World Economy* 45(11), 3475–3506. DOI 10.1111/twec.13314 **[V-abs]**
  Monthly intra-EU gravity; trade fell by more than 20% after the COVID outbreak.
- PLOS ONE (2021). "Effects of COVID-19 on trade flows: Measuring their impact through government policy responses." https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8513914/ **[V; authors not verified]**
  Monthly data, 68 exporters × 222 destinations. The paper explicitly notes that monthly gravity evidence is "scarce and far from conclusive".
- **Hayakawa, K. & Kumagai, S. (2022).** IDE Discussion Paper 857 (Russia 2022). https://www.ide.go.jp/English/Publish/Reports/Dp/857.html **[V-abs; exact title U]**
  Monthly bilateral data for 40 countries × 220 partners.
- **Freeman, R., Manova, K., Prayer, T. & Sampson, T. (2022).** "Unravelling deep integration: UK trade in the wake of Brexit." CEP DP 1847. https://econpapers.repec.org/RePEc:cep:cepdps:dp1847 **[V-abs; title from memory of index record, treat as U]**
  Uses monthly/high-frequency data; finds a sudden, persistent fall of about 25% in UK imports from the EU relative to the rest of the world from 2021.

None of these monthly-gravity papers reports out-of-sample forecast accuracy.

### The fixed-effects problem (explicit)

With PPML on $X_{ijt} = \exp(\pi_{it} + \chi_{jt} + \mu_{ij} + \beta' z_{ijt})\varepsilon_{ijt}$:

1. **The aggregate time path is absorbed.** Summing over partners, a country's total exports in period *t* are determined mainly by $\pi_{it}$ (output and outward multilateral resistance) and the partners' $\chi_{jt}$ (expenditure and inward multilateral resistance). Germany's total exports next month are thus almost entirely a function of $\hat\pi_{DE,t+h}$ and $\{\hat\chi_{j,t+h}\}$. These do not exist for out-of-sample periods.
2. **Forecasting therefore requires a second model.** Options include a random walk or AR for each fixed effect, a mapping of the fixed effects onto forecastable macro variables (GDP and industrial production forecasts, PMIs, price indices), or imposing the structural solution for multilateral resistance. In every case, the forecast accuracy for aggregates is inherited from that auxiliary model. The gravity layer adds only the *bilateral redistribution* through $\mu_{ij}$ and time-varying $z_{ijt}$ (tariffs, sanctions, RTAs, exchange rates).
3. **Monthly frequency makes this worse.** It means about 2×N×T fixed effects, strong seasonality, many zeros, CIF/FOB asymmetries and revisions, and very little high-frequency variation in classic gravity covariates (distance, language, RTA dummies are constant or step functions).
4. **Hence the honest framing:** gravity can (a) **decompose** or **allocate** an aggregate nowcast across partners, and (b) produce **conditional nowcasts** of the effects of a known shock, such as tariffs or sanctions, holding the fixed effects at baseline. It cannot replace a time-series nowcast of the level.

No paper was found that forecasts the exporter-time and importer-time fixed effects and evaluates this in real time at monthly or quarterly frequency. This is a genuine gap, and also a sign that the approach is not expected to win.

---

## 3. WTO and IMF forecasting practice

**WTO trade forecasts.**
- *Global Trade Outlook and Statistics*, April 2025. https://www.wto.org/english/res_e/booksp_e/trade_outlook25_e.pdf ; press release https://www.wto.org/english/news_e/news25_e/tfore_16apr25_e.htm **[V via WTO search index]**
- The method combines a **consensus regional GDP forecast with trade–GDP relationships** (Keck & Raubold 2006 lineage) and expert judgement.
- In shock periods the WTO "used policy simulations generated by the organization's **Global Trade Model** to adjust their regular trade forecasts" (April 2025: −0.2% for 2025; revised to +0.9% in August and 2.4% in October 2025).
- The Global Trade Model is a recursive-dynamic CGE model built with GTAP, intended for medium/long-run projections (WTO iLibrary record **[V-abs]**).
- WTO material reports the long-run trade/GDP elasticity at about 1.4, falling recently (**[U]**: figure taken from secondary summaries).

**WTO Goods Trade Barometer.** Release pages, e.g. https://www.wto.org/english/news_e/news24_e/wtoi_04sep24_e.htm **[V]**
- Composite leading indicator (export orders, air freight, container shipping, automotive, electronic components, raw materials). 100 = trend.
- Leads trade by roughly 2–3 months; export orders are the most predictive component.
- The methodology technical note is linked from these pages but was **not read**.

**IMF.**
- WEO world trade volume (goods and services) projections are aggregated from country-desk projections within the WEO macro framework.
- **No public IMF methodology note specific to WEO trade-volume forecasting was found [gap].**
- Related verified IMF work:
  - **WEO October 2016, Ch. 2** "Global trade: What's behind the slowdown?" Import-demand model: weak activity, especially investment, explains up to three-quarters of the slowdown. https://www.imf.org/external/pubs/ft/weo/2016/02/ **[V-abs]**
  - **Celasun, Lee, Mrkaic & Timmermann (2021)**, "An evaluation of WEO growth forecasts, 2004–17," IMF WP 21/216. https://econpapers.repec.org/RePEc:imf:imfwpa:2021/216 **[V-abs]**. Growth forecasts only; it suggests using partner growth more efficiently.
  - The IMF trade-nowcasting papers listed in §1 (WP 25/093, 26/048, 26/099).
- The CEPR/VoxEU column "Trade illusion and disillusion: a cyclical phenomenon" (based on Borin et al. 2017) is relevant. Its point: most of the IMF's trade forecast error comes from the **income elasticity**, not from GDP. As the horizon shortens, GDP forecasts improve but the elasticity forecast does not. https://cepr.org/voxeu/columns/trade-illusion-and-disillusion-cyclical-phenomenon **[V-abs; authors U]**

**Synthesis, area 3.** Neither the WTO nor the IMF uses gravity for short-term trade projections. The WTO uses a GDP-elasticity time-series model plus a CGE model for scenarios. The IMF uses country-desk aggregation, and IMF research nowcasts with DFMs and AIS data.

---

## Implications for the empirical design

1. **Recast the question.** Do not test "gravity versus time series" for aggregate German or world trade levels; theory and the evidence above predict gravity loses. Instead test whether **gravity structure adds information** to a time-series nowcast:
   - (a) for *bilateral/partner-level* German trade;
   - (b) for aggregates, through bottom-up aggregation of gravity-allocated flows (compare Burgert & Dées 2008: bottom-up usually loses);
   - (c) for *conditional* nowcasts after policy shocks (tariffs 2025, Russia sanctions).
2. **Benchmarks (all in real time):**
   - random walk in log levels and in growth rates (seasonal RW for non-seasonally-adjusted data);
   - AR(p)/seasonal ARIMA with p selected recursively;
   - **bridge equation** (industrial production, PMI new export orders, ifo Export Climate, Kiel Trade Indicator/PortWatch) and a MIDAS variant for quarterly targets;
   - a small DFM (Guichard & Rusticelli style) as the strong benchmark.
3. **Gravity candidates:**
   - PPML with pair fixed effects and time-varying covariates (tariffs, sanctions dummies, real exchange rate, partner industrial production/PMI as proxies for $\chi_{jt}$, German production/prices as proxies for $\pi_{it}$);
   - 3-way PPML whose exporter-time and importer-time fixed effects are forecast by AR/RW or mapped onto indicators (two-step).
   - Report explicitly how much of the forecast comes from the fixed-effects sub-model.
4. **A fair out-of-sample test:**
   - recursive (expanding) window with a pseudo-real-time **data vintage** structure, respecting publication lags (Destatis about 40 days; IMTS later; CPB about 8 weeks);
   - horizons h = 0 (nowcast), 1, 3 months and 1–2 quarters;
   - identical information sets across models;
   - losses: RMSE/MAE of y/y and m/m growth, plus directional accuracy;
   - tests: Diebold–Mariano (Clark–West for nested models), with Giacomini–White for conditional performance;
   - sub-samples: pre-2020, COVID, 2022 energy/sanctions, 2025 tariffs;
   - forecast combinations (gravity + bridge).
   - Pre-register the specification to avoid search over fixed-effects structures.
5. **Data needed:**
   - **IMF IMTS** (successor of DOTS) monthly bilateral goods trade, nominal USD, for Germany × partners and a world panel. Seasonality, CIF/FOB mismatch and revisions must be handled; there are no volumes.
   - **Destatis** monthly German trade by partner (current prices) and export/import price indices for deflation.
   - **Eurostat Comext** monthly bilateral data, for product detail.
   - **CPB World Trade Monitor** volumes as the world target.
   - Indicators: industrial production, PMIs/new export orders, ifo Export Climate, Kiel Trade Indicator, IMF PortWatch.
   - Policy data: WITS/MacMap tariffs, Global Sanctions Database, Global Trade Alert.
   - Real-time vintages: the Bundesbank real-time database; ALFRED/OECD MEI vintages.

**Expected result, from the literature:** gravity will not beat bridge/DFM benchmarks for aggregate German or world trade. Its plausible contribution is in partner allocation and shock-conditional nowcasts, and only there is a positive finding likely.
