#!/usr/bin/env python3
import glob
import json
import time
from pathlib import Path


GATES_DIR = Path("docs/release/gates")
SOAK_DIR = Path("docs/release/soak")
OUT_JSON = Path("docs/release/release-gate-report.json")
OUT_MD = Path("docs/release/go-no-go.md")


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def gate_status(name: str, data):
    if data is None:
        return {"gate": name, "status": "MISSING"}
    return {"gate": name, "status": "PASS" if data.get("pass") else "FAIL"}


def latest_soak_summary():
    files = sorted(glob.glob(str(SOAK_DIR / "*.summary.json")))
    if not files:
        return None
    p = Path(files[-1])
    return read_json(p)


def main():
    reports = {
        "rel-06": read_json(GATES_DIR / "rel-06-hardening-report.json"),
        "rel-07": read_json(GATES_DIR / "anti-mock-report.json"),
        "rel-08": read_json(GATES_DIR / "endpoint-report.json"),
        "rel-09": read_json(GATES_DIR / "write-before-after-report.json"),
        "rel-10-openapi-drift": read_json(GATES_DIR / "openapi-drift-report.json"),
        "rel-10-ios-sync": read_json(GATES_DIR / "ios-endpoint-sync-report.json"),
        "rel-11": read_json(GATES_DIR / "observability-slo-report.json"),
        "rel-12": read_json(GATES_DIR / "security-pii-audit-report.json"),
        "rel-13": read_json(GATES_DIR / "ios-smoke-42-report.json"),
        "rel-14": read_json(GATES_DIR / "ios-functional-138-report.json"),
        "rel-15": latest_soak_summary(),
    }

    gates = [gate_status(k, v) for k, v in reports.items()]

    # rel-15 can be IN_PROGRESS while soak is running (no final summary yet)
    if reports["rel-15"] is None:
        for g in gates:
            if g["gate"] == "rel-15":
                g["status"] = "IN_PROGRESS"

    blocking = [g for g in gates if g["status"] in {"FAIL", "MISSING"}]
    all_pass = all(g["status"] == "PASS" for g in gates)
    decision = "GO" if all_pass else "NO_GO"

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "gates": gates,
        "decision": decision,
        "blocking_items": blocking,
        "note": "GO requires all gates PASS including rel-15 soak 24h.",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Go/No-Go",
        "",
        f"- Decision: **{decision}**",
        "- Rule: all release gates must be PASS.",
        "",
        "## Gates",
    ]
    for g in gates:
        lines.append(f"- `{g['gate']}`: **{g['status']}**")
    if blocking:
        lines.append("")
        lines.append("## Blocking Items")
        for b in blocking:
            lines.append(f"- `{b['gate']}` -> `{b['status']}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"report={OUT_JSON}")
    print(f"markdown={OUT_MD}")


if __name__ == "__main__":
    main()
