"""End-to-end runtime benchmark for the PUFGuard pipeline.

Times the three pipeline stages over N runs and writes per-run timings plus a
summary. Each stage is launched as a subprocess, exactly as ``run_all.ps1``
invokes it, so the measurement reflects the pipeline a user actually runs.

This requires the five raw workbooks in ``data/raw/`` (Stage 1 reads them). It
is a hardware-specific descriptive benchmark, not a portable performance claim.

Usage:
    python experiments/runtime/run_benchmark.py --project-root . --runs 5
"""

from __future__ import annotations

import argparse
import csv
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

STAGES = [
    ("stage1_profiling", "src/pufguard/analyze_corpus.py"),
    ("stage2_asp", "src/pufguard/run_logic.py"),
    ("stage3_report", "src/pufguard/build_report.py"),
]


def time_stage(script: Path, root: Path) -> float:
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script), "--project-root", str(root)],
        capture_output=True, text=True,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"stage failed: {script}\n{proc.stderr[-2000:]}")
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    root = args.project_root.resolve()

    # One untimed warmup run so the recorded timings reflect a warm filesystem
    # cache rather than first-touch disk reads (standard benchmark practice).
    for _name, script in STAGES:
        time_stage(root / script, root)

    rows = []
    for run in range(1, args.runs + 1):
        timings = {name: time_stage(root / script, root) for name, script in STAGES}
        timings["total"] = sum(timings.values())
        timings["run"] = run
        rows.append(timings)
        print(f"run {run}: " + ", ".join(f"{k}={timings[k]:.2f}s" for _, k in
              [("", n) for n, _ in STAGES] + [("", "total")]))

    out_dir = root / "experiments/runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = ["run"] + [n for n, _ in STAGES] + ["total"]
    with (out_dir / "runtime_results.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(r[k], 3) if k != "run" else r[k]) for k in fields})

    totals = [r["total"] for r in rows]
    print("\n=== summary ===")
    print(f"platform: {platform.platform()} | python {platform.python_version()}")
    for name, _ in STAGES:
        vals = [r[name] for r in rows]
        print(f"{name}: mean {statistics.mean(vals):.2f}s")
    print(f"total: mean {statistics.mean(totals):.2f}s, "
          f"range {min(totals):.2f}-{max(totals):.2f}s over {args.runs} runs")


if __name__ == "__main__":
    main()
