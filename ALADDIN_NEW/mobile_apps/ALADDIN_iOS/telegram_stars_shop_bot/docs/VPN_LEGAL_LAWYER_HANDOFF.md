# Пакет для юриста — vpn-54 + vpn-77

**Дата:** 2026-06-28 · **Статус:** готово к review и sign-off  
**Задачи Cursor:** vpn-r13 (vpn-54), vpn-r36 (vpn-77)

---

## Что изменилось в редакции 1.1

| Документ | Файл | Изменение |
|----------|------|-----------|
| Соглашение | `aladdin_shop_vpn_api/.../legal_docs/vpn-terms.md` | §2.5–2.7: RU first hop, EU egress, профили, без «обхода блокировок» |
| Политика данных | `legal_docs/vpn-data.md` | §6.5–6.6: subprocessors (Contabo, RU relay, Cloudflare, платежи) |
| AUP | `legal_docs/vpn-aup.md` | v1.1, запрет злоупотребления «обходом» |
| Инструкции | `legal_docs/vpn-instructions.md` | порядок профилей 4G (уже было) |
| Тезисы RU bridge | `VPN54_RU_BRIDGE_LEGAL_DRAFT.md` | исходный brief |

**Публичные URL после deploy:**

- `https://aladdin-ai.ru/v1/legal/vpn-terms`
- `https://aladdin-ai.ru/v1/legal/vpn-data`
- `https://aladdin-ai.ru/v1/legal/vpn-aup`
- `https://aladdin-ai.ru/v1/legal/vpn-instructions`

---

## Вопросы на sign-off (юрист)

| # | Вопрос | Рекомендация ops |
|---|--------|------------------|
| 1 | Достаточно ли раскрытия RU transit в terms §2.5 без отдельного согласия? | Да + инструкция + выбор профиля |
| 2 | Таблица subprocessors в vpn-data §6.5 — полнота для GA? | Добавить ИП/реквизиты Contabo при необходимости |
| 3 | Cloudflare — отдельное согласие или достаточно политики? | Достаточно §6.5 при optional CDN |
| 4 | Формулировка «защита в публичных сетях» для маркетинга | OK, без «обход блокировок» |
| 5 | Возраст / гео (`VPN02_LEGAL_CHECKLIST.md`) | Согласовать |

---

## Sign-off (заполнить юристу)

```
Дата: ___________
Юрист / ФИО: ___________
vpn-54 RU bridge: [ ] OK  [ ] правки в ___
vpn-77 полный пакет: [ ] OK  [ ] правки в ___
Комментарий: ___________
```

После sign-off ops:

1. Зафиксировать финальный markdown в `legal_docs/`
2. Deploy vpn-api на Contabo → `systemctl restart aladdin-shop-vpn-api`
3. `curl -fsS https://aladdin-ai.ru/v1/legal/vpn-terms | head -5` — дата 28.06.2026
4. Отметить vpn-r13, vpn-r36 ✅ в реестре
5. В journal: `"legal_signoff": {"vpn54": true, "vpn77": true, "date": "..."}`

---

## Бот

Перед оплатой: `vpn_legal_gate` — две галочки (политика + соглашение), ссылки на `/v1/legal/vpn-*`.

Проверить после deploy бота + api.
