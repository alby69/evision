#!/usr/bin/env python3
"""Downloads the latest OpenEV Data dataset (CSV) into backend/data/.

OpenEV Data is an open, community-maintained dataset of EV specifications
(https://github.com/open-ev-data/open-ev-data-dataset), licensed under
CDLA-Permissive-2.0.

Usage:
    python backend/scripts/update_ev_dataset.py
"""

import json
import sys
import urllib.request
from pathlib import Path

REPO = "open-ev-data/open-ev-data-dataset"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
DEST = Path(__file__).resolve().parents[1] / "data" / "open-ev-data.csv"


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "evision-dataset-updater"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        return response.read()


def main() -> int:
    release = json.loads(_get(API_LATEST))
    tag = release.get("tag_name", "?")
    asset = next(
        (a for a in release.get("assets", []) if a["name"].endswith(".csv")),
        None,
    )
    if asset is None:
        print(f"No CSV asset found in release {tag}", file=sys.stderr)
        return 1

    print(f"Downloading {asset['name']} ({asset['size']} bytes, release {tag})...")
    data = _get(asset["browser_download_url"])
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    print(f"Saved {len(data)} bytes to {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
