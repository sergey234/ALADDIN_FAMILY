# VPN02 — чеклист для юриста (не заменяет legal-тексты)

**Тексты в репо:** `aladdin_shop_vpn_api/legal_docs/vpn-data.md` (политика), `vpn-terms.md` (соглашение), `vpn-aup.md`; зеркала `.txt`: `telegram_stars_shop_bot/legal/privacy_policy_vpn_ru.txt`, `terms_of_service_vpn_ru.txt`. Публично: `GET /v1/legal/vpn-data`, `vpn-terms` (дата 07.05.2026, по образцу Stars/Premium).

## Согласовать

- [ ] Возраст и гео ограничения продукта
- [ ] Финальные тексты: terms, AUP, data minimization
- [ ] Формулировка «какие данные храним» vs `telegram_user_id` + технические логи
- [ ] Политика хранения IP в nginx (`limit_req`, `/sub/`) — срок / маскирование
- [ ] Процедура удаления данных по запросу
- [ ] Согласование с логированием Sentry / Prometheus (без секретов VPN в событиях)

После подписания — заменить markdown в `legal_docs/` и выкатить vpn-api + проверить публичные URL.
