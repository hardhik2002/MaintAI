from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
DESTINATION = Path("ml/data/raw/ai4i2020.csv")


def main() -> None:
    import io
    import zipfile

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        data = archive.read("ai4i2020.csv")
    DESTINATION.write_bytes(data)
    print(
        f"Downloaded {DESTINATION} ({len(data):,} bytes, sha256={hashlib.sha256(data).hexdigest()})"
    )


if __name__ == "__main__":
    main()
