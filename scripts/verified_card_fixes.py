"""Apply corrections from the claim-by-claim check of data/insights.json against the PSI records.

Every insight-card statement was compared with the investigation's PSI record (objectives, approach,
hardware, research impacts) and its experiment table. Statements that PSI does not support were
rewritten to what PSI does say, and each card gets a `verified` note recording the source.
Run once: python scripts/verified_card_fixes.py
"""
import json
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / "data" / "insights.json"
FIX = {
    "PSI-25": {
        "takeaway": "Measured ignition, flame growth, flame spread and extinction limits for realistic solids in low-speed opposed and concurrent flow, at oxygen levels at and below cabin air, to bridge NASA's normal-gravity screening test (NASA-STD-6001 Test 1) and actual flammability in microgravity. PSI notes the results help engineers select the safest materials and improve firefighting methods.",
        "what_varied": ["Material and geometry (films, slabs, rods/cylinders, spherical sections, fabric)", "Flow speed (up to 40 cm/s) and direction (opposed, concurrent)", "Oxygen concentration (lowered below 21% by adding nitrogen; 13.6 to 22.2% in the table)"],
        "held_constant": ["Cabin-like pressure (~1 atm)", "Small wind tunnel in the Microgravity Science Glovebox"],
        "measurements": ["Flame appearance, growth and spread rate from imaging", "Radiometer", "O2, CO2 and CO before and after each burn (table)"],
        "verified": "PSI-25 objectives, approach and research impacts; BASS-II experiment table",
    },
    "PSI-26": {
        "takeaway": "Tested how microgravity flammability of practical solids relates to NASA's normal-gravity screening test and how well nitrogen, an inert extinguishing agent similar to the one used on ISS, puts out flames over different materials, geometries and flows. PSI notes the results feed heat-release models and a performance-based material selection process.",
        "what_varied": ["Material (SIBAL cotton-fiberglass, Nomex, Ultem, PMMA)", "Geometry (fabric strips, spheres, cylinders)", "Flow speed (up to 40 cm/s) and direction (opposed, concurrent)", "Nitrogen suppressant"],
        "held_constant": ["ISS cabin air", "76 mm x 76 mm flow duct in the Microgravity Science Glovebox"],
        "measurements": ["Top- and edge-view video: flame size, shape and color", "Flame spread rate", "Flame quenching"],
        "verified": "PSI-26 objectives, approach and research impacts",
    },
    "PSI-69": {
        "summary": "Burned isolated methanol and heptane droplets to map the flammability limits of liquid fuels and measure how gaseous suppressants (CO2 and helium in the table) change them, over a range of oxygen levels and pressures.",
        "takeaway": "Determined the limiting oxygen index (the lowest oxygen level that sustains burning) as a function of pressure, and how suppressants shift it: the basis for choosing suppressant concentrations in microgravity.",
        "measurements": ["Droplet burning rate and extinction diameter (droplet imaging)", "Flame radiation", "Soot and temperature (stated goals)", "Burn time and how each test ended (table)"],
        "limitations": ["Liquid droplets, not solid cabin materials", "Pressures about 0.7 to 3 atm: no tests at spacesuit pressure"],
        "verified": "PSI-69 objectives and approach; FLEX experiment table",
    },
    "PSI-68": {
        "takeaway": "Benchmark data on how pure and two-component fuel droplets burn and extinguish from 0.5 to 3 atm and up to 30% O2 (the approach cites 10 to 40%), in nitrogen or helium, with slow imposed flow.",
        "measurements": ["Color video of droplet and flame", "Chamber pressure and temperature", "Soot formation (stated objective)"],
        "verified": "PSI-68 objectives and approach; FLEX-2 experiment table",
    },
    "PSI-39": {
        "takeaway": "Cool flames are low-temperature reactions that can continue after the visible flame goes out. CFI mapped their behavior versus pressure, helium dilution and droplet size, which PSI notes provides critical validation for chemical kinetic models and supports the design of safer spacecraft systems.",
        "what_varied": ["Pressure", "O2 (17 to 21%)", "Helium fraction", "Free vs fiber-supported droplets", "Fuel (n-dodecane, iso-dodecane blends)"],
        "measurements": ["Black-and-white camera for droplet size", "UV camera for OH* emission and flame size", "Narrow-band and wide-band radiometers"],
        "verified": "PSI-39 objectives, approach and research impacts; CFI experiment table",
    },
    "PSI-159": {
        "summary": "Gaseous cool flames (ethane, propane, butane in the table) on a spherical porous burner, in normal flames and inverse flames where oxygen-enriched gas up to 85% O2 flows out of the burner. Cool diffusion flames peak at only 500 to 1000 K.",
        "measurements": ["Cameras", "Radiometers", "Photomultiplier tubes", "Thermocouples (burner temperature)"],
        "verified": "PSI-159 objectives, approach and research impacts; CFI-G experiment tables",
    },
    "PSI-10": {
        "summary": "Spherical ethylene flames (methane per the objectives; propane also appears in the table), normal and inverse, to find when flames start producing soot and when they extinguish, across dilution, flow rate and pressure.",
        "takeaway": "Maps soot-inception and extinction limits (radiative or kinetic) of spherical flames versus flow rate, mixture fraction, inert dilution and pressure. Soot governs how much heat a flame radiates.",
        "measurements": ["Cameras", "Radiometers", "Photomultiplier tubes", "Thermocouples"],
        "verified": "PSI-10 objectives and approach; Flame Design experiment tables",
    },
    "PSI-20": {
        "measurements": ["Heat flux sensor", "Burner surface temperature", "Flame observation"],
        "modeling_value": "Burning and extinction conditions expressed in terms of material properties: flammability maps that relate gas-burner flames to condensed (solid) fuels.",
        "verified": "PSI-20 objectives, approach and research impacts; BRE experiment table",
    },
    "PSI-21": {
        "measurements": ["OH* and CH* chemiluminescence imaging (lift-off, flame shape)", "Soot luminosity and laser extinction (soot temperature, volume fraction)", "Thin-filament pyrometry (gas temperature)"],
        "verified": "PSI-21 objectives and approach",
    },
    "PSI-22": {
        "takeaway": "Applying an electric field pushes on the ions in a flame. The challenge brief identifies this as the only way partial gravity was mimicked in PSI data, a stand-in until lunar-gravity combustion data (LUCI, FM2) arrive.",
        "measurements": ["Ion current through the flame", "Flame response time to electric forcing", "Flame imaging and soot behavior"],
        "limitations": ["Analog, not true gravity", "PSI states the work was not conducted to serve space applications; the partial-gravity use comes from the challenge brief", "O2/pressure assumed cabin-like"],
        "verified": "PSI-22 objectives, approach and research impacts; challenge brief",
    },
    "PSI-23": {
        "measurements": ["Spectrally resolved images", "Flame and burner temperatures", "Radiative flux"],
        "verified": "PSI-23 objectives and approach",
    },
    "PSI-98": {
        "summary": "A realistic, large-scale fire: a SIBAL fabric sample about 0.94 m x 0.4 m burned inside an uncrewed Cygnus cargo vehicle after it left the ISS.",
        "takeaway": "Measured how fast a large fire grows in low gravity and compared flammability with NASA's 1-g screening test. In the table, the fabric burned 420 s in concurrent flow versus 70 s in opposed flow.",
        "measurements": ["Two cameras", "Thermocouples (flow, flame and plume temperature)", "Two radiometers", "Pressure, CO2 and O2 sensors", "Two anemometers (flow velocity)"],
        "verified": "PSI-98 objectives, approach and research impacts; SAFFIRE-I table",
    },
    "PSI-99": {
        "takeaway": "Flammability rankings can change between 1-g and microgravity: in the table, thin silicone samples burned completely in 1-g tests but barely at all in microgravity, while SIBAL fabric burned its full 29 cm length in both.",
        "measurements": ["Two cameras", "Thermocouples, two radiometers", "Pressure, CO2 and O2 sensors", "Burn length and spread rate in microgravity and in 1-g (table)"],
        "verified": "PSI-99 objectives and approach; SAFFIRE-II table",
    },
    "PSI-100": {
        "measurements": ["Two cameras", "Thermocouples, two radiometers", "Pressure, CO2 and O2 sensors", "Two anemometers"],
        "verified": "PSI-100 objectives and approach; SAFFIRE-III table",
    },
    "PSI-107": {
        "summary": "Measured the smoke point, the fuel flow at which a jet flame starts releasing soot, for ethylene, propane and propylene mixtures (methane also tested) at three burner diameters and co-flow speeds of 5.4 to 65 cm/s.",
        "takeaway": "Identified when non-buoyant flames begin emitting soot for different fuels, burner sizes and co-flow speeds. PSI notes this improves understanding of soot formation and helps design safer spacecraft environments.",
        "measurements": ["Still and video cameras (flame length, soot emission)", "Radiative heat loss", "Co-flow air velocity"],
        "modeling_value": "469 flame tests with fuel and co-flow rates (smoke points are identified from the imagery); input for soot models.",
        "verified": "PSI-107 objectives, approach and research impacts; SPICE table",
    },
    "PSI-106": {
        "summary": "Studied the structure, stability and liftoff of jet flames in co-flowing air for methane, ethane and ethylene, with nitrogen dilution.",
        "takeaway": "Liftoff velocity limits and flame-base stability in microgravity, which PSI notes give insight into flame stability for fire safety and validate soot and radiation models.",
        "measurements": ["High-resolution still images (4,000+)", "Flow-rate and temperature sensors", "Pyrometry (calibration tests noted in the table)"],
        "modeling_value": "Liftoff limits and flame structure.",
        "verified": "PSI-106 objectives, approach and research impacts; SLICE table",
    },
    "PSI-102": {
        "summary": "Overheated common spacecraft materials (Teflon, Kapton, silicone rubber, lampwick, dibutyl phthalate) to make smoke, then measured the smoke particle sizes in microgravity.",
        "takeaway": "Provides the reduced-gravity smoke baseline against which future spacecraft detector technology is evaluated, including quantitative data on how existing detectors respond to microgravity smoke.",
        "measurements": ["Thermophoretic samplers (particle size by electron microscopy)", "Two smoke detectors (response from video record)", "Sample mass loss", "DustTrak and ionization detector"],
        "verified": "PSI-102 objectives, approach and research impacts; PSI-101 approach",
    },
    "PSI-101": {
        "summary": "Reflight of SAME with a new material (Pyrell foam), higher heating temperatures, a no-flow condition and a new instrument (M-pass). PSI reports 66 flight test points; the table has 109 rows.",
        "takeaway": "Relates smoke particle size to how the smoke was generated and transported (material, heating, flow and aging time): baseline data for advanced spacecraft fire detectors.",
        "measurements": ["Thermal precipitators (particle samples)", "M-pass instrument (new in SAME-R)", "DustTrak and ionization detector"],
        "limitations": ["Cabin air only", "Particle sizes rely on a lognormal distribution assumption (checked in post-flight ground tests)"],
        "verified": "PSI-101 objectives and approach; SAME-R table",
    },
    "PSI-47": {
        "takeaway": "Showed that the modified P-Trak particle counter used by SAME works in microgravity (compared against a DustTrak), which underpins trust in SAME's smoke data. PSI notes it informs instruments for other challenging environments.",
        "measurements": ["Modified TSI P-Trak", "DustTrak (control)"],
        "verified": "PSI-47 objectives, approach and research impacts",
    },
    "PSI-179": {"verified": "PSI-179 objectives, approach and research impacts"},
}


# Round 2 (after an independent AI review): takeaways now separate what PSI says a study was DESIGNED
# to do ("Designed to ...", from objectives/approach) from what PSI REPORTS as a result (research
# impacts written as outcomes) or what the experiment TABLE shows. No unsupported superlatives.
ROUND2 = {
    "PSI-25": "Designed to bridge NASA's normal-gravity screening test (NASA-STD-6001 Test 1) and actual microgravity flammability. Per the PSI approach, flame appearance, growth and spread rates were determined for realistic solids in opposed and concurrent flow up to 40 cm/s, with oxygen lowered below 21%. PSI states the results help engineers select the safest materials and improve firefighting methods.",
    "PSI-26": "Designed to relate the flammability of practical solids in microgravity to NASA's normal-gravity screening test, and to assess nitrogen (an inert agent similar to the one used on ISS) as an extinguishant across materials, geometries and flows. PSI states the results are used in first-order models of heat release and toward a performance-based material selection process.",
    "PSI-98": "Designed to determine how rapidly a large-scale fire grows in low gravity and to compare low-g flammability with NASA's 1-g screening test. In the table, the fabric burned 420 s in concurrent flow versus 70 s in opposed flow.",
    "PSI-99": "In the table, flammability differed between 1-g and microgravity: thin silicone samples burned completely in 1-g tests but barely at all in microgravity, while SIBAL fabric burned its full 29 cm length in both. Designed to compare low-g flammability limits with NASA's 1-g screening test.",
    "PSI-100": "Same objectives as Saffire-I (large-scale fire growth and low-g flammability), repeated at 30 cm/s instead of 20 cm/s in concurrent and opposed flow, giving a second flow speed for large-scale fabric fires.",
    "PSI-69": "Designed to determine the limiting oxygen index (the lowest oxygen level that sustains burning) as a function of pressure, and how suppressants (CO2 and helium in the table) shift it. The table reports burning rate, extinction diameter and burn time for 274 tests: the inputs for choosing suppressant concentrations.",
    "PSI-68": "Designed to provide benchmark data on pure and two-component fuel droplets. The table lists the condition matrix: 0.5 to 3 atm, 17 to 30% O2 (the approach cites 10 to 40%), nitrogen or helium, and slow imposed flow.",
    "PSI-39": "Cool flames are low-temperature reactions. CFI was designed to examine them for n-dodecane and blends from 0.25 to 5 atm, with helium dilution and different droplet sizes; PSI states it provides critical validation for chemical kinetic mechanisms and supports the design of safer spacecraft systems.",
    "PSI-159": "Among the PSI combustion experiment tables, CFI-G spans the widest oxygen range (12 to 85% O2), covering the 30%+ O2 expected in Moon bases and rovers. Designed to determine the conditions under which cool diffusion flames occur.",
    "PSI-10": "Designed to obtain soot-inception and extinction limits (radiative or kinetic) of spherical flames as functions of flow rate, mixture fraction, inert dilution and pressure. The tables list 327 tests with their conditions; soot governs how much heat a flame radiates.",
    "PSI-20": "PSI reports that flames emulating burning PMMA and nylon kept burning steadily with no air flow in elevated-oxygen atmospheres, while similar flames at 21% O2 self-extinguished quickly. Since stopping ventilation is an established step in fighting spacecraft fires, turning off fans alone may not be enough at elevated oxygen. PSI notes these results are still preliminary.",
    "PSI-21": "Designed to provide data for rigorous testing of computational models at the extremes of fuel dilution: flame shape, lift-off height, temperatures, extinction limits and sooting of weak coflow flames.",
    "PSI-22": "Applying an electric field pushes on the ions in a flame. The challenge brief notes that E-FIELD Flames used this effect to mimic partial gravity, making it a partial-gravity analog until lunar-gravity combustion data (LUCI, FM2) arrive.",
    "PSI-23": "Designed to compare transient spherical flame structure and extinction limits with detailed numerical simulations, testing the transport and chemistry models that fire simulation codes rely on.",
    "PSI-107": "Per the PSI approach, fuel flow was adjusted to identify the smoke point (onset of soot emission) of non-buoyant flames for different fuels, burner sizes and co-flow speeds. PSI states this will improve understanding of soot formation and help design safer spacecraft environments.",
    "PSI-106": "Designed to determine liftoff velocity limits and flame-base stability of jet flames in microgravity, and to validate numerical models of flame dynamics, soot and thermal radiation. PSI states the work gives insight into flame stability to enhance fire safety.",
    "PSI-102": "PSI states SAME was intended to provide the reduced-gravity smoke baseline against which future spacecraft detector technology is evaluated, including quantitative data on how existing detectors respond to microgravity smoke.",
    "PSI-101": "Designed, like SAME, to relate smoke particle size to how smoke was generated and transported, with a new material, broader heating conditions and a new instrument. PSI states the results can lead to advanced fire-detector technology for future spacecraft.",
    "PSI-47": "PSI reports the successful adaptation of the P-Trak particle counter (used by SAME) for microgravity, checked against a DustTrak, which underpins trust in SAME's smoke data. PSI notes it informs instruments for other challenging environments.",
    "PSI-179": "PSI states the data can support the design and selection of particle detectors and air filtration suited to low gravity; background cabin aerosol is the 'normal' a smoke detector must distinguish from fire smoke.",
}


# Round 2 wording fixes in other fields: no superlatives or "first" claims that PSI does not state.
ROUND2_FIELDS = {
    "PSI-25": {"habitat_note": "The largest solid-material test set in PSI with varied oxygen (129 tests), but all at or below ~22% O2; extrapolating to 30%+ Moon-base air requires models."},
    "PSI-26": {"summary": "ISS campaign burning practical solid fuels (SIBAL fabric, PMMA, Nomex, Ultem) in the glovebox flow duct, including wake flames and tests of an inert gaseous extinguishing agent."},
    "PSI-98": {"habitat_note": "Realistic, vehicle-scale fire data (together with Saffire-II and -III, the large-scale fire tests in PSI); directly relevant to spacecraft and rover cabin fire scenarios."},
    "PSI-20": {"habitat_note": "Its objectives list NASA's candidate exploration atmospheres, including 34% O2 at 8.2 psia, which is why it ranks first for Moon-base and rover atmospheres in this dashboard."},
    "PSI-102": {"habitat_note": "Applies to any closed habitat, where early smoke detection is critical."},
}


def main() -> None:
    d = json.loads(P.read_text(encoding="utf-8"))
    for c in d["investigations"]:
        c.update(FIX.get(c["accession"], {}))
        c.update(ROUND2_FIELDS.get(c["accession"], {}))
        if c["accession"] in ROUND2:
            c["takeaway"] = ROUND2[c["accession"]]
            if "; reviewed again" not in c.get("verified", ""):
                c["verified"] = c.get("verified", "") + "; reviewed again to separate stated objectives from reported results"
        assert "verified" in c, f"{c['accession']} has no verification note"
    P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Applied fixes to {len(FIX)} cards and {len(ROUND2)} round-2 takeaways; "
          f"all {len(d['investigations'])} cards carry a verification note")


if __name__ == "__main__":
    main()
