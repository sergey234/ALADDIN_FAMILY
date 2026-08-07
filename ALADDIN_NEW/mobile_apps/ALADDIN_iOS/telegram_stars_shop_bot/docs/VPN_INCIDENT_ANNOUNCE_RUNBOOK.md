# Runbook: инцидент VPN → Happ announce

**Связано:** `p4-bot-status`, `obs-download-alert`, `VPN34_STATUS_POST_TEMPLATES.md`, `VPN53_SNI_ROTATION_RUNBOOK.md`

**Серверы:** Contabo `185.225.233.150` (vpn-api, xray), MAIN `149.154.65.180` (bridge)

---

## 1. Когда поднимать announce

| Триггер | Авто? | Действие |
|---------|-------|----------|
| `vpn_download_alert_check.py` exit 2 (downlink < 100 KB при uplink > 1 MB) | да | announce preset `4g` |
| `vpn_prod_smoke.py` FAIL на Contabo | ops | announce preset `4g` или свой текст |
| xray inactive / массовые тикеты 4G | вручную | announce + пост в канал |
| Плановая ротация SNI/REALITY | план | announce «плановые работы» + `VPN53` |
| После fix | вручную | `/admin_vpn_announce clear` |

---

## 2. Быстрый чеклист (staging → prod)

1. **Диагностика**
   - `ssh root@185.225.233.150 'systemctl is-active xray aladdin-shop-vpn-api'`
   - `python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py`
   - `python3 deploy/scripts/vpn_session_bytes_report.py --uuid <UUID> --since 1h`

2. **Включить announce** (в боте от admin)
   ```
   /admin_vpn_announce preset 4g
   ```
   или
   ```
   /admin_vpn_announce set Временные проблемы на 4G. Попробуйте 🇪🇺 Авто WiFi ⚡…
   ```

3. **Пост в статус-канал** (если `VPN_STATUS_CHANNEL_POST_ID` задан — бот постит сам при `set`)

4. **Починить data plane** (см. handoff §P0/P1)

5. **Проверить Happ** — staging TID `493897224`: обновить подписку 🔄 → announce виден

6. **Снять announce**
   ```
   /admin_vpn_announce clear
   ```

7. **Postmortem** — 3 строки в `SHADOWNET_ADOPTION_PLAN_ML_HANDOFF.md` §incidents

---

## 3. Тексты announce (готовые)

**4G / МегаФон:**
```
Временные проблемы на 4G. Попробуйте 🇪🇺 Авто WiFi ⚡ или обновите подписку 🔄
```

**Общий:**
```
Ведутся работы. На Wi‑Fi — 🇪🇺 Авто WiFi ⚡; на 4G — 🇪🇺 Авто 4G 📶. Обновите подписку 🔄
```

**Плановые работы:**
```
Плановые работы ~30 мин. После обновления подписки выберите 🇪🇺 Авто 4G 📶 на LTE.
```

---

## 4. Ротация REALITY (p5-reality-key-rotation)

1. Backup: `cp /opt/xray/config.json config.json.bak.$(date +%Y%m%d)`
2. `python3 deploy/scripts/apply_p5_dual_sni_overlap.py /opt/xray/config.json NEW_SNI`
3. `systemctl restart xray && python3 deploy/scripts/vpn_prod_smoke.py`
4. announce «плановые работы» → через 24–48h overlap убрать старый SNI
5. Подробно: `aladdin_shop_vpn_api/deploy/VPN53_SNI_ROTATION_RUNBOOK.md`

---

## 5. Dry-run на staging

```bash
# Деплой observability (timer + скрипты)
bash /opt/aladdin-shop-vpn-api/deploy/scripts/apply_obs_deploy.sh

# Установить тестовый announce
curl -sS -H "User-Agent: Happ" -H "X-HWID: test" \
  http://127.0.0.1:8091/sub/9R8T1iCLEULlrGmdTw4IQm2dFXfE8zOx -D - | grep -i announce

# Сброс
# /admin_vpn_announce clear в боте
```

---

## 6. Кто сбрасывает

- **ops/admin** — `/admin_vpn_announce clear` после green smoke
- **auto** — `vpn_download-alert.timer` + `vpn_download_alert_check.py` снимает announce при нормализации bytes (exit 0)

**Prod (2026-07-03):** timer active на Contabo; dry-run `action=clear` при пустом/нормальном логе.
