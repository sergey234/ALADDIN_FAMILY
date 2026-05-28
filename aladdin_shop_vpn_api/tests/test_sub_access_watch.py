from __future__ import annotations

import asyncio

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.settings import load_settings
from aladdin_shop_vpn_api.sub_access_watch import (
    ensure_sub_access_log_table,
    hot_token_hashes,
    record_sub_access,
)


def test_hot_token_detects_burst() -> None:
    async def _run() -> None:
        settings = load_settings()
        conn = await hmac_auth.open_db(settings.vpn_db_path)
        try:
            await ensure_sub_access_log_table(conn)
            await conn.execute("DELETE FROM sub_access_log")
            await conn.commit()
            for _ in range(5):
                await record_sub_access(conn, opaque_token="same-token-abc")
            hot = await hot_token_hashes(conn, per_hour_threshold=3)
            assert len(hot) == 1
            assert hot[0][1] == 5
            assert len(hot[0][0]) == 16
        finally:
            await conn.close()

    asyncio.run(_run())
