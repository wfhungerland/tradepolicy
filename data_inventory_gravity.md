# Data inventory for structural gravity scenario analysis

Scope: tariff scenarios (US-EU), EU integration and RTA effects, transport cost shocks. Compiled 2026-11-05.

**Verification status.** In this session, the hosts usitc.gov, wto.org and cepii.fr could not be fetched (DNS blocked by the sandbox). Following the session rules, no further hosts were tried. So **every fact below is marked [U]**: it comes from web search snippets, which often quote the official pages, and was not read directly on the official page. A fact gets "[U, official snippet]" when the snippet came from the provider's own domain, which makes it stronger. Before citing, re-check versions and licences on the official pages listed (see "Blocked domains" at the end).

Already held (not repeated): BACI HS92, CEPII Gravity V202211, MAcMap-HS6 2001-2019, TRADHIST, RICardo, Federico-Tena, UN voting, Comext, IMF IMTS.

---

## 1. Domestic (intranational) trade and production

**USITC ITPD-E (International Trade and Production Database for Estimation)**
- Content: bilateral international **and domestic** trade flows built from reported data only (no imputation), for agriculture, mining and energy, manufacturing and services [U, official snippet].
- Coverage: Release 2025 covers 1986-2023, 266 countries, 170 industries. Release 3 covers 1986-2022. Release 2 covered 1986/1988-2019, with services from 2000 [U, official snippet]. Frequency is annual.
- Latest version: Release 2025 (2023 data). Documentation is Borchert, Larch, Shikher and Yotov, USITC WP (lsy_itpd_e_r2025) [U, official snippet].
- Access: free CSV download at usitc.gov/data/gravity/itpde.htm and the gravity portal, no registration [U].
- Licence: public domain (US federal work, according to the data.gov catalog) [U].
- Literature: Borchert, Larch, Shikher and Yotov (2021), *International Economics*, introduces the database [U]. Larch and Yotov (2023), "Estimating the effects of trade agreements: Lessons from 60 years of methods and data", CESifo WP 10267 [U].
- Gap filled: domestic flows for GE-PPML, and sectoral production at the same time. **This is the core fix for the biggest gap.**

**USITC ITPD-S (for Simulation)**
- Content: a "squared", fully balanced version of ITPD-E with gaps filled, built for counterfactual simulations [U, official snippet].
- Coverage: Release 2025 has the same dimensions as ITPD-E R2025 (349 million observations). A 2017-19 subset is offered as a separate file [U, official snippet].
- Latest version: R2025. The first release was Dec 2024 [U].
- Access and licence: free download, public domain according to data.gov [U].
- Literature: Borchert, Larch, Shikher and Yotov (2024), USITC WP 2024-11-A [U].
- Gap filled: a ready baseline for the GE counterfactual when ITPD-E has holes (for example missing domestic flows).

**USITC Dynamic Gravity Dataset (DGD)**
- Content: more than 60 time-varying gravity covariates: geography, RTAs (agree_fta, agree_cu and others), sanctions, hostility, institutions, macro [U, official snippet].
- Coverage: 1948-2019, 286 countries, annual. Version 2.1 is from May 2021. CSV files cover 1948-1999 and 2000-2019, plus a file designed to merge with ITPD-E [U, official snippet].
- Access and licence: free, public domain [U].
- Literature: Gurevich and Herman (2018), USITC WP 2018-02-A [U].
- Gap filled: covariates that align with ITPD-E codes, with sanctions variables. It does **not** extend RTA coverage beyond 2019.

**WTO-UNCTAD Advanced Guide datasets / Structural Gravity Database**
- Content: replication data and Stata code for Yotov, Piermartini, Monteiro and Larch (2016/2017), *An Advanced Guide to Trade Policy Analysis: The Structural Gravity Model*. The data include international and domestic manufacturing flows [U].
- Coverage: a teaching dataset (about 69 countries, 1986-2006, at 4-year intervals), according to the Guide; from memory, not confirmed in this session [U].
- Access: WTO website (blocked here). Licence: WTO terms [U].
- Gap filled: a method benchmark and code template for GE-PPML (Anderson, Larch and Yotov 2018, *World Economy* 41(10), the GEPPML paper) [U]. It is not suitable for current scenarios.

**OECD ICIO / TiVA**
- Content: inter-country input-output tables (ISIC Rev.4, 45 industries in the 2023 edition) and value-added trade indicators [U].
- Coverage: the 2023 edition covers 76 countries plus rest of world, 1995-2020. The **2025 edition** was launched Nov 2025, reportedly covering 1995-2022; the exact country count is not confirmed [U].
- Access: free download from oecd.org (CSV), no registration [U]. Licence: OECD terms of use; open data since 2024 (CC BY 4.0) is from memory, so check it [U].
- Gap filled: domestic intermediate and final absorption by sector, which gives the input-output layer for multi-sector or value-added gravity (for example Hagemejer and Muck 2025 on EU enlargements and Brexit, value-added structural gravity) [U].

**WIOD 2016 Release**
- Content: world input-output tables, 43 countries plus RoW, 56 sectors, 2000-2014 [U, official snippet].
- Access: GGDC/RUG, DOI 10.34894/PJ2M1C. Licence: **CC BY 4.0** [U, official snippet].
- Gap filled: a classic, freely redistributable IO baseline. The data are dated (they end in 2014) and there is no update.

**Eora (Eora26 / full MRIO)**
- Content: MRIO for about 190 countries. Eora26 uses a harmonised 26-sector version [U].
- Licence: **free only for academic users at degree-granting institutions** (registration with a university e-mail), with attribution required. Others need a paid licence (KGM and Associates) [U]. The year range was not confirmed.
- Gap filled: wide country coverage, including developing economies. Quality varies, and most gravity papers prefer ITPD-E or ICIO.

---

## 2. Tariffs after 2019 and annual

**WITS / UNCTAD TRAINS**
- Content: MFN and preferential applied tariffs at HS6 (tariff line aggregated), including AVEs of specific duties [U, official snippet].
- Coverage: about 1988 onward, annual where reported. Gaps vary by country. The latest year depends on the reporter [U].
- Access: free, but **registration is required** to use the bulk download. There is a limit of 100,000 records per query, and a REST API is available [U, official snippet].
- Licence: World Bank WITS terms and conditions; redistribution limits apply to raw TRAINS data (check TermsAndConditions.aspx) [U].
- Caveat: when preferences are missing, WITS falls back to the MFN rate, which creates artificial spikes (Teti 2024) [U].

**WTO Tariff and Trade Data portal (ttd.wto.org; IDB plus Tariff Download Facility)**
- Content: IDB holds MFN applied duties, preferential duties where notified, and imports by partner, from 1996 onward. CTS holds bound rates [U, official snippet].
- Access: free download by year and economy (beta portal). The legacy TAO needs a login [U].
- Licence: WTO terms [U].
- Gap filled: the most current official MFN schedules (2023-2025 notifications), annual.

**Teti Global Tariff Database (GTD)**
- Content: bilateral statutory MFN and preferential tariffs, with gaps filled and preferences correctly assigned [U].
- Coverage: 1988-2021, 200 importers, HS6 (HS88/92), more than 6.7 billion observations. Version beta1-2024-12 [U].
- Access: only **aggregated** versions are public at feodorateti.github.io. HS6 microdata are not public (contact teti@ifo.de) [U].
- Literature: Teti (2024), "Missing Tariffs", CESifo WP 11590 / CEPR DP 19851 [U].
- Gap filled: annual bilateral tariffs, the best way to fill MAcMap's 3-year gaps up to 2021.

**MAcMap-HS6 (CEPII/ITC)**
- See the CEPII section. No public version after 2019 was found [U].

**Global Trade Alert (GTA)**
- Content: state interventions affecting trade (tariffs, subsidies, export controls) since Nov 2008, more than 85,000 entries. Includes premium "US Tariff Estimates" and NIPO data [U, official snippet].
- Access: browsing and some exports are free. API, bulk use and **redistribution need a paid licence** (layered General and Channel terms) [U, official snippet].
- Gap filled: timing of 2025 US tariff actions and NTM-type measures, in real time. It is licence-restricted.

---

## 3. Non-tariff measures

**UNCTAD TRAINS NTM**
- Content: regulatory NTMs (SPS, TBT, export measures and others) coded with the UNCTAD-MAST classification at HS6, collected from legal texts [U].
- Coverage: about 100 to 109 countries (figures differ by source and date); irregular snapshots, not annual [U].
- Access: free at trainsonline.unctad.org, WITS, and ITC MacMap [U]. Licence: UNCTAD terms [U].
- Literature: used for the GTAP 11 NTM-AVE satellite database. The AVE method follows Kee, Nicita and Olarreaga (2009, *Economic Journal*); that citation is from memory and was not confirmed in this session [U].
- Gap filled: an NTM incidence matrix for gravity controls or AVE scenarios.

**CEPII NTM-MAP and AVEs-Services**
- See the CEPII section (both are dated).

---

## 4. RTA depth, content and dates beyond 2021

**WTO RTA Database (RTA-IS)**
- Content: all notified RTAs with dates of signature, entry into force and notification, members, and type (FTA, CU, EIA) [U, official snippet].
- Coverage: about 383 RTAs notified and in force. The homepage was updated 1 Apr 2026. The WTO identified at least 84 RTAs in force but not notified (Oct 2026) [U, official snippet].
- Access: free Excel export at rtais.wto.org, no registration [U].
- Gap filled: dates after 2021 (for example EU-NZ, EU-Kenya), which are the raw input to update the RTA dummies.

**Mario Larch's Regional Trade Agreements Database (Egger and Larch 2008)**
- Content: a bilateral matrix of RTA dummies (FTA, CU, EIA, PSA, combined forms) based on WTO notifications, 280 countries [U, official snippet].
- Coverage: 1950-2023. Last update was 11 Jan 2026 [U, official snippet].
- Access: free download at ewf.uni-bayreuth.de/en/research/RTA-data [U]. Licence: academic use with citation [U].
- Literature: Egger and Larch (2008), *JIE* 76(2); used in Yotov et al. (2016) and Larch and Yotov (2023) [U].
- Gap filled: **directly extends your RTA dummies to 2023** in the format gravity specialists use.

**DESTA (Design of Trade Agreements)**
- Content: coding of PTA content (about 10 sectors of cooperation, more than 100 items) and depth indices (Duer, Baccini and Elsig 2014, *RIO* 9(3)) [U, official snippet].
- Latest version: 2.3, September 2025 [U, official snippet].
- Access: free download (CSV/Stata), no registration [U].
- Gap filled: depth and heterogeneity of agreements, and a consistent depth index.

**World Bank Deep Trade Agreements (DTA 1.0 and 2.0)**
- Content: DTA 1.0 is horizontal (52 policy areas). DTA 2.0 is vertical: provision-level content in 18 policy areas, nearly 1,000 provisions [U].
- Coverage: 400 PTAs signed 1958-2023 (latest), an Excel workbook [U].
- Access: free at datatopics.worldbank.org/dta and the WB Data Catalog. Licence: WB open data (CC BY 4.0 per catalogue convention; check it) [U].
- Literature: Mattoo, Mulabdic and Ruta (2022), *CJE* 55(3); Fontagne, Rocha, Ruta and Santoni (2023), *WBER* 37(3), GE assessment of deep agreements [U].
- Gap filled: **the main source for EU integration depth heterogeneity**.

---

## 5. Time-varying transport costs and chokepoints

**OECD ITIC (International Transport and Insurance Costs of Merchandise Trade)**
- Content: bilateral CIF/FOB margins by product (HS4), combining reported values with gravity-model predictions [U, official snippet].
- Coverage: the 2024 edition covers more than 200 countries and partners and more than 1,200 HS4 products, 1995-2022, annual [U, official snippet].
- Access: free on OECD Data Explorer [U]. Licence: OECD terms, open data since 2024 (check) [U].
- Gap filled: **the best panel of bilateral ad-valorem transport costs** to calibrate a transport-cost shock.

**OECD Maritime Transport Costs (MTC)**
- Content: bilateral maritime freight costs at HS6 for 43 importers [U].
- Coverage: 1991 onward. The end year (about 2016) is not confirmed [U].
- Literature: Korinek and Sourdin (2010), *AEPP* 32(3) [U].
- Gap filled: maritime-specific costs. It has been superseded by ITIC for recent years.

**ECLAC BTI (International Transport Database)**
- Content: Latin American trade by transport mode, with tonnage and values. Freight charges for some reporters [U].
- Gap filled: a regional niche only. Low priority for EU and US scenarios.

**CERDI-seadistance**
- Content: bilateral maritime distances for 227 countries along existing sea routes, with road legs to the port [U].
- Version: v1, March 2016 (Zenodo record 46822). Free [U].
- Literature: Bertoli, Goujon and Santoni (2016), CERDI Etudes et Documents 7 [U].
- Gap filled: a baseline for **counterfactual routing** (Suez closed means the route goes via the Cape; Panama restricted). You need to recompute routes yourself for the scenario.

**IMF PortWatch (with Oxford)**
- Content: daily transit calls and estimated trade volumes through about 24 to 28 chokepoints (Suez, Bab el-Mandeb, Panama, Hormuz, Cape of Good Hope), and port calls, based on UN Global Platform AIS data [U].
- Coverage: from 2019, daily, with a few days of lag [U].
- Access: free on portwatch.imf.org; an ArcGIS REST API returns 1,000 records per call [U].
- Licence: IMF special terms (a "imf-special-terms" label was seen in a third-party listing); attribution required, and redistribution needs checking [U].
- Gap filled: **timing and size of the Red Sea 2024 and Panama 2023-24 disruptions**, to calibrate shock intensity. Example uses: Bank of Israel (Etkes and Feldman) on Red Sea trade (-10% of Red Sea-routed trade); ECB/VoxEU column (CEPR) on muted trade effects [U].

**AIS-based academic route measures**
- Heiland, Moxnes, Ulltveit-Moe and Zi, "Trade from Space" (CEPR DP 14193): MarineTraffic AIS data, the 2016 Panama Canal expansion, +9 to 11% trade for exposed pairs, and +USD 20bn world real income [U]. The AIS data are **commercial** (MarineTraffic, now Kpler), but the paper is the template for a network-based transport-shock gravity design.

**NY Fed Global Supply Chain Pressure Index (GSCPI)**
- Content: a factor combining PMI supply components for 7 economies, Baltic Dry, Harpex and airfreight price indices, adjusted for demand [U].
- Coverage: monthly from 1997, revised [U].
- Access: free download (xlsx) at newyorkfed.org. Benigno, di Giovanni, Groen and Noble (2022), NY Fed Staff Report 1017 [U].
- Gap filled: an aggregate time-series shock indicator. It is not bilateral, so use it as an interaction or to scale shocks.

**Freight rate indices (licensing flag)**
- Freightos Baltic Index (FBX): weekly container spot rates on 12 lanes. Headline values are public; the time series and lane data need a **paid subscription** (Freightos Terminal or Baltic Exchange) [U].
- Baltic Dry Index, Harpex (Harper Petersen), Drewry WCI: headline values appear in press and in the GSCPI. Historical series are **proprietary and need a licence**. Redistribution is not allowed by default [U]; terms were not found in this session.
- Gap filled: lane-level time variation (Shanghai-Rotterdam during the Red Sea crisis). Use summary values only unless you have a licence.

**Kiel Trade Indicator (IfW Kiel)**
- Content: nowcasts of imports and exports for 75 countries and regions, the EU and the world, from container-ship AIS data (FleetMon/Kpler) and machine learning. Price-adjusted, month-on-month, seasonally adjusted [U].
- Frequency: updated about twice a month [U].
- Access: published results on ifw-kiel.de. The underlying ship data are **not** redistributable [U].
- Gap filled: early detection of shock effects. It is not a gravity input.

---

## 6. CEPII catalogue (systematic check)

cepii.fr was **blocked for fetching**. Everything below comes from search snippets, most of which quote cepii.fr pages directly ([U, official snippet]). CEPII databases are generally free, registration-free downloads under **Etalab 2.0** (an open licence that allows redistribution with attribution), unless stated otherwise.

**Gravity**
- No release newer than **V202211** was found. That version covers 1948-2021 in the files; the paper says 1948-2020. Earlier versions are kept only for reproducibility [U, official snippet].
- Documentation: Conte, Cotterlaz and Mayer (2022), CEPII WP 2022-05; the "Gravity_documentation.pdf" serves as the toolkit and codebook [U].
- Your RTA dummies end there, so use Larch's RTA database or RTA-IS for later years.

**BACI**
- The latest release is **V202601**, with release notes comparing it to V202501 [U, official snippet].
- HS92 runs 1995 to the latest year (the BACI page says 1995-2023 for the previous release; check whether V202601 adds 2024). The last year is often incomplete [U, official snippet].
- You hold data to 2024, so check for revisions.

**TradeProd**
- Content: international **and domestic** flows (production minus exports) plus tariffs, 9 manufacturing sectors, 165 countries, 1966-2020 [U, official snippet].
- Versions: the TPe version is for estimation (unsquared); the TPc version is complete, with domestic production extrapolated. Doc V202401 exists, and a newer **DocV202606** points to a June 2026 release [U, official snippet].
- Literature: Mayer, Santoni and Vicard (2023), CEPII WP 2023-01 [U].
- Gap filled: **domestic flows for manufacturing, consistent with BACI**. It is the alternative or complement to ITPD-E.

**TRADHIST**
- v4 (Nov 2016), 1827-2014, Fouquin and Hugot (2016), CEPII WP 2016-14. Already held [U, official snippet].

**MAcMap-HS6**
- The public version has tariffs only for 2001-2019, every 3 years [U, official snippet]. The JIE 2022 replication package has an HS6 rev.3 version (2001-2016) [U].
- ITC keeps property rights. Full versions and other years are "available on request for academic use", subject to an **ITC subscription** plus a CEPII request [U, official snippet].
- No 2022 public release was found.

**ProTEE (Product-level Trade Elasticities)**
- Content: HS6 trade elasticities for 152 importers, estimated from tariff variation in a CES structural gravity model (median about -6). Also aggregated to HS4, TiVA, GTAP-10 and WIOD [U, official snippet].
- Version 0.1, CSV, Etalab 2.0 [U, official snippet]. Literature: Fontagne, Guimbard and Orefice (2022), *JIE* 137 [U].
- Gap filled: **sector-specific sigma values to turn tariff scenarios into trade-cost changes** in GE-PPML.

**GeoDist (distances)**
- geo_cepii and dist_cepii: 225 countries, population-weighted distances including **internal distances**, contiguity, language, colonial links. Mayer and Zignago (2011), CEPII WP 2011-25, Etalab 2.0 [U, official snippet].
- It is time-invariant and is mostly superseded by Gravity.

**Language database**
- No standalone CEPII language database by Melitz and Toubal could be confirmed in this session. Language variables are in GeoDist and Gravity [U].

**CHELEM**
- Harmonised trade (since 1967), GDP and balance-of-payments accounts, about 200 countries [U].
- Access status is conflicting: CEPII states the data are now public (with a DBnomics mirror), while older sources describe a subscription (Bureau van Dijk) and Moody's resells it [U]. Check the licence before redistributing.

**Trade Unit Values (TUV)**
- A bilateral unit-value matrix, about 230 countries and 5,100 products (2000-2015 in the snippet; probably extended) [U].
- Gap filled: quality and price adjustments, and converting specific tariffs to AVEs.

**WTFC (World Trade Flows Characterization)**
- Content: BACI flows classified into one-way, horizontal and vertical two-way trade, with price ranges. HS96, April 2021 version [U, official snippet].
- Literature: Emlinger and Piton (2014), CEPII WP 2014-26 [U].
- Relevance: low for the scenarios; useful for quality-heterogeneity robustness checks.

**EconMap 3.1 (MaGE)**
- GDP and factor projections for 170 countries, 1980-2100, SSP scenarios. May 2022 version [U, official snippet].
- Gap filled: baseline GDP paths for dynamic or long-run counterfactuals.

**NTM-MAP**
- NTM incidence built from the UNCTAD database. Last update Nov 2015 [U, official snippet]. Outdated; use TRAINS NTM instead.

**AVEs-Services**
- Tariff equivalents of services trade barriers, 117 countries, 2011. Last update Dec 2016 [U, official snippet].
- Gap filled: the only CEPII services-barrier data, a single cross-section. Combine with ITPD-E services flows.

**Not found in the catalogue**
- There is no dedicated CEPII services-trade-flow database [U].

---

## 7. Recommended core set

**(a) US-EU tariff scenario, GE-PPML for Germany**
1. ITPD-E R2025 (plus ITPD-S): domestic and international flows by industry to 2023, so the GE system closes properly for DEU.
2. Teti GTD (aggregated) plus WTO IDB/TDF 2022-2025: annual baseline tariffs (Teti to 2021; IDB for the most recent MFN schedules).
3. MAcMap-HS6 (already held, request newer years): preferential AVEs consistent with CEPII data.
4. ProTEE: sector elasticities to map tariff shocks into trade costs.
5. Global Trade Alert (licensed) or US official tariff notices: dates and coverage of 2025 US tariff actions.
6. Larch RTA database or DGD: up-to-date RTA and sanctions controls in the estimation stage.

**(b) EU integration effects**
1. ITPD-E R2025: domestic flows identify border effects and RTA effects in line with theory (Yotov 2021, CESifo WP 9057).
2. CEPII TradeProd: a manufacturing robustness check with BACI-consistent domestic flows to 2020.
3. Larch RTA database (to 2023): RTA dummies by type (CU versus FTA versus EIA) for the EU, EEA and EU FTAs.
4. World Bank DTA 2.0: provision-level depth, the template from Mattoo, Mulabdic and Ruta (2022) and Fontagne et al. (2023).
5. DESTA 2.3: an alternative depth index as a robustness check.
6. OECD ICIO 2025: a value-added gravity extension and input-output linkages within the Single Market.

**(c) Transport-cost shock scenario (Red Sea, Panama)**
1. OECD ITIC 2024: bilateral CIF/FOB margins by HS4, 1995-2022, to calibrate transport-cost elasticities.
2. IMF PortWatch: daily chokepoint transits that date and scale the Red Sea and Panama shocks.
3. CERDI-seadistance (plus your own rerouting): pair-specific extra distance when Suez or Panama is closed.
4. ITPD-E R2025: GE baseline with domestic flows, so trade diverts to internal trade.
5. NY Fed GSCPI: an aggregate pressure series to validate shock timing.
6. FBX or Drewry WCI (licence required): lane-level freight rates if a licence is available; otherwise use summary values only.

---

## Blocked domains (allow these to verify facts)

DNS-blocked in this session:
- www.usitc.gov (also usitc.gov, gravity.usitc.gov)
- www.wto.org
- www.cepii.fr (also cepii.fr)

Not tried after the block, but needed to turn [U] into [V]:
- rtais.wto.org, ttd.wto.org
- wits.worldbank.org, datatopics.worldbank.org, datacatalog.worldbank.org
- www.oecd.org, data-explorer.oecd.org
- portwatch.imf.org
- www.newyorkfed.org
- www.ewf.uni-bayreuth.de
- www.designoftradeagreements.org
- feodorateti.github.io
- globaltradealert.org
- trainsonline.unctad.org, unctad.org
- www.rug.nl
- worldmrio.com, www.eora.org
- zenodo.org, ferdi.fr
- www.ifw-kiel.de
- www.freightos.com, www.balticexchange.com, www.drewry.co.uk
