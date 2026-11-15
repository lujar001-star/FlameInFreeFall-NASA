"""Print a quick per-investigation summary of data/tests.csv (sanity check)."""
import csv
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = defaultdict(lambda: {"n": 0, "o2": [], "p": [], "fl": [], "assumed": 0})
for r in csv.DictReader((ROOT / "data" / "tests.csv").open(encoding="utf-8")):
    s = S[r["investigation"]]
    s["n"] += 1
    for key, cols in (("o2", ("o2_min_pct", "o2_max_pct")),
                      ("p", ("pressure_min_atm", "pressure_max_atm")),
                      ("fl", ("flow_min_cm_s", "flow_max_cm_s"))):
        for c in cols:
            try:
                s[key].append(float(r[c]))
            except ValueError:
                pass
    s["assumed"] += bool(r["assumed"])


def rng(v):
    return f"{min(v):.3g}-{max(v):.3g}" if v else "-"


for k, s in S.items():
    print(f"{k:<22}{s['n']:>5}  O2% {rng(s['o2']):<12} P(atm) {rng(s['p']):<12} "
          f"flow {rng(s['fl']):<10} assumed {s['assumed']}")
