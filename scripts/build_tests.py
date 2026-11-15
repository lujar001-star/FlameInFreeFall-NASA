"""Normalize every PSI experiment table into one common table: data/tests.csv

Each investigation's CSV has its own columns, so each gets a small handler that maps its rows
into the shared schema below. Values the table does not record but that are known from the
investigation description (e.g. BASS ran in ISS cabin air) are filled in and flagged in
`assumed` so the dashboard can show them differently from measured values.

Run: python scripts/build_tests.py
"""
import csv
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "tables"
OUT = ROOT / "data" / "tests.csv"

FIELDS = [
    "accession", "investigation", "test_id", "fuel", "fuel_phase", "config",
    "o2_min_pct", "o2_max_pct", "pressure_min_atm", "pressure_max_atm",
    "flow_min_cm_s", "flow_max_cm_s", "diluent", "sample_size", "outcome",
    "gravity", "assumed", "notes",
]

ISS_AIR_O2 = 21.0
ISS_P_ATM = 1.0


# ---------- parsing helpers ----------
def read(name: str) -> list[dict]:
    raw = (TABLES / name).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]]
    out = []
    for r in rows[1:]:
        if not any(c.strip() for c in r):
            continue
        out.append({header[i]: (r[i].strip() if i < len(r) else "") for i in range(len(header))})
    return out


NUM = re.compile(r"-?\d*\.?\d+")


def nums(text: str) -> list[float]:
    """All numbers in a string. '3400%' style Excel artifacts are rescaled to percent."""
    if text is None:
        return []
    vals = []
    for m in NUM.findall(str(text).replace(",", "")):
        try:
            vals.append(float(m))
        except ValueError:
            pass
    if str(text).strip().endswith("%") and vals and vals[0] > 100:
        vals = [v / 100 for v in vals]
    return vals


def span(text: str, scale: float = 1.0) -> tuple:
    v = nums(text)
    if not v:
        return "", ""
    return round(min(v) * scale, 4), round(max(v) * scale, 4)


def one(text: str, scale: float = 1.0):
    v = nums(text)
    return round(v[0] * scale, 4) if v else ""


def row(**kw) -> dict:
    base = {f: "" for f in FIELDS}
    base["gravity"] = "microgravity (ISS)"
    base.update({k: v for k, v in kw.items() if v is not None})
    return base


def cabin(r: dict, notes_assumed: str = "O2 and pressure = ISS cabin air") -> dict:
    """Fill missing O2/pressure with ISS cabin air and flag it."""
    flags = []
    if r["o2_min_pct"] == "":
        r["o2_min_pct"] = r["o2_max_pct"] = ISS_AIR_O2
        flags.append("o2")
    if r["pressure_min_atm"] == "":
        r["pressure_min_atm"] = r["pressure_max_atm"] = ISS_P_ATM
        flags.append("pressure")
    if flags:
        r["assumed"] = ";".join(filter(None, [r["assumed"], *flags]))
    return r


# ---------- per-investigation handlers ----------
def flex():
    out = []
    for r in read("PSI-69_Experimental table_FLEX.csv"):
        o2 = one(r.get("O initial ambient composition; mole fraction"), 100)
        p = one(r.get("Ambient pressure; mmHg"), 1 / 760)
        co2 = one(r.get("CO initial ambient composition; mole fraction"))
        he = one(r.get("He initial ambient composition; mole fraction"))
        dil = ["N2"] + (["CO2"] if co2 not in ("", 0) else []) + (["He"] if he not in ("", 0) else [])
        out.append(row(
            accession="PSI-69", investigation="FLEX", test_id=r.get("FLEX Identifier"),
            fuel=r.get("Fuel"), fuel_phase="liquid", config="droplet (MDCA)",
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p,
            diluent="+".join(dil),
            sample_size=f"droplet {r.get('Droplet initial diameter; mm')} mm",
            outcome=r.get("Test end", ""),
            notes=f"CO2 frac {co2}; He frac {he}; burn time {r.get('Burn time; s')} s",
        ))
    return out


def flex2():
    out = []
    for r in read("PSI-68_Experimental table_Flex2.csv"):
        o2 = span(r.get("Oxygen Mole Fraction"), 100)
        p = span(r.get("Ambient Pressure (atm)"))
        f = span(r.get("Flow Velocity (cm/s)"))
        out.append(row(
            accession="PSI-68", investigation="FLEX-2", test_id="matrix",
            fuel=r.get("Sample (Fuel Type)"), fuel_phase="liquid", config="droplet (MDCA)",
            o2_min_pct=o2[0], o2_max_pct=o2[1], pressure_min_atm=p[0], pressure_max_atm=p[1],
            flow_min_cm_s=f[0], flow_max_cm_s=f[1], diluent=r.get("Ambient Gas Mixture"),
            sample_size=f"droplet {r.get('Initial Droplet Diameter (mm)')} mm",
            notes="Test-matrix summary row (range of conditions), not a single test",
        ))
    return out


def cfi():
    out = []
    for r in read("PSI-39_Experimental table_CFI.csv"):
        o2 = one(r.get("Oxygen"), 100)
        p = one(r.get("Pressure"))
        he = one(r.get("Helium"))
        out.append(row(
            accession="PSI-39", investigation="CFI", test_id=r.get("CIR") or r.get("Flex Number"),
            fuel=r.get("Fuel"), fuel_phase="liquid",
            config="droplet (MDCA)" + (", fiber-supported" if r.get("Fiber", "").lower() == "yes" else ""),
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p,
            diluent="N2" + ("+He" if he not in ("", 0) else ""),
        ))
    return out


def bass():
    out = []
    for r in read("PSI-26_Experimental table_BASS.csv"):
        out.append(cabin(row(
            accession="PSI-26", investigation="BASS", test_id=r.get("As Run Test #"),
            fuel=r.get("Fuel Sample Material"), fuel_phase="solid", config="flat/rod sample in flow duct (MSG)",
            diluent="N2 (air)",
        )))
    return out


def bass2():
    out = []
    for r in read("PSI-25_Experimental table_BASS-II.csv"):
        o2 = one(r.get("Calibrated  initial O2 % by vol"))
        out.append(cabin(row(
            accession="PSI-25", investigation="BASS-II", test_id=r.get("Test #"),
            fuel=r.get("Fuel Sample Material"), fuel_phase="solid", config="flat/rod sample in flow duct (MSG)",
            o2_min_pct=o2, o2_max_pct=o2, diluent="N2 (air)",
            notes=f"Fan display {r.get('Fan display')}; flow restrictor {r.get('Flow restrictor')}; "
                  f"final O2 {r.get('Calibrated final O2 % by vol')}%",
        )))
    return out


def saffire(acc, name, file):
    out = []
    for r in read(file):
        sid = r.get("Sample Number", "")
        if not sid or "Note" in sid or sid.startswith("F"):
            continue
        o2 = span(r.get("Percent O2") or r.get("Percent O2 (Note 1)") or "")
        flow = one(r.get("Air Flow (cm/s)") or r.get("Air Flow") or "")
        thick = r.get("Sample Thickness (cm)") or r.get("Sample Thickness") or r.get("Samle Thickness") or ""
        length = r.get("Sample Length (cm)") or r.get("Sample Length") or ""
        width = r.get("Sample Width (cm)") or r.get("Sample Width") or ""
        out.append(cabin(row(
            accession=acc, investigation=name, test_id=sid,
            fuel=r.get("Material") or "(see previous)", fuel_phase="solid",
            config="large sample, " + (r.get("Flow Direction") or r.get("Direction") or "").strip().lower() + " flow (Cygnus)",
            o2_min_pct=o2[0], o2_max_pct=o2[1], flow_min_cm_s=flow, flow_max_cm_s=flow,
            diluent="N2 (air)", sample_size=f"thick {thick}; L {length}; W {width}",
            outcome=f"burn time {r.get('Burn Time (s)', '')}",
            gravity="microgravity (Cygnus vehicle)",
        )))
    return out


def same():
    out = []
    for r in read("PSI-102_Experimental table_SAME.csv"):
        out.append(cabin(row(
            accession="PSI-102", investigation="SAME", test_id=r.get("Sample #"),
            fuel=r.get("Sample Material"), fuel_phase="solid (smoke source)", config="heated sample, smoke aging (MSG)",
            flow_min_cm_s=one(r.get("Air Flow (cm/s)")), flow_max_cm_s=one(r.get("Air Flow (cm/s)")),
            diluent="N2 (air)",
            notes=f"weight loss {r.get('Weight loss rate (mg/min)')} mg/min; aging {r.get('Aging Duration (minutes)')} min",
        )))
    return out


def same_r():
    out = []
    for r in read("PSI-101_Experimental table_SAME-R.csv"):
        v = one(r.get("Inlet velocity (cm/s)"))
        out.append(cabin(row(
            accession="PSI-101", investigation="SAME-R", test_id=r.get("SAME Test #"),
            fuel=r.get("Sample Type"), fuel_phase="solid (smoke source)", config="heated sample, smoke aging (MSG)",
            flow_min_cm_s=v, flow_max_cm_s=v, diluent="N2 (air)",
            notes=f"{r.get('Description')}; duration {r.get('Duration (sec)')} s",
        )))
    return out


def daft():
    out = []
    for r in read("PSI-47_Experimental table_DAFT.csv"):
        out.append(cabin(row(
            accession="PSI-47", investigation="DAFT / DAFT-2", test_id=r.get("Session Name"),
            fuel=r.get("Sample Material")[:80], fuel_phase="aerosol (dust)", config="particle counter (P-Trak) in cabin",
            notes=r.get("Hardware Description"),
        )))
    return out


def spice():
    out = []
    for r in read("PSI-107_Experimental table_Spice.csv"):
        if not r.get("Fuel"):
            continue
        a = one(r.get("Air Rate (cm/s)"))
        out.append(cabin(row(
            accession="PSI-107", investigation="SPICE", test_id=f"{r.get('GMT date')}-{r.get('GMT ignition')}",
            fuel=r.get("Fuel"), fuel_phase="gas", config="co-flow jet flame, fan-driven duct (MSG)",
            flow_min_cm_s=a, flow_max_cm_s=a, diluent="N2 (air)",
            sample_size=f"nozzle {r.get('Nozzle (mm)')} mm",
            notes=f"fuel rate {r.get('Fuel Rate (mg/s)')} mg/s",
        )))
    return out


def slice_():
    out = []
    for r in read("PSI-106_Experimental table_Slice.csv"):
        out.append(cabin(row(
            accession="PSI-106", investigation="SLICE", test_id=r.get("Test Date", "")[:11].strip(),
            fuel=r.get("Fuel Type"), fuel_phase="gas", config="co-flow jet flame, fan-driven duct (MSG)",
            diluent="N2 (air)",
        )))
    return out


def acme_bre():
    out = []
    for r in read("PSI-20_Experimental table_ACME BRE.csv"):
        raw = r.get("Oxygen Conc (percent)", "")
        o2 = nums(raw)
        o2 = [v / 100 if v > 100 else v for v in o2]
        out.append(row(
            accession="PSI-20", investigation="ACME BRE", test_id=f"{r.get('Year')}-{r.get('Month')}-{r.get('Date')}",
            fuel=r.get("Fuel Bottle"), fuel_phase="gas (solid emulator)", config="porous burner emulating burning solid (CIR)",
            o2_min_pct=min(o2) if o2 else "", o2_max_pct=max(o2) if o2 else "",
            diluent="N2", sample_size=f"burner {r.get('Burner Size (mm)')} mm",
            outcome=f"{r.get('Flames Ignited')} flames ignited",
            assumed="", notes="Pressure varied but not listed in table",
        ))
    return out


def acme_daylog(acc, name, file, config):
    out = []
    for r in read(file):
        atm = r.get("Atmosphere", "") or r.get("Atmosphere*", "")
        pct = [float(x) for x in re.findall(r"(\d+\.?\d*)\s*%", atm)]  # "~21% O2" -> 21, ignores "O2"
        o2 = (min(pct), max(pct)) if pct and "O2" in atm else ("", "")
        rr = row(
            accession=acc, investigation=name, test_id=r.get("Test Day") or r.get("Test Day*"),
            fuel=r.get("Fuel Bottle"), fuel_phase="gas", config=config,
            o2_min_pct=o2[0], o2_max_pct=o2[1],
            outcome=f"{r.get('Flames ignited') or r.get('Flames Ignited') or r.get('Flames Ignited*')} flames ignited",
            notes=(r.get("Test Type", "") + ("; mesh " + r["Mesh Polarity"] if r.get("Mesh Polarity") else "")),
        )
        out.append(cabin(rr) if rr["o2_min_pct"] == "" and acc != "PSI-21" else rr)
    return out


def flame_design():
    out = []
    for r in read("PSI-10_Experimental table_Flame Design_Normal Flame.csv"):
        o2 = one(r.get("XO2 (init)"), 100)
        p = one(r.get("pmean (atm)"))
        out.append(row(
            accession="PSI-10", investigation="ACME Flame Design", test_id=r.get("Test"),
            fuel=r.get("Fuel"), fuel_phase="gas", config="spherical burner, normal flame (CIR)",
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p, diluent="N2",
            notes=f"Tad {r.get('Tad (K)')} K; Zst {r.get('mean Zst')}",
        ))
    for r in read("PSI-10_Experimental table_Flame Design_Inverse Flame.csv"):
        o2 = one(r.get("XO2"), 100)
        p = one(r.get("pmean (atm)"))
        out.append(row(
            accession="PSI-10", investigation="ACME Flame Design", test_id=r.get("Test"),
            fuel="C2H4 (ambient)", fuel_phase="gas", config="spherical burner, inverse flame (CIR)",
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p, diluent="N2",
            notes=f"O2 issues from burner; Tad {r.get('Tad (K)')} K",
        ))
    return out


def cfi_g():
    out = []
    for r in read("PSI-159_Experimental table_CFI-G_Normal Flames.csv"):
        o2 = one(r.get("XO2 before test"), 100)
        p = one(r.get("approx p (bar)"), 1 / 1.01325)
        out.append(row(
            accession="PSI-159", investigation="ACME CFI-G", test_id=r.get("Test"),
            fuel=r.get("Fuel"), fuel_phase="gas", config="spherical burner, normal flame (CIR)",
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p, diluent="N2",
            outcome=f"cool flame: {r.get('Cool flame?') or 'n/a'}; hot ignition: {r.get('Hot ignition')}; "
                    f"{r.get('Self-ext or flow term')}",
            notes=r.get("Comments", ""),
        ))
    for r in read("PSI-159_Experimental table_CFI-G_Inverse Flames.csv"):
        o2 = one(r.get("XO2"), 100)
        p = one(r.get("approx p (bar)"), 1 / 1.01325)
        out.append(row(
            accession="PSI-159", investigation="ACME CFI-G", test_id=r.get("Test"),
            fuel=f"{r.get('Fuel')} (ambient)", fuel_phase="gas", config="spherical burner, inverse flame (CIR)",
            o2_min_pct=o2, o2_max_pct=o2, pressure_min_atm=p, pressure_max_atm=p, diluent="N2",
            outcome=f"hot ignition: {r.get('Hot ignition')}; {r.get('Self -ext or flow term')}",
            notes=f"O2 issues from burner; {r.get('Comments', '')}",
        ))
    return out


HANDLERS = [
    flex, flex2, cfi, bass, bass2,
    lambda: saffire("PSI-98", "SAFFIRE-I", "PSI-98_Experimental table_SAFFIRE-1.csv"),
    lambda: saffire("PSI-99", "SAFFIRE-II", "PSI-99_Experimental table_SAFFIRE-2.csv"),
    lambda: saffire("PSI-100", "SAFFIRE-III", "PSI-100_Experimental table_SAFFIRE-3.csv"),
    same, same_r, daft, spice, slice_, acme_bre,
    lambda: acme_daylog("PSI-21", "ACME CLD Flame", "PSI-21_Experimental table_CLD Flame.csv",
                        "co-flow laminar diffusion flame (CIR)"),
    lambda: acme_daylog("PSI-22", "ACME E-FIELD Flames", "PSI-22_Experimental table_ACME E-FIELD Flames.csv",
                        "co-flow flame in electric field, partial-g analog (CIR)"),
    lambda: acme_daylog("PSI-23", "ACME s-Flame", "PSI-23_Experimental table_ACME s-Flame.csv",
                        "spherical burner (CIR)"),
    flame_design, cfi_g,
]


def validate(r: dict) -> dict:
    """Blank out physically impossible values (typos/sensor offsets) rather than guess."""
    bad = []

    def num(c):
        try:
            return float(r[c])
        except (ValueError, TypeError):
            return None

    for c in ("o2_min_pct", "o2_max_pct"):
        v = num(c)
        if v is not None and not (0 < v <= 100):
            bad.append(f"{c}={r[c]}")
            r[c] = ""
    for c in ("pressure_min_atm", "pressure_max_atm"):
        v = num(c)
        if v is not None and v <= 0:
            bad.append(f"{c}={r[c]}")
            r[c] = ""
    for c in ("flow_min_cm_s", "flow_max_cm_s"):
        v = num(c)
        if v is not None and v < 0:
            bad.append(f"{c}={r[c]}")
            r[c] = ""
    if bad:
        r["notes"] = (r["notes"] + "; " if r["notes"] else "") + "removed invalid: " + ", ".join(bad)
    return r


def main() -> None:
    rows = []
    for h in HANDLERS:
        got = [validate(r) for r in h()]
        rows.extend(got)
        if got:
            print(f"{got[0]['investigation']:<22} {len(got):>5} rows")
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
