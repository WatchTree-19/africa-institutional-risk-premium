# Anti-Corruption Reform Follow-Through Dataset — Codebook

*Companion to the working paper "Does the presence of corruption inhibit a nation's growth prospects?" by Sandeep Rai.*

## Purpose

This dataset operationalises a new institutional-quality variable that the cross-country corruption-and-growth literature has not yet measured: **speed and depth of follow-through after anti-corruption reform.**

Existing measures (CPI, WGI, V-Dem) capture perceived corruption levels but not the institutional functioning of anti-corruption enforcement. The Indonesia-Nigeria contrast in Section 6 demonstrates the gap: both countries established anti-corruption commissions in 2003 with similar nominal forms; only one produced sustained high-profile convictions. The dataset measures that difference directly.

## Inclusion criteria

An "anti-corruption reform event" enters the dataset if it satisfies all four:

1. **Discrete event.** The reform has an identifiable establishment year (founding legislation, agency establishment, or major prosecutorial operation launch). Continuous programmes (e.g. Rwanda's post-1994 institutional rebuild) are coded against a proxy treatment year where the reform consolidated; we flag the proxy assignment.

2. **Formal scope.** The reform establishes or substantially empowers an anti-corruption agency, commission, court, or prosecutorial operation with mandate over national-level corruption (state-level / municipal-level reforms excluded).

3. **Post-1990 establishment.** We restrict to reforms from 1990 onwards to keep within a comparable institutional and global-finance environment, and because reliable contemporary news archives become available.

4. **Data availability for outcome.** At least three years of post-reform sovereign-spread or lending-rate data must exist in our panel or in publicly accessible sources for the country.

## Variables

For each event, we code the following:

| Variable | Definition |
|---|---|
| `event_id` | Short unique identifier (e.g. IDN_KPK_2003) |
| `country` | ISO-3 code |
| `reform_name` | Common name of the reform (e.g. "KPK", "EFCC", "Lava Jato") |
| `reform_year` | Year the reform took effect (year of establishment or year of major prosecutorial launch) |
| `first_conviction_lag_yrs` | Years from `reform_year` to the first sustained conviction of a senior official (cabinet minister, governor, head of state-owned enterprise, or equivalent) under the reform. Censored at 10 years if no qualifying conviction by then. |
| `n_high_profile_convictions_5yr` | Count of sustained convictions of senior officials produced by the reform within five years of `reform_year` |
| `survival_status_10yr` | One of: `intact`, `weakened`, `dismantled` — assessed at year 10 (or 2023 if reform is younger than 10) |
| `lead_prosecutor_tenure_yrs` | Years served by the head of the agency/operation before removal or end of term (0 if never resolved) |
| `political_coalition_stable_5yr` | Binary: did the political coalition that established the reform retain effective control through year 5 (yes/no) |
| `composite_follow_through` | Composite index 0-10. See construction below. |

## "Sustained conviction" definition

A conviction is "sustained" if it satisfies one of the following at the relevant assessment date:

- All appeals exhausted and the conviction was upheld, OR
- The convicted official served substantial custodial time (at least six months), OR
- A formal sanction was applied (asset forfeiture above a threshold, lifetime ban from public office, etc.) that the original political coalition did not subsequently reverse.

Convictions that were later annulled on jurisdictional or procedural grounds (e.g. the 2021 Brazilian Supreme Court annulment of Lula's Lava Jato convictions) are flagged but counted at the time of the original conviction. We discuss the implications.

## Composite follow-through index (0-10)

Constructed from the four core variables. The construction is deliberately simple and pre-specified to avoid post-hoc tuning:

```
composite_follow_through = (
    + 3 * speed_score             # 0 to 3 based on first_conviction_lag_yrs
    + 3 * depth_score             # 0 to 3 based on n_high_profile_convictions_5yr
    + 2 * survival_score          # 0 to 2 based on survival_status_10yr
    + 2 * coalition_score         # 0 to 2 based on political_coalition_stable_5yr
)

speed_score:
    0 if first_conviction_lag_yrs > 7 or censored
    1 if 5 < lag <= 7
    2 if 3 < lag <= 5
    3 if lag <= 3

depth_score:
    0 if n_convictions_5yr == 0
    1 if 1 <= n_convictions_5yr <= 3
    2 if 4 <= n_convictions_5yr <= 7
    3 if n_convictions_5yr >= 8

survival_score:
    0 if dismantled
    1 if weakened
    2 if intact

coalition_score:
    0 if political_coalition_stable_5yr == "no"
    2 if political_coalition_stable_5yr == "yes"
```

Index range: 0 (lowest follow-through) to 10 (highest).

## Source hierarchy

For each coded cell, we use the highest-tier source available and document the source in the dataset notes.

**Tier 1 (primary).** Official court records, agency annual reports, government gazettes.
**Tier 2 (academic).** Peer-reviewed scholarly works on the specific reform.
**Tier 3 (journalistic).** Major international news outlets (Reuters, AP, BBC, FT, Economist, regional flagship newspapers) for reform-event reporting.
**Tier 4 (encyclopaedic).** Wikipedia and reference works, where they cite primary sources.

This is a working-paper dataset coded from publicly accessible sources, principally tier 3 and tier 4. A production version of this dataset would require tier 1 and tier 2 verification for every cell. We flag this as the central limitation of the dataset.

## Limitations

1. **Coding rules are simple.** Real institutional functioning is multidimensional. The four-variable scheme captures the most directly observable dimensions but does not capture sentencing severity, procedural fairness, deterrent effects, or downstream behavioural change.

2. **Source coverage is uneven.** Reforms in countries with strong international press coverage (Brazil, Indonesia, South Korea) have richer documentation than reforms in less-covered countries (Senegal, Zambia). We acknowledge this and flag specific cells with weaker source documentation.

3. **The "high-profile" threshold is judgmental.** A cabinet minister in a small country may not be equivalent to a cabinet minister in a large one. We use a consistent threshold (minister, governor, head of major SOE, or equivalent) but acknowledge that within-country and across-country comparability is imperfect.

4. **Sample size.** Our dataset contains roughly twenty events. Cross-event regression analyses on this sample will have limited statistical power. The contribution is primarily the variable and the conceptual framework; the statistical results are illustrative.

5. **The censoring at ten years matters.** For reforms younger than ten years (or where data ends before year ten), the first-conviction-lag and survival-status variables are right-censored. We report results both including and excluding right-censored cases.

## Citation

If you use this dataset, please cite:

Rai, Sandeep. (2024). Anti-Corruption Reform Follow-Through Dataset, v1.0. Companion to "Does the presence of corruption inhibit a nation's growth prospects?" Working paper.
