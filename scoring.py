"""Habitat relevance scoring for PSI combustion investigations.

Usage from the Streamlit app:
    from scoring import HABITATS, load_data, rank
    tests, cards = load_data()
    df = rank(tests, cards, HABITATS["Moon base / pressurized rover"])

Every score is a transparent weighted sum of four 0-1 components, and the breakdown is
returned so the dashboard can show *why* an investigation ranks where it does.
"""
from __future__ import annotations

import json
import math
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"

PSI_TO_ATM = 1 / 14.696

# Target crew atmospheres. Ranges where NASA gives a band rather than a single value.
MOON_O2 = (30.0, 34.0)
MOON_P = (8.2 * PSI_TO_ATM, 10.2 * PSI_TO_ATM)

# Target crew atmospheres. Ranges where NASA gives a band rather than a single value.
# `weights` are the default pillar weights (prevention, detection, suppression) for that environment;
# users can change them on the site. They encode what dominates fire risk there, and say why.
HABITATS = {
    "ISS / spacecraft cabin": {
        "o2": (20.5, 21.5), "p_atm": (0.97, 1.03), "gravity": "microgravity", "label": "21% O₂ · 14.7 psi",
        "weights": {"prevention": 1, "detection": 1, "suppression": 1},
        "note": "Sea-level-like air: 21% O2 at 14.7 psi. Most existing PSI data was taken in these conditions.",
    },
    "Exploration atmosphere": {
        "o2": (26.5, 26.5), "p_atm": (10.2 * PSI_TO_ATM, 10.2 * PSI_TO_ATM), "gravity": "microgravity",
        "weights": {"prevention": 2, "detection": 1, "suppression": 1},
        "note": "NASA's candidate exploration atmosphere of 26.5% O2 at 10.2 psi (as listed in the ACME BRE "
                "objectives), considered for vehicles that support frequent spacewalks.",
    },
    "Moon base": {
        "o2": MOON_O2, "p_atm": MOON_P, "gravity": "lunar (1/6 g)",
        "weights": {"prevention": 2, "detection": 1, "suppression": 1},
        "note": "30 to 34% O2 at 8.2 to 10.2 psi to shorten spacesuit pre-breathe. Oxygen-enriched air makes "
                "material selection (prevention) the first line of defence.",
    },
    "Pressurized rover": {
        "o2": MOON_O2, "p_atm": MOON_P, "gravity": "lunar (1/6 g)",
        "weights": {"prevention": 2, "detection": 2, "suppression": 2},
        "note": "Same oxygen-enriched air as the Moon base, but a small cabin far from the base: smoke and heat "
                "build up within minutes and there is little room to retreat, so early detection and fast "
                "suppression weigh as much as prevention. The atmosphere match is identical to the Moon base; "
                "the gap specific to rovers is that the only vehicle-scale fire data (Saffire) was taken at 21% O2.",
    },
    "Mars habitat": {
        "o2": MOON_O2, "p_atm": MOON_P, "gravity": "Martian (3/8 g)",
        "weights": {"prevention": 2, "detection": 1, "suppression": 1},
        "note": "Assumed similar to the Moon-base atmosphere.",
    },
    "Spacesuit": {
        "o2": (100.0, 100.0), "p_atm": (4.3 * PSI_TO_ATM, 4.3 * PSI_TO_ATM), "gravity": "any",
        "weights": {"prevention": 3, "detection": 0, "suppression": 0},
        "note": "100% O2 at 4.3 psi. There is no practical way to detect or fight a fire inside a suit, so only "
                "prevention (ignition and material control) applies.",
    },
}

FUEL_RELEVANCE = {  # how directly a fuel type represents cabin fire hazards
    "solid": 1.0,
    "gas (solid emulator)": 0.9,
    "solid (smoke source)": 0.8,
    "liquid": 0.6,
    "gas": 0.5,
    "aerosol (dust)": 0.4,
    "aerosol (cabin)": 0.3,
}

COMPONENT_WEIGHTS = {"conditions": 0.40, "safety_focus": 0.25, "fuel": 0.20, "data": 0.15}
O2_SCALE = 5.0     # percentage points at which closeness falls off
P_SCALE = 0.25     # atm at which closeness falls off
ASSUMED_WEIGHT = 0.7  # assumed (not measured) conditions count for less


def load_data() -> tuple[pd.DataFrame, list[dict]]:
    tests = pd.read_csv(DATA / "tests.csv")
    cards = json.loads((DATA / "insights.json").read_text(encoding="utf-8"))["investigations"]
    return tests, cards


def _gap(lo: float, hi: float, tlo: float, thi: float) -> float:
    """Distance between interval [lo,hi] and target interval [tlo,thi] (0 if they overlap)."""
    if hi < tlo:
        return tlo - hi
    if lo > thi:
        return lo - thi
    return 0.0


def test_closeness(tests: pd.DataFrame, habitat: dict) -> pd.Series:
    """0-1 closeness of each test's O2/pressure to the habitat target. NaN if O2 unknown."""
    (tlo, thi), (plo, phi) = habitat["o2"], habitat["p_atm"]
    def levels(text):
        return [float(x) for x in str(text).split(";") if x.strip() not in ("", "nan")]

    out = []
    for r in tests.itertuples():
        if pd.isna(r.o2_min_pct):
            out.append(math.nan)
            continue
        # Rows that list discrete levels (ACME BRE days, FLEX-2 matrix) are scored on the levels actually
        # tested, not on the min-max range (a day testing "21; 26.5; 40" did not test 30-34%).
        o2s = levels(getattr(r, "o2_levels_pct", "")) or None
        ps = levels(getattr(r, "p_levels_atm", "")) or None
        o2_gaps = [_gap(v, v, tlo, thi) for v in o2s] if o2s else [_gap(r.o2_min_pct, r.o2_max_pct, tlo, thi)]
        if pd.isna(r.pressure_min_atm):
            p_gaps = [None]  # unknown pressure: mild penalty
        else:
            p_gaps = [_gap(v, v, plo, phi) for v in ps] if ps else [_gap(r.pressure_min_atm, r.pressure_max_atm, plo, phi)]
        c = max(math.exp(-((go / O2_SCALE) ** 2 + (0.5 if gp is None else gp / P_SCALE) ** 2))
                for go in o2_gaps for gp in p_gaps)
        if isinstance(r.assumed, str) and r.assumed:
            c *= ASSUMED_WEIGHT
        out.append(c)
    return pd.Series(out, index=tests.index)


def rank(tests: pd.DataFrame, cards: list[dict], habitat: dict,
         pillar_weights: dict | None = None) -> pd.DataFrame:
    """Return one row per investigation with overall score and its components (all 0-100)."""
    pillar_weights = pillar_weights or habitat.get("weights") or {"prevention": 1, "detection": 1, "suppression": 1}
    wsum = sum(pillar_weights.values()) or 1
    t = tests.copy()
    t["closeness"] = test_closeness(t, habitat)

    rows = []
    for card in cards:
        sub = t[t["accession"] == card["accession"]]
        n = len(sub)
        if n == 0:
            continue  # context-only study (no experiment table): not ranked
        known = sub["closeness"].dropna()
        if len(known):
            best = known.max()
            share = (known > 0.5).mean()
            conditions = 0.5 * best + 0.5 * min(1.0, share * 3)
        else:
            best, share, conditions = 0.0, 0.0, 0.0

        focus = sum(pillar_weights[p] * card["pillars"].get(p, 0) / 3 for p in pillar_weights) / wsum
        fuel = FUEL_RELEVANCE.get(card["fuel_phase"], 0.5)
        data = min(1.0, math.log10(n + 1) / math.log10(300)) if n else 0.0

        comps = {"conditions": conditions, "safety_focus": focus, "fuel": fuel, "data": data}
        score = sum(COMPONENT_WEIGHTS[k] * v for k, v in comps.items())

        why = []
        if best > 0.8:
            why.append("has tests matching this atmosphere")
        elif best > 0.4:
            why.append("has tests near this atmosphere")
        else:
            why.append("tested far from this atmosphere")
        if fuel >= 0.9:
            why.append("realistic solid-material fire hazard")
        top_pillar = max(card["pillars"], key=card["pillars"].get)
        why.append(f"strongest on {top_pillar}")

        rows.append({
            "accession": card["accession"], "investigation": card["name"],
            "family": card["family"], "fuel_phase": card["fuel_phase"], "tests": n,
            "score": round(100 * score, 1),
            **{k: round(100 * v, 1) for k, v in comps.items()},
            "matching_tests": int((known > 0.5).sum()),
            "why": "; ".join(why),
        })
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    tests, cards = load_data()
    for name, hab in HABITATS.items():
        print(f"\n=== {name} ===")
        print(rank(tests, cards, hab)[["investigation", "score", "conditions", "safety_focus",
                                       "fuel", "data", "matching_tests"]].head(8).to_string(index=False))
