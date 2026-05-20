"""
analysis.py
===========

Run the empirical analysis for the working paper.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore")


HERE = Path(__file__).resolve().parent
PROC = HERE.parent.parent / "data" / "processed"
TABLES = HERE.parent.parent / "output" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

AFRICA = {"NGA","SEN","GHA","ZMB","ZWE","RWA","BWA","MUS"}
ASIA = {"SGP","IND","KOR","IDN","MYS"}
LATAM = {"BRA","CHL"}


def load_panel():
    df = pd.read_csv(PROC / "panel.csv")
    df = df.set_index(["economy", "year"]).sort_index()
    return df


def load_pwt():
    return pd.read_csv(PROC / "pwt.csv")


def panel_fe(df, dep, regressor, controls, label, time_effects=True):
    cols = [dep, regressor] + controls
    sub = df[cols].dropna()
    if len(sub) < 30:
        return None
    y = sub[dep]
    X = sub[[regressor] + controls]
    try:
        mod = PanelOLS(y, X, entity_effects=True, time_effects=time_effects,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        return {"label": label, "error": str(e)[:200]}
    return {
        "label": label,
        "dep": dep,
        "regressor": regressor,
        "controls": controls,
        "n_obs": int(res.nobs),
        "n_entities": int(res.entity_info.total),
        "coef": float(res.params[regressor]),
        "se": float(res.std_errors[regressor]),
        "t": float(res.tstats[regressor]),
        "p": float(res.pvalues[regressor]),
        "r2_within": float(res.rsquared_within),
        "time_effects": time_effects,
    }


def run_panel_regressions(df):
    print("\n=== Section 4.1: Panel FE regressions ===")
    controls_basic = ["gdp_growth", "inflation"]
    controls_full = ["gdp_growth", "inflation",
                     "current_account_pct_gdp",
                     "reserves_months_imports",
                     "trade_openness"]
    results = {}

    results["m1_headline"] = panel_fe(
        df, "log_spread", "wgi_cc_inv", controls_full,
        "Headline: log spread on inverted WGI + full macro controls"
    )
    results["m2_log_lending"] = panel_fe(
        df, "log_lending", "wgi_cc_inv", controls_full,
        "Robustness: log lending rate on inverted WGI + full macro controls"
    )
    results["m3_cpi"] = panel_fe(
        df, "log_lending", "cpi_inverted", controls_full,
        "Robustness: log lending on inverted CPI (2012+) + full controls"
    )
    results["m4_parsimonious"] = panel_fe(
        df, "log_lending", "wgi_cc_inv", controls_basic,
        "Robustness: log lending on inverted WGI + parsimonious controls"
    )
    results["m5_no_time_fe"] = panel_fe(
        df, "log_lending", "wgi_cc_inv", controls_full,
        "Robustness: log lending on inverted WGI + full controls, country FE only",
        time_effects=False,
    )
    results["m6_risk_premium"] = panel_fe(
        df, "lending_risk_premium", "wgi_cc_inv", controls_basic,
        "WDI risk premium on inverted WGI + parsimonious controls"
    )

    for k, r in results.items():
        if r is None:
            print(f"  {k}: not estimated (insufficient obs)")
            continue
        if "error" in r:
            print(f"  {k}: error - {r['error']}")
            continue
        print(f"  {k} ({r['label']})")
        print(f"      coef={r['coef']:.4f} se={r['se']:.4f} "
              f"t={r['t']:.2f} p={r['p']:.4f} N={r['n_obs']} R2w={r['r2_within']:.3f}")

    (TABLES / "panel_fe.json").write_text(json.dumps(results, indent=2))
    return results


REFORM_EVENTS = [
    {"country": "IDN", "year": 2003, "name": "Indonesia KPK 2003"},
    {"country": "NGA", "year": 2003, "name": "Nigeria EFCC 2003"},
    {"country": "BRA", "year": 2014, "name": "Brazil Lava Jato 2014"},
    {"country": "IND", "year": 2014, "name": "India Lokpal 2014"},
    {"country": "RWA", "year": 2003, "name": "Rwanda post-1994 (2003-treatment proxy)"},
    {"country": "KOR", "year": 2003, "name": "South Korea consolidation (2003-proxy)"},
]


def run_did(df, event):
    country = event["country"]
    yr = event["year"]
    sub = df.reset_index()
    sub = sub[["economy", "year", "log_lending"]].dropna()
    sub = sub[(sub["year"] >= yr - 5) & (sub["year"] <= yr + 5)]
    sub["treated"] = (sub["economy"] == country).astype(int)
    sub["post"] = (sub["year"] >= yr).astype(int)
    sub["did"] = sub["treated"] * sub["post"]
    if (sub["did"] == 1).sum() < 2:
        return {"event": event["name"], "error": "insufficient post-treatment obs"}
    sub = sub.set_index(["economy", "year"]).sort_index()
    try:
        mod = PanelOLS(sub["log_lending"], sub[["did"]],
                       entity_effects=True, time_effects=True,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        return {"event": event["name"], "error": str(e)[:200]}
    return {
        "event": event["name"],
        "country": country,
        "year": yr,
        "n_obs": int(res.nobs),
        "coef_did": float(res.params["did"]),
        "se_did": float(res.std_errors["did"]),
        "t_did": float(res.tstats["did"]),
        "p_did": float(res.pvalues["did"]),
        "coef_pct_change": float((np.exp(res.params["did"]) - 1) * 100),
    }


def run_event_studies(df):
    print("\n=== Section 4.3: DiD event studies ===")
    results = []
    for ev in REFORM_EVENTS:
        r = run_did(df, ev)
        results.append(r)
        if "error" in r:
            print(f"  {ev['name']}: error - {r['error']}")
        else:
            print(f"  {ev['name']}: coef={r['coef_did']:.4f} "
                  f"({r['coef_pct_change']:+.1f}%) se={r['se_did']:.4f} "
                  f"t={r['t_did']:.2f} p={r['p_did']:.4f} N={r['n_obs']}")
    (TABLES / "did_events.json").write_text(json.dumps(results, indent=2))
    return results


def growth_accounting(pwt):
    print("\n=== Section 5: Growth accounting ===")
    alpha = 1/3
    pwt = pwt.copy()
    pwt = pwt.dropna(subset=["rgdpna", "rkna", "emp", "hc"])
    pwt = pwt[pwt["emp"] > 0]
    pwt["y"] = pwt["rgdpna"] / pwt["emp"]
    pwt["k"] = pwt["rkna"] / pwt["emp"]
    pwt["log_y"] = np.log(pwt["y"])
    pwt["log_k"] = np.log(pwt["k"])
    pwt["log_h"] = np.log(pwt["hc"])
    pwt["log_tfp"] = pwt["log_y"] - alpha * pwt["log_k"] - (1 - alpha) * pwt["log_h"]

    last_year = pwt.groupby("economy")["year"].max()
    pwt_last = pwt[pwt.apply(lambda r: r["year"] == last_year[r["economy"]], axis=1)]
    var_y = pwt_last["log_y"].var()
    var_k_contrib = (alpha * pwt_last["log_k"]).var()
    var_h_contrib = ((1 - alpha) * pwt_last["log_h"]).var()
    var_tfp_contrib = pwt_last["log_tfp"].var()

    levels = {
        "method": "levels variance decomposition (Caselli 2005)",
        "var_log_y": float(var_y),
        "share_capital": float(var_k_contrib / var_y),
        "share_human_capital": float(var_h_contrib / var_y),
        "share_tfp": float(var_tfp_contrib / var_y),
        "year_observed": int(pwt_last["year"].max()),
    }
    print(f"  Levels decomposition (year={levels['year_observed']}):")
    print(f"    capital share:  {levels['share_capital']*100:.1f}%")
    print(f"    human capital:  {levels['share_human_capital']*100:.1f}%")
    print(f"    TFP residual:   {levels['share_tfp']*100:.1f}%")

    pwt["region"] = pwt["economy"].map(
        lambda c: "Africa" if c in AFRICA else ("Asia" if c in ASIA else "LatAm")
    )
    growth_by = pwt.groupby(["economy", "region"]).apply(
        lambda d: pd.Series({
            "g_y": (d["log_y"].iloc[-1] - d["log_y"].iloc[0]) / (d["year"].iloc[-1] - d["year"].iloc[0]),
            "g_k": (d["log_k"].iloc[-1] - d["log_k"].iloc[0]) / (d["year"].iloc[-1] - d["year"].iloc[0]),
            "g_h": (d["log_h"].iloc[-1] - d["log_h"].iloc[0]) / (d["year"].iloc[-1] - d["year"].iloc[0]),
            "g_tfp": (d["log_tfp"].iloc[-1] - d["log_tfp"].iloc[0]) / (d["year"].iloc[-1] - d["year"].iloc[0]),
        })
    ).reset_index()

    africa = growth_by[growth_by["region"] == "Africa"].mean(numeric_only=True)
    asia = growth_by[growth_by["region"] == "Asia"].mean(numeric_only=True)
    gap = asia - africa
    growth_gap = {
        "africa_g_y": float(africa["g_y"]),
        "asia_g_y": float(asia["g_y"]),
        "gap_g_y": float(gap["g_y"]),
        "gap_g_k_contrib": float(alpha * gap["g_k"]),
        "gap_g_h_contrib": float((1-alpha) * gap["g_h"]),
        "gap_g_tfp_contrib": float(gap["g_tfp"]),
        "share_capital": float(alpha * gap["g_k"] / gap["g_y"]) if gap["g_y"] != 0 else None,
        "share_human_capital": float((1-alpha) * gap["g_h"] / gap["g_y"]) if gap["g_y"] != 0 else None,
        "share_tfp": float(gap["g_tfp"] / gap["g_y"]) if gap["g_y"] != 0 else None,
    }
    print(f"  Africa-Asia growth gap decomposition (avg pp/yr):")
    print(f"    Africa avg growth: {africa['g_y']*100:.2f}%")
    print(f"    Asia avg growth:   {asia['g_y']*100:.2f}%")
    print(f"    Gap:               {gap['g_y']*100:.2f}pp")
    if growth_gap["share_tfp"] is not None:
        print(f"    Share from K:      {growth_gap['share_capital']*100:.1f}%")
        print(f"    Share from H:      {growth_gap['share_human_capital']*100:.1f}%")
        print(f"    Share from TFP:    {growth_gap['share_tfp']*100:.1f}%")

    out = {
        "levels": levels,
        "growth_gap": growth_gap,
        "country_growth_rates": growth_by.to_dict("records"),
    }

    print("\n  TFP-on-corruption regression:")
    panel = load_panel().reset_index()
    merged = pwt[["economy", "year", "log_tfp"]].merge(
        panel[["economy", "year", "wgi_cc_inv", "gdp_growth", "inflation", "trade_openness"]],
        on=["economy", "year"], how="inner"
    )
    merged = merged.dropna(subset=["log_tfp", "wgi_cc_inv"])
    merged = merged.set_index(["economy", "year"]).sort_index()
    try:
        mod = PanelOLS(merged["log_tfp"],
                       merged[["wgi_cc_inv", "gdp_growth", "inflation", "trade_openness"]],
                       entity_effects=True, time_effects=True,
                       drop_absorbed=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        tfp_reg = {
            "n_obs": int(res.nobs),
            "coef_wgi_cc_inv": float(res.params["wgi_cc_inv"]),
            "se": float(res.std_errors["wgi_cc_inv"]),
            "t": float(res.tstats["wgi_cc_inv"]),
            "p": float(res.pvalues["wgi_cc_inv"]),
        }
        print(f"    coef={tfp_reg['coef_wgi_cc_inv']:.4f} se={tfp_reg['se']:.4f} "
              f"t={tfp_reg['t']:.2f} p={tfp_reg['p']:.4f} N={tfp_reg['n_obs']}")
        out["tfp_regression"] = tfp_reg
    except Exception as e:
        print(f"    error: {str(e)[:200]}")
        out["tfp_regression"] = {"error": str(e)[:200]}

    (TABLES / "growth_accounting.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def descriptive_stats(df):
    print("\n=== Descriptive statistics ===")
    panel = df.reset_index()
    panel["region"] = panel["economy"].map(
        lambda c: "Africa" if c in AFRICA else ("Asia" if c in ASIA else "LatAm")
    )
    cols = ["wgi_cc_inv", "lending_rate", "spread_bps", "gdp_growth", "inflation"]
    stats = panel.groupby("region")[cols].mean()
    print(stats.to_string())
    stats.to_csv(TABLES / "descriptive_stats.csv")
    return stats


def main():
    df = load_panel()
    pwt = load_pwt()
    descriptive_stats(df)
    panel_results = run_panel_regressions(df)
    did_results = run_event_studies(df)
    ga_results = growth_accounting(pwt)
    print("\nAll results written to:", TABLES)


if __name__ == "__main__":
    main()
