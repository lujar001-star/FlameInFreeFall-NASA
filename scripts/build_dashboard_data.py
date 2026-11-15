"""Bundle everything the website needs into one file: data/dashboard.js

The site is plain HTML (no server), so the data ships as a JS file that sets
window.DASH = {...}. That works when opening index.html directly and on GitHub Pages.

Contents:
  investigations - insight cards + stats computed from data/tests.csv + PSI metadata
  habitats       - target atmospheres + per-investigation score components
  tests          - compact per-test rows for the O2 vs pressure chart
  gaps           - data gaps computed from the tests
  ground_studies - PSI ground studies that reuse flight data

Run: python scripts/build_dashboard_data.py   (after build_tests.py)
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scoring import COMPONENT_WEIGHTS, FUEL_RELEVANCE, HABITATS, load_data, test_closeness  # noqa: E402

DATA = ROOT / "data"
PSI_PAGE = "https://psi.nasa.gov/physci/repo/data/investigations/{}"

# Data dictionary for data/tests.csv. role: condition (model input), calculated (design parameter computed
# by the investigators, not measured), result (measured outcome / model output).
VARS = [
    ("fuel", "Fuel / material", "", "condition", "Fuel, fuel mixture or solid material as listed in the PSI table."),
    ("o2_pct", "Oxygen", "% vol", "condition", "Ambient O2 (for ACME inverse flames: O2 in the burner stream)."),
    ("pressure_atm", "Pressure", "atm", "condition", "Chamber or cabin pressure (bar and mmHg converted)."),
    ("flow_cm_s", "Flow speed", "cm/s", "condition", "Imposed air or co-flow speed."),
    ("flow_direction", "Flow direction", "", "condition", "Concurrent or opposed to flame spread (Saffire)."),
    ("co2_pct", "CO2 in atmosphere", "% vol", "condition", "Initial CO2 (FLEX suppressant dilution; BASS-II background)."),
    ("he_pct", "Helium in atmosphere", "% vol", "condition", "Initial helium diluent (FLEX, CFI)."),
    ("size_mm", "Sample / droplet / burner size", "mm", "condition", "Droplet initial diameter, nozzle or burner diameter, or solid sample thickness."),
    ("fuel_flow_mg_s", "Fuel flow rate", "mg/s", "condition", "Gaseous fuel mass flow (SPICE, ACME)."),
    ("aging_time_s", "Smoke aging time", "s", "condition", "Time smoke was aged before measurement (SAME, SAME-R)."),
    ("t_adiabatic_K", "Adiabatic flame temperature", "K", "calculated", "Computed by the investigators from the mixture; not a measurement."),
    ("z_st", "Stoichiometric mixture fraction", "", "calculated", "Computed flame-structure parameter (ACME)."),
    ("ignited", "Ignited", "yes/no/flash", "result", "Whether a hot flame ignited (ACME CFI-G)."),
    ("end_state", "How the test ended", "", "result", "Extinction, burn to completion, disruption, self-extinguished, flow terminated."),
    ("burn_time_s", "Burn time", "s", "result", "Flame duration."),
    ("burning_rate_mm2_s", "Droplet burning rate", "mm²/s", "result", "Burning-rate constant (FLEX; table header reads 'mm')."),
    ("extinction_diam_mm", "Extinction diameter", "mm", "result", "Droplet diameter when the visible flame went out (FLEX)."),
    ("spread_rate_mm_s", "Flame spread rate (microgravity)", "mm/s", "result", "Flame spread over the solid in microgravity (Saffire-II)."),
    ("spread_rate_1g_mm_s", "Flame spread rate (1-g)", "mm/s", "result", "Same material in normal gravity, for comparison (Saffire-II)."),
    ("final_o2_pct", "Final O2", "% vol", "result", "O2 left in the duct after the burn (BASS-II)."),
    ("final_co2_pct", "Final CO2", "% vol", "result", "CO2 after the burn (BASS-II)."),
    ("final_co_ppm", "Final CO", "ppm", "result", "Carbon monoxide after the burn (BASS-II)."),
    ("peak_burner_temp_K", "Peak burner temperature", "K", "result", "Maximum burner surface temperature (ACME CFI-G)."),
    ("cool_flame", "Cool flame observed", "yes/no", "result", "Whether a cool flame was detected (ACME CFI-G normal flames)."),
    ("flames_ignited", "Flames ignited (per test day)", "count", "result", "Number of flames ignited in a day's session (ACME day logs)."),
    ("rt_r0", "Rt/R0", "ratio", "result", "Smoke measurement ratio exactly as reported in the SAME-R table."),
]
NUMERIC_EXPLORER = ["o2_pct", "pressure_atm", "flow_cm_s", "co2_pct", "he_pct", "size_mm", "fuel_flow_mg_s",
                    "aging_time_s", "t_adiabatic_K", "z_st", "burn_time_s", "burning_rate_mm2_s",
                    "extinction_diam_mm", "spread_rate_mm_s", "spread_rate_1g_mm_s", "final_o2_pct",
                    "final_co2_pct", "final_co_ppm", "peak_burner_temp_K", "flames_ignited", "rt_r0"]
CATEGORICAL_EXPLORER = ["fuel", "ignited", "end_state", "flow_direction", "config"]


def with_mid_columns(t):
    """Add single-value o2/pressure/flow columns (midpoint of the min/max range)."""
    t = t.copy()
    for k, a, b in (("o2_pct", "o2_min_pct", "o2_max_pct"), ("pressure_atm", "pressure_min_atm", "pressure_max_atm"),
                    ("flow_cm_s", "flow_min_cm_s", "flow_max_cm_s")):
        t[k] = (t[a] + t[b]) / 2
    return t


RANGE_COLS = {"o2_pct": ("o2_min_pct", "o2_max_pct"), "pressure_atm": ("pressure_min_atm", "pressure_max_atm"),
              "flow_cm_s": ("flow_min_cm_s", "flow_max_cm_s")}


def variable_matrix(t, accessions):
    import pandas as pd
    """Per investigation and variable: how many tests report it and whether it varies."""
    out = {}
    for acc in accessions:
        sub = t[t["accession"] == acc]
        assumed = sub["assumed"].fillna("")
        row = {}
        for key, *_ in VARS:
            col = sub[key].dropna()
            col = col[col.astype(str).str.strip() != ""]
            if col.empty:
                continue
            levels = int(col.astype(str).str.strip().str.lower().nunique())
            if key in RANGE_COLS:  # count both ends of reported ranges (e.g. FLEX-2 "17-30% O2" rows)
                lo, hi = RANGE_COLS[key]
                levels = int(pd.concat([sub[lo], sub[hi]]).dropna().round(4).nunique())
            status = "varied" if levels > 1 else "fixed"
            if key == "o2_pct" and assumed.str.contains("o2").all():
                status = "assumed"
            if key == "pressure_atm" and assumed.str.contains("pressure").all():
                status = "assumed"
            row[key] = {"n": int(len(col)), "levels": levels, "status": status}
        out[acc] = row
    return out


def rng(series):
    s = series.dropna()
    if s.empty:
        return None
    return [round(float(s.min()), 3), round(float(s.max()), 3)]


def main() -> None:
    tests, cards = load_data()
    details = json.loads((DATA / "psi_details.json").read_text(encoding="utf-8"))
    ground = json.loads((DATA / "insights.json").read_text(encoding="utf-8"))["ground_studies"]

    # Rule: anything with numbers (ranking, tables, charts, compare) only includes investigations with
    # experiment-table data. Studies without tables are shipped separately as context.
    has_tests = set(tests["accession"].unique())
    context = [c for c in cards if c["accession"] not in has_tests]
    cards = [c for c in cards if c["accession"] in has_tests]

    invs = []
    for c in cards:
        acc = c["accession"]
        sub = tests[tests["accession"] == acc]
        d = details.get(acc, {})
        measured_o2 = sub[~sub["assumed"].fillna("").str.contains("o2")]
        fuels = sub["fuel"].dropna().astype(str).str.strip()
        invs.append({
            **c,
            "title": d.get("title", c["full_name"]),
            "hardware": d.get("experimentHardware", ""),
            "doi": d.get("doi", ""),
            "psi_url": PSI_PAGE.format(acc),
            "publications": len(d.get("publications") or []),
            "start": d.get("investigationStartDate", ""),
            "end": d.get("investigationEndDate", ""),
            "stats": {
                "tests": int(len(sub)),
                "o2": rng(pd_concat(sub, "o2_min_pct", "o2_max_pct")),
                "o2_measured": bool(len(measured_o2)),
                "pressure": rng(pd_concat(sub, "pressure_min_atm", "pressure_max_atm")),
                "flow": rng(pd_concat(sub, "flow_min_cm_s", "flow_max_cm_s")),
                "fuels": fuels.value_counts().head(6).index.tolist(),
                "assumed_share": round(float((sub["assumed"].fillna("") != "").mean()), 2) if len(sub) else 0,
            },
        })

    habitats = {}
    for name, hab in HABITATS.items():
        close = test_closeness(tests, hab)
        comps = {}
        for c in cards:
            acc = c["accession"]
            known = close[tests["accession"] == acc].dropna()
            n = int((tests["accession"] == acc).sum())
            if len(known):
                best = float(known.max())
                share = float((known > 0.5).mean())
                cond = 0.5 * best + 0.5 * min(1.0, share * 3)
            else:
                best, cond = 0.0, 0.0
            comps[acc] = {
                "conditions": round(cond, 3),
                "best": round(best, 3),
                "matching": int((known > 0.5).sum()),
                "fuel": FUEL_RELEVANCE.get(c["fuel_phase"], 0.5),
                "data": round(min(1.0, math.log10(n + 1) / math.log10(300)) if n else 0.0, 3),
            }
        habitats[name] = {
            "o2": list(hab["o2"]), "p_atm": [round(x, 3) for x in hab["p_atm"]],
            "gravity": hab["gravity"], "note": hab["note"], "weights": hab["weights"], "components": comps,
        }

    # compact test rows for the chart: [accession, name, o2, p, phase, o2_assumed(0/1), fuel, test_id, config]
    name_of = {c["accession"]: c["name"] for c in cards}
    rows = []
    def levels(text):
        return [float(x) for x in str(text).split(";") if x.strip() not in ("", "nan")]

    for r in tests.itertuples():
        if math.isnan(r.o2_min_pct) if isinstance(r.o2_min_pct, float) else False:
            continue
        # rows that list several discrete levels (BRE days, FLEX-2 matrix) become one point per level,
        # instead of a misleading midpoint
        o2s = levels(r.o2_levels_pct) or [(r.o2_min_pct + r.o2_max_pct) / 2]
        no_p = isinstance(r.pressure_min_atm, float) and math.isnan(r.pressure_min_atm)
        ps = levels(r.p_levels_atm) or [None if no_p else (r.pressure_min_atm + r.pressure_max_atm) / 2]
        for o2 in o2s:
            for p in ps:
                rows.append([r.accession, name_of.get(r.accession, r.investigation), round(o2, 2),
                             None if p is None else round(p, 3),
                             r.fuel_phase, int(isinstance(r.assumed, str) and "o2" in r.assumed),
                             str(r.fuel)[:40], str(r.test_id), str(r.config)])

    # computed gaps
    t = tests.copy()
    solid = t[t["fuel_phase"].str.startswith("solid") & ~t["assumed"].fillna("").str.contains("o2")]
    gaps = {
        "solid_max_o2_measured": round(float(solid["o2_max_pct"].max()), 1) if len(solid) else None,
        "solid_tests": int((t["fuel_phase"] == "solid").sum()),
        "tests_at_moon_o2": int(((t["o2_max_pct"] >= 30) & (t["o2_min_pct"] <= 34)).sum()),
        "solid_tests_at_moon_o2": int(((t["fuel_phase"] == "solid") & (t["o2_max_pct"] >= 30)).sum()),
        "tests_total": int(len(t)),
        "max_o2": round(float(t["o2_max_pct"].max()), 1),
        "min_p": round(float(t["pressure_min_atm"].min()), 3),
        "partial_gravity_tests": 0,
    }

    # columnar per-test data for the modeling explorer (numbers rounded to keep the bundle small)
    tm = with_mid_columns(tests)
    ex_cols = ["accession", "test_id", *CATEGORICAL_EXPLORER, *NUMERIC_EXPLORER]
    ex = tm[ex_cols].copy()
    for c in NUMERIC_EXPLORER:
        ex[c] = ex[c].round(4)
    ex = ex.astype(object).where(ex.notna(), None)
    explorer = {"cols": ex_cols, "rows": ex.values.tolist()}

    bundle = {
        "generated_from": "NASA PSI (psi.nasa.gov) experiment tables and investigation records",
        "generated_on": __import__("datetime").date.today().isoformat(),
        "weights": COMPONENT_WEIGHTS,
        "investigations": invs, "habitats": habitats, "tests": rows,
        "gaps": gaps, "ground_studies": ground,
        "variables": [dict(zip(("key", "label", "unit", "role", "desc"), v)) for v in VARS],
        "matrix": variable_matrix(tm, [c["accession"] for c in cards]),
        "explorer": explorer,
        "context_studies": [{**c, "psi_url": PSI_PAGE.format(c["accession"]),
                             "doi": details.get(c["accession"], {}).get("doi", "")} for c in context],
    }
    js = "window.DASH = " + json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (DATA / "dashboard.js").write_text(js, encoding="utf-8")
    print(f"Wrote data/dashboard.js ({len(js):,} bytes): {len(invs)} investigations, {len(rows)} chart points")
    print("Gaps:", gaps)


def pd_concat(sub, a, b):
    import pandas as pd
    return pd.concat([sub[a], sub[b]])


if __name__ == "__main__":
    main()
