# Profile slim + VPN status — TODO Tracker

**SSOT Cursor TODO** · ids `pf-*`  
**План:** `PLAN_PROFILE_REF_DEDUP_VPN_STATUS_2026-07-14.md`  
**Цель:** убрать рефку из профиля; статус VPN в профиле и VPN-разделе; `nav:ref` не трогать.

Отметки: `[ ]` / `[~]` / `[x]` · Cursor: только `TodoWrite merge: true` по `pf-*`.  
**Ничего не удалять** из Cursor TODO при обновлениях. Соседи: `br-*`, `rb-*`, `cc-*`.

---

## Phase 0 — Канон

- [x] `pf-00-canon` — SSOT рефки = только `nav:ref`; профиль без реф-контента
- [x] `pf-00-align-rb` — согласовать с `rb-r4-profile` (💳/🎁 + VPN-only hint)

---

## Phase 1 — VPN status helper

- [x] `pf-1-remaining-format` — format «X дней Y часов» из `paid_until` (UTC→MSK display)
- [x] `pf-1-status-helper` — единый `vpn_user_status_block_html` (active / inactive)
- [x] `pf-1-inactive-copy` — профиль: «Не активен»; VPN-раздел: «VPN не подключён» (variants ok)
- [x] `pf-1-source-vpn-db` — читать live из vpn.db (существующий fetch), без кэша сообщения

---

## Phase 2 — Профиль

- [x] `pf-2-body-rewrite` — `profile_body_html`: ID, дата регистрации, **💳/🎁 + VPN-only hint**, VPN-блок (**OWNER** тела профиля; `rb-r4-profile` только verify)
- [x] `pf-2-strip-ref-text` — убрать ссылку/условия/статистику приглашений из тела
- [x] `pf-2-strip-ref-kb` — `nav_profile`: без `append_referral_action_rows`, без `nav:reffaq`
- [x] `pf-2-keep-non-ref-nav` — оставить «В меню»; sell/заявки — только если не реф (явное решение в PR)

---

## Phase 3 — VPN раздел

- [x] `pf-3-vpn-main-use-helper` — встроить helper в `vpn_main_block_html` / account section
- [x] `pf-3-active-fields` — Активен + осталось + действует до
- [x] `pf-3-inactive-fields` — ❌ VPN не подключён

---

## Phase 4 — Рефка freeze + docs

- [ ] `pf-4-ref-smoke` — smoke: `nav:ref` без регрессии (ссылка/стат/кнопки)
- [x] `pf-4-ux-doc` — обновить `REFERRAL_UNIFIED_UX_PLAN.md` §3.1 (профиль ≠ рефка)
- [x] `pf-4-arch-note` — краткая пометка в architecture / tracks index

---

## Phase 5 — Тесты / деплой

- [x] `pf-5-test-profile-no-ref` — в HTML профиля нет `start=ref_` / «Пригласить»
- [x] `pf-5-test-status-active` — мок active → дни+часы+дата
- [x] `pf-5-test-status-inactive` — нет аккаунта / expired → inactive
- [x] `pf-5-deploy` — Contabo deploy (**один** выкат с `rb-r6-deploy`, если общий PR)
- [ ] `pf-5-e2e` — ручной: slim профиль + VPN статус + ref ок (+ балансы вместе с rb smoke)

---

## Definition of Done

- [ ] Дубля рефералки в профиле нет
- [ ] `nav:ref` работает как раньше
- [ ] VPN статус актуален в профиле и VPN
- [ ] Согласовано с отображением двух балансов (`rb-*`)
