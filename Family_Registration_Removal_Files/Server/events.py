import logging

_logger = logging.getLogger("family")
_handler = logging.StreamHandler()
_formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
_handler.setFormatter(_formatter)
if not _logger.handlers:
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)

def log_tariff_source_used(*, source: str, warn: bool = False) -> None:
    msg = f"tariff_source_used source={source}"
    if warn:
        _logger.warning(msg)
    else:
        _logger.info(msg)

def emit_limit_reached(tariff: str, limit: int, current: int, family_id: str) -> None:
    _logger.info(
        "limit_reached tariff=%s limit=%d current=%d family_id=%s",
        tariff, limit, current, family_id
    )