"""Write docs/verification_bundle.md: everything an outside fact-checker (human or AI) needs in ONE file.

Contains: the insight cards, the website's hard-coded claims (Equipment, Earth, Case Studies text pulled
out of index.html), per-investigation summaries computed from tests.csv, and all 22 original PSI
experiment tables verbatim. Upload this single file instead of many separate ones.

Run: python scripts/build_verification_bundle.py
"""
import json
import pathlib
import re

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "verification_bundle.md"


def js_array(html: str, name: str) -> str:
    """Return the source text of `const NAME = [ ... ];` from index.html."""
    m = re.search(r"const " + name + r" = \[(.*?)\n  \];", html, re.S)
    return m.group(1).strip() if m else f"(array {name} not found)"


def main() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    cards = json.loads((ROOT / "data" / "insights.json").read_text(encoding="utf-8"))
    tests = pd.read_csv(ROOT / "data" / "tests.csv")

    parts = ["# Verification bundle: Spacecraft Fire Safety Data Explorer",
             "",
             "One file for fact-checking. Sections: (1) insight cards, (2) website claims from index.html,",
             "(3) per-investigation numbers computed from tests.csv, (4) all 22 original PSI experiment",
             "tables, verbatim. PSI records: https://psi.nasa.gov/geode-py/ws/repo/investigations/<ACCESSION>",
             ""]

    parts += ["## 1. Insight cards (data/insights.json)", "", "```json",
              json.dumps(cards["investigations"], indent=1, ensure_ascii=False), "```", ""]

    parts += ["## 2. Website claims (from index.html)", ""]
    for name, title in (("EQUIP", "Equipment & Controls cards"), ("EARTH", "Earth Applications cards"),
                        ("CASES", "Case Studies")):
        parts += [f"### {title} (`{name}`)", "",
                  "Values like ${G.solid_max_o2_measured} are filled in from the data at page load "
                  "(solid_max_o2_measured = 22.2, solid_tests = 264).", "", "```js", js_array(html, name), "```", ""]
    gap = re.search(r"getElementById\('gapCallout'\)\.innerHTML = `(.*?)`;", html, re.S)
    if gap:
        parts += ["### Overview gap statement", "", gap.group(1).strip(), ""]

    parts += ["## 3. Numbers computed from tests.csv", "",
              "Units: O2 % by volume, pressure atm, flow cm/s. 'assumed' = filled with ISS cabin air because the "
              "original table does not record it.", "",
              "| Investigation | Accession | Rows | O2 min-max | Pressure min-max (atm) | Flow min-max (cm/s) | Rows with assumed O2 | Rows with assumed pressure |",
              "|---|---|---|---|---|---|---|---|"]
    for (inv, acc), s in tests.groupby(["investigation", "accession"]):
        def rng(a, b, d=2):
            v = pd.concat([s[a], s[b]]).dropna()
            return "-" if v.empty else f"{v.min():.{d}f}-{v.max():.{d}f}"
        a = s["assumed"].fillna("")
        parts.append(f"| {inv} | {acc} | {len(s)} | {rng('o2_min_pct', 'o2_max_pct', 1)} | "
                     f"{rng('pressure_min_atm', 'pressure_max_atm')} | {rng('flow_min_cm_s', 'flow_max_cm_s', 1)} | "
                     f"{a.str.contains('o2').sum()} | {a.str.contains('pressure').sum()} |")
    parts += ["", f"Total rows: {len(tests)}. Solid-material rows: {(tests['fuel_phase'] == 'solid').sum()}; "
              f"highest O2 in a solid row with measured O2: "
              f"{tests[(tests['fuel_phase'] == 'solid') & ~tests['assumed'].fillna('').str.contains('o2')]['o2_max_pct'].max()}%.", ""]

    parts += ["## 4. Original PSI experiment tables (verbatim)", ""]
    for p in sorted((ROOT / "data" / "tables").glob("*.csv")):
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")
        parts += [f"### {p.name}", "", "```csv", text.strip(), "```", ""]

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
