"""
data_cleaning.py
================

Build the balanced panel from raw data pulled by data_collection.py.

Outputs:
    data/processed/panel.csv   — country-year panel for regressions
    data/processed/pwt.csv     — country-year PWT extract for growth accounting

Voice rule: late-2023 cutoff respected. Series truncated at 2023.
"""

from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RAW = HERE.parent.parent / "data" / "raw"
PROC = HERE.parent.parent / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

SAMPLE = {
    "NGA": "Nigeria", "SEN": "Senegal", "GHA": "Ghana", "ZMB": "Zambia",
    "ZWE": "Zimbabwe", "RWA": "Rwanda", "BWA": "Botswana", "MUS": "Mauritius",
    "SGP": "Singapore", "IND": "India", "KOR": "Korea, Rep.", "IDN": "Indonesia",
    "MYS": "Malaysia", "BRA": "Brazil", "CHL": "Chile",
}
COUNTRIES = list(SAMPLE.keys())
AFRICA = {"NGA","SEN","GHA","ZMB","ZWE","RWA","BWA","MUS"}
ASIA = {"SGP","IND","KOR","IDN","MYS"}
LATAM = {"BRA","CHL"}
START_YEAR = 1998
END_YEAR = 2023


# ----------------------------------------------------------------------
def load_wgi():
    """WGI Control of Corruption — Estimate by country-year."""
    xl = pd.ExcelFile(RAW / "wgi.xlsx")
    df = pd.read_excel(xl, sheet_name="ControlofCorruption", header=None)
    # Year header on row 13 (0-indexed), variable type on row 14, codes on column 1
    years = df.iloc[13].values
    var_labels = df.iloc[14].values
    data = df.iloc[15:].copy()
    data.columns = list(range(data.shape[1]))
    out = []
    code_col = 1
    # iterate columns and find Estimate columns
    for col in range(2, len(years)):
        if pd.notna(years[col]) and var_labels[col] == "Estimate":
            yr = int(years[col])
            chunk = data[[code_col, col]].copy()
            chunk.columns = ["economy", "wgi_cc"]
            chunk["year"] = yr
            out.append(chunk)
    wgi = pd.concat(out)
    wgi = wgi[wgi["economy"].isin(COUNTRIES)].copy()
    wgi["wgi_cc"] = pd.to_numeric(wgi["wgi_cc"], errors="coerce")
    return wgi[["economy", "year", "wgi_cc"]]


# ----------------------------------------------------------------------
def load_cpi():
    """CPI from OWID. Note: methodology break in 2012; we use 2012+ only."""
    df = pd.read_csv(RAW / "cpi_owid.csv")
    df = df.rename(columns={"Code": "economy", "Year": "year",
                            "Corruption Perceptions Index": "cpi_raw"})
    df = df[df["economy"].isin(COUNTRIES)].copy()
    df = df[df["year"].between(2012, END_YEAR)]
    # Invert so higher = more corruption (matches headline framing)
    df["cpi_inverted"] = 100 - df["cpi_raw"]
    return df[["economy", "year", "cpi_raw", "cpi_inverted"]]


# ----------------------------------------------------------------------
def load_wdi():
    return pd.read_csv(RAW / "wdi.csv")


# ----------------------------------------------------------------------
def load_us10y():
    df = pd.read_csv(RAW / "fred_us10y.csv")
    df.columns = ["date", "us10y"]
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["us10y"] = pd.to_numeric(df["us10y"], errors="coerce")
    annual = df.dropna(subset=["us10y"]).groupby("year")["us10y"].mean().reset_index()
    annual = annual[annual["year"].between(START_YEAR, END_YEAR)]
    return annual


# ----------------------------------------------------------------------
def load_fred_country_yields():
    """Long-term yields for countries where FRED has them (KOR, CHL, MEX)."""
    df = pd.read_csv(RAW / "fred_country_yields.csv")
    df.columns = ["date"] + list(df.columns[1:])
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    annuals = []
    for iso in df.columns:
        if iso in ("date", "year"):
            continue
        if iso not in COUNTRIES:
            continue
        d = df[["year", iso]].copy()
        d.columns = ["year", "country_yield"]
        d["country_yield"] = pd.to_numeric(d["country_yield"], errors="coerce")
        d = d.dropna(subset=["country_yield"]).groupby("year")["country_yield"].mean().reset_index()
        d["economy"] = iso
        annuals.append(d)
    if annuals:
        out = pd.concat(annuals)
        return out[["economy", "year", "country_yield"]]
    return pd.DataFrame(columns=["economy", "year", "country_yield"])


# ----------------------------------------------------------------------
def load_pwt():
    """PWT 10.01 extract for growth accounting."""
    xl = pd.ExcelFile(RAW / "pwt1001.xlsx")
    df = pd.read_excel(xl, sheet_name="Data")
    df = df[df["countrycode"].isin(COUNTRIES)].copy()
    df = df[df["year"].between(START_YEAR, END_YEAR)]
    keep = ["countrycode", "country", "year",
            "rgdpna", "rkna", "emp", "hc", "ctfp", "rtfpna", "labsh", "pop"]
    df = df[keep].rename(columns={"countrycode": "economy"})
    return df


# ----------------------------------------------------------------------
def assemble_panel():
    """Merge all sources into a single balanced panel."""
    # Build skeleton: country x year
    skeleton = pd.DataFrame(
        [(c, y) for c in COUNTRIES for y in range(START_YEAR, END_YEAR + 1)],
        columns=["economy", "year"],
    )

    wgi = load_wgi()
    cpi = load_cpi()
    wdi = load_wdi()
    us10y = load_us10y()
    cyields = load_fred_country_yields()

    df = (skeleton
          .merge(wgi, on=["economy", "year"], how="left")
          .merge(cpi, on=["economy", "year"], how="left")
          .merge(wdi, on=["economy", "year"], how="left")
          .merge(us10y, on="year", how="left")
          .merge(cyields, on=["economy", "year"], how="left"))

    # Region tags
    df["region"] = df["economy"].map(
        lambda c: "Africa" if c in AFRICA else ("Asia" if c in ASIA else "LatAm")
    )
    df["country_name"] = df["economy"].map(SAMPLE)

    # Headline outcome: institutional risk premium proxy
    # Where FRED yield available, use country_yield - us10y
    # Elsewhere, use lending_rate - us10y as the cost-of-capital premium
    df["spread_fred"] = df["country_yield"] - df["us10y"]
    df["spread_wdi"] = df["lending_rate"] - df["us10y"]
    # Primary spread: prefer FRED, fall back to WDI lending - US10y
    df["spread_bps"] = (df["spread_fred"]
                       .fillna(df["spread_wdi"])) * 100  # basis points

    # Log spread for the headline specification (require positive)
    df["log_spread"] = np.where(df["spread_bps"] > 0,
                                np.log(df["spread_bps"]),
                                np.nan)

    # Log lending rate as alternative outcome
    df["log_lending"] = np.where(df["lending_rate"] > 0,
                                 np.log(df["lending_rate"]),
                                 np.nan)

    # Convenience: inverted WGI so higher = more corruption (mirrors CPI)
    df["wgi_cc_inv"] = -df["wgi_cc"]

    # Trade openness
    df["trade_openness"] = df["exports_pct_gdp"] + df["imports_pct_gdp"]

    # Drop columns with no analytical use after merging
    drop_cols = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Sort and write
    df = df.sort_values(["economy", "year"]).reset_index(drop=True)
    out = PROC / "panel.csv"
    df.to_csv(out, index=False)
    print(f"Panel: {len(df)} rows, {df['economy'].nunique()} countries, "
          f"{df['year'].nunique()} years -> {out.name}")
    return df


# ----------------------------------------------------------------------
def assemble_pwt():
    pwt = load_pwt()
    out = PROC / "pwt.csv"
    pwt.to_csv(out, index=False)
    print(f"PWT: {len(pwt)} rows -> {out.name}")
    return pwt


# ----------------------------------------------------------------------
def coverage_report(df):
    print("\nKey variable coverage (non-null obs by country):")
    keys = ["wgi_cc", "cpi_inverted", "lending_rate", "spread_bps",
            "gdp_growth", "inflation", "external_debt_pct_gni"]
    summary = df.groupby("economy")[keys].apply(lambda x: x.notna().sum())
    print(summary.to_string())


def main():
    df = assemble_panel()
    pwt = assemble_pwt()
    coverage_report(df)


if __name__ == "__main__":
    main()
