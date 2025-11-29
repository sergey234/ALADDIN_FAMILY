import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Dict

import bcrypt

TARIFF_PRICES: Dict[str, int] = {
    "free": 0,
    "personal": 29000,
    "family": 49000,
    "premium": 99000,
}


def hash_pin(pin: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pin.encode(), salt).decode()


def verify_pin(pin: str, hashed: str) -> bool:
    return bcrypt.checkpw(pin.encode(), hashed.encode())


def generate_activation_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    body = "-".join(
        "".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3)
    )
    return f"ALDN-{body}"


def code_expiration(days: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)

