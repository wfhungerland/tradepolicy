# "Big G" for Germany: public procurement facts from TED (pilot, 2026-11-11)

Question: can the stylised facts of Cox, Müller, Pasten, Schoenle and Weber ("Big G",
JPE 2024) be reproduced for Germany? Data: all TED contract award notices with a buyer in
Germany, 2016-2025 (legacy XML monthly packages via tools/ted_legacy_packages.py; eForms
via the TED search API, tools/ted_eforms_api.py), 734,000 awards in 469,000 notices.
Script: 85_bigg_ted.py; site tab "Beschaffung" (data/bigg_ted.json).

Coverage: only contracts above EU thresholds; 35-90 bn EUR a year of award values
(Destatis Vergabestatistik 2024, all contracts from 25,000 EUR: 135 bn EUR). Values present in
57-85 % of awards before 2024 and 46-60 % in eForms years; contractor named in 85-94 %;
bid count in 79-96 %. Many defence contracts are exempt from EU-wide tendering. Award values
are not spending (framework agreements are often not exhausted).

Cleaning: awards above 5 bn EUR dropped; values of multi-contractor awards split equally;
>= 3 awards of one notice with an identical value read as a repeated notice total and split
(BMG mask open-house 2020: 37 x 637 m EUR); federal buyers identified by name in addition to
the reported legal type; firm names harmonised roughly (legal forms removed).

Results:
1. Volatility (F1, partly): federal buyers award 19 % of the volume but account for 38 % of
   the variance of year-on-year changes in quarterly award values (utilities and other 29 %
   and 39 %, Länder and municipalities 39 % and 20 %). Big G: federal 1/6 of G, about half
   of its short-run variance. Direction confirmed, weaker; no payment data.
2. Granularity (F2): on average the 100 largest contractors receive 41 % of the volume, the
   largest 1 % of contracts 51 %; the 100 largest firms account for 28-47 % of the absolute
   year-on-year changes in firm-level volumes.
3. Competition (F3): median three bids; single-bid awards rose from 17 % (2016) to 28 %
   (2022/23) and 22 % (2025). Supplies 39 % single-bid, services 22 %, works 11 %; federal
   buyers 28 %, Länder and municipalities 19 %.
4. Persistence (F4): about 70 % of the volume (2022-2025) goes to firms that won a contract
   in the three preceding years; 16-24 % to the same buyer-firm pair. Contract duration is
   too sparsely reported (eForms 13 %) to test long contracts.
5. Composition (F5): services 38 %, works 37 %, supplies 25 % of the volume; construction
   (CPV 45) 33 %. The link to price stickiness needs external price-change frequencies.

Vergabestatistik (VergStatVO as amended 12 May 2026): a business statistic run by Destatis on
behalf of the BMWE, not an FDZ product. Federal authorities get statistical evaluations on request
to the BMWE (§ 4(4)); research institutions get anonymised micro data via the BMWE (§ 5). It covers
contracts from 50,000 EUR below the EU thresholds (Annex 8: buyer name and detailed level, CPV,
value, procedure, date; bid counts voluntary) and above them (Annex 1: also bid counts and the
OJ notice number, which links records to TED). Contractors appear only as SME yes/no and country
of origin, so granularity and supplier persistence cannot be measured with it.

Next steps if pursued: special evaluations of the Vergabestatistik (volume and volatility
including below-threshold contracts, by detailed buyer level); federal budget execution data for spending instead of awards; firm identifiers
(Handelsregister) instead of name matching; sector price-change frequencies (e.g. PRISMA).

## On hold (Wiedervorlage, 2026-11-11)

Request to the BMWE procurement unit for special evaluations of the Vergabestatistik
(§ 4(4) VergStatVO), parked by the owner. Draft (German, in the chat of 2026-11-11) asks for,
quarterly from 2021, above and below thresholds: (1) number and volume by fine buyer level and
contract type; (2) size distribution (value classes from 50k EUR; share of the largest 1 % and
10 % of contracts); (3) distribution of bid counts by procedure, contract type and buyer level,
volume share of single-bid awards; (4) SME awards by buyer level and value class; (5) if
permitted, a list of above-threshold records with OJ notice number, value, buyer level and
bid count to link with TED.
