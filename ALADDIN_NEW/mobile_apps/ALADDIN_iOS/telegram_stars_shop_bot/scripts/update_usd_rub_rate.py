#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CBR_DAILY_XML_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Update USD_RUB_RATE in .env from CBR + markup")
    p.add_argument(
        "--env-file",
        default="/opt/aladdin-telegram-shop-bot/shared/.env",
        help="Path to environment file (default: production shared/.env)",
    )
    p.add_argument(
        "--markup-rub",
        type=float,
        default=5.0,
        help="Additive markup over CBR USD rate, RUB (default: 5.0)",
    )
    p.add_argument(
        "--timeout-sec",
        type=int,
        default=15,
        help="HTTP timeout for CBR request",
    )
    p.add_argument(
        "--usdt-rub-mode",
        choices=("keep", "match-usd", "zero"),
        default="keep",
        help=(
            "After updating USD_RUB_RATE: keep USDT_RUB_RATE as-is; "
            "match-usd = set USDT_RUB_RATE to the same number (ориентир USDT = курс ₽-прайса); "
            "zero = USDT_RUB_RATE=0 (бот берёт USDT-ориентир из USD_RUB_RATE, один источник)."
        ),
    )
    return p.parse_args()


def _fetch_cbr_usd_rate(timeout_sec: int) -> float:
    with urllib.request.urlopen(CBR_DAILY_XML_URL, timeout=timeout_sec) as resp:
        xml_body = resp.read().decode("cp1251", errors="replace")
    root = ET.fromstring(xml_body)
    for valute in root.findall("Valute"):
        code = (valute.findtext("CharCode") or "").strip().upper()
        if code != "USD":
            continue
        value_raw = (valute.findtext("Value") or "").strip().replace(",", ".")
        nominal_raw = (valute.findtext("Nominal") or "").strip()
        nominal = int(nominal_raw or "1")
        value = float(value_raw)
        if nominal <= 0:
            raise RuntimeError("CBR nominal for USD is invalid")
        return value / nominal
    raise RuntimeError("USD entry not found in CBR XML")


def _rewrite_env_fx(
    env_file: Path,
    usd_new: float,
    *,
    usdt_mode: str,
) -> tuple[float | None, float]:
    """Переписать USD_RUB_RATE и при необходимости USDT_RUB_RATE одним сохранением."""
    if not env_file.exists():
        raise FileNotFoundError(f"Env file not found: {env_file}")
    lines = env_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    out: list[str] = []
    seen_usd = False
    seen_usdt = False
    old_usd: float | None = None
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped.startswith("USD_RUB_RATE="):
            seen_usd = True
            old_raw = stripped.split("=", 1)[1].strip()
            try:
                old_usd = float(old_raw)
            except ValueError:
                old_usd = None
            out.append(f"USD_RUB_RATE={usd_new:.3f}")
            continue
        if stripped and not stripped.startswith("#") and stripped.startswith("USDT_RUB_RATE="):
            seen_usdt = True
            if usdt_mode == "keep":
                out.append(line)
            elif usdt_mode == "zero":
                out.append("USDT_RUB_RATE=0")
            else:
                out.append(f"USDT_RUB_RATE={usd_new:.3f}")
            continue
        out.append(line)
    if not seen_usd:
        out.append(f"USD_RUB_RATE={usd_new:.3f}")
    if usdt_mode != "keep" and not seen_usdt:
        if usdt_mode == "zero":
            out.append("USDT_RUB_RATE=0")
        else:
            out.append(f"USDT_RUB_RATE={usd_new:.3f}")
    env_file.write_text("\n".join(out) + "\n", encoding="utf-8")
    return old_usd, usd_new


def main() -> int:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    env_path = Path(args.env_file)
    cbr = _fetch_cbr_usd_rate(timeout_sec=max(3, int(args.timeout_sec)))
    effective = round(cbr + float(args.markup_rub), 3)
    if effective <= 0:
        raise RuntimeError(f"Computed USD_RUB_RATE is invalid: {effective}")
    old_rate, new_rate = _rewrite_env_fx(env_path, effective, usdt_mode=str(args.usdt_rub_mode))
    logging.info(
        "USD_RUB_RATE updated in %s: old=%s cbr=%.3f markup=%.3f new=%.3f usdt_mode=%s",
        str(env_path),
        "n/a" if old_rate is None else f"{old_rate:.3f}",
        cbr,
        float(args.markup_rub),
        new_rate,
        args.usdt_rub_mode,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
