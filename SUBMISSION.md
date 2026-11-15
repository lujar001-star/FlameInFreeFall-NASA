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

---

## Demo video script (about 2 minutes)

Check the form's video length limit first; if it is 30 seconds, use the short script below.
Setup: open the site, start on Overview, browser full screen, zoom 110-125% so text is readable.
Speak at a relaxed pace; about 300 words fits 2 minutes.

| Time | On screen (what to click) | Narration (what to say) |
|---|---|---|
| 0:00-0:15 | Overview: hero, then scroll to the red key numbers | "NASA plans Moon bases and pressurized rovers with 30% oxygen or more, which makes materials far more flammable. Two decades of microgravity fire experiments sit in NASA's PSI database, but they're hard to find, compare and interpret. We built the Spacecraft Fire Safety Data Explorer to fix that." |
| 0:15-0:30 | Point at the 1,993 / 22.2% / 0 stats and the red "Critical gap" box | "We pulled every PSI combustion experiment table into one cleaned dataset: nearly two thousand tests from 19 investigations. And the data shows a gap: none of the 264 solid-material tests, the fabrics and plastics that actually fill a cabin, were run above 22% oxygen." |
| 0:30-0:55 | Explore the data → Mission Relevance → click Moon base, then Pressurized rover; hover the score breakdown | "Objective one: which research matters for your crew environment? Pick a habitat and every investigation is ranked with a transparent score: how close its tests are to that oxygen and pressure, its safety focus, fuel realism and amount of data. For a Moon base, the top dataset is ACME BRE, which tested 34% oxygen. The summary also states the biggest gap." |
| 0:55-1:10 | Test Conditions → type PMMA in Highlight | "Here's that gap on the map. Every PMMA test sits near 21% oxygen, far from the red Moon-base box." |
| 1:10-1:30 | Explore the data → Modeling Data → the FLEX plot, then scroll to the matrix | "Objective two: data for predictive models. We extracted both the test conditions and the measured results, like burn time, burning rate and extinction diameter, in consistent units, with an explorer, a variable matrix and a data dictionary. Everything downloads as one CSV." |
| 1:30-1:45 | Fire safety → Equipment & Controls → ventilation card | "Objective three: next-generation equipment. For example, BRE's gas flames kept burning with the fans off at elevated oxygen, so on a Moon base, shutting off ventilation alone may not put out a fire." |
| 1:45-1:55 | Investigations → open a card → point at "Checked against"; open Ask the data and click "What matters most for a lunar rover?" | "Every claim traces to its PSI record and was fact-checked. And you can simply ask the data questions, with answers computed from the dataset." |
| 1:55-2:05 | Case Studies, then Earth Applications, end on Overview | "We also connect the data to real spacecraft fires and to fire safety on Earth, like oxygen-enriched hospital rooms. We're the Golden Go-figures from the University of Minnesota. Let's make the next giant leap a safer one." |

### Short script (30 seconds)

| Time | On screen | Narration |
|---|---|---|
| 0:00-0:08 | Overview key numbers | "Moon bases will run at 30% oxygen or more, but none of NASA's 264 microgravity fire tests on solid materials went above 22%." |
| 0:08-0:16 | Mission Relevance → Moon base | "Our dashboard ranks every PSI combustion experiment for your habitat, ISS to lunar rover, with a transparent score." |
| 0:16-0:24 | Modeling Data plot, then Equipment & Controls | "It extracts model-ready conditions and results, and turns the research into findings for next-generation fire safety equipment." |
| 0:24-0:30 | Open a card → "Checked against" | "Every claim traces back to NASA's data. Let's make the next giant leap a safer one." |
