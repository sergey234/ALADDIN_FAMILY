# Family recovery code = invite → owner JWT

## 0) Карточка

- `date_start_utc:` product contract since early family auth (pre-2026-07 on MAIN)
- `date_end_utc:` open — Step A shield 2026-11-06; Step B pending GO
- `component:` auth / family
- `incident_type:` design-debt / privilege
- `short_summary:` `recovery_code` product rule equals `family_id`. Manual invite `FAM-…` compact-matches the same id, so anyone with an invite can call `/api/auth/login-by-recovery-code` and receive the **owner** JWT.

## 1) Почему так сделали (намеренно)

1. Анонимность: без email/телефона/пароля.
2. UX: один код «восстановить семью» для родителя.
3. iOS до сих пор шлёт `recovery_code = family_id` после recover.

Это не «случайный баг вчера» — это MVP-контракт. Цена: инвайт ≈ ключ владельца.

## 2) Step A (сделано / щит, UX тот же)

- Семья должна существовать в БД.
- Нормализация `FAM_` / `FAM-`.
- Rate limit **40 / час / IP** (щедро: Wi‑Fi, ретраи, несколько телефонов).
- Journal: `SECURITY recovery_login outcome=ok|fail|rate_limited` (без Telegram на каждый вход — MAIN не достаёт Bot API стабильно).
- **Не** принимаем сырой `invite_token` как owner login (не расширяем дыру).

## 3) Step B (после GATES + GO, не в слепой bump 18)

GATES (черновик):

1. Отдельный секрет recovery (Keychain iOS, hash на сервере).
2. Инвайт → только join member, не owner JWT.
3. Старый путь `recovery_code == family_id` — deprecation window или только с device уже известным как owner.
4. Регистрация / вход родителя ≤ 2 тапа, без «банковской» длинной процедуры.
5. Device QA + unit + curl evidence.

## 4) Action items

- [x] Step A code + deploy MAIN
- [ ] Step B product GO + GATES sign-off
- [ ] Optional: Brain greps `SECURITY recovery_login rate_limited` → ALADDIN alert
