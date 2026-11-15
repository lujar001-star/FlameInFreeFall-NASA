"""Download metadata for every PSI investigation from NASA's public PSI API.

Saves data/psi_investigations.json (all investigations, all research areas).
Run: python scripts/fetch_psi_metadata.py
"""
import json
import pathlib
import urllib.parse
import urllib.request

API = "https://psi.nasa.gov/geode-py/ws/repo/search"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "psi_investigations.json"


def search(term: str = "") -> list[dict]:
    params = {
        "term": term,
        "source": "psi",
        "type": "investigation",
        "sort": "Public Release Date",
        "order": "desc",
        "size": 1000,
    }
    url = f"{API}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.load(resp)
    return [hit["_source"] for hit in data["hits"]["hits"]]


def main() -> None:
    records = search("")
    records.sort(key=lambda r: int(r["Accession"].split("-")[1]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    combustion = [r for r in records if r.get("Research Area") == "Combustion Science"]
    print(f"Saved {len(records)} investigations ({len(combustion)} combustion) to {OUT}")


if __name__ == "__main__":
    main()
