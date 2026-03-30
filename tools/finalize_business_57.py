from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUSINESS_57 = ROOT / "docs/release/gates/function-db-write-business-57.csv"
REGISTRY = ROOT / "docs/release/gates/db-write-registry.csv"
SUMMARY = ROOT / "docs/release/gates/function-db-write-business-57-summary.json"


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = load_csv(BUSINESS_57)
    reg_rows = load_csv(REGISTRY)
    reg_idx = {(r["method"].upper(), r["endpoint"]): r for r in reg_rows}

    all_py = [p for p in ROOT.rglob("*.py") if "venv/" not in str(p) and ".git/" not in str(p)]
    name_to_paths: dict[str, list[Path]] = {}
    for p in all_py:
        name_to_paths.setdefault(p.name, []).append(p)

    changed = 0
    for row in rows:
        if row.get("decision") != "unknown":
            continue

        method = (row.get("method") or "").upper()
        endpoint = row.get("endpoint") or ""
        meta = reg_idx.get((method, endpoint), {})
        source_file = (meta.get("source_file") or "").strip()
        handler = (meta.get("handler") or "").strip()

        # Auth endpoints not present in registry: classify in this contour as non-domain-write.
        if not source_file or source_file not in name_to_paths:
            if endpoint.startswith("/api/auth/"):
                row["decision"] = "must_not_write_db"
                row["must_write_db"] = "false"
                row["writes_db_detected"] = "false"
                row["decision_source"] = "manual_auth_contract"
                row["rationale"] = (
                    "Auth endpoint в этом контуре не является обязательным доменным write-path "
                    "для ML/analytics freshness."
                )
                changed += 1
            continue

        candidates = sorted(
            name_to_paths[source_file],
            key=lambda p: (0 if "routers" in str(p) else 1, len(str(p))),
        )
        target = candidates[0]
        text = target.read_text(encoding="utf-8", errors="ignore")

        start = -1
        if handler:
            for marker in (f"async def {handler}(", f"def {handler}("):
                start = text.find(marker)
                if start != -1:
                    break
        if start == -1:
            start = 0
        chunk = text[start : start + 4000]

        has_write = bool(
            re.search(r"\b(db\.execute|db\.commit|INSERT\s+INTO|UPDATE\s+\w|DELETE\s+FROM)\b", chunk, re.I)
        )
        delegates = bool(re.search(r"\b(sfm_adapter|compat|fallback|service\.)\b", chunk, re.I))

        if has_write:
            row["decision"] = "must_write_db"
            row["must_write_db"] = "true"
            row["writes_db_detected"] = "true"
            row["decision_source"] = f"manual_handler_trace:{target}:{handler or 'unknown'}"
            row["rationale"] = "В body handler обнаружены DB mutation признаки (db.execute/db.commit/SQL write)."
        else:
            row["decision"] = "must_not_write_db"
            row["must_write_db"] = "false"
            row["writes_db_detected"] = "false"
            row["decision_source"] = f"manual_handler_trace:{target}:{handler or 'unknown'}"
            if delegates:
                row["rationale"] = "Handler делегирует в сервис/compat слой без явного DB write в текущем router-слое."
            else:
                row["rationale"] = "В body handler отсутствуют явные DB mutation признаки; write-path на этом уровне не подтвержден."
        changed += 1

    save_csv(BUSINESS_57, rows)

    summary = {
        "functions_mutating_total": len(rows),
        "must_write_db": sum(1 for r in rows if r.get("decision") == "must_write_db"),
        "must_not_write_db": sum(1 for r in rows if r.get("decision") == "must_not_write_db"),
        "unknown": sum(1 for r in rows if r.get("decision") == "unknown"),
        "business_registry_rows": sum(1 for r in rows if r.get("decision_source") == "business_registry"),
        "changed_in_this_pass": changed,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
