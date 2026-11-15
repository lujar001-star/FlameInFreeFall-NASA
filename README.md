# Flame in Free Fall

NASA Space Apps Challenge 2026 project: an AI-powered web dashboard that summarizes, ranks and interprets
microgravity combustion investigations from NASA's Physical Sciences Informatics (PSI) database for
spacecraft and lunar habitat fire safety.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data

Experiment tables from NASA PSI go in `data/`. Large raw files (video, sensor dumps) go in `data/raw/`,
which git ignores.
