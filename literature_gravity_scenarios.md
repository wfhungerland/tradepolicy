# Structural Gravity for Trade-Policy Scenarios: Methods, Data and Elasticities in the Peer-Reviewed Literature

*Compiled 5 November 2026 for strand 3 (counterfactual scenarios for Germany and the EU). Companion to `data_inventory_gravity.md`.*

**How sources were checked.** Direct page fetches from this session were blocked (HTTP 403 via the proxy for doi.org, aeaweb.org, sciencedirect.com, academic.oup.com, ideas.repec.org and econpapers.repec.org; api.openalex.org and api.crossref.org unreachable). Every reference was therefore checked through web search results that quote index records (EconPapers/RePEc, publisher landing pages, EconBiz, author or institutional repositories). **[V]** means authors, year, journal, volume and pages (or article number) were confirmed by at least one such index record; content statements rest on abstracts, not full texts. **[U]** means not checked. Working papers are flagged **(WP)**.

---

## 1. Workhorse methods

**Structural gravity with PPML and fixed effects.** Head and Mayer (2014) is the standard reference for estimation: naive gravity estimators give biased and misread results, and estimation is the first step before a welfare analysis [V]. Fally (2015) shows that PPML with exporter and importer fixed effects automatically satisfies the adding-up constraints of structural gravity, so the fixed effects are the multilateral resistance terms; OLS and Gamma-PML do not have this property [V]. This is why PPML is the default estimator in every applied paper below.

**GE-PPML.** Anderson, Larch and Yotov (2018) replace a nonlinear solver with a sequence of constrained PPML regressions to compute general equilibrium comparative statics, with calibrated or estimated trade costs [V]. Yotov, Piermartini, Monteiro and Larch (2016), the WTO-UNCTAD *Advanced Guide*, gives the full recipe and Stata code: partial equilibrium estimation with domestic flows, pair fixed effects and time-varying exporter and importer effects, then "conditional" and "full endowment" GE counterfactuals [V; book, not a journal, but the de facto manual for government users]. This is a one-sector (or sector-by-sector) Armington or Eaton-Kortum endowment model without input-output links.

**Exact hat algebra.** Dekle, Eaton and Kortum (2008) solve counterfactuals in changes, needing only baseline trade shares, GDP and one trade elasticity [V]. Arkolakis, Costinot and Rodríguez-Clare (2012) show that in a broad class of models the welfare change depends only on the change in the domestic trade share and the trade elasticity [V]. Costinot and Rodríguez-Clare (2014) extend hat algebra to multi-sector models with intermediate inputs and show that sectoral heterogeneity and input-output links raise the gains from trade substantially relative to one-sector models [V]. Eaton and Kortum (2002) supply the Ricardian micro-foundation in which the trade elasticity is the Fréchet dispersion parameter [V].

**Multi-sector with input-output.** Caliendo and Parro (2015) build sectoral linkages, intermediate trade and sectoral heterogeneity into a Ricardian model, estimate sector-specific elasticities from tariff variation, and find that ignoring input-output linkages understates the welfare effects of tariff changes (NAFTA: Mexico +1.31 percent, US +0.08 percent, Canada -0.06 percent) [V]. The authors' page provides code and data [V].

**Which approach top papers use.**
- *Tariff scenarios* (2018 and 2025 US tariffs): multi-sector models with input-output and tariff revenue, solved in hat algebra (Fajgelbaum et al. 2020; Ignatenko et al. 2025; Caliendo and Parro 2015). Tariffs enter as observed ad valorem rates, so the elasticity is the parameter that matters.
- *RTA and EU integration*: two-step structural gravity. Step 1 estimates the RTA or EU effect with PPML, pair fixed effects and domestic flows; step 2 runs GE counterfactuals (Mayer, Vicard and Zignago 2019; Baier, Yotov and Zylkin 2019; Felbermayr et al. 2015, 2022). Brexit work with policy weight (Dhingra et al. 2017) uses multi-sector models with intermediates.
- *Transport shocks*: quasi-experimental reduced-form gravity on route-specific distance changes (Feyrer 2019, 2021; Heiland et al. 2025), sometimes followed by a GE welfare calculation.

---

## 2. Tariff scenario papers, tariff data and elasticities

**2018 US tariffs.** Fajgelbaum, Goldberg, Kennedy and Khandelwal (2020) estimate import demand and foreign export supply elasticities from the 2018 tariff waves and embed them in a GE model with tariff revenue: complete pass-through to US buyers, a gross loss of USD 51 billion (0.27 percent of GDP) and a net real income loss of USD 7.2 billion (0.04 percent of GDP) [V]. Amiti, Redding and Weinstein (2019) find full pass-through into US domestic prices and an aggregate real income loss of about USD 1.4 billion per month by end-2018 [V]. Both use US product-level (HS10) import data and the published tariff lists; neither is a gravity model, but both show that in the short run pass-through to the tariff-imposing country is close to complete, which a gravity scenario should match.

**2025 US tariffs.** The only peer-reviewed paper found is Ignatenko, Lashkaripour, Macedoni and Simonovska (2025), *JIE* 157, article 104138: a 194-country quantitative model with flexible pass-through and endogenous trade deficits [V]. Without retaliation the US gains modestly; with optimal foreign retaliation US welfare falls by up to 3.38 percent with input-output linkages (journal abstract; the NBER WP 33771 version gave 3.8 percent) [V]. Other 2025-26 tariff studies found were working papers or lower-tier outlets and are not used here. Note the dataset in the inventory: the GTD U.S. Trade War Extension is documented in Rodriguez-Clare, Teti, Ulate, Vasquez and Zarate (2025), CESifo WP 12179 (WP) [V via inventory].

**Trade elasticities.**
- Fontagné, Guimbard and Orefice (2022), *JIE* 137: HS6 elasticities for more than 5,000 products from bilateral tariff variation in structural gravity, 2001-2016 [V]. This is the ProTEE dataset in the inventory. At HS6 the median magnitude in ProTEE_0_1 is about 7.9 (inventory computation), higher than typical aggregate values, so aggregation to model sectors must be trade-weighted.
- Boehm, Levchenko and Pandalai-Nayar (2023), *AER* 113(4): MFN tariff changes as shocks, local projections; short-run (one-year) elasticity about 0.76, long-run 1.75-2.25, with 7-10 years to converge [V; figures from the replication-package summary]. These are much lower than standard values.
- Simonovska and Waugh (2014), *JIE* 92(1): aggregate elasticity of about 4 from price-gap data, about half the Eaton-Kortum estimate [V].
- Caliendo and Parro (2015): sector-specific elasticities from tariff variation, consistent with any multiplicative gravity model; widely reused in multi-sector models [V; sector values not checked here].

---

## 3. EU integration and RTA effects

- **Mayer, Vicard and Zignago (2019)**, *Economic Policy* 34(98): gravity estimates of the trade created by the EU, then GE counterfactuals of the EU reverting to a shallow RTA or to WTO rules, with and without Brexit; welfare by member state [V]. This is the closest template for a German single-market scenario. Their exact trade and RTA data were not checked [U].
- **Baier, Yotov and Zylkin (2019)**, *JIE* 116: 908 pair-and-direction-specific FTA effects (1986-2006) from structural gravity with domestic flows; about two-thirds of heterogeneity is within agreements; effects are weaker for distant pairs and pairs with an existing agreement; GE simulation of TTIP [V]. Lesson: a single EU dummy hides large pair heterogeneity; estimate pair- or direction-specific effects.
- **Felbermayr, Heid, Larch and Yalcin (2015)**, *Economic Policy* 30(83): structurally estimated GE model for 173 countries; TTIP as a 16-26 percentage point cut in transatlantic ad valorem trade costs; Germany +3.5 percent, EU +3.9 percent, most third countries lose [V].
- **Felbermayr, Gröschl and Steininger (2022)**, *Review of World Economics* 158(2): ex post EU and RTA effects estimated with structural gravity, then ex ante Brexit in a multi-sector model with 50 industries and inter- and intranational production networks, 43 countries plus rest of world [V]. Field journal, peer-reviewed; not on the owner's list.
- **Dhingra, Huang, Ottaviano, Pessoa, Sampson and Van Reenen (2017)**, *Economic Policy* 32(92): multi-sector GE model with intermediate trade; UK welfare loss 1.3 percent (soft) to 2.7 percent (hard Brexit), more with dynamic productivity effects [V]. Use of WIOD is from memory [U].

**Data used in these papers.** The common elements are domestic (intranational) flows to identify border and RTA effects, RTA dummies by type and date, and for multi-sector work world input-output tables. The ITPD-E documentation paper is Borchert, Larch, Shikher and Yotov (2021), *International Economics* 166, 140-166 [V] (peer-reviewed but not on the owner's list); the R2025 release is a USITC working paper (WP).

---

## 4. Transport cost shocks

- **Feyrer (2021)**, *Journal of Development Economics* 153: the 1967-1975 Suez closure as a natural experiment in sea distance; the distance elasticity of trade is about half the usual cross-sectional estimate; trade raises income [V]. **Correction to the brief:** the Suez paper is in *JDE*, not *AEJ: Applied*. Feyrer's *AEJ: Applied* paper is Feyrer (2019), 11(4), 1-35, which uses the rise of air transport as a time-varying geographic instrument (income elasticity of trade about one-half) [V].
- **Hummels (2007)**, *JEP* 21(3): survey of the level and evolution of ocean and air transport costs [V; content not read].
- **Hummels and Schaur (2013)**, *AER* 103(7): each day in transit is equivalent to an ad valorem tariff of 0.6 to 2.1 percent, highest for parts and components [V]. This converts Red Sea rerouting days into tariff equivalents.
- **Heiland, Moxnes, Ulltveit-Moe and Zi (2025)**, *Review of Economics and Statistics*, doi 10.1162/rest.a.267: satellite (AIS) container-ship data, optimal routes, 2016 Panama Canal expansion as a natural experiment; trade between canal-using pairs rose about 9-10 percent; gains spread widely through the shipping network [V from author pages and Google Scholar; journal landing page not seen; earlier CEPR DP 14193, 2019].
- **Red Sea 2023-25.** No peer-reviewed structural gravity paper was found in the listed journals. Existing work is UNCTAD reports, VoxEU columns and working papers; do not cite these as journal evidence.

---

## 5. Recommendation: minimal credible combination per scenario

The common core is **ITPD-E R2025** (domestic plus international flows by industry to 2023), **PPML with exporter-year, importer-year and pair fixed effects**, and a **GE step**. The datasets match what the journals use: domestic flows (ITPD-E, as in Yotov et al. 2016 and Baier et al. 2019), tariff-based elasticities (ProTEE = Fontagné et al. 2022), and route-based distance (CERDI-seadistance, analogous to Feyrer's sea distances).

| Scenario | Minimal model | Data from inventory | Key elasticity | Journal template |
|---|---|---|---|---|
| (a) US tariffs 2025-26 | Multi-sector hat algebra with input-output and tariff revenue (Caliendo-Parro style); GE-PPML by sector as a cross-check | ITPD-E R2025 (trade shares), OECD ICIO 2025 or WIOD (IO shares), CEPII US tariffs 2025-26 (current US AVEs), MAcMap-HS6 or Teti GTD (baseline), GTD Trade War Extension (dates, retaliation) | Sector elasticities from ProTEE, trade-weighted to ICIO sectors; sensitivity with Caliendo-Parro sector values, an aggregate of about 4 (Simonovska-Waugh) and the Boehm et al. short-run value for a 1-2 year horizon | Caliendo and Parro 2015; Ignatenko et al. 2025; Fajgelbaum et al. 2020 |
| (b) EU integration and RTAs | Two-step: PPML with domestic flows and pair- or direction-specific EU/RTA effects, then GE-PPML (endowment model), plus an IO variant for Germany | ITPD-E R2025, Larch RTA database (1950-2025, by type), CEPII Gravity V202211 (controls), DTA 2.0 or DESTA for depth, TradeProd as robustness | The PPML step identifies trade-cost changes directly; the GE step needs one elasticity (4 to 8 band, report both) | Mayer, Vicard and Zignago 2019; Baier, Yotov and Zylkin 2019; Felbermayr et al. 2015, 2022 |
| (c) Transport shocks (Red Sea, Panama) | Route-based shock to bilateral trade costs (extra sea distance plus days times Hummels-Schaur tariff equivalent), fed into GE-PPML or hat algebra; short horizon | CERDI-seadistance with own Cape and Panama rerouting, PortWatch (timing and scale of transit drops), OECD ITIC (CIF/FOB margins by HS4 to scale cost changes), ITPD-E R2025 (baseline), GSCPI (validation) | Distance elasticity from time variation (Feyrer 2021, about half the cross-section) rather than the cross-sectional value; trade elasticity on the short-run side (Boehm et al.) because the shock is temporary | Feyrer 2021; Heiland et al. 2025; Hummels and Schaur 2013 |

**Key elasticity choice.** The welfare numbers scale roughly with the inverse of the trade elasticity (ACR 2012), so this is the decisive assumption. Recommended: a central case with ProTEE sector elasticities (journal-backed, tariff-identified, matching the tariff data source), and two bounds, Simonovska-Waugh (about 4) and Boehm et al. (about 2 long-run, 0.76 short-run). State the horizon explicitly: the Boehm et al. values imply much larger short-run welfare effects for given tariffs than standard values.

**Caveats.** (1) Results for Germany are sensitive to how the US trade deficit is closed (Ignatenko et al. treat deficits endogenously; Dekle et al. 2008 show rebalancing matters). (2) The one-sector GE-PPML endowment model understates tariff effects relative to IO models (Caliendo and Parro 2015; Costinot and Rodríguez-Clare 2014). (3) ProTEE median magnitudes at HS6 (about 7.9) exceed aggregate estimates; aggregation choice will move results.

---

## References

- Amiti, M., Redding, S.J. and Weinstein, D.E. (2019). The Impact of the 2018 Tariffs on Prices and Welfare. *Journal of Economic Perspectives* 33(4), 187-210. doi:10.1257/jep.33.4.187 [V]
- Anderson, J.E., Larch, M. and Yotov, Y.V. (2018). GEPPML: General Equilibrium Analysis with PPML. *The World Economy* 41(10), 2750-2782. doi:10.1111/twec.12664 [V]
- Arkolakis, C., Costinot, A. and Rodríguez-Clare, A. (2012). New Trade Models, Same Old Gains? *American Economic Review* 102(1), 94-130. doi:10.1257/aer.102.1.94 [V]
- Baier, S.L., Yotov, Y.V. and Zylkin, T. (2019). On the Widely Differing Effects of Free Trade Agreements: Lessons from Twenty Years of Trade Integration. *Journal of International Economics* 116, 206-226. doi:10.1016/j.jinteco.2018.11.002 [V]
- Boehm, C.E., Levchenko, A.A. and Pandalai-Nayar, N. (2023). The Long and Short (Run) of Trade Elasticities. *American Economic Review* 113(4), 861-905. doi:10.1257/aer.20210225 [V]
- Borchert, I., Larch, M., Shikher, S. and Yotov, Y.V. (2021). The International Trade and Production Database for Estimation (ITPD-E). *International Economics* 166, 140-166. doi:10.1016/j.inteco.2020.08.001 [V]
- Caliendo, L. and Parro, F. (2015). Estimates of the Trade and Welfare Effects of NAFTA. *Review of Economic Studies* 82(1), 1-44. doi:10.1093/restud/rdu035 [V]
- Costinot, A. and Rodríguez-Clare, A. (2014). Trade Theory with Numbers: Quantifying the Consequences of Globalization. In Gopinath, Helpman and Rogoff (eds), *Handbook of International Economics* Vol. 4, 197-261. Elsevier. [V]
- Dekle, R., Eaton, J. and Kortum, S. (2008). Global Rebalancing with Gravity: Measuring the Burden of Adjustment. *IMF Staff Papers* 55(3), 511-540. doi:10.1057/imfsp.2008.17 [V]
- Dhingra, S., Huang, H., Ottaviano, G., Pessoa, J.P., Sampson, T. and Van Reenen, J. (2017). The Costs and Benefits of Leaving the EU: Trade Effects. *Economic Policy* 32(92), 651-705. doi:10.1093/epolic/eix015 [V]
- Eaton, J. and Kortum, S. (2002). Technology, Geography, and Trade. *Econometrica* 70(5), 1741-1779. doi:10.1111/1468-0262.00352 [V]
- Fajgelbaum, P.D., Goldberg, P.K., Kennedy, P.J. and Khandelwal, A.K. (2020). The Return to Protectionism. *Quarterly Journal of Economics* 135(1), 1-55. doi:10.1093/qje/qjz036 [V]
- Fally, T. (2015). Structural Gravity and Fixed Effects. *Journal of International Economics* 97(1), 76-85. doi:10.1016/j.jinteco.2015.05.005 [V]
- Felbermayr, G., Gröschl, J. and Steininger, M. (2022). Quantifying Brexit: From Ex Post to Ex Ante Using Structural Gravity. *Review of World Economics* 158(2), 401-465. doi:10.1007/s10290-021-00436-z [V]
- Felbermayr, G., Heid, B., Larch, M. and Yalcin, E. (2015). Macroeconomic Potentials of Transatlantic Free Trade: A High Resolution Perspective for Europe and the World. *Economic Policy* 30(83), 491-537. doi:10.1093/epolic/eiv009 [V]
- Feyrer, J. (2019). Trade and Income: Exploiting Time Series in Geography. *American Economic Journal: Applied Economics* 11(4), 1-35. doi:10.1257/app.20170616 [V]
- Feyrer, J. (2021). Distance, Trade, and Income: The 1967 to 1975 Closing of the Suez Canal as a Natural Experiment. *Journal of Development Economics* 153, 102708. doi:10.1016/j.jdeveco.2021.102708 [V]
- Fontagné, L., Guimbard, H. and Orefice, G. (2022). Tariff-Based Product-Level Trade Elasticities. *Journal of International Economics* 137, 103593. doi:10.1016/j.jinteco.2022.103593 [V]
- Head, K. and Mayer, T. (2014). Gravity Equations: Workhorse, Toolkit, and Cookbook. In Gopinath, Helpman and Rogoff (eds), *Handbook of International Economics* Vol. 4, 131-195. doi:10.1016/B978-0-444-54314-1.00003-3 [V]
- Heiland, I., Moxnes, A., Ulltveit-Moe, K.H. and Zi, Y. (2025). Trade From Space: Shipping Networks and the Global Implications of Local Shocks. *Review of Economics and Statistics*. doi:10.1162/rest.a.267 [V, author pages only; volume and pages not confirmed]
- Hummels, D. (2007). Transportation Costs and International Trade in the Second Era of Globalization. *Journal of Economic Perspectives* 21(3), 131-154. doi:10.1257/jep.21.3.131 [V]
- Hummels, D.L. and Schaur, G. (2013). Time as a Trade Barrier. *American Economic Review* 103(7), 2935-2959. doi:10.1257/aer.103.7.2935 [V]
- Ignatenko, A., Lashkaripour, A., Macedoni, L. and Simonovska, I. (2025). Making America Great Again? The Economic Impacts of Liberation Day Tariffs. *Journal of International Economics* 157, 104138. doi:10.1016/j.jinteco.2025.104138 [V]
- Mayer, T., Vicard, V. and Zignago, S. (2019). The Cost of Non-Europe, Revisited. *Economic Policy* 34(98), 145-199. doi:10.1093/epolic/eiz002 [V]
- Simonovska, I. and Waugh, M.E. (2014). The Elasticity of Trade: Estimates and Evidence. *Journal of International Economics* 92(1), 34-50. doi:10.1016/j.jinteco.2013.10.001 [V]
- Yotov, Y.V., Piermartini, R., Monteiro, J.-A. and Larch, M. (2016). *An Advanced Guide to Trade Policy Analysis: The Structural Gravity Model*. Geneva: WTO and UNCTAD. [V; some print records date it 2017]
- (WP) Rodriguez-Clare, A., Teti, F., Ulate, M., Vasquez, J.P. and Zarate, R. (2025). CESifo Working Paper 12179 (documentation of the GTD U.S. Trade War Extension). [V via data inventory; title not checked here]
