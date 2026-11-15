# Flame in Free Fall: Spacecraft Fire Safety Data Explorer

NASA Space Apps Challenge 2026 project by the Golden Go-figures (University of Minnesota AEM).

A web dashboard that turns every combustion experiment table in NASA's Physical Sciences Informatics
(PSI) database into one comparable dataset. It ranks investigations by relevance to a chosen crew
environment (ISS, Orion/Gateway, Moon base / rover, Mars, spacesuit) and interprets each one for
fire prevention, detection and suppression.

## View the site

Static HTML, no server code. Start a local server from the project folder:

```bash
python -m http.server 8000
```

Then open http://localhost:8000. It can also be hosted directly on GitHub Pages.

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The dashboard (single page, plain HTML/CSS/JS, Plotly for the chart) |
| `assets/logo.png` | Team logo |
| `data/tables/` | Original PSI experiment-table CSVs (unmodified) |
| `data/tests.csv` | All tests normalized to common units, with `assumed` flags |
| `data/insights.json` | Curated insight cards per investigation |
| `data/psi_investigations.json`, `data/psi_details.json` | PSI investigation metadata |
| `data/dashboard.js` | Bundle the website loads (generated) |
| `scoring.py` | Habitat relevance scoring |
| `scripts/` | Data pipeline |

## Rebuild the data

```bash
pip install -r requirements.txt
python scripts/fetch_psi_metadata.py     # list of PSI investigations
python scripts/fetch_psi_details.py      # detail records for combustion investigations
python scripts/download_tables.py        # experiment-table CSVs
python scripts/build_tests.py            # normalize into data/tests.csv
python scripts/build_dashboard_data.py   # bundle for the website
```

## Data notes

- O2 is % by volume, pressure is atm, flow is cm/s.
- Where a table does not record O2 or pressure and the test ran in ISS cabin air, 21% / 1 atm is used and
  the row is flagged in `assumed`.
- Physically impossible values are blanked (never guessed) and noted in the row.
- In ACME inverse flames the O2 value is the burner oxidizer stream, not the ambient atmosphere.
- Data: NASA PSI, CC0. Cite each investigation by its DOI (listed on the site's Data & Methods tab).
