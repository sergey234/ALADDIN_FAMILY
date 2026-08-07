# Ref share + crypto withdraw — TODO Tracker

**План:** `PLAN_REF_SHARE_AND_CRYPTO_WITHDRAW_2026-07-22.md`  
**Дата:** 2026-07-22  
**Ids:** `refwd-*`  
**Деплой:** `20260722-2314xx` (Contabo + MAIN)

## Todo

- [x] `refwd-00` Аудит шаринга + крипто (вход) + withdraw карта
- [x] `refwd-01` План MD
- [x] `refwd-02` Share text → Ai Monkey Stars
- [x] `refwd-03` Тест шаринга + деплой Contabo
- [x] `refwd-04` Миграция `ref_withdraw_requests` (method / crypto_channel / payout_target)
- [x] `refwd-05` UX: выбор карта vs крипта + ввод реквизитов
- [x] `refwd-06` Админ list/paid с крипто-полями
- [x] `refwd-07` Тексты home: «карта или крипта»
- [x] `refwd-08` Тесты + деплой
- [ ] `refwd-09` (later) Crypto Pay auto-transfer

## Канон v1

- Шаринг: `url=` = реф-ссылка; `text=` = бренд без дубля ссылки
- Крипто-вывод: **ручная** заявка (как карта), не авто-payout
- Сети v1: USDT TRC20 + CryptoBot `@user`
- Мин. 500 ₽, одна pending
