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
HABITATS = {
    "ISS / spacecraft cabin": {
        "o2": (20.5, 21.5), "p_atm": (0.97, 1.03), "gravity": "microgravity",
        "note": "Sea-level-like air: 21% O2 at 14.7 psi.",
    },
    "Exploration cabin (Orion/Gateway)": {
        "o2": (26.5, 26.5), "p_atm": (10.2 * PSI_TO_ATM, 10.2 * PSI_TO_ATM), "gravity": "microgravity",
        "note": "Candidate exploration atmosphere: 26.5% O2 at 10.2 psi.",
    },
    "Moon base / pressurized rover": {
        "o2": (30.0, 34.0), "p_atm": (8.2 * PSI_TO_ATM, 10.2 * PSI_TO_ATM), "gravity": "lunar (1/6 g)",
        "note": "30 to 34% O2 at 8.2 to 10.2 psi to shorten spacesuit pre-breathe.",
    },
    "Mars habitat": {
        "o2": (30.0, 34.0), "p_atm": (8.2 * PSI_TO_ATM, 10.2 * PSI_TO_ATM), "gravity": "Martian (3/8 g)",
        "note": "Assumed similar to the Moon-base atmosphere.",
    },
    "Spacesuit": {
        "o2": (100.0, 100.0), "p_atm": (4.3 * PSI_TO_ATM, 4.3 * PSI_TO_ATM), "gravity": "any",
        "note": "100% O2 at 4.3 psi.",
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
O2_SCALE = 8.0     # percentage points at which closeness falls off
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
    out = []
    for r in tests.itertuples():
        if pd.isna(r.o2_min_pct):
            out.append(math.nan)
            continue
        d_o2 = _gap(r.o2_min_pct, r.o2_max_pct, tlo, thi) / O2_SCALE
        if pd.isna(r.pressure_min_atm):
            d_p = 0.5  # unknown pressure: mild penalty
        else:
            d_p = _gap(r.pressure_min_atm, r.pressure_max_atm, plo, phi) / P_SCALE
        c = math.exp(-(d_o2 ** 2 + d_p ** 2))
        if isinstance(r.assumed, str) and r.assumed:
            c *= ASSUMED_WEIGHT
        out.append(c)
    return pd.Series(out, index=tests.index)


def rank(tests: pd.DataFrame, cards: list[dict], habitat: dict,
         pillar_weights: dict | None = None) -> pd.DataFrame:
    """Return one row per investigation with overall score and its components (all 0-100)."""
    pillar_weights = pillar_weights or {"prevention": 1, "detection": 1, "suppression": 1}
    wsum = sum(pillar_weights.values()) or 1
    t = tests.copy()
    t["closeness"] = test_closeness(t, habitat)

    rows = []
    for card in cards:
        sub = t[t["accession"] == card["accession"]]
        n = len(sub)
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
