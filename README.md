# Flame in Free Fall: Spacecraft Fire Safety Data Explorer

NASA Space Apps Challenge 2026 project by the Golden Go-figures (University of Minnesota AEM):
Isaac Fouts and Fabian Lujardo.

A web dashboard that turns every combustion experiment table in NASA's Physical Sciences Informatics
(PSI) database into one comparable dataset: **1,993 tests from 19 investigations, with 2,807 measured
results**. It ranks the investigations for a chosen crew environment, extracts model-ready data and
connects the research to next-generation fire safety equipment.

**Headline finding:** none of PSI's 264 solid-material tests (fabrics, plastics) were run above 22.2%
oxygen, while Moon bases and pressurized rovers are expected to run at 30% or more.

## Features

| Section | What it does |
|---|---|
| Overview | Key numbers, the main data gaps, and how each challenge objective is answered |
| Mission Relevance | Ranks investigations for the ISS, an exploration atmosphere, a Moon base, a pressurized rover, a Mars habitat or a spacesuit, with a transparent score and a plain-English summary |
| Investigations | Insight card for each study: objective, variables, sensors, takeaway, limitations, PSI link, DOI; each card states what it was checked against |
| Test Conditions | Every test plotted by oxygen and pressure against habitat targets, with search highlighting |
| Compare | Up to three investigations in a chart and side by side |
| Modeling Data | Model-ready datasets, a result-vs-condition explorer, a variable matrix and a data dictionary |
| Equipment & Controls | What PSI research means for ventilation shutdown, material testing, detectors, extinguishing agents, oxygen limits, atmosphere monitoring and fire models |
| Case Studies | Apollo 1, Apollo 13, Mir, ISS 2006, Artemis II and a lunar rover scenario, read through the data |
| Earth Applications | Hospital oxygen fires, smoke detectors, clean-agent suppression and more |
| Ask the data | Rule-based chat assistant; answers are computed from the dashboard's data (no AI service) |

## View the site

It's a static site with no server code.

- **Quickest:** double-click `index.html`. Needs internet only for the chart library and fonts.
- **Local server:** run `python -m http.server 8000` in this folder, then open http://localhost:8000.
- **Public link (GitHub Pages):** see below.

### Publish on GitHub Pages (at submission time)

GitHub Pages needs the repository to be **public** on a free account.

1. On GitHub: **Settings → General → Danger Zone → Change visibility → Public**.
2. **Settings → Pages → Build and deployment**: Source **Deploy from a branch**, Branch **main**,
   folder **/ (root)**, then **Save**.
3. Wait 1-2 minutes. The site is live at https://lujar001-star.github.io/FlameInFreeFall-NASA/
4. Open that link on a phone and a laptop and click through every menu item before submitting.

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The dashboard (single page; HTML, CSS, JavaScript; Plotly for charts) |
| `assets/logo.png` | Team logo |
| `data/tables/` | Original PSI experiment-table CSVs (unmodified) |
| `data/tests.csv` | All tests normalized: conditions and measured results, common units, `assumed` flags |
| `data/insights.json` | Insight cards, each with a `verified` note |
| `data/psi_investigations.json`, `data/psi_details.json` | PSI investigation metadata |
| `data/dashboard.js` | Data bundle the website loads (generated) |
| `scoring.py` | Habitat relevance scoring |
| `scripts/` | Data pipeline |
| `SUBMISSION.md` | Draft text for the Space Apps submission form |

## Rebuild the data

```bash
pip install -r requirements.txt
python scripts/fetch_psi_metadata.py     # list of PSI investigations
python scripts/fetch_psi_details.py      # detail records for combustion investigations
python scripts/download_tables.py        # experiment-table CSVs
python scripts/build_tests.py            # normalize into data/tests.csv
python scripts/verified_card_fixes.py    # apply the verified insight-card corrections
python scripts/build_dashboard_data.py   # bundle for the website
```

## Data notes

- Units: O2 % by volume, pressure atm, flow cm/s, sizes mm, times s, temperatures K.
- Where a table does not record O2 or pressure and the test ran in ISS cabin air, 21% / 1 atm is used
  and the row is flagged in `assumed`.
- Physically impossible values are blanked (never guessed) and noted in the row.
- In ACME inverse flames, the O2 value is the burner oxidizer stream, not the ambient atmosphere.
- Adiabatic flame temperature and stoichiometric mixture fraction are calculated by the
  investigators, not measured.
- Rows that list several levels (ACME BRE days, the FLEX-2 test matrix) keep them in `o2_levels_pct` /
  `p_levels_atm`.
- Data: NASA PSI, CC0. Cite each investigation by its DOI (listed on the Data & Methods tab).

## AI use

Claude (Anthropic) helped build the data pipeline and website and draft the insight cards. Gemini
(Google) was used as an independent fact-checker. ChatGPT (OpenAI) made the logo. Every insight-card
statement was checked against the PSI records. The "Ask the data" assistant is rule-based and does
not call any AI service.
