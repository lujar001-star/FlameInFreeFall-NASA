# Space Apps 2026 submission draft: Flame in Free Fall

Copy each section into the matching field of the Space Apps project submission form.
Replace anything in [brackets] before submitting.

---

## Project name
Spacecraft Fire Safety Data Explorer

## Team
The Golden Go-figures (University of Minnesota, Aerospace Engineering and Mechanics):
Isaac Fouts (web page developer), Fabian Lujardo (data analyst)

## Link to final project
- Live dashboard: https://lujar001-star.github.io/FlameInFreeFall-NASA/ [works after GitHub Pages is turned on]
- Source code and data: https://github.com/lujar001-star/FlameInFreeFall-NASA
- Demo video: [link]

---

## High-level summary (short field)
NASA's future Moon bases and pressurized rovers are expected to run at 30% oxygen or more, which makes
materials far more flammable, yet two decades of microgravity combustion data in NASA's Physical
Sciences Informatics (PSI) database are hard to find, compare and interpret. Our dashboard pulls every
combustion experiment table in PSI into one cleaned dataset (1,993 tests from 19 investigations,
2,807 measured results), ranks the investigations for the crew environment you are designing
(ISS, exploration atmosphere, Moon base, pressurized rover, Mars habitat, spacesuit), extracts
model-ready data, and turns the research into findings for next-generation fire safety equipment. Its
headline result: none of PSI's 264 solid-material tests (fabrics, plastics) were run above 22.2%
oxygen, so fire safety for the planned Moon-base atmosphere currently rests on extrapolation.

---

## Project details

### What it does
The dashboard answers the three objectives of the challenge:

1. **Which investigations matter for my crew environment?** The Mission Relevance tab ranks all 19
   PSI combustion investigations for six crew environments with a transparent 0-100 score
   (40% match to the target oxygen and pressure, 25% prevention/detection/suppression focus,
   20% fuel realism, 15% amount of data). Every score shows its breakdown, and each environment
   opens with a plain-English summary of the most relevant datasets and the biggest data gap.
2. **What data supports predictive modeling?** The Modeling Data tab provides each test's
   conditions (oxygen, pressure, flow, diluents, sample size, fuel flow) and measured results (burn
   time, droplet burning rate, extinction diameter, ignition, flame spread rate, post-burn O2/CO2/CO,
   burner temperature) in one file with consistent units, a variable matrix showing what each
   investigation varied and measured, an interactive explorer to plot any result against any
   condition, and a data dictionary.
3. **What research informs next-generation controls and equipment?** The Equipment & Controls
   section maps PSI findings to ventilation shutdown, material flammability testing, smoke
   detectors, extinguishing agents, cabin oxygen limits, post-fire atmosphere monitoring and fire
   models, each with its source and remaining gap. For example, ACME BRE reports that flames kept
   burning with ventilation off in elevated-oxygen atmospheres, while similar flames at 21% oxygen
   self-extinguished, so fan shutoff alone may not be enough on a Moon base.

It also includes:
- A **condition map** plotting every test by oxygen and pressure against the habitat targets, with
  search highlighting (e.g. "PMMA", "heptane").
- **Insight cards** for every investigation: objective, what varied and what was held constant,
  sensors, fire-safety takeaway, modeling value, habitat relevance, limitations, PSI link and DOI.
- A **flame lab**: an animated flame with gravity (microgravity, Moon, Mars, Earth), oxygen, pressure
  and airflow sliders that shows how a flame changes, from Earth's flickering yellow teardrop to the
  dim blue sphere of microgravity, and lists the PSI tests that exist near the chosen conditions
  (a qualitative illustration, not a simulation).
- A **Compare** view with a visual chart and a side-by-side table for up to three investigations.
- **Case studies** (Apollo 1, Apollo 13, Mir, ISS 2006, Artemis II, and a lunar rover fire
  scenario) read through the PSI data.
- **Earth applications**: oxygen-enriched fires in hospitals and homes, smoke detectors, clean-agent
  suppression, vehicle material testing, reduced-pressure fires, soot and cool-flame hazards.
- **Ask the data**: a chat assistant that answers questions ("What matters most for a lunar
  rover?", "tests above 30% oxygen", "compare FLEX and BASS-II") by computing answers from the
  dashboard's data and linking to the source.

### How it works
1. Python scripts read NASA PSI's public investigation records and download every combustion
   experiment table (22 CSV files).
2. A cleaning script converts each investigation's own column format into one schema with
   consistent units (mmHg and bar to atm, mole fractions to %, cm thickness to mm).
   - Values a table does not record but that are known from the investigation (e.g. BASS ran in
     ISS cabin air) are filled in and flagged as *assumed*, then shown differently and down-weighted.
   - Physically impossible values (0 atm, 200% O2, negative flows, 0 °C burner temperatures) are
     removed, never guessed, and noted in the row.
3. Insight cards were drafted with AI assistance and then checked claim by claim against each
   investigation's PSI record and table: our own full audit plus two independent AI fact-checks
   (the final one found 0 contradicted claims). Each card states what it was checked against and
   separates what a study was *designed* to do from what PSI *reports* and what the *table* shows.
   A single-file verification bundle (docs/verification_bundle.md) lets anyone repeat the check.
4. The website is a single static page (HTML, CSS, JavaScript with Plotly), so it runs on GitHub
   Pages, opens offline from a file, and needs no server or API key.

### Benefits and intended impact
- **Engineers** designing lunar habitats and rovers get the relevant data for their atmosphere in
  minutes, with the gaps stated plainly.
- **Researchers** get a clean, documented, citable dataset of microgravity combustion conditions and
  results to validate fire models, plus a map of which experiments are missing (solid materials
  above 22% oxygen, partial gravity, vehicle-scale fires at elevated oxygen).
- **Mission planners** see why upcoming experiments such as FM2 and LUCI matter.
- **On Earth**, the same data informs oxygen-enriched hospital fire safety, smoke detection and
  clean-agent suppression.

### Tools and technologies
Python (pandas), HTML/CSS/JavaScript, Plotly.js, GitHub and GitHub Pages, NASA PSI public data
interface.

---

## Use of artificial intelligence
- **Claude (Anthropic):** helped write the data pipeline and website code, draft the insight cards,
  and review data quality. The team directed the work and reviewed the results. Every insight-card
  statement was then checked against the PSI records and tables, and unsupported statements were
  rewritten or removed.
- **Gemini (Google):** used as an independent reviewer to fact-check the insight cards against PSI.
- **ChatGPT (OpenAI):** created the team logo.
- The dashboard's "Ask the data" assistant does **not** use an AI service: it is rule-based and
  computes answers from the dashboard's data.

---

## NASA data used
NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov: investigation records and experiment
tables for all combustion investigations with experiment tables (license CC0):

ACME Flame Design (PSI-10), ACME BRE (PSI-20), ACME CLD Flame (PSI-21), ACME E-FIELD Flames (PSI-22),
ACME s-Flame (PSI-23), BASS-II (PSI-25), BASS (PSI-26), CFI (PSI-39), DAFT/DAFT-2 (PSI-47),
FLEX-2 (PSI-68), FLEX (PSI-69), SAFFIRE-I (PSI-98), SAFFIRE-II (PSI-99), SAFFIRE-III (PSI-100),
SAME-R (PSI-101), SAME (PSI-102), SLICE (PSI-106), SPICE (PSI-107), ACME CFI-G (PSI-159).

Context only (no experiment table): ASE (PSI-179) and the PSI ground studies PSI-60, PSI-62, PSI-115,
PSI-117 and PSI-142. Each investigation's DOI is listed on the dashboard's Data & Methods tab.

## Space agency partner data
None used.

## References
- NASA Physical Sciences Informatics database and investigation records (DOIs on the Data & Methods tab)
- NASA Space Apps Challenge 2026, "Flame in Free Fall" challenge brief and resources
- Historical case studies summarize widely published NASA accounts of Apollo 1, Apollo 13, the 1997 Mir
  fire and the 2006 ISS Elektron event; the Artemis II entry uses only the challenge brief.
