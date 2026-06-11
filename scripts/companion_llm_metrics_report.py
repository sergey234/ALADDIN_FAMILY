#!/usr/bin/env python3
"""Отчёт по companion_llm.log за N дней (задача 2.5)."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="/var/log/aladdin-backend/companion_llm.log")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(f"No log file: {path}", file=sys.stderr)
        return 1

    cutoff = int(time.time()) - args.days * 86400
    paths: Counter[str] = Counter()
    latencies: list[int] = []
    contexts: Counter[str] = Counter()

    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if int(row.get("ts", 0)) < cutoff:
                continue
            p = str(row.get("llm_path") or "unknown")
            paths[p] += 1
            contexts[str(row.get("ui_context") or "")] += 1
            if row.get("latency_ms") is not None:
                latencies.append(int(row["latency_ms"]))

    total = sum(paths.values()) or 1
    lines = [
        f"# companion_llm report ({args.days}d)",
        f"total_turns={total}",
        f"hermes_pct={100 * paths.get('hermes', 0) / total:.2f}",
        f"sfm_pct={100 * paths.get('sfm', 0) / total:.2f}",
        f"kb_rag_pct={100 * paths.get('kb_rag', 0) / total:.2f}",
        f"ollama_pct={100 * paths.get('ollama', 0) / total:.2f}",
        f"p95_latency_ms={int(statistics.quantiles(latencies, n=20)[18]) if len(latencies) >= 20 else (max(latencies) if latencies else 0)}",
        f"contexts={dict(contexts)}",
        f"path_counts={dict(paths)}",
    ]
    report = "\n".join(lines)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
