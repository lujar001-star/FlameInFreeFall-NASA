"""Download full detail records for the fire-safety-relevant PSI investigations.

Reads data/psi_investigations.json (from fetch_psi_metadata.py), fetches each combustion
investigation's detail record from the public PSI API, and saves data/psi_details.json.
Also writes data/DOWNLOAD_CHECKLIST.md listing each experiment table file to download by hand.

Run: python scripts/fetch_psi_details.py
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DETAIL_API = "https://psi.nasa.gov/geode-py/ws/repo/investigations/{}"
PAGE = "https://psi.nasa.gov/physci/repo/data/investigations/{}"

# Extra non-combustion investigations that matter for fire safety (smoke/aerosol sensing).
EXTRA = {"PSI-179"}  # ASE - Aerosol Sampling Experiment


def fetch(accession: str) -> dict:
    with urllib.request.urlopen(DETAIL_API.format(accession), timeout=60) as resp:
        return json.load(resp)


def main() -> None:
    index = json.loads((DATA / "psi_investigations.json").read_text(encoding="utf-8"))
    wanted = [r["Accession"] for r in index
              if r.get("Research Area") == "Combustion Science" or r["Accession"] in EXTRA]

    details = {}
    for acc in wanted:
        print("fetching", acc)
        details[acc] = fetch(acc)
    (DATA / "psi_details.json").write_text(
        json.dumps(details, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    lines = ["# Experiment tables to download", "",
             "Open each link, go to **Data files and documents** -> **Experimental table** folder,",
             "tick the CSV, click Download, and save it into `data/tables/`.", ""]
    for acc, d in details.items():
        name = d.get("investigationAcronym") or d.get("title", "")[:60]
        files = [f["file_name"] for f in d.get("experimentalTable") or []]
        kind = d.get("projectType", "")
        lines.append(f"- [ ] **{acc} {name}** ({kind}) - {PAGE.format(acc)}")
        for f in files:
            lines.append(f"    - `{f}`")
        if not files:
            lines.append("    - (no experiment table listed)")
    (DATA / "DOWNLOAD_CHECKLIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {len(details)} detail records and data/DOWNLOAD_CHECKLIST.md")


if __name__ == "__main__":
    main()
