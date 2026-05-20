"""
data_collection.py
==================

Pull raw data from public sources for the working paper:
    "Does the presence of corruption inhibit a nation's growth prospects?"

Sources pulled:
    1. WGI (Worldwide Governance Indicators) — Control of Corruption — directly
       from worldbank.org dam.
    2. CPI (Corruption Perceptions Index) — Transparency International, via
       Our World in Data mirror (2012-onward; pre-2012 has a methodology
       break and is not used).
    3. WDI macro controls — World Bank API via wbgapi.
    4. PWT 10.01 — Penn World Table via dataverse.nl (Groningen mirror).
    5. FRED US 10-year Treasury yield (DGS10) via pandas_datareader.
    6. FRED long-term yields where available for sample countries.

Outputs raw files to ../../data/raw/.

Late-2023 cutoff respected: all series are truncated at end-2023.
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import wbgapi as wb
import pandas_datareader.data as web
import datetime as dt


HERE = Path(__file__).resolve().parent
RAW = HERE.parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Sample
# ----------------------------------------------------------------------
SAMPLE = {
    # Africa (8)
    "NGA": "Nigeria",
    "SEN": "Senegal",
    "GHA": "Ghana",
    "ZMB": "Zambia",
    "ZWE": "Zimbabwe",
    "RWA": "Rwanda",
    "BWA": "Botswana",
    "MUS": "Mauritius",
    # Asia (5)
    "SGP": "Singapore",
    "IND": "India",
    "KOR": "Korea, Rep.",
    "IDN": "Indonesia",
    "MYS": "Malaysia",
    # Latin America controls (2)
    "BRA": "Brazil",
    "CHL": "Chile",
}
COUNTRIES = list(SAMPLE.keys())
START_YEAR = 1998
END_YEAR = 2023
YEARS = list(range(START_YEAR, END_YEAR + 1))


# ----------------------------------------------------------------------
# 1. WGI — Worldwide Governance Indicators
# ----------------------------------------------------------------------
def pull_wgi():
    print("[1/6] Pulling WGI from worldbank.org ...", flush=True)
    url = "https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset.xlsx"
    out = RAW / "wgi.xlsx"
    if not out.exists():
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
    print(f"      saved {out.name} ({out.stat().st_size//1024} KB)")
    return out


# ----------------------------------------------------------------------
# 2. CPI — Corruption Perceptions Index
# ----------------------------------------------------------------------
def pull_cpi():
    print("[2/6] Pulling CPI from Our World in Data mirror ...", flush=True)
    url = "https://ourworldindata.org/grapher/corruption-perception-index.csv"
    out = RAW / "cpi_owid.csv"
    if not out.exists():
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
    print(f"      saved {out.name}")
    return out


# ----------------------------------------------------------------------
# 3. WDI — World Development Indicators
# ----------------------------------------------------------------------
WDI_INDICATORS = {
    # Outcomes / treatments
    "FR.INR.LEND": "lending_rate",
    "FR.INR.RINR": "real_interest_rate",
    "FR.INR.DPST": "deposit_rate",
    "FR.INR.RISK": "lending_risk_premium",
    # GDP / growth
    "NY.GDP.PCAP.KD": "gdp_pc_constant",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "NY.GDP.PCAP.PP.KD": "gdp_pc_ppp",
    # Macro controls
    "FP.CPI.TOTL.ZG": "inflation",
    "NE.EXP.GNFS.ZS": "exports_pct_gdp",
    "NE.IMP.GNFS.ZS": "imports_pct_gdp",
    "DT.DOD.DECT.GN.ZS": "external_debt_pct_gni",
    "BN.CAB.XOKA.GD.ZS": "current_account_pct_gdp",
    "FI.RES.TOTL.MO": "reserves_months_imports",
    # Growth accounting inputs
    "SL.TLF.TOTL.IN": "labour_force",
    "SE.SEC.ENRR": "secondary_enrollment",
    "SP.POP.TOTL": "population",
    # Investment
    "NE.GDI.TOTL.ZS": "gross_capital_formation_pct_gdp",
    # Trade
    "NE.TRD.GNFS.ZS": "trade_pct_gdp",
}


def pull_wdi():
    print("[3/6] Pulling WDI indicators via wbgapi ...", flush=True)
    out = RAW / "wdi.csv"
    if out.exists():
        print(f"      cached {out.name}")
        return out
    frames = []
    for code, name in WDI_INDICATORS.items():
        try:
            df = wb.data.DataFrame(
                code, economy=COUNTRIES, time=YEARS,
                columns="time", skipBlanks=False, labels=False,
            )
            df = df.reset_index().melt(
                id_vars="economy", var_name="year", value_name=name
            )
            df["year"] = df["year"].str.replace("YR", "").astype(int)
            frames.append(df.set_index(["economy", "year"]))
            print(f"      ok    {code:25} {name}")
        except Exception as e:
            print(f"      FAIL  {code:25} {name}: {str(e)[:80]}")
        time.sleep(0.2)
    merged = pd.concat(frames, axis=1).reset_index()
    merged.to_csv(out, index=False)
    print(f"      saved {out.name} ({len(merged)} rows)")
    return out


# ----------------------------------------------------------------------
# 4. PWT — Penn World Table 10.01
# ----------------------------------------------------------------------
def pull_pwt():
    print("[4/6] Pulling PWT 10.01 from dataverse.nl ...", flush=True)
    url = "https://dataverse.nl/api/access/datafile/354095"
    out = RAW / "pwt1001.xlsx"
    if not out.exists():
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
    print(f"      saved {out.name} ({out.stat().st_size//1024} KB)")
    return out


# ----------------------------------------------------------------------
# 5. FRED — US Treasury yields and long-term rates where available
# ----------------------------------------------------------------------
def pull_fred():
    print("[5/6] Pulling FRED series ...", flush=True)
    start = dt.datetime(START_YEAR, 1, 1)
    end = dt.datetime(END_YEAR, 12, 31)
    out_us = RAW / "fred_us10y.csv"
    if not out_us.exists():
        us10y = web.DataReader("DGS10", "fred", start, end)
        us10y.to_csv(out_us)
    print(f"      saved {out_us.name}")

    # Try long-term yield series for sample countries (OECD coverage)
    fred_country_yields = {
        "SGP": "IRLTLT01SGM156N",
        "KOR": "IRLTLT01KRM156N",
        "CHL": "IRLTLT01CLM156N",
        "MEX": "IRLTLT01MXM156N",  # for benchmark, not in sample
    }
    out_country = RAW / "fred_country_yields.csv"
    if not out_country.exists():
        frames = []
        for iso, series in fred_country_yields.items():
            try:
                df = web.DataReader(series, "fred", start, end)
                df.columns = [iso]
                frames.append(df)
                print(f"      ok    FRED {iso} ({series}) {len(df)} obs")
            except Exception as e:
                print(f"      FAIL  FRED {iso} ({series}): {str(e)[:80]}")
        if frames:
            merged = pd.concat(frames, axis=1)
            merged.to_csv(out_country)
    print(f"      saved {out_country.name}")
    return out_us, out_country


# ----------------------------------------------------------------------
# 6. Reform events (constants, not pulled)
# ----------------------------------------------------------------------
def write_reform_events():
    print("[6/6] Writing reform event metadata ...", flush=True)
    events = pd.DataFrame([
        {"country": "IDN", "event": "KPK established",        "year": 2003, "type": "anti-corruption commission"},
        {"country": "NGA", "event": "EFCC established",       "year": 2003, "type": "anti-corruption commission"},
        {"country": "BRA", "event": "Operation Lava Jato",    "year": 2014, "type": "prosecutorial operation"},
        {"country": "IND", "event": "Lokpal Act",             "year": 2014, "type": "anti-corruption commission"},
        {"country": "RWA", "event": "Post-1994 inst. rebuild","year": 1998, "type": "institutional rebuild"},  # window starts at sample start
        {"country": "KOR", "event": "Post-1987 consolidation","year": 1998, "type": "democratic consolidation"},  # window starts at sample start
    ])
    out = RAW / "reform_events.csv"
    events.to_csv(out, index=False)
    print(f"      saved {out.name}")
    return out


# ----------------------------------------------------------------------
def main():
    print(f"Working paper data collection — sample 1998-2023, {len(COUNTRIES)} countries")
    print(f"Output dir: {RAW}")
    print()
    pull_wgi()
    pull_cpi()
    pull_wdi()
    pull_pwt()
    pull_fred()
    write_reform_events()
    print()
    print("Done. Raw files in", RAW)


if __name__ == "__main__":
    main()
