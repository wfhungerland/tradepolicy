# Economic complexity from BACI HS92: methods review and recommended specification

Scope: Germany vs. large exporters (CHN, USA, JPN, KOR, ITA, FRA, GBR, NLD and others), 1995-2024, BACI HS92 HS6 bilateral exports aggregated to country-product-year exports. Measures: Balassa RCA, binary matrix M, diversity, ubiquity, ECI, PCI, proximity, density, COI, COG.

Verification note: web search worked in this session, but direct fetches of atlas.hks.harvard.edu, growthlab.hks.harvard.edu, dataverse.harvard.edu, oec.world, cepii.fr, arxiv.org and pmc.ncbi.nlm.nih.gov were blocked by the network allow-list. Claims marked [V] were checked against a search result or a fetched page (py-ecomplexity on GitHub was read in full). Claims marked [U] come from background knowledge and still need checking against the primary document.

## 1. Notation

RCA_cp = (X_cp / X_c) / (X_p / X_w), where X_c is country c's total exports, X_p is world exports of product p and X_w is total world exports (Balassa). M_cp = 1 if RCA_cp >= 1. Diversity k_c,0 = sum_p M_cp; ubiquity k_p,0 = sum_c M_cp.

## 2. Method of reflections vs. eigenvector formulation

**Reflections (Hidalgo & Hausmann 2009).** The algorithm iterates k_c,N = (1/k_c,0) sum_p M_cp k_p,N-1 and k_p,N = (1/k_p,0) sum_c M_cp k_c,N-1. Even N describe countries and odd N describe products [V: PNAS paper].

**Eigenvector form (Hausmann et al. 2014 Atlas; Mealy et al. 2019).** Substitute one step into the other and you get k_c,N = sum_c' Mtilde_cc' k_c',N-2, with Mtilde_cc' = sum_p M_cp M_c'p / (k_c,0 k_p,0). This is a row-stochastic matrix. ECI is the eigenvector belonging to its second largest eigenvalue, standardised to a z-score. PCI is the matching eigenvector of the product matrix [V: Mealy et al. 2019; the Atlas rankings page states "eigenvector associated with the second largest eigenvalue" and z-score normalisation]. Mealy, Farmer & Teytelboym (2019) show that this is the same thing as spectral clustering: it is the solution that splits the country similarity graph into two parts (normalised cut). They also show that ECI is orthogonal to diversity, so ECI is not "diversity corrected for ubiquity" [V]. Kemp-Benedict (2014) had already made the orthogonality point and argued that the ECI-income link may reflect the known export-income relationship [V: SEI/MPRA abstract].

**Why the two are equivalent in the limit.** Each double reflection is one step of power iteration on Mtilde. Because Mtilde is row-stochastic, its leading eigenvalue is 1 and its eigenvector is constant. The iteration therefore converges to a vector in which every country has the same value, so all information disappears in the strict limit. Ranking information survives only in the deviations from that constant. Those deviations shrink like lambda_2^N, so after normalisation they are dominated by the second eigenvector, which is the ECI. Mtilde is similar to the symmetric positive semi-definite matrix D^-1/2 M U^-1 M' D^-1/2, so its eigenvalues are real and lie in [0, 1] [U: standard linear algebra, consistent with Mealy et al.].

**Practical problems with reflections.** Odd and even steps alternate between products and countries; settling speed depends on lambda_3/lambda_2, so with a small spectral gap ranks keep shifting; geometric decay erodes numerical precision; and the stopping rule is arbitrary, so year-to-year changes partly reflect stopping noise. The eigen-solution is exact, deterministic and fast (roughly 200x200 matrix).

**Recommendation.** Use the eigenvector formulation. Fix the sign so that ECI correlates positively with diversity, which is what py-ecomplexity does (`s1 = np.sign(np.corrcoef(diversity, kc))`) [V: source code]. Run reflections only as a check that the code reproduces the eigenvector ranking.

## 3. Current standard practice

**Harvard Growth Lab Atlas.**
- *Data and cleaning.* The Atlas builds its trade data from UN Comtrade (goods) and IMF (services). Goods data are cleaned by mirroring with country reliability scores, giving a weighted average of importer and exporter reports. This is the Bustos-Yildirim method, now documented in Growth Lab WP 251 (2025) [V].
- *Classification.* HS92 data start in 1995, and the public product level is 4-digit [V: Atlas data downloads, API docs]. The Atlas ECI has traditionally been computed on HS4 (about 1,200 products) [U: precise current level for the rankings not confirmed].
- *Countries in rankings.* Population at least 1 million, average annual trade at least USD 1 billion, reliable reporting history [V: Atlas data downloads page]; the 2011 book used 1.2 million [V].
- *2026 change.* Starting in 2026, the Atlas replaces the binary RCA test with a "continuous scale" of competitiveness [V: Atlas rankings page; formula not found]. Atlas ECI levels after 2026 are therefore not directly comparable with a binary-M replication.
- *Product exclusions and smoothing.* Older Atlas and OEC documentation excluded small products and averaged RCA or exports over neighbouring years to reduce noise [U: exact thresholds and window not verified].
- *Recent ranking.* In 2024 the Growth Lab ranked Japan, Korea, Switzerland, Singapore, Taiwan and Germany as the top six, with the UK 10th, the US 14th and China 18th [V: Growth Lab post on X].

**py-ecomplexity (Growth Lab)** [V: source code and README]: presence test "rca" by default with threshold 1 (alternatives "rpop", "both", "manual"); PCI = eigenvector of the second largest eigenvalue of Mpp = (M/U)'(M/D), ECI = (M/D) PCI; PCI standardised with ECI's moments so that ECI equals the mean PCI of a country's products; ECI z-scored per year; proximity binary (default) or continuous, symmetric or asymmetric; density optionally via k nearest neighbours; COI and COG from proximity. No cleaning, thresholds or smoothing: the user must supply them.

**OEC** [V: methods page and rankings via search snippets]: ECI per HS revision (HS92 to HS22) at HS4 and HS6 depth; country and product thresholds rise with the number of available years; HS6 product thresholds are one quarter of HS4 values because HS6 has about 4 times as many categories (table values not retrieved); ECI described as the average PCI of activities present.

**Comparability over time.** ECI is z-scored within each year in py-ecomplexity [V: code], so it is a relative position: a rising German ECI means a gain relative to the sample, not absolute capability growth, and it depends on sample composition. Remedies [U: general practice]: a fixed country and product panel; reporting ranks and peer gaps (DEU minus CHN etc.); optionally projecting yearly M onto PCI weights from a pooled base period.

## 4. Alternatives and critiques

**Fitness-Complexity (Tacchella et al. 2012).** The algorithm uses non-linear maps. Country fitness is F_c = sum_p M_cp Q_p, and product complexity is Q_p = 1 / sum_c M_cp (1/F_c), with both normalised at each step. Product complexity is driven by the least-fit exporters, which matches the nested (triangular) structure of M [V].

*Pros:* rewards diversification instead of averaging it away; captures nestedness. *Cons:*
- Its convergence depends on the structure of M. Only matrices whose "diagonal does not cross the empty part" give non-zero fixed points. Otherwise many values collapse towards zero, and in practice people iterate a fixed number of times and use ranks or logs [V: Pugliese, Zaccaria & Pietronero 2016].
- Morrison et al. (2017) find an intrinsic instability in the non-linear definition. They find that "complex" products are often simply rarely exported ones, and that small changes in the RCA threshold substantially change fitness values and rankings [V].

**GENEPY (Sciarra et al. 2020).** GENEPY puts the method of reflections and Fitness-Complexity into one linear-algebra framework on a non-linearly normalised country-country matrix. It combines the first two eigenvectors into one index, which reconciles the two methods' conflicting rankings [V: abstract]. It is a useful third robustness index [U: formula details from memory; implement from the paper].

**Other variants.** ECI+ and related corrections (Albeaik et al. 2017, "Improving the Economic Complexity Index") [V: title/arXiv; content U].

**Sensitivity.**
- *RCA threshold.* Mealy et al. test thresholds of 0.5, 1 and 2 on HS6 data and report that some country-level results are sensitive [V: search snippet of SI]. Morrison et al. report strong threshold sensitivity for Fitness [V].
- *Aggregation.* Morrison et al. treat aggregation level as a fundamental modelling choice [V]. No study found here systematically compares HS4 and HS6 ECI, so this must be tested directly.
- *Noise at HS6.* Many of the about 5,000 HS6 cells are small, so M flips 0/1 between years and ubiquity is noisy; this argues for value thresholds and smoothing [U: reasoning].

**BACI-specific issues.**
- *Reconciliation.* BACI reconciles exporter and importer declarations with an original procedure: CIF/FOB adjustment and reliability-weighted mirror flows (Gaulier & Zignago 2010). It covers more than 200 countries and about 5,000 products [V: CEPII WP abstract and keywords].
- *Re-exports.* BACI does not remove re-exports, inflating diversity of hubs (NLD, BEL, SGP, HKG); NLD is a peer, so this matters [U: not confirmed in BACI docs].
- *HS revisions.* Using the HS92 vintage throughout gives one fixed nomenclature for 1995-2024, so there is no concordance break inside the panel. CEPII converts later declarations back to HS92, which means newer products (for example post-2007 electronics splits) are folded into older codes. Even the Growth Lab notes that 2023 Comtrade data converted back to HS92 have only about 4,500 six-digit codes [V].
- *Low-quality codes.* Drop non-product and residual codes: HS chapter 99 if present, and "not elsewhere specified" codes with unstable content [U].

## 5. Relatedness

**Proximity (Hidalgo et al. 2007).** phi_pp' = min{P(M_p=1 | M_p'=1), P(M_p'=1 | M_p=1)} = sum_c M_cp M_cp' / max(k_p, k_p'). Taking the minimum guards against a rare product appearing close to everything [V: Science paper; formula standard].

**Density.** omega_cp = sum_p' M_cp' phi_pp' / sum_p' phi_pp'. Distance is d_cp = 1 - omega_cp.

**COI and COG (Hausmann et al. 2014).**
- COI_c = sum_p (1 - d_cp)(1 - M_cp) PCI_p.
- COG_cp = sum_p' [phi_pp' / sum_p'' phi_p''p'] (1 - M_cp') PCI_p' - (1 - d_cp) PCI_p.
- COI is z-scored each year in py-ecomplexity, and COG is scaled by the standard deviation of ECI [V: code; formulas U, check against Atlas book].

**Newer measures.**
- Hidalgo (2021) reviews relatedness and complexity metrics and describes complexity measures as dimensionality reductions of specialisation matrices [V].
- Balland et al. (2022) set out the "new paradigm" principles and policy uses such as recommendation systems [V].
- Hausmann, Stock & Yildirim (2022), "Implied comparative advantage", estimate expected RCA from the relatedness structure, offering a model-based alternative to density [V].
- Continuous measures, such as RCA correlations (the `continuous=True` option in py-ecomplexity) [V] or the new Atlas continuous scale [V], avoid the knife-edge at RCA = 1.

**Implication for Germany.** With a highly diversified basket, density is high almost everywhere, so COI and COG are low for incumbents by construction; read them relative to peers [U].

## 6. Recommended specification

1. **Aggregation level:** Main run at HS4 (about 1,240 HS92 headings), aggregated from BACI HS6. This matches Atlas and OEC practice and reduces sparsity and noise.
2. **HS6 parallel run:** Compute everything at HS6 as well, with product value thresholds at one quarter of the HS4 ones (the OEC rule). This shows whether Germany's position depends on granularity.
3. **Exports measure:** BACI value (v) summed over destinations, using the HS92 vintage only. This gives one nomenclature for 1995-2024 with no concordance breaks.
4. **Country filter:** Population of at least 1 million and average exports of at least USD 1 billion over the period. This follows the Atlas inclusion rule and removes micro-states that distort ubiquity.
5. **Product filter:** Drop products with world exports below a fixed real threshold (for example USD 10 million at HS6 or USD 40 million at HS4, both to be calibrated) and drop residual or "nes" codes. Tiny world markets make M arbitrary.
6. **Fixed panel:** Use the same set of countries and products in every year. Because ECI is z-scored every year, a changing sample would otherwise change the scale.
7. **Smoothing:** Use 3-year centred moving averages of X_cp before computing RCA (with 1995-1997 and 2022-2024 as endpoints). This dampens 0/1 flipping, especially at HS6.
8. **RCA threshold:** Balassa RCA >= 1 for M. This is the literature and py-ecomplexity default and keeps results comparable.
9. **Algorithm:** Eigenvector of the second largest eigenvalue of Mtilde (py-ecomplexity), with the sign aligned to diversity. It is exact, has no stopping-rule or odd/even problems, and is equivalent to reflections in the limit.
10. **Normalisation:** z-score ECI within each year. Scale PCI by ECI's moments. Report Germany's rank and its gap to each peer. As a supplementary series, project yearly M onto pooled-period PCI weights. Yearly z-scores are relative, and the pooled projection adds a fixed yardstick over time.
11. **Relatedness:** Binary proximity (minimum conditional probability), density over the full proximity matrix, and COI/COG as defined in Hausmann et al. (2014). This is the standard definition, so results can be compared with the Atlas.
12. **Robustness: algorithm.** Compute Fitness-Complexity (fixed number of iterations, log fitness, report ranks) and GENEPY, and give Spearman correlations with ECI for DEU and the peers. This tests whether the conclusions depend on linear averaging vs. nested non-linear weighting.
13. **Robustness: thresholds.** RCA thresholds 0.75, 1.25 and 2, plus continuous RCA or the RCA-correlation proximity. These address the documented threshold sensitivity (Mealy et al.; Morrison et al.).
14. **Robustness: aggregation and smoothing.** HS4 vs. HS6, and smoothing windows of 1, 3 and 5 years. These separate signal from granularity and noise.
15. **Robustness: re-exports.** Re-run with NLD, BEL, SGP and HKG flagged or excluded, and with leave-one-peer-out runs. Entrepot re-exports inflate diversity, and ECI depends on the sample.
16. **Validation:** Check that the top-10 ECI ranking for recent years broadly matches the Atlas binary-era rankings (Germany near rank 5-6). This is a sanity check against a known benchmark, while remembering that the Atlas has used a continuous method since 2026.

## References

- Albeaik, S., Kaltenberg, M., Alsaleh, M., Hidalgo, C.A. (2017). Improving the Economic Complexity Index. arXiv:1707.05826. https://arxiv.org/abs/1707.05826 [title/URL V; authors U]
- Balland, P.-A., Broekel, T., Diodato, D., Giuliani, E., Hausmann, R., O'Clery, N., Rigby, D. (2022). The new paradigm of economic complexity. Research Policy 51(3), 104450. https://doi.org/10.1016/j.respol.2021.104450 [V]
- Bustos, S., Jackson, E., Torun, D., Leonard, B., Tuzcu, N., Lukaszuk, P., White, A., Hausmann, R., Yildirim, M.A. (2025). Tackling Discrepancies in Trade Data: The Harvard Growth Lab International Trade Datasets. Growth Lab WP 251. https://econpapers.repec.org/paper/glhwpfacu/251.htm [V]
- Gaulier, G., Zignago, S. (2010). BACI: International Trade Database at the Product-Level. The 1994-2007 Version. CEPII WP 2010-23. https://ideas.repec.org/p/cii/cepidt/2010-23.html [V]
- Growth Lab. Atlas Data Downloads and Rankings pages. https://atlas.hks.harvard.edu/data-downloads/ ; https://atlas.hks.harvard.edu/rankings/ [V via search snippets]
- Growth Lab. py-ecomplexity. https://github.com/cid-harvard/py-ecomplexity [V, code read]
- Hausmann, R., Hidalgo, C.A., Bustos, S., Coscia, M., Simoes, A., Yildirim, M.A. (2014). The Atlas of Economic Complexity: Mapping Paths to Prosperity. MIT Press. ISBN 978-0-262-52542-8. https://doi.org/10.7551/mitpress/9647.001.0001 [V; DOI is the DOAB record, edition match U]
- Hausmann, R., Stock, D.P., Yildirim, M.A. (2022). Implied comparative advantage. Research Policy 51(8), 104143. https://doi.org/10.1016/j.respol.2020.104143 [V]
- Hidalgo, C.A. (2021). Economic complexity theory and applications. Nature Reviews Physics 3, 92-113. https://doi.org/10.1038/s42254-020-00275-1 [V; DOI inferred from publisher URL]
- Hidalgo, C.A., Hausmann, R. (2009). The building blocks of economic complexity. PNAS 106(26), 10570-10575. https://doi.org/10.1073/pnas.0900943106 [V]
- Hidalgo, C.A., Klinger, B., Barabasi, A.-L., Hausmann, R. (2007). The product space conditions the development of nations. Science 317(5837), 482-487. https://doi.org/10.1126/science.1144581 [V]
- Kemp-Benedict, E. (2014). An interpretation and critique of the Method of Reflections. MPRA Paper 60705. https://mpra.ub.uni-muenchen.de/60705 [V]
- Mealy, P., Farmer, J.D., Teytelboym, A. (2019). Interpreting economic complexity. Science Advances 5(1), eaau1705. https://doi.org/10.1126/sciadv.aau1705 [V]
- Morrison, G., Buldyrev, S.V., Imbruno, M., Doria Arrieta, O.A., Rungi, A., Riccaboni, M., Pammolli, F. (2017). On economic complexity and the fitness of nations. Scientific Reports 7, 15332. https://doi.org/10.1038/s41598-017-14603-6 [V; article number U]
- OEC. Methods. https://oec.world/en/resources/methods [V via search snippet]
- Pugliese, E., Zaccaria, A., Pietronero, L. (2016). On the convergence of the Fitness-Complexity algorithm. European Physical Journal ST 225(10), 1893-1911. https://doi.org/10.1140/epjst/e2015-50118-1 [V]
- Sciarra, C., Chiarotti, G., Ridolfi, L., Laio, F. (2020). Reconciling contrasting views on economic complexity. Nature Communications 11, 3352. https://doi.org/10.1038/s41467-020-16992-1 [V]
- Tacchella, A., Cristelli, M., Caldarelli, G., Gabrielli, A., Pietronero, L. (2012). A new metrics for countries' fitness and products' complexity. Scientific Reports 2, 723. https://doi.org/10.1038/srep00723 [V]
