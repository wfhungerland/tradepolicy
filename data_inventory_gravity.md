# Data inventory for structural gravity scenario analysis

Scope: tariff scenarios (US-EU), EU integration and RTA effects, transport cost shocks. Compiled 2026-11-05; checked against official pages on 2026-11-05.

**Verification status (2026-11-05).** Each fact tag now means one of the following:
- [V: url, accessed 2026-11-05]: read directly on the official page or official file.
- [V corrected: url, accessed 2026-11-05]: the official page contradicted the earlier text, which has been corrected.
- [S: url, search snippet only, accessed 2026-11-05]: supported only by a web search snippet that quotes the provider's own domain, because the host itself was blocked. Treat as stronger than [U] but not as verified.
- [U: reason]: could not be checked.

Counts: **84 verified [V]**, **30 corrected [V corrected]**, **5 snippet-supported only [S]**, **41 still unverified [U]** (160 tagged facts; the second pass on 2026-11-05 re-checked every [S] and [U] fact after more hosts were opened, and split some facts further). Counting [S] as unverified, 114 facts are verified or corrected and 46 remain unverified. The 5 remaining [S] facts all depend on www.oecd.org.

Hosts that still blocked checking on the second pass: www.oecd.org and oecd.org (HTTP 403 with every User-Agent tried), t4.oecd.org, search.oecd.org, ttd.wto.org (HTTP 403), datacatalogfiles.worldbank.org (HTTP 403), datacatalogapi.worldbank.org, per-file Dropbox content hosts (*.dl.dropboxusercontent.com; dl.dropboxusercontent.com itself works), api-trains2.unctad.org, www.cesifo.org, www.ifo.de, worldmrio.com, www.ifw-kiel.de, www.freightos.com, ferdi.fr. Now reachable and used: sdmx.oecd.org, www.newyorkfed.org, www.ewf.uni-bayreuth.de, dl.dropboxusercontent.com, globaltradealert.org, unctad.org, trainsonline.unctad.org, catalog.data.gov, services9.arcgis.com, www.designoftradeagreements.org, datacatalog.worldbank.org, datatopics.worldbank.org. Note: www.usitc.gov refuses requests sent with a browser User-Agent (Akamai 403) but works with the default curl User-Agent.

Already held (not repeated): BACI HS92, CEPII Gravity V202211, MAcMap-HS6 2001-2019, TRADHIST, RICardo, Federico-Tena, UN voting, Comext, IMF IMTS.

---

## 1. Domestic (intranational) trade and production

**USITC ITPD-E (International Trade and Production Database for Estimation)**
- Content: bilateral international **and domestic** trade flows at industry level built from reported administrative data only (no statistical estimation), for agriculture, mining and energy, manufacturing and services [V: https://www.usitc.gov/data/gravity/itpde.htm, accessed 2026-11-05].
- Coverage: Release 2025 covers 1986-2023 (agriculture 1986-2023; manufacturing, mining and energy 1988-2023; services 2000-2023), 266 countries, 170 industries, 87.5 million observations. Release 3 (June 2025) covers 1986-2022 with 264 countries. Release 2 (July 2022) covered 1986/1988-2019, services from 2000, 265 countries. Release 1 (May 2020) covered 2000-2016, 243 countries [V corrected: https://www.usitc.gov/data/gravity/itpde.htm, accessed 2026-11-05]. Frequency is annual.
- Latest version: Release 2025 (2023 data); releases are now named by year of internal availability. Documentation is **Larch, Shikher and Yotov (2026)**, "The International Trade and Production Database for Estimation - Release 2025 (ITPD-E-R2025)", USITC Working Paper 2026-08-A (file lsy_itpd_e_r2025.pdf); Borchert is not an author of the R2025 paper [V corrected: https://www.usitc.gov/data/gravity/gravity_portal_itpd_e_whats_new.htm and https://www.usitc.gov/data/gravity/itpde.htm, accessed 2026-11-05].
- Access: free zipped CSV, no registration. Direct link: https://www.usitc.gov/data/gravity/itpd_e/r2025/ITPD_E_R2025.zip (about 807 MB zipped, 8.7 GB unzipped; link answered HTTP 206 to a range request). Release 3: https://www.usitc.gov/data/gravity/itpd_e/r03/ITPDE_R03.zip. Smaller versions and concordances: https://www.usitc.gov/data/gravity/gravity_portal_itpd_e_additional_downloads.htm [V: https://www.usitc.gov/data/gravity/itpde.htm, accessed 2026-11-05].
- Licence: public domain (the data.gov record gives the usa.gov public domain label, http://www.usa.gov/publicdomain/label/1.0/, publisher USITC Office of Economics; note that the record's download URL still points to the Release 1 file itpd_e_r01.zip). The USITC page itself states no licence [V: https://catalog.data.gov/dataset/international-trade-and-production-database-for-estimation-itpd-e, accessed 2026-11-05].
- Literature: Borchert, Larch, Shikher and Yotov (2021), *International Economics* 166, 140-166, introduces the database and must be cited with the release paper [V: https://www.usitc.gov/data/gravity/itpde.htm, accessed 2026-11-05]. Larch and Yotov (2023), "Estimating the effects of trade agreements: Lessons from 60 years of methods and data", CESifo WP 10267 [U: only a third-party RePEc listing was seen].
- Gap filled: domestic flows for GE-PPML, and sectoral production at the same time. **This is the core fix for the biggest gap.**

**USITC ITPD-S (for Simulation)**
- Content: same detail as ITPD-E, but with **missing domestic trade observations filled in**, in theory-based steps, for simulation [V corrected: https://www.usitc.gov/data/gravity/itpds, accessed 2026-11-05].
- Coverage: Release 2025 is derived from ITPD-E R2025 and has the same coverage (1986-2023, 266 countries, 170 industries), 349,443,202 observations. R2025 subsets: 2021-23 only and 2023 only. The **2017-19 subset belongs to the older Release 1.1** (1986-2019, 265 countries), not to R2025 [V corrected: https://www.usitc.gov/data/gravity/itpds, accessed 2026-11-05].
- Latest version: R2025; the previous one is Release 1.1 (Release 1.0 omitted mining and energy) [V: https://www.usitc.gov/data/gravity/itpds, accessed 2026-11-05]. First release in Dec 2024 [U: date not stated on the official page].
- Access: free zipped CSV, no registration. https://www.usitc.gov/data/gravity/itpd_s/r2025/itpd_s_r2025.zip (1.26 GB, 35 GB unzipped), plus itpd_s_r2025_no_names.zip, itpd_s_r2025_2021_2023.zip and itpd_s_r2025_2023.zip in the same folder [V: https://www.usitc.gov/data/gravity/itpds, accessed 2026-11-05]. Licence: public domain; ITPD-S has its own data.gov record with the usa.gov public domain label (its distributions list the Release 1.1 files) [V: https://catalog.data.gov/dataset/international-trade-and-production-database-for-simulation-itpd-s, accessed 2026-11-05].
- Literature: Borchert, Larch, Shikher and Yotov (2024), "Globalization, Trade, and Inequality: Evidence from a New Database", USITC WP 2024-11-A [V: https://www.usitc.gov/data/gravity/itpds, accessed 2026-11-05].
- Gap filled: a ready baseline for the GE counterfactual when ITPD-E has holes (for example missing domestic flows).
- Related: the portal also offers ITPD-U (trade by end use: consumer, intermediate, final) [V: https://www.usitc.gov/data/gravity/index.htm, accessed 2026-11-05].

**USITC Dynamic Gravity Dataset (DGD)**
- Content: more than 60 variables: macro indicators, geography, trade agreements (FTA, EIA, CU, PSA; agree_fta_eia and agree_cu_eia added in v2), services agreements, IO membership, culture, political stability, hostility, economic sanctions; square dataset with within-country records [V: https://www.usitc.gov/data/gravity/dgd.htm, accessed 2026-11-05].
- Coverage: 1948-2019, 286 countries and territories, annual. Version 2.1 released May 2021. Files: 1948-1999, 2000-2016 (matches ITPD-E **R01**) and 2000-2019 (matches ITPD-E **R02**); there is no file aligned with R03 or R2025 [V corrected: https://www.usitc.gov/data/gravity/dgd.htm, accessed 2026-11-05]. Downloads: https://www.usitc.gov/data/gravity/dgd_docs/release_2.1_1948_1999.zip and https://www.usitc.gov/data/gravity/dgd_docs/release_2.1_2000_2019.zip.
- Access and licence: free, no registration [V: https://www.usitc.gov/data/gravity/dgd.htm, accessed 2026-11-05]; public domain [U: no licence stated on the page; no data.gov record for the DGD was found (catalog.data.gov is reachable, but guessed record names returned 404 and its search page is script-driven)].
- Literature: Gurevich and Herman (2018), "The Dynamic Gravity Dataset: 1948-2016", USITC WP 2018-02-A [V: https://www.usitc.gov/data/gravity/dgd.htm, accessed 2026-11-05].
- Gap filled: covariates that align with ITPD-E codes, with sanctions variables. It does **not** extend RTA coverage beyond 2019.

**WTO-UNCTAD Advanced Guide datasets / Structural Gravity Database**
- Content: application and exercise files (Stata) for Yotov, Piermartini, Monteiro and Larch (2016), *An Advanced Guide to Trade Policy Analysis: The Structural Gravity Model*, co-published by WTO and UNCTAD [V: https://www.wto.org/english/res_e/publications_e/advancedguide2016_e.htm, accessed 2026-11-05]. Separately, the WTO offers a **Structural Gravity Manufacturing Database** (Monteiro 2020) with international and domestic manufacturing trade for 186 partners, 1980-2016, Stata format: https://www.wto.org/english/res_e/reser_e/structural.gravity.manufacturing.database.Ver1.zip [V corrected: https://www.wto.org/english/res_e/reser_e/structural_gravity_e.htm and https://www.wto.org/english/res_e/reser_e/database_documentation_e.pdf, accessed 2026-11-05].
- Coverage: the Guide's teaching sample is a balanced panel of aggregate manufacturing for 69 countries, 1986-2006, used at 4-year intervals [V: https://www.wto.org/english/res_e/booksp_e/advancedwtounctad2016_e.pdf, accessed 2026-11-05].
- Access: free download, https://www.wto.org/english/res_e/reser_e/AdvancedGuideFiles.zip and https://www.wto.org/english/res_e/publications_e/advancedwtounctad2016_stata_e.zip [V: https://www.wto.org/english/res_e/publications_e/advancedguide2016_e.htm, accessed 2026-11-05]. Licence: WTO terms [U: no licence stated on the pages; only a research disclaimer].
- Gap filled: a method benchmark and code template for GE-PPML (Anderson, Larch and Yotov 2018, *World Economy* 41(10), the GEPPML paper) [U: citation not checked]. The Guide sample is not suitable for current scenarios; the 1980-2016 database is a longer manufacturing alternative.

**OECD ICIO / TiVA**
- Content: inter-country input-output tables (ISIC Rev.4, 45 industries in the 2023 edition) and value-added trade indicators [S: https://t4.oecd.org/sti/ind/inter-country-input-output-tables.htm, search snippet only (2023 edition page), accessed 2026-11-05].
- Coverage: the 2023 edition covers 76 countries plus rest of world, 1995-2020 [S: same snippet]. The **2025 edition** was launched in Nov 2025 [S: https://www.oecd.org/en/blogs/2025/11/oecd-inter-country-input-output-icio-tables-and-trade-in-value-added-tiva-database-launch-of-the-2025-edition.html, search snippet only, accessed 2026-11-05]. The TiVA 2025 edition, derived from the ICIO tables, covers **80 economies (plus regional aggregates), 50 economic activities (ISIC Rev.4) and 1995-2022** [V: https://sdmx.oecd.org/public/rest/dataflow/all (description of dataflow OECD.STI.PIE DSD_TIVA_MAINLV@DF_MAINLV 1.1), accessed 2026-11-05].
- Access: TiVA 2025 indicators are on OECD Data Explorer and the SDMX API (dataflows DSD_TIVA_MAINLV@DF_MAINLV, DSD_TIVA_MAINSH@DF_MAINSH, DSD_TIVA_EXGRVA@DF_EXGRVA, DSD_TIVA_FDVA@DF_FDVA, DSD_TIVA_IMGRVA@DF_IMGRVA, agency OECD.STI.PIE) [V: https://sdmx.oecd.org/public/rest/dataflow/all, accessed 2026-11-05]. The ICIO tables themselves are not an SDMX dataflow; free CSV download from oecd.org, no registration [U: www.oecd.org still returns HTTP 403 with every User-Agent tried]. Licence: OECD terms; CC BY 4.0 since 2024 is from memory [U: www.oecd.org blocked; the SDMX metadata carry no licence field].
- Gap filled: domestic intermediate and final absorption by sector, which gives the input-output layer for multi-sector or value-added gravity (for example Hagemejer and Muck 2025 on EU enlargements and Brexit, value-added structural gravity) [U: not checked].

**WIOD 2016 Release**
- Content: world input-output tables, 43 countries (28 EU plus 15 others) plus a RoW model, 56 sectors (ISIC Rev.4), 2000-2014; also SUTs and Socio Economic Accounts [V: https://www.rug.nl/ggdc/valuechain/wiod/wiod-2016-release, accessed 2026-11-05].
- Access: GGDC/RUG, DOI 10.34894/PJ2M1C (DataverseNL). Licence: **CC BY 4.0** [V: https://dataverse.nl/api/datasets/:persistentId?persistentId=doi:10.34894/PJ2M1C, accessed 2026-11-05].
- Gap filled: a classic, freely redistributable IO baseline. The data are dated (they end in 2014) and there is no update.

**Eora (Eora26 / full MRIO)**
- Content: MRIO for about 190 countries. Eora26 uses a harmonised 26-sector version [U: worldmrio.com blocked].
- Licence: **free only for academic users at degree-granting institutions** (registration with a university e-mail), with attribution required. Others need a paid licence (KGM and Associates) [U: worldmrio.com blocked]. The year range was not confirmed.
- Gap filled: wide country coverage, including developing economies. Quality varies, and most gravity papers prefer ITPD-E or ICIO.

---

## 2. Tariffs after 2019 and annual

**WITS / UNCTAD TRAINS**
- Content: HS-based applied tariffs: general (MFN) applied rates and preferential rates, including GSP and many regional and bilateral preferences, plus imports by origin [V: https://wits.worldbank.org/faqs.html, accessed 2026-11-05]. AVEs of specific duties [U: not stated on the pages read].
- Coverage: more than 1,000 country-years, more than 160 countries, years since 1988; the latest year depends on the reporter [V: https://wits.worldbank.org/faqs.html, accessed 2026-11-05].
- Access: TRAINS is free and unlimited, but **registration with WITS is required** (no charge). The **100,000-records-per-query limit applies to UN Comtrade data accessed via WITS, not to TRAINS** [V corrected: https://wits.worldbank.org/faqs.html, accessed 2026-11-05]. A REST API (SDMX and URL-based, XML or JSON) currently serves the TRAINS dataset; dataflow list: https://wits.worldbank.org/API/V1/SDMX/V21/rest/dataflow/wbg_wits/ (dataflow DF_WITS_Tariff_TRAINS, answered on 2026-11-05); user guide: http://wits.worldbank.org/data/public/WITSAPI_UserGuide.pdf [V: https://wits.worldbank.org/witsapiintro.aspx, accessed 2026-11-05].
- Licence: TRAINS is governed by UNCTAD TRAINS terms of use and dissemination policy (referenced in the WITS FAQ); TermsAndConditions.aspx returned an empty page. The general UNCTAD/UN website terms allow download and copying for personal, non-commercial use only, without any right to resell, redistribute or compile derivative works [V: https://unctad.org/terms, accessed 2026-11-05]. Whether a separate, more permissive TRAINS dissemination policy applies [U: no TRAINS-specific terms page found on unctad.org or trainsonline.unctad.org].
- Caveat: when preferences are missing, WITS falls back to the MFN rate, which creates artificial spikes (Teti 2024) [U: not checked in the paper].

**WTO Tariff and Trade Data portal (ttd.wto.org; IDB plus CTS and Analytical Database)**
- Content: IDB holds applied MFN tariffs at national tariff-line level and imports by origin and tariff line; non-reciprocal preferential tariffs are required notifications, RTA preferential tariffs are optional. CTS holds bound rates. The WTO Analytical Database combines IDB, CTS, RTA-database preferences, ITC, UN Comtrade and TDM data at HS subheading level; the platform covers over 150 economies [V corrected: https://www.wto.org/english/tratop_e/tariffs_e/idb_e.htm and https://www.wto.org/english/tratop_e/tariffs_e/tariff_data_e.htm, accessed 2026-11-05]. Coverage from 1996 onward [U: not stated on the pages read].
- Access: the platform has a six-digit download page, https://ttd.wto.org/en/download/six-digit (linked from the WTO page) [V: https://www.wto.org/english/tratop_e/tariffs_e/tariff_data_e.htm, accessed 2026-11-05]; whether it needs login [U: ttd.wto.org returned HTTP 403]. The legacy TAO needs a login [U: not checked].
- Licence: IDB/CTS use conditions: acknowledge WTO copyright, add a disclaimer to analyses, and get prior WTO Secretariat approval for any re-dissemination beyond publication of analytical work; restricted data not published below HS6 [V corrected: https://wits.worldbank.org/faqs.html (WTO IDB/CTS conditions reproduced there), accessed 2026-11-05].
- Gap filled: the most current official MFN schedules (2023-2025 notifications), annual. Members notify applied tariffs by 30 March each year [V: https://www.wto.org/english/tratop_e/tariffs_e/idb_e.htm, accessed 2026-11-05].

**Teti Global Tariff Database (GTD)**
- Content: bilateral statutory MFN and preferential tariffs; excludes safeguards, anti-dumping and US trade-war tariffs [V: https://feodorateti.github.io/data.html, accessed 2026-11-05].
- Coverage: 1988-2021 (34 years), 200 importers and their partners, HS6 (HS88/92), **more than 6.9 billion observations**. Version v_beta1-2024-12 (beta) [V corrected: https://feodorateti.github.io/data.html, accessed 2026-11-05].
- Access: only **aggregated** versions are public (pair-level, ag-nonAg, HS sections, ISIC 2-digit, GTAP; simple and trade-weighted averages; .dta and .csv in .7z) via Dropbox links on the data page, for example the pair-level file https://www.dropbox.com/scl/fi/wnsgnkkqz2ifb2vqiuyce/Pairs_vbeta1-2024-12.7z?rlkey=5m4ka7142bl9y1z0dndsaso36&st=b0tq7wr2&dl=1. HS6 microdata are restricted to a small beta test group: apply by e-mail (teti@ifo.de) with a project form; access not guaranteed [V corrected: https://feodorateti.github.io/data.html, accessed 2026-11-05].
- Files (all 7 Dropbox links on the data page answered HTTP 206 to a 1-byte range request when the host is changed to dl.dropboxusercontent.com; sizes from Content-Range): GTD v_beta1-2024-12 aggregates Pairs_vbeta1-2024-12.7z (28.6 MB), Ag-NonAg_vbeta1-2024-12.7z (50.0 MB), section_88_21_vbeta1-2024-12.7z (253.4 MB), isic33_vbeta1-2024-12.7z (350.8 MB, ISIC 2-digit), GTAP_vbeta1-2024-12.7z (417.5 MB); Trade War Extension v_2025-10: GTD-tradeWar_US-hts10.7z (40.3 MB) and GTD-tradeWar_hs6.7z (18.4 MB) [V: https://feodorateti.github.io/data.html and the linked Dropbox files, accessed 2026-11-05].
- Licence: the data page states **no licence**; it only asks users to cite "Feodora Teti's Global Tariff Database (v_beta1-2024-12) from Teti (2024)" (and Rodriguez-Clare et al. 2025 for the extension). Check redistribution with the author [V: https://feodorateti.github.io/data.html, accessed 2026-11-05].
- Literature: Teti (2024), "Missing Tariffs", CESifo WP 11590 [V: https://feodorateti.github.io/data.html, accessed 2026-11-05]; CEPR DP 19851 [U: not listed on the data page].
- New on the same page: **GTD U.S. Trade War Extension (v_2025-10)**: daily product-level US import tariffs and partners' tariffs on US exports, Jan 2018 to 15 Aug 2025, HTS10 (US) and HS6 bilateral (HS 2017); Rodriguez-Clare, Teti, Ulate, Vasquez and Zarate (2025), CESifo WP 12179 [V: https://feodorateti.github.io/data.html, accessed 2026-11-05].
- Gap filled: annual bilateral tariffs, the best way to fill MAcMap's 3-year gaps up to 2021; the extension covers the 2018-2025 US tariff actions.

**MAcMap-HS6 (CEPII/ITC)**
- See the CEPII section. No public version after 2019 was found [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=12, accessed 2026-11-05]. New: CEPII's **U.S. Import Tariffs 2025-2026** dataset (see CEPII section) is built on MAcMap-HS6 v2022.

**Global Trade Alert (GTA)**
- Content: trade and industrial policy interventions (tariffs, subsidies, export controls and others) since Nov 2008, more than 85,000 entries, updated daily. **Coverage is not global: 63 jurisdictions are monitored on a standing basis** (36 on a priority tier). Premium layers: Enhanced Data Fields (named firms, size of change, stated motive), NIPO data (New Industrial Policy Observatory) and US Tariff Estimates (file edition: US Applied Tariff Register) [V corrected: https://globaltradealert.org/data-access and https://globaltradealert.org/coverage, accessed 2026-11-05].
- Free: the website gives free public access to the full core intervention database (browsing and filtering, e-mail notifications, **self-serve exports from the Data Center**); website content is under **CC BY-NC 4.0** unless otherwise stated. The MCP channel has a free tier of 20 intervention records a month; aggregate statistics stay free [V: https://globaltradealert.org/data-access and https://globaltradealert.org/mcp/pricing, accessed 2026-11-05].
- Paid: the API, Dashboard, Data Files (Excel or CSV by SFTP or e-mail) and paid MCP plans (CHF 20 to 200 a month; team seats CHF 300 to 2,500 a year) are licensed; the Enhanced Data Fields are not on the website or MCP, and NIPO and US Tariff Estimates need Max or team MCP seats or a licensed channel. The General Terms (version 28 July 2026) define three licence classes: Internal Use (default), Derived Use and Redistribution; **Derived Use and Redistribution need an express grant**; an Academic Subscription is a limited non-commercial Derived Use (no sharing of raw data outside the team). Attribution format: "Source: Global Trade Alert, [Month Year]" [V: https://globaltradealert.org/terms and https://sgeptupload.s3.eu-west-1.amazonaws.com/terms/GTA+Licensed+Data+-+General+Terms.pdf, accessed 2026-11-05].
- Gap filled: timing of 2025 US tariff actions and NTM-type measures, in real time. The core records are free for non-commercial use; the US tariff estimates and bulk or programmatic access are licensed.

---

## 3. Non-tariff measures

**UNCTAD TRAINS NTM**
- Content: regulatory NTMs (SPS, TBT, export measures and others) coded with the UNCTAD classification developed since 2012, collected at national tariff-line level and aggregated to HS6 for comparison [V: https://wits.worldbank.org/Data/Public/NTM/NTM_metadata.html, accessed 2026-11-05].
- Coverage: the UNCTAD data-collection page states that **as of 2018 UNCTAD had collected comprehensive and comparable NTM data in 109 countries, with more than 65,000 measures**; it does not give the "about 150 economies" figure [V corrected: https://unctad.org/topic/trade-analysis/non-tariff-measures/NTMs-data-collection, accessed 2026-11-05]. A newer economy count and the year pattern (irregular snapshots, not annual) [U: the TRAINS portal's data-availability view runs on api-trains2.unctad.org, which this session cannot reach].
- Access: free via UNCTAD TRAINS and WITS (WITS has an NTM data download section) [V: https://wits.worldbank.org/witsapiintro.aspx (navigation), accessed 2026-11-05]. The TRAINS Portal (https://trainsonline.unctad.org) offers search downloads with a size limit for anonymous users, a higher limit after sign-in, larger downloads on request (trains.online@unctad.org), and a "Bulk Data Download" section for researchers in CSV and Stata format [V: https://trainsonline.unctad.org/ (application code main.2ab0187b17b438f5.js), accessed 2026-11-05]; ITC MacMap [U: not checked]. Licence: the UNCTAD website terms (personal, non-commercial use, no redistribution) apply unless TRAINS has its own policy [V: https://unctad.org/terms, accessed 2026-11-05].
- Literature: used for the GTAP 11 NTM-AVE satellite database. The AVE method follows Kee, Nicita and Olarreaga (2009, *Economic Journal*) [U: not checked].
- Gap filled: an NTM incidence matrix for gravity controls or AVE scenarios.

**CEPII NTM-MAP and AVEs-Services**
- See the CEPII section (both are dated).

---

## 4. RTA depth, content and dates beyond 2021

**WTO RTA Database (RTA-IS)**
- Content: all notified RTAs with dates of signature, notification and entry into force (separately for goods and services), inactive date, coverage, type (FTA, CU, EIA, PSA), status, current and original signatories, region [V: https://rtais.wto.org/UI/ExportAllRTAList.aspx (column headers of AllRTAs.xlsx), accessed 2026-11-05].
- Coverage: **390 RTAs notified and in force**; **84 RTAs in force not yet notified**; the homepage shows "Last updated on: Thursday, November 5, 2026" [V corrected: https://rtais.wto.org/UI/PublicMaintainRTAHome.aspx, accessed 2026-11-05].
- Access: free bulk Excel export, no registration: https://rtais.wto.org/UI/ExportAllRTAList.aspx returns AllRTAs.xlsx (662 rows including early announcements and inactive RTAs) [V: https://rtais.wto.org/UI/ExportAllRTAList.aspx, accessed 2026-11-05].
- Gap filled: dates after 2021, which are the raw input to update the RTA dummies. Examples: EU-New Zealand (signed 9 Jul 2023, in force 1 May 2024), EU-Kenya (signed 18 Dec 2023, in force 1 Jul 2024) [V: https://rtais.wto.org/UI/ExportAllRTAList.aspx, accessed 2026-11-05].

**Mario Larch's Regional Trade Agreements Database (Egger and Larch 2008)**
- Content: a bilateral panel of RTA dummies based on WTO notifications (RTA Gateway), with dummies rta, cu, fta, psa, eia, cueia, ftaeia, psaeia; **605 agreements** (active and inactive) in seven categories, plus founding, joining and leaving indicators; 280 countries (5,958,400 pair-year observations) [V: https://www.ewf.uni-bayreuth.de/pool/dokumente/readme_RTA3.pdf, accessed 2026-11-05]. An "essential" file (rta_20260111) with type dummies and a "complete" file (rta_individual_agreements_20260111) with three dummies per agreement, each in Stata .dta and CSV [V: https://www.ewf.uni-bayreuth.de/en/research/daten/01rta-data/index.html, accessed 2026-11-05].
- Coverage: **1950-2025 (76 years); last updated 11 January 2026** ("concerning RTAs and corrections"). The earlier snippet figure of 1950-2022 is outdated [V corrected: https://www.ewf.uni-bayreuth.de/pool/dokumente/readme_RTA3.pdf and https://www.ewf.uni-bayreuth.de/en/research/daten/01rta-data/index.html, accessed 2026-11-05].
- Access: free download, no registration, from the **new page URL https://www.ewf.uni-bayreuth.de/en/research/daten/01rta-data/index.html** (the old .../en/research/RTA-data/index.html returns 404). Files: https://www.ewf.uni-bayreuth.de/pool/dokumente/rta_20260111_csv.zip (16.8 MB), rta_20260111_dta.zip (10.3 MB), rta_individual_agreements_20260111_csv.zip (69.9 MB), rta_individual_agreements_20260111_dta.zip (47.5 MB), all in the same /pool/dokumente/ folder (HTTP 200 to HEAD, last modified 20 Jan 2026) [V corrected: https://www.ewf.uni-bayreuth.de/en/research/daten/01rta-data/index.html, accessed 2026-11-05]. Licence: **no licence is stated**; the page and readme only ask users to cite "Mario Larch's Regional Trade Agreements Database from Egger and Larch (2008)" [V: https://www.ewf.uni-bayreuth.de/en/research/daten/01rta-data/index.html, accessed 2026-11-05].
- Literature: Egger and Larch (2008), "Interdependent Preferential Trade Agreement Memberships: An Empirical Analysis", *JIE* 76(2), 384-399; Yotov et al. (2016) is in the list of papers using the database [V: https://www.ewf.uni-bayreuth.de/pool/dokumente/readme_RTA3.pdf, accessed 2026-11-05]. Use in Larch and Yotov (2023) [U: not in the readme list; paper not checked].
- Gap filled: **extends your RTA dummies to 2025** in the format gravity specialists use.

**DESTA (Design of Trade Agreements)**
- Content: hand-coded design features of PTAs (customs unions, FTAs, partial agreements), from market access commitments, flexibility instruments and enforcement tools to non-trade issues; more than 710 agreements coded (as of October 2020), period 1948-2019 in the project description; cite Duer, Baccini and Elsig (2014), *RIO* 9(3), 353-375 [V: https://www.designoftradeagreements.org/project-description/, accessed 2026-11-05]. Depth, flexibility and dispute-settlement indices are separate files [V: https://www.designoftradeagreements.org/downloads/, accessed 2026-11-05]. The "about 10 sectors, more than 100 items" structure [U: not stated on the pages read; codebook not opened].
- Latest version: 2.3, current version September 2025 (treaty list, withdrawals, content coding and indices); the citation block of the indices section still says version 2.2 (2023) [V: https://www.designoftradeagreements.org/downloads/, accessed 2026-11-05].
- Access: free download as **CSV and XLSX** (not Stata) with codebook and explanatory notes; archive of 2.2, 2.1, 2.0, 1.6; R package for 2.1 [V: https://www.designoftradeagreements.org/downloads/, accessed 2026-11-05]. **No registration**: direct file links, e.g. https://www.designoftradeagreements.org/media/filer_public/53/af/53af422c-29b0-48f9-bf1c-3537f5c028d4/desta_version_02_03.csv (HTTP 200, 716 KB, last modified 23 Sep 2025) and https://www.designoftradeagreements.org/media/filer_public/0c/64/0c64ec71-5728-409f-91d8-64c324bf4400/desta_indices_version_02_03.csv [V: https://www.designoftradeagreements.org/downloads/, accessed 2026-11-05]. Licence: none stated on the downloads page [V: https://www.designoftradeagreements.org/downloads/, accessed 2026-11-05].
- Gap filled: depth and heterogeneity of agreements, and a consistent depth index.

**World Bank Deep Trade Agreements (DTA 1.0 and 2.0)**
- Content: the vertical dataset ("2.0") codes provision-level content of the **18 policy areas** most frequently covered in PTAs, from the Handbook of Deep Trade Agreements [V: https://datatopics.worldbank.org/dta/index.html, accessed 2026-11-05]. The catalogue entry holds one Excel file per chapter (Ch. 3 Export Restrictions to Ch. 19 Labor Market Regulations, with Ch. 11 split into anti-dumping and countervailing duties), a combined "DTA 2.0 - Vertical Content" file and a "DTA 1.0 - Horizontal Content" file (10.6 MB) [V: https://datacatalog.worldbank.org/search/dataset/0065624/content-of-deep-trade-agreements-version-2, accessed 2026-11-05]. That the horizontal file maps 52 policy areas and the vertical data hold nearly 1,000 provisions [U: not stated on the pages read].
- Coverage: **Version 2 (the current version) covers 400 agreements currently in force and notified to the WTO between 1958 and 2022** (temporal coverage field: 1957-2022; metadata last updated 1 Feb 2024; files dated 31 Jan 2024). The 400 figure describes the whole V2 update, which revises the V1 mapping; it is not limited to the horizontal file, and the end year is 2022, not 2023 [V corrected: https://datacatalog.worldbank.org/search/dataset/0065624/content-of-deep-trade-agreements-version-2, accessed 2026-11-05]. Version 1 covered 381 PTAs [U: version 1 record not opened].
- Access: free at datatopics.worldbank.org/dta (dashboard) and the WB Data Catalog (Excel files, each with an "API Service" option); licence **CC BY 4.0**, classification Public [V: https://datacatalog.worldbank.org/search/dataset/0065624/content-of-deep-trade-agreements-version-2, accessed 2026-11-05]. The file host datacatalogfiles.worldbank.org refused this session (HTTP 403), so the files themselves were not tested.
- Literature: Mattoo, Mulabdic and Ruta (2022), *CJE* 55(3); Fontagne, Rocha, Ruta and Santoni (2023), *WBER* 37(3), GE assessment of deep agreements [U: not checked].
- Gap filled: **the main source for EU integration depth heterogeneity**.

---

## 5. Time-varying transport costs and chokepoints

**OECD ITIC (International Transport and Insurance Costs of Merchandise Trade)**
- Content: bilateral CIF/FOB margins, (CIF-FOB)/CIF in percent of the CIF import value, by product (HS 2017 at 4 digits); reference area is the importer, counterpart the exporter. Built in four steps: a gravity model estimated on reported HS6 margins (34 reporting countries), model estimates for non-reporters, statistical imputation for the rest, and calibration to reported data; each observation carries a methodology code [V: https://sdmx.oecd.org/public/rest/dataflow/all (description of dataflow OECD.SDD.TPS DSD_ITIC@DF_ITIC 1.1), accessed 2026-11-05].
- Coverage: **more than 200 reporters and 240 partners, over 1,200 HS4 products, 1995-2024**, annual (the availability constraint returns 1995-01-01 to 2024-12-31); the end year 2022 in the earlier text is outdated [V corrected: https://sdmx.oecd.org/sti-public/rest/availableconstraint/OECD.SDD.TPS,DSD_ITIC@DF_ITIC,1.1/all/all/TIME_PERIOD, accessed 2026-11-05]. Method paper named in the metadata: "Recent trends in transport and insurance costs and estimates at disaggregated product level" [V: same dataflow description]; that it is OECD Statistics WP 2024/05 of 28 June 2024 [S: https://www.oecd.org/en/publications/cif-fob-margins_469123ab-en.html, search snippet only, accessed 2026-11-05].
- Access: free on OECD Data Explorer [S: https://oecd.org/en/data/datasets/international-transport-and-insurance-costs-of-merchandise-trade-itic.html, search snippet only, accessed 2026-11-05]. **SDMX API works** (no key): data are served from the sti-public route and need a full seven-part key REF_AREA.COUNTERPART_AREA.MEASURE.PRODUCT_TYPE.COMM_HS2017.FREQ.UNIT_MEASURE, e.g. https://sdmx.oecd.org/sti-public/rest/data/OECD.SDD.TPS,DSD_ITIC@DF_ITIC,1.1/DEU.USA.C_F.C._T.A.PT_IM_CIF?startPeriod=2020&format=csvfilewithlabels (HTTP 200; DEU imports from USA, 2022 margin 6.31%). The /public/rest/data route answered HTTP 500 and keys with empty positions were rejected [V: https://sdmx.oecd.org/sti-public/rest/data/OECD.SDD.TPS,DSD_ITIC@DF_ITIC,1.1/DEU.USA.C_F.C._T.A.PT_IM_CIF, accessed 2026-11-05]. Licence: OECD terms, open data since 2024 [U: www.oecd.org still HTTP 403; no licence in the SDMX metadata].
- Gap filled: **the best panel of bilateral ad-valorem transport costs** to calibrate a transport-cost shock.

**OECD Maritime Transport Costs (MTC)**
- Content: bilateral maritime freight costs at HS6 for 43 importers [U: www.oecd.org blocked; MTC is not among the dataflows of the OECD SDMX catalogue, so it may no longer be on Data Explorer].
- Coverage: 1991 onward. The end year (about 2016) is not confirmed [U: www.oecd.org blocked].
- Literature: Korinek and Sourdin (2010), *AEPP* 32(3) [U: not checked].
- Gap filled: maritime-specific costs. It has been superseded by ITIC for recent years.

**ECLAC BTI (International Transport Database)**
- Content: Latin American trade by transport mode, with tonnage and values. Freight charges for some reporters [U: not checked, low priority].
- Gap filled: a regional niche only. Low priority for EU and US scenarios.

**CERDI-seadistance**
- Content: bilateral maritime distances between countries along sea routes, with road legs to the port, for 227 countries [U: country count not on the Zenodo record].
- Version: v1 (2 March 2016, Zenodo record 46822) was **updated by V1.1 (12 Jan 2017, Zenodo record 240493)**, which changes the projection choice and the Russian port for Armenia and Azerbaijan. Licence **CC BY 4.0**. Downloads: https://zenodo.org/api/records/240493/files/CERDI-seadistance_V1.1.dta/content (also .xlsx, readme.txt, used_ports.zip) [V corrected: https://zenodo.org/records/240493, accessed 2026-11-05].
- Literature: Bertoli, Goujon and Santoni (2016), "The CERDI-seadistance database", CERDI Working Paper 2016/07 [V: https://zenodo.org/records/46822, accessed 2026-11-05].
- Gap filled: a baseline for **counterfactual routing** (Suez closed means the route goes via the Cape; Panama restricted). You need to recompute routes yourself for the scenario.

**IMF PortWatch (with Oxford)**
- Content: daily transit calls and estimated transit trade volumes (metric tons) for **28 chokepoints**, by 5 ship categories (container, dry bulk, general cargo, ro-ro, tanker); daily port calls and import/export estimates; a chokepoints and a ports database; disruption and spillover-simulator layers. Based on AIS signals; method in Arslanalp, Koepke and Verschuur (2021), IMF WP 2021/225 [V corrected: https://portwatch.imf.org/api/search/v1/collections/dataset/items, accessed 2026-11-05]. Raw AIS data come from the **UN Global Platform** (satellite AIS supplied by Spire; archive from 1 Dec 2018); recommended citation "Sources: UN Global Platform; IMF PortWatch (portwatch.imf.org)" [V: https://portwatch.imf.org/api/search/v1/collections/dataset/items?limit=100, accessed 2026-11-05].
- Coverage: AIS-based estimates from 2019 (chokepoint vessel averages use 2019-2024) [V: https://portwatch.imf.org/api/search/v1/collections/dataset/items, accessed 2026-11-05]; daily. On 2026-11-05 the latest date was **2026-10-25 for chokepoints and 2026-10-30 for ports**, so the lag is about one to two weeks [V: https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query (min/max statistics on date), accessed 2026-11-05].
- Access: free on portwatch.imf.org. Data sit in ArcGIS FeatureServer layers, e.g. Daily_Chokepoints_Data (item 3da2b9ca97684916b75c4013f95d18ab): https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query?where=1%3D1&outFields=*&f=json, and Daily_Ports_Data (item 83b1bbc7b3354c5fb1f40673bb8f852e) [V: https://portwatch.imf.org/api/search/v1/collections/dataset/items, accessed 2026-11-05]. The hub CSV route (portwatch.imf.org/api/download/v1/items/...) answers "Downloads are not supported for this item", so the ArcGIS REST query endpoints are the bulk route. Daily_Chokepoints_Data held 79,940 records (2019-01-01 to 2026-10-25), Daily_Ports_Data 5,905,900 records (2019-01-01 to 2026-10-30, fields: port calls, imports and exports by the 5 ship types), and PortWatch_chokepoints_database 28 records; the layer maxRecordCount is **1,000 records per call**, so page with resultOffset and resultRecordCount [V: https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Ports_Data/FeatureServer/0?f=json and the query endpoints, accessed 2026-11-05]. The Daily_Chokepoints_Data service metadata URL (.../FeatureServer?f=json) intermittently answered "Invalid URL" while its /0/query endpoint worked.
- Licence: the datasets point to the **IMF Copyright and Usage terms (https://www.imf.org/external/terms.htm)**, not a separate "special terms" label; attribution required, redistribution to be checked in those terms [V corrected: https://portwatch.imf.org/api/search/v1/collections/dataset/items, accessed 2026-11-05].
- Gap filled: **timing and size of the Red Sea 2024 and Panama 2023-24 disruptions**, to calibrate shock intensity. Example uses: Bank of Israel (Etkes and Feldman) on Red Sea trade (-10% of Red Sea-routed trade); ECB/VoxEU column (CEPR) on muted trade effects [U: not checked].

**AIS-based academic route measures**
- Heiland, Moxnes, Ulltveit-Moe and Zi, "Trade from Space" (CEPR DP 14193): MarineTraffic AIS data, the 2016 Panama Canal expansion, +9 to 11% trade for exposed pairs, and +USD 20bn world real income [U: not checked]. The AIS data are **commercial** (MarineTraffic, now Kpler), but the paper is the template for a network-based transport-shock gravity design.

**NY Fed Global Supply Chain Pressure Index (GSCPI)**
- Content: principal-component factor combining PMI supply components (delivery times, backlogs, purchased stocks) for 7 economies (euro area, China, Japan, South Korea, Taiwan, UK, US), Baltic Dry, Harpex and BLS airfreight price indices, after filtering out demand effects (regressions on PMI new orders and quantities purchased); US PMI data start only in 2007 and are combined with ISM data; readings are in standard deviations from the index's historical average [V: https://www.newyorkfed.org/research/policy/gscpi (page content served from https://www.newyorkfed.org/medialibrary/research/interactives/data/gscpi/gscpi.json), accessed 2026-11-05].
- Coverage: monthly from **September 1997** (first observation 30-Sep-1997), revisable up to a year back; updated at or shortly after 10:00 a.m. on the fourth business day of each month; latest reading October 2026 = 1.26. Note: since 6 Nov 2025 the index "is being published with limited data" because necessary source data were suspended [V: https://www.newyorkfed.org/research/policy/gscpi and https://www.newyorkfed.org/medialibrary/research/interactives/data/gscpi/gscpi_interactive_data.csv, accessed 2026-11-05].
- Access: free xlsx at https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx (HTTP 200 to HEAD, 252 KB; URL taken from the page's application code); the interactive also uses a CSV of all vintages (one column per release) at https://www.newyorkfed.org/medialibrary/research/interactives/data/gscpi/gscpi_interactive_data.csv [V: https://www.newyorkfed.org/research/policy/gscpi, accessed 2026-11-05]. Benigno, di Giovanni, Groen and Noble (2022), "The GSCPI: A New Barometer of Global Supply Chain Pressures", NY Fed Staff Report 1017, May 2022 [V: https://www.newyorkfed.org/research/staff_reports/sr1017, accessed 2026-11-05].
- Gap filled: an aggregate time-series shock indicator. It is not bilateral, so use it as an interaction or to scale shocks.

**Freight rate indices (licensing flag)**
- Freightos Baltic Index (FBX): weekly container spot rates on 12 lanes. Headline values are public; the time series and lane data need a **paid subscription** (Freightos Terminal or Baltic Exchange) [U: www.freightos.com blocked].
- Baltic Dry Index, Harpex (Harper Petersen), Drewry WCI: headline values appear in press and in the GSCPI. Historical series are **proprietary and need a licence**. Redistribution is not allowed by default [U: providers' terms not checked].
- Gap filled: lane-level time variation (Shanghai-Rotterdam during the Red Sea crisis). Use summary values only unless you have a licence.

**Kiel Trade Indicator (IfW Kiel)**
- Content: nowcasts of imports and exports for 75 countries and regions, the EU and the world, from container-ship AIS data (FleetMon/Kpler) and machine learning. Price-adjusted, month-on-month, seasonally adjusted [U: www.ifw-kiel.de blocked].
- Frequency: updated about twice a month [U: www.ifw-kiel.de blocked].
- Access: published results on ifw-kiel.de. The underlying ship data are **not** redistributable [U: www.ifw-kiel.de blocked].
- Gap filled: early detection of shock effects. It is not a gravity input.

---

## 6. CEPII catalogue (systematic check)

All items below were read on cepii.fr (database pages at https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=N). CEPII databases are free, registration-free downloads, mostly under **Etalab 2.0** (open licence, redistribution with attribution). **Exceptions: MAcMap-HS6 is CC BY-NC-SA; U.S. Import Tariffs 2025-2026 is CC BY-NC 4.0; CHELEM states no licence** [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele.asp and item pages, accessed 2026-11-05].

**Gravity**
- No release newer than **V202211** exists; the page says "This is the 202211 version" and describes coverage as 1948 to 2020; versions 202202, 202102, 202010 and 2015 are kept only for reproducibility [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=8, accessed 2026-11-05]. That the files run to 2021 [U: files not opened].
- Documentation: Conte, Cotterlaz and Mayer (2022), "The CEPII Gravity database", CEPII WP 2022-05, July 2022; Gravity_documentation.pdf. Downloads: https://www.cepii.fr/DATA_DOWNLOAD/gravity/data/Gravity_csv_V202211.zip (also _dta_ and _rds_), https://www.cepii.fr/DATA_DOWNLOAD/gravity/doc/Gravity_documentation.pdf [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=8, accessed 2026-11-05].
- Your RTA dummies end there, so use Larch's RTA database or RTA-IS for later years.

**BACI**
- The latest release is **V202601** (last update 30 Jan 2026), with release notes https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/release_notes_202601.pdf [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37, accessed 2026-11-05].
- **HS92 in V202601 runs 1995-2024** (HS96 1996-2024, HS02 2002-2024; also HS07, HS12, HS17, HS22); 200 countries, about 5,000 products. Download: https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS92_V202601.zip [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37, accessed 2026-11-05]. That the last year is often incomplete [U: not stated on the page].
- You hold data to 2024, so check for revisions.

**TradeProd**
- Content: international **and domestic** flows plus trade protection, **9 industrial sectors, 168 countries, 1966-2022** [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=5, accessed 2026-11-05].
- Versions: **V202606 is released** (last update July 2026), with DocV202606.pdf; files TPe (for estimation) and TPc (complete, balanced, for counterfactuals): https://www.cepii.fr/DATA_DOWNLOAD/tradeprod/V202606/TPe_V202606_csv.zip and https://www.cepii.fr/DATA_DOWNLOAD/tradeprod/V202606/TPc_V202606_csv.zip, plus Gravity country keys; V202401 and V202201 remain online [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=5, accessed 2026-11-05].
- Literature: Mayer, Santoni and Vicard (2023), CEPII WP 2023-01 [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=5, accessed 2026-11-05].
- Gap filled: **domestic flows for manufacturing, consistent with BACI**. It is the alternative or complement to ITPD-E.

**TRADHIST**
- v4 (Nov 2016), 1827-2014, Fouquin and Hugot (2016), CEPII WP 2016-14, Etalab 2.0. Already held [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=32, accessed 2026-11-05].

**MAcMap-HS6**
- Public data: the JIE 2022 replication package (Fontagne, Guimbard and Orefice) has an HS6 version (revision 2007) for 152 importers and 189 exporters, 2001-2016 every 3 years; year 2019 is available in a version that contains tariffs only, 2001-2019 every 3 years (Dropbox link on the page: https://www.dropbox.com/scl/fi/rfow5essm4b5kt30o0gdx/Tariffs_2001_2019.zip?rlkey=yd3d66fegws2yv58ng0kmlryl&dl=0; the file answered HTTP 206 via dl.dropboxusercontent.com and is 2.7 GB); aggregated HS2/GTAP files for 2001, 2004, 2007. Licence **CC BY-NC-SA** [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=12, accessed 2026-11-05].
- Other versions are "available on request for academic use" (macmaphs6@cepii.fr). **The page does not mention an ITC subscription or ITC property rights**; it says ITC collects and processes tariff-line data, and the tariff-line MAcMap is managed by ITC at macmap.org [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=12, accessed 2026-11-05].
- No 2022 public release was found [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=12, accessed 2026-11-05]; CEPII does use MAcMap-HS6 v2022 internally as the baseline of the US tariff dataset below.

**U.S. Import Tariffs 2025-2026 (new, not in the earlier inventory)**
- Content: AVE of applied US import tariffs at HS6 (HS 2022) by exporter and entry-into-force date, from 1 Jan 2025 (MAcMap-HS6 2022 baseline plus pre-existing Section 301) through Section 232, IEEPA, Section 122, 301, 338 measures and framework deals (UK, EU, Japan, Korea, Switzerland); only measures in force at generation date. Guimbard (2026), CEPII WP 2026-07. Licence CC BY-NC 4.0. Download (CSV and Parquet): https://www.cepii.fr/DATA_DOWNLOAD/usa_tariffs/usa_tariffs_20260907.zip (the page text names usa_tariffs_20260822, the link points to 20260907) [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=44, accessed 2026-11-05].
- Gap filled: **the US side of a US-EU tariff scenario**, consistent with MAcMap and BACI.

**ProTEE (Product-level Trade Elasticities)**
- Content: HS6 (rev. 2007) trade elasticities for 152 importers, estimated from tariff variation in a structural gravity model (2001-2016 data, every 3 years); non-significant or positive HS6 values replaced by HS4 averages and flagged. The project page also gives elasticities by HS4, TiVA, GTAP-10, WIOD, ICIO sectors and the distance elasticity of transport costs [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=35, accessed 2026-11-05]. The median is **about -7.9, not -6**: in ProTEE_0_1.csv the column sigma has values for 4,566 of 5,050 HS6 codes, median -7.89, mean -10.93 (computed from the 111 KB file) [V corrected: https://www.cepii.fr/DATA_DOWNLOAD/ProTEE/ProTEE_0_1.csv, accessed 2026-11-05].
- Version 0.1, CSV (https://www.cepii.fr/DATA_DOWNLOAD/ProTEE/ProTEE_0_1.csv), Etalab 2.0. Literature: Fontagne, Guimbard and Orefice (2022), *JIE* 137 [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=35, accessed 2026-11-05].
- Gap filled: **sector-specific sigma values to turn tariff scenarios into trade-cost changes** in GE-PPML.

**GeoDist (distances)**
- geo_cepii and dist_cepii: 225 countries, city-level population-weighted distances including **intra-national distances**, languages, landlocked status, colonial links. Mayer and Zignago (2011), CEPII WP 2011-25, Etalab 2.0. Listed under "Legacy" [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=6, accessed 2026-11-05].
- It is time-invariant and is mostly superseded by Gravity.

**Language database**
- **A standalone CEPII Language database exists**: Melitz and Toubal (2014), *JIE* 92(2), 351-363; common official, spoken and native language plus linguistic proximity, 195 countries; last update Nov 2012; Etalab 2.0; https://www.cepii.fr/DATA_DOWNLOAD/language/ling_web.dta [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=19, accessed 2026-11-05].

**CHELEM**
- **CHELEM-TRADE covers bilateral trade since 2000** (71 CHELEM, 43 GTAP or 147 ISIC categories); CHELEM-GDP covers about 200 countries since 1960; CHELEM-BOP about 200 countries since 1967; 95 elementary zones [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=17, accessed 2026-11-05].
- Access: the February 2025 version (and July 2022 CSVs) are free downloads on cepii.fr, also on DBnomics; the page states no licence [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=17, accessed 2026-11-05]. Check the licence before redistributing.

**Trade Unit Values (TUV)**
- Bilateral unit values (USD/ton) at HS6, CIF (importer) and FOB (exporter) files for HS96, HS02, HS07, HS12; April 2021 version (V202104), Etalab 2.0 [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=2, accessed 2026-11-05]. About 230 countries, 5,100 products, years [U: not stated on the page].
- Gap filled: quality and price adjustments, and converting specific tariffs to AVEs.

**WTFC (World Trade Flows Characterization)**
- Content: reconciled unit values per flow, trade type (one-way, two-way similar, two-way differentiated) and price range; HS96, April 2021 version (V202104), Etalab 2.0; https://www.cepii.fr/DATA_DOWNLOAD/WTFC/data/WTFC_HS96_V202104.zip [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=29, accessed 2026-11-05].
- Literature: Emlinger and Piton (2014), CEPII WP 2014-26 [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=29, accessed 2026-11-05].
- Relevance: low for the scenarios; useful for quality-heterogeneity robustness checks.

**EconMap 3.1 (MaGE)**
- GDP and factor projections for 170 countries, 1980-2100, central plus five SSP scenarios. Update of May 2022 (EconMap_3.1_update.zip); reference Fontagne, Perego and Santoni (2022), *International Economics* 172 [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=11, accessed 2026-11-05].
- Gap filled: baseline GDP paths for dynamic or long-run counterfactuals.

**NTM-MAP**
- NTM incidence indices (frequency, coverage, prevalence) from UNCTAD TRAINS for 71 countries and EU28, most recent year in 2009-2015; last update Nov 2015; "not maintained" [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=28, accessed 2026-11-05]. Outdated; use TRAINS NTM instead.

**AVEs-Services**
- Tariff equivalents of cross-border services restrictions for **118 countries and 9 sectors** (117 countries in the 2011 estimation), 2011, plus 2004 and 2007 for the original 64 countries. Last update Dec 2016 [V corrected: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=33, accessed 2026-11-05].
- Gap filled: the only CEPII services-barrier data, essentially a single cross-section. Combine with ITPD-E services flows.

**Not found in the catalogue**
- There is no dedicated CEPII services-trade-flow database [V: https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele.asp, accessed 2026-11-05].

---

## 7. Recommended core set

**(a) US-EU tariff scenario, GE-PPML for Germany**
1. ITPD-E R2025 (plus ITPD-S R2025): domestic and international flows by industry to 2023, so the GE system closes properly for DEU.
2. Teti GTD (aggregated, to 2021) plus WTO IDB/TDF 2022-2025: annual baseline tariffs; Teti's GTD U.S. Trade War extension (to Aug 2025) for US measures.
3. MAcMap-HS6 (already held, request newer years) plus CEPII U.S. Import Tariffs 2025-2026: preferential AVEs and current US tariffs consistent with CEPII data (both non-commercial licences).
4. ProTEE: sector elasticities to map tariff shocks into trade costs.
5. Global Trade Alert (core records free under CC BY-NC; US Tariff Estimates licensed) or US official tariff notices: dates and coverage of 2025 US tariff actions.
6. Larch RTA database or DGD: up-to-date RTA and sanctions controls in the estimation stage (DGD ends 2019).

**(b) EU integration effects**
1. ITPD-E R2025: domestic flows identify border effects and RTA effects in line with theory (Yotov 2021, CESifo WP 9057).
2. CEPII TradeProd V202606: a manufacturing robustness check with BACI-consistent domestic flows to 2022.
3. Larch RTA database (1950-2025, updated 11 Jan 2026) and RTA-IS export: RTA dummies by type (CU versus FTA versus EIA) for the EU, EEA and EU FTAs.
4. World Bank DTA 2.0: provision-level depth, the template from Mattoo, Mulabdic and Ruta (2022) and Fontagne et al. (2023).
5. DESTA 2.3: an alternative depth index as a robustness check.
6. OECD ICIO 2025: a value-added gravity extension and input-output linkages within the Single Market.

**(c) Transport-cost shock scenario (Red Sea, Panama)**
1. OECD ITIC: bilateral CIF/FOB margins by HS4, 1995-2024, to calibrate transport-cost elasticities.
2. IMF PortWatch: daily transits at 28 chokepoints that date and scale the Red Sea and Panama shocks.
3. CERDI-seadistance V1.1 (plus your own rerouting): pair-specific extra distance when Suez or Panama is closed.
4. ITPD-E R2025: GE baseline with domestic flows, so trade diverts to internal trade.
5. NY Fed GSCPI: an aggregate pressure series to validate shock timing.
6. FBX or Drewry WCI (licence required): lane-level freight rates if a licence is available; otherwise use summary values only.

---

## Bulk download URLs confirmed on 2026-11-05 (HTTP 206 to a 1-byte range request unless noted)

- ITPD-E R2025: https://www.usitc.gov/data/gravity/itpd_e/r2025/ITPD_E_R2025.zip
- ITPD-S R2025: https://www.usitc.gov/data/gravity/itpd_s/r2025/itpd_s_r2025.zip (variants _no_names, _2021_2023, _2023)
- DGD v2.1: https://www.usitc.gov/data/gravity/dgd_docs/release_2.1_2000_2019.zip and .../release_2.1_1948_1999.zip
- CEPII Gravity V202211: https://www.cepii.fr/DATA_DOWNLOAD/gravity/data/Gravity_csv_V202211.zip
- BACI HS92 V202601: https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS92_V202601.zip
- TradeProd V202606: https://www.cepii.fr/DATA_DOWNLOAD/tradeprod/V202606/TPe_V202606_csv.zip and .../TPc_V202606_csv.zip
- ProTEE 0.1: https://www.cepii.fr/DATA_DOWNLOAD/ProTEE/ProTEE_0_1.csv
- CEPII US tariffs 2025-2026: https://www.cepii.fr/DATA_DOWNLOAD/usa_tariffs/usa_tariffs_20260907.zip
- WTFC: https://www.cepii.fr/DATA_DOWNLOAD/WTFC/data/WTFC_HS96_V202104.zip
- WTO Structural Gravity Manufacturing Database: https://www.wto.org/english/res_e/reser_e/structural.gravity.manufacturing.database.Ver1.zip
- RTA-IS all RTAs: https://rtais.wto.org/UI/ExportAllRTAList.aspx (HTTP 200, AllRTAs.xlsx)
- CERDI-seadistance V1.1: https://zenodo.org/api/records/240493/files/CERDI-seadistance_V1.1.dta/content
- WITS SDMX API (TRAINS): https://wits.worldbank.org/API/V1/SDMX/V21/rest/dataflow/wbg_wits/ (HTTP 200)
- PortWatch dataset catalogue: https://portwatch.imf.org/api/search/v1/collections/dataset/items (HTTP 200)
- PortWatch daily chokepoint transits (ArcGIS REST, 1,000 records per call, page with resultOffset): https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query?where=1%3D1&outFields=*&f=json (HTTP 200, 79,940 records)
- PortWatch daily port calls and trade: https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Ports_Data/FeatureServer/0/query?where=1%3D1&outFields=*&f=json (HTTP 200, 5,905,900 records); chokepoint and port reference tables: .../PortWatch_chokepoints_database/FeatureServer/0/query and .../PortWatch_ports_database/FeatureServer/0/query
- Larch RTA database (11 Jan 2026, HTTP 200 to HEAD): https://www.ewf.uni-bayreuth.de/pool/dokumente/rta_20260111_csv.zip, .../rta_20260111_dta.zip, .../rta_individual_agreements_20260111_csv.zip, .../rta_individual_agreements_20260111_dta.zip; readme https://www.ewf.uni-bayreuth.de/pool/dokumente/readme_RTA3.pdf
- OECD ITIC SDMX API (HTTP 200, full seven-part key required): https://sdmx.oecd.org/sti-public/rest/data/OECD.SDD.TPS,DSD_ITIC@DF_ITIC,1.1/DEU.USA.C_F.C._T.A.PT_IM_CIF?format=csvfilewithlabels; dataflow catalogue https://sdmx.oecd.org/public/rest/dataflow/all
- NY Fed GSCPI: https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx (HTTP 200 to HEAD) and https://www.newyorkfed.org/medialibrary/research/interactives/data/gscpi/gscpi_interactive_data.csv (HTTP 200)
- Teti GTD v_beta1-2024-12 and Trade War Extension v_2025-10: the 7 Dropbox links on https://feodorateti.github.io/data.html work when www.dropbox.com is replaced by dl.dropboxusercontent.com (HTTP 206), e.g. https://dl.dropboxusercontent.com/scl/fi/wnsgnkkqz2ifb2vqiuyce/Pairs_vbeta1-2024-12.7z?rlkey=5m4ka7142bl9y1z0dndsaso36&st=b0tq7wr2&dl=1
- CEPII MAcMap-HS6 tariffs 2001-2019 (2.7 GB): https://dl.dropboxusercontent.com/scl/fi/rfow5essm4b5kt30o0gdx/Tariffs_2001_2019.zip?rlkey=yd3d66fegws2yv58ng0kmlryl&dl=1 (HTTP 206)
- DESTA 2.3: https://www.designoftradeagreements.org/media/filer_public/53/af/53af422c-29b0-48f9-bf1c-3537f5c028d4/desta_version_02_03.csv (HTTP 200 to HEAD); indices, treaty lists and withdrawals are linked on https://www.designoftradeagreements.org/downloads/
- Not testable here: World Bank DTA 2.0 files on datacatalogfiles.worldbank.org (HTTP 403 from this session; URLs are listed on the Data Catalog page), WTO TTD six-digit downloads (ttd.wto.org, HTTP 403).

---

## Blocked domains (allow these to verify the remaining facts)

Still blocked or refusing on 2026-11-05 (re-checked after more hosts were opened):
- www.oecd.org and oecd.org (HTTP 403 with default, browser, Wget and python-requests User-Agents), t4.oecd.org, search.oecd.org (CONNECT refused). sdmx.oecd.org now works (use the sti-public route for ITIC data); data-explorer.oecd.org answers but is a script-only app.
- ttd.wto.org (HTTP 403)
- datacatalogfiles.worldbank.org (HTTP 403) and datacatalogapi.worldbank.org (CONNECT refused); the catalogue pages on datacatalog.worldbank.org work
- per-file Dropbox content hosts (*.dl.dropboxusercontent.com, CONNECT refused); workaround: rewrite www.dropbox.com/scl/fi/... links to dl.dropboxusercontent.com/scl/fi/...
- api-trains2.unctad.org (TRAINS Portal back end)
- www.cesifo.org and www.ifo.de (needed for the CESifo working-paper numbers)
- worldmrio.com, www.ifw-kiel.de, www.freightos.com, ferdi.fr

Worked: www.usitc.gov (default curl User-Agent only), www.cepii.fr, www.wto.org, rtais.wto.org, wits.worldbank.org, portwatch.imf.org, services9.arcgis.com, feodorateti.github.io, zenodo.org, www.rug.nl, dataverse.nl, sdmx.oecd.org, www.newyorkfed.org, www.ewf.uni-bayreuth.de, dl.dropboxusercontent.com, globaltradealert.org, unctad.org, trainsonline.unctad.org, catalog.data.gov, www.designoftradeagreements.org, datacatalog.worldbank.org, datatopics.worldbank.org.
