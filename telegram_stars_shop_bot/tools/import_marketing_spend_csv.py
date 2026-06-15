from __future__ import annotations

import argparse
import asyncio
import csv
from pathlib import Path

from bot.db.database import connect
from bot.services.marketing_spend_repo import SpendRow, bulk_upsert_daily_spend


def _parse_float(raw: str) -> float:
    s = (raw or "").strip().replace(",", ".")
    return float(s) if s else 0.0


def _parse_int(raw: str) -> int:
    s = (raw or "").strip()
    return int(float(s)) if s else 0


def _read_rows(csv_path: Path) -> list[SpendRow]:
    rows: list[SpendRow] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"date", "source", "campaign", "spend_rub", "clicks", "impressions"}
        missing = required.difference(set(reader.fieldnames or []))
        if missing:
            miss = ", ".join(sorted(missing))
            raise ValueError(f"CSV missing columns: {miss}")
        for i, r in enumerate(reader, start=2):
            try:
                rows.append(
                    SpendRow(
                        spend_date=(r.get("date") or "").strip(),
                        source=(r.get("source") or "").strip(),
                        campaign=(r.get("campaign") or "").strip(),
                        spend_rub=_parse_float(r.get("spend_rub") or ""),
                        clicks=_parse_int(r.get("clicks") or ""),
                        impressions=_parse_int(r.get("impressions") or ""),
                        meta={"row_number": i},
                    )
                )
            except Exception as exc:
                raise ValueError(f"bad CSV row {i}: {exc}") from exc
    return rows


async def _run(csv_path: Path, db_path: Path) -> int:
    rows = _read_rows(csv_path)
    conn = await connect(db_path)
    try:
        return await bulk_upsert_daily_spend(conn, rows)
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import daily marketing spend CSV into marketing_spend_daily."
    )
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument(
        "--db",
        default="data/shop.db",
        help="Path to shop.db (default: data/shop.db relative to current directory)",
    )
    args = parser.parse_args()
    csv_path = Path(args.csv).expanduser().resolve()
    db_path = Path(args.db).expanduser().resolve()
    imported = asyncio.run(_run(csv_path, db_path))
    print(f"imported_rows={imported}")


if __name__ == "__main__":
    main()
