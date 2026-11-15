"""Download every experiment-table CSV listed in data/psi_details.json.

Uses the same public download flow as the PSI website's Download button: ask the site
for a temporary link to the file, then fetch it. Only small experiment tables are fetched.

Run: python scripts/download_tables.py
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "tables"
LINK_API = "https://psi.nasa.gov/geode-py/ws/studies/{acc}/download?file={file}&version={ver}&redirect=false"
MAX_BYTES = 5_000_000  # safety: experiment tables are tiny; never pull anything big


def main() -> None:
    details = json.loads((DATA / "psi_details.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for acc, d in details.items():
        for f in d.get("experimentalTable") or []:
            name = f["file_name"]
            target = OUT / name
            if target.exists():
                print("have   ", name)
                continue
            if f.get("file_size", 0) > MAX_BYTES:
                print("SKIP (too big)", name, f.get("file_size"))
                continue
            link_url = LINK_API.format(acc=acc, file=urllib.parse.quote(name), ver=f.get("version", 1))
            link = urllib.request.urlopen(link_url, timeout=60).read().decode().strip().strip('"')
            body = urllib.request.urlopen(link, timeout=120).read()
            target.write_bytes(body)
            print(f"saved   {name} ({len(body):,} bytes)")
            time.sleep(0.5)  # be polite to NASA's server


if __name__ == "__main__":
    main()
