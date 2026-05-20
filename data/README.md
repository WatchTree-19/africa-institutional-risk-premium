# Data sources

*Document each variable's source: URL, version, access date, time coverage, units. Per research-practice mandatories in the project's `guidelines-and-mandatories.md`.*

*Cutoff: late 2023. No data points later than Q4 2023.*

---

## Sovereign-spread data

### World Bank Global Economic Monitor EMBI mirror

- **What.** Daily stripped EMBI spreads, mirror of JP Morgan EMBI Global Diversified.
- **URL.** databank.worldbank.org/source/global-economic-monitor
- **Coverage.** Nigeria, Ghana, Zambia, Brazil, Chile, Indonesia, Malaysia (local-currency index), Botswana, Mauritius, Rwanda.
- **Frequency.** Daily.
- **Access date.** [fill when downloaded]

### IMF International Financial Statistics

- **What.** Monthly long-term government bond yields.
- **URL.** data.imf.org
- **Coverage.** India, Korea, Malaysia, Indonesia, Brazil, Chile, Singapore.
- **Frequency.** Monthly.
- **Access date.** [fill when downloaded]

### FRED (St. Louis Fed)

- **What.** OECD-sourced sovereign bond yield mirror.
- **URL.** fred.stlouisfed.org
- **Series of interest.**
  - India 10-year: `INDIRLTLT01STM` (Dec 2011 onwards)
  - Korea 10-year: `IRLTLT01KRM156N` (2000 onwards)
  - South Africa 10-year: `IRLTLT01ZAM156N`
- **Frequency.** Monthly.
- **Access date.** [fill when downloaded]

### Monetary Authority of Singapore (MAS)

- **What.** Daily Singapore Government Securities yields.
- **URL.** eservices.mas.gov.sg/statistics/fdanet/BenchmarkPricesAndYields.aspx
- **Coverage.** Singapore only. Back to 1998.
- **Frequency.** Daily.
- **Access date.** [fill when downloaded]

### Country central bank portals (where IFS / FRED gaps exist)

- **Bank of Zambia open data.** bankofzambia.opendataforafrica.org
- **Bank of Ghana statistical bulletins.** bog.gov.gh
- **Central Bank of Nigeria.** cbn.gov.ng
- **Bank of Botswana statistical bulletins.** bankofbotswana.bw
- **Bank of Mauritius.** bom.mu

### World Bank International Debt Statistics

- **What.** Annual interest-on-external-debt as proxy yield.
- **URL.** datacatalog.worldbank.org/dataset/international-debt-statistics
- **Use.** Fallback for Zimbabwe (used as qualitative case-study proxy only, not in main spread regression).

---

## Macroeconomic data

### World Bank World Development Indicators

- **What.** GDP per capita, gross capital formation, labor force, inflation, agricultural employment share, fiscal balance, debt-to-GDP ratio, reserves.
- **URL.** data.worldbank.org
- **Coverage.** All 15 countries through 2023.
- **Access date.** [fill when downloaded]

### Penn World Table 10.01

- **What.** GDP, capital stocks, labor inputs, TFP at constant national prices and current PPPs.
- **URL.** rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100
- **Coverage.** 183 countries, 1950 to 2019.
- **Note.** Splice with WDI for 2020-2023. Document the splice.
- **Access date.** [fill when downloaded]

### Maddison Project Database 2023

- **What.** Historical GDP per capita in 2011 international dollars.
- **URL.** rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023
- **Coverage.** 169 countries through 2022.
- **Access date.** [fill when downloaded]

---

## Corruption and institutional quality data

### Transparency International Corruption Perceptions Index (CPI)

- **What.** Annual CPI scores per country.
- **URL.** transparency.org/en/cpi
- **Note.** Original 0-10 scale (pre-2012) rescaled to match 0-100 scale (2012 onwards). Original thesis used 0-10 rescaled; replicate that scaling.
- **Coverage.** 1998 to 2023.
- **Access date.** [fill when downloaded]

### Worldwide Governance Indicators (WGI), Control of Corruption sub-index

- **What.** Six governance dimensions including Control of Corruption.
- **URL.** info.worldbank.org/governance/wgi
- **Coverage.** 1996 to 2023.
- **Access date.** [fill when downloaded]

### V-Dem (Varieties of Democracy), corruption sub-indices

- **What.** Political Corruption Index plus sub-indices (bribery, public theft, etc.).
- **URL.** v-dem.net/data/the-v-dem-dataset
- **Coverage.** 175 countries, 1789 onwards. Use 1998-2023 window.
- **Access date.** [fill when downloaded]

---

## Reform-event dates (DiD analysis)

For each of the six reform events, document the exact treatment date and any pre-period defining details. Compiled from official agency websites, secondary literature, and Wikipedia cross-checks. Document sources in `code/stata/did_event_studies.do` header.

- **Indonesia KPK.** Established 27 December 2002, operational from 2003.
- **Nigeria EFCC.** Established 2003 (Economic and Financial Crimes Commission Establishment Act).
- **Brazil Lava Jato.** Operation began 17 March 2014.
- **India Lokpal.** Lokpal and Lokayuktas Act 2013 passed; Lokpal operational from 2014.
- **Rwanda post-1994.** Institutional rebuild period beginning 1995. Treat treatment date as 1995 with a longer post-period.
- **South Korea post-1987.** Constitutional reform 1987. Treat treatment date as 1987 with extended post-period.

---

## Missing data handling

Document any imputation, interpolation, or omission decisions per research-practice mandatories.

- Zimbabwe inflation 2007-2009: hyperinflation periods omitted or mean-imputed (matches original thesis methodology).
- Africa frontier-market yield gaps pre-2008: filled from World Bank IDS proxy where IFS/EMBI series are too thin.
- Document each decision in the relevant cleaning script's header.
