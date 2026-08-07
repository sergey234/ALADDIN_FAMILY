# vpn-77 — Legal полный (Track C)

**Статус:** ✅ **legal_docs v1.1 в репо** · sign-off юриста ⏳  
**Cursor:** vpn-r36

## Документы

| Документ | URL prod | Репо v1.1 |
|----------|----------|-----------|
| Политика | `/v1/legal/vpn-data` | ✅ subprocessors + RU/CDN |
| Соглашение | `/v1/legal/vpn-terms` | ✅ §2.5 маршрутизация |
| AUP | `/v1/legal/vpn-aup` | ✅ v1.1 |
| Инструкции | `/v1/legal/vpn-instructions` | ✅ |
| Пакет юристу | `VPN_LEGAL_LAWYER_HANDOFF.md` | ✅ |

## Deploy legal

```bash
ssh aladdin-contabo
cd /opt/aladdin-shop-vpn-api && git pull
sudo systemctl restart aladdin-shop-vpn-api
curl -fsS https://aladdin-ai.ru/v1/legal/vpn-terms | grep "28 июня"
```

## Закрытие vpn-r36

Только после sign-off юриста (`VPN_LEGAL_LAWYER_HANDOFF.md`).

## Тест в боте

`VPN_DEPLOY_AND_BOT_TEST_GUIDE.md` — часть B2 (legal gate).
