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


def main() -> None:
    d = json.loads(P.read_text(encoding="utf-8"))
    for c in d["investigations"]:
        c.update(FIX.get(c["accession"], {}))
        assert "verified" in c, f"{c['accession']} has no verification note"
    P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Applied fixes to {len(FIX)} cards; all {len(d['investigations'])} cards carry a verification note")


if __name__ == "__main__":
    main()
