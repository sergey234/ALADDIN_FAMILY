# iOS Family Rewards UX + Referral A — Task Registry

**Plan:** `docs/PLAN_IOS_FAMILY_REFERRAL_A_AND_REWARDS_UX_2026-09-13.md`  
**Rule:** `.cursor/rules/ios-family-ref-rewards-todo-ssot.mdc`  
**Дата:** 2026-09-13  
**Out of scope:** Вариант B (мост VPN-бот) · MLM L2/L3 · вывод ₽

## Status legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | pending |
| 🔄 | in progress |
| ✅ | done |

---

## Batch RWD — Child rewards / punish visibility

| ID | Task | Status |
|----|------|--------|
| `rwd-00` | Канон ролей: parent/elderly = опекун; child/teen = ребёнок; Kids force child | ✅ |
| `rwd-01` | Helper resolve роли из roster (`your_member_id` + FamilyLocalStore), не только UD | ✅ |
| `rwd-02` | `ChildRewardsScreen`: `parentQuickActions` по resolve; elderly = опекун | ✅ |
| `rwd-03` | Входы Main / Family / Parental: не затирать опекуна; Kids → child | ✅ |
| `rwd-04` | PIN/биометрия на Вознаградить/Наказать для опекуна (как Parental) | ✅ |
| `rwd-05` | Smoke: parent видит кнопки; child нет; 60+ видит; лог `CHILD_REWARDS.UI` | ✅ |

---

## Batch REF-A — Family Invite Pro

| ID | Task | Status |
|----|------|--------|
| `ref-a-00` | Product lock: бонусы = дни/скидка/слот; без ₽ и без моста в бот | ✅ |
| `ref-a-01` | Сервер: модель qualify (paid **или** active≥14д) + антиабуз | ✅ `app/services/family_referral_a.py` |
| `ref-a-02` | Сервер: ledger начислений (reason, days/% , status, pair families) | ✅ `family_referral_ledger.py` + SQL |
| `ref-a-03` | Сервер: уровни Bronze→Platinum + таблица бонусов рефереру | ✅ |
| `ref-a-04` | Сервер: бонус другу (−20% канон) | ✅ |
| `ref-a-05` | API: overview / stats / ledger / apply-on-qualify | ✅ `/api/referral/a/*` |
| `ref-a-06` | Unit/integration tests qualify + anti-self-ref + one-pair | ✅ + ledger helpers |
| `ref-a-07` | iOS `ReferralScreen`: уровни, прогресс, ledger UI | ✅ |
| `ref-a-08` | iOS: копирайт safe (семья / дни защиты / скидка) | ✅ |
| `ref-a-09` | Связка invite deep-link / QR с серверным apply | ✅ attach + deep-link router |
| `ref-a-10` | Verify скрипт / smoke checklist; деплой только после GO DEPLOY | ✅ verify + **DEPLOYED 2026-09-13** MAIN `:8002` |

---

## Batch REF-A+ — TOP усилители (6 шляп, P0–P1)

| ID | Task | Status |
|----|------|--------|
| `ref-a-11` | Push/in-app при grant бонуса («+N дней защиты») | ✅ local notification |
| `ref-a-12` | Analytics funnel: invite → open → signup → qualify → grant | ✅ `FamilyReferralAnalytics` |
| `ref-a-13` | Вход в рефку из Профиля + Семьи (явный CTA) | ✅ |
| `ref-a-14` | Level-up celebrate (лёгкая анимация / бейдж) | ✅ |
| `ref-a-15` | FAQ 3 вопроса на ReferralScreen | ✅ |
| `ref-a-16` | Soft anti-fraud: pair family_id + soft device signal | ✅ `device_soft_hash` |
| `ref-a-17` | Реф-экран только для опекунов (parent/elderly); дети не видят | ✅ |
| `ref-a-18` | Локализация RU/EN ключей рефки A + review-safe copy | ✅ |

---

## Work order (простым языком)

```
1) Починить кнопки наград детей     rwd-00…05     ✅
2) Зафиксировать правила рефки A    ref-a-00      ✅
3) Сервер qualify + ledger + тесты  ref-a-01…06   ✅
4) Экран рефки в приложении         ref-a-07…09,17,18 ✅
5) Проверки offline                 ref-a-10      ✅ (deploy ⏳)
6) TOP-усилители                    ref-a-11…16   ✅
```

**Next owner:** `GO DEPLOY` → migrate SQL on MAIN — Аладдин (`…180`) `:8002` → smoke API → Xcode build на устройстве.

RWD / REF-A code ready. Вариант B / MLM / вывод ₽ — **не делаем**.
