from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

import aiosqlite
from fastapi import Depends

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.settings import Settings, load_settings


def get_settings() -> Settings:
    return load_settings()


async def get_db(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[aiosqlite.Connection, None]:
    conn = await hmac_auth.open_db(settings.vpn_db_path)
    try:
        yield conn
    finally:
        await conn.close()
