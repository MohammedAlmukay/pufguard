"""Verify the five source workbooks against the integrity manifest.

Run this after downloading the inputs described in ``docs/INPUT_ACQUISITION.md``
and before running the pipeline. It checks that every file named in
``data/metadata/integrity_manifest.csv`` exists at its expected path, has the
expected byte size, and hashes to the expected SHA-256 digest.

Exit status is 0 only when every declared input verifies, so this can be used as
a gate in a script or CI job.

Usage:
    python verify_inputs.py --project-root .
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

CHUNK = 1 << 20


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.project_root.resolve()

    manifest = root / "data/metadata/integrity_manifest.csv"
    if not manifest.exists():
        print(f"FAIL  manifest not found: {manifest}")
        return 2

    rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig")))
    ok = missing = mismatched = 0

    for row in rows:
        rel = row["relative_path"]
        path = root / rel
        expected_hash = row["sha256"].strip().lower()
        expected_size = int(row["size_bytes"])

        if not path.exists():
            print(f"MISSING   {rel}")
            print(f"          get it from {row['repository_url']}")
            missing += 1
            continue

        actual_size = path.stat().st_size
        actual_hash = sha256_of(path)
        if actual_hash != expected_hash or actual_size != expected_size:
            print(f"MISMATCH  {rel}")
            if actual_size != expected_size:
                print(f"          size     expected {expected_size}, got {actual_size}")
            if actual_hash != expected_hash:
                print(f"          sha256   expected {expected_hash}")
                print(f"                   got      {actual_hash}")
            print("          This is not the file the study used. Re-download the")
            print(f"          exact repository version at {row['repository_url']}")
            mismatched += 1
            continue

        print(f"OK        {rel}")
        ok += 1

    total = len(rows)
    print(f"\n{ok}/{total} verified, {missing} missing, {mismatched} mismatched")
    if missing or mismatched:
        print("\nInputs are not ready. See docs/INPUT_ACQUISITION.md.")
        return 1
    print("All declared inputs verified. The pipeline can be run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
