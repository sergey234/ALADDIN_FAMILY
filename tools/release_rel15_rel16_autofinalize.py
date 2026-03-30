#!/usr/bin/env python3
import json
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple


SOAK_DIR = Path("docs/release/soak")
LOG_PATH = SOAK_DIR / "rel15-rel16-autofinalize.log"


def _log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _latest_samples_file() -> Optional[Path]:
    files = sorted(SOAK_DIR.glob("soak-*.samples.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _load_samples(path: Path):
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    return [json.loads(x) for x in lines]


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def main() -> None:
    _log("autofinalize started")
    samples_file = _latest_samples_file()
    if not samples_file:
        _log("no soak samples file found; exit")
        return

    _log(f"tracking samples file: {samples_file}")

    while True:
        try:
            samples = _load_samples(samples_file)
            if not samples:
                _log("samples file is empty; sleep 60s")
                time.sleep(60)
                continue
            first_ts = int(samples[0]["ts"])
            last_ts = int(samples[-1]["ts"])
            due_ts = first_ts + 24 * 3600
            now_ts = int(time.time())
            hours = (last_ts - first_ts) / 3600.0
            _log(f"progress: samples={len(samples)}, hours={hours:.2f}, now<due={now_ts < due_ts}")

            if now_ts < due_ts:
                # 5 min cadence to match soak interval
                time.sleep(300)
                continue

            # Wait briefly for soak runner to flush final summary on natural exit.
            _log("24h window reached, waiting up to 10m for soak summary file")
            summary_found = False
            deadline = time.time() + 600
            while time.time() < deadline:
                summaries = sorted(SOAK_DIR.glob("soak-*.summary.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                if summaries:
                    _log(f"found summary: {summaries[0]}")
                    summary_found = True
                    break
                time.sleep(20)

            if not summary_found:
                _log("summary not found after wait; continue polling")
                time.sleep(120)
                continue

            # Finalize rel-16
            _log("running release_go_no_go_aggregator.py")
            rc, out, err = _run(["python3", "tools/release_go_no_go_aggregator.py"])
            _log(f"aggregator rc={rc}")
            if out.strip():
                _log(out.strip())
            if err.strip():
                _log(err.strip())
            _log("autofinalize completed")
            return
        except Exception as e:
            _log(f"exception: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
