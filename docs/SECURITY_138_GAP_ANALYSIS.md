# Security 138 — Gap Analysis (prod truth, 2026-06-09)

**Метод:** прод-тесты SSH + код iOS + OpenAPI + сравнение с `EXTENDED_138_CHECKLIST.md`  
**Важно:** чеклист 138 помечает всё `ok`, но smoke часто = «endpoint ответил 404/422/mock» ≠ **реальная функция в приложении**.

**Мастер-трекер:** `.cursor/SECURITY_138_MASTER_TODO.md`  
**Anti-fake деталь:** `.cursor/ANTIFAKE_PRODUCTION_TODO.md` (не удалять, синхронно с MASTER § AF)

---

## 1. Три уровня «работает»

| Уровень | Что значит | Сегодня для 100 угроз |
|---------|------------|------------------------|
| **L1 Каталог** | Toggle категории в UI + тексты тарифов | ~9 категорий видны |
| **L2 API toggle** | POST `/api/protection/*` persist | ❌ stub + 500 enable |
| **L3 Действие** | Пользователь получает результат (скан, вердикт, блок) | ❌ ~15–20% категорий |

**138 functions:** 100 threats + 32 parental + 6 extras.

---

## 2. Матрица 100 угроз (9 категорий)

| Категория | Функций | L1 UI | L2 API | L3 Реальное действие | Главный gap |
|-----------|---------|-------|--------|----------------------|-------------|
| **cyberThreats** | 10 | ⚠️ toggle | ❌ | ⚠️ Antivirus частично | Malware screen TODO scan; wildcard mock |
| **fraud** | 12 | ⚠️ | ❌ | ⚠️ Identity modal | Нет SNILS/credit/fraud agents API |
| **childThreats** | 17 | ✅ | ✅ | ✅ Parental Control | Мониторинг detail был mock envelope |
| **dataLeaks** | 12 | ⚠️ | ❌ | ⚠️ Dark Web fixed stats | Cleanup agent; privacy agents |
| **deepfakes** | 8 | ⚠️ | ❌ | ❌ | **Нет вердикта** — см. AF batches |
| **internetThreats** | 6 | ✅ VPN | ✅ | ✅ Network Protection | Content blocker Safari отдельно |
| **mobileThreats** | 10 | ⚠️ | ❌ | ❌ | MobileSecuritySettings TODO |
| **familyThreats** | 15 | ✅ Family | ✅ | ✅ | FamilyModals monitoring TODO zeros |
| **iotThreats** | 10 | ⚠️ | ❌ | ❌ | IoT fix threat TODO; нет реального scan |

---

## 3. 32 родительских — статус

| Модуль | UI | API | Gap |
|--------|-----|-----|-----|
| contentBlock | ✅ | ✅ | — |
| timeControl | ✅ | ✅ | — |
| monitoring | ✅ | ⚠️ | `GET monitoring/detail` → mock envelope (документировано) |
| location | ✅ | ✅ | geocode TODO в Family |
| reports | ✅ | ⚠️ | driving stats smoke ≠ полный PDF export |
| additional | ✅ | ✅ | — |
| bypassProtection | ✅ | ⚠️ | prod no-mock policy — отдельный трек |
| rewards | ✅ | ✅ | — |

**Вывод:** parental **лучший** сегмент; дыры в **monitoring detail** и геокодировании.

---

## 4. 6 дополнительных (EX-*)

| ID | Функция | UI | Реальность | Gap |
|----|---------|-----|------------|-----|
| EX-VPN | VPN | ✅ | ✅ | — |
| EX-AI | AI Assistant | ✅ | ✅ | reject sfm_mock на клиенте |
| EX-ELD | Elderly | ✅ | ⚠️ | `09_ElderlyInterfaceScreen` mockData |
| EX-VOICE | Voice control | ⚠️ | ⚠️ | component config smoke only |
| EX-GAME | Gamification | ✅ | ✅ | — |
| EX-ANON | Anonymous profiles | ⚠️ | ⚠️ | privacy PATCH partial |

---

## 5. Специфичные агенты (вне каталожного toggle)

Подтверждено дек. 2025 + прод июнь 2026:

| Агент | Обещание в UI | Прод сегодня | Batch |
|-------|---------------|--------------|-------|
| fake_news_detection_agent | FAQ, Premium | wildcard empty result | **AF** |
| fake_documents_agent | deepfakes #6 | нет cv2, нет router | **AF** |
| deepfake_protection_system | video/audio | stub / import error | **AF** |
| dark_web_monitoring_agent | Analytics modal | stats user-scoped ✅; scan agent ⚠️ | **DW** |
| russian_identity_theft_protection_agent | Identity modal | reports stats; SNILS ❌ | **ID** |
| personal_data_cleanup_agent | Advanced protection | toggles; scan/remove ⚠️ | **DC** |
| location_bubble_agent | Advanced protection | toggles; generate bubble ⚠️ | **LOC** |
| crash_detection_agent | Network screen alert | UI alert; settings modal off | **EM** |
| roadside_assistance_agent | Support sheet | UI only, нет API call | **EM** |
| phishing / malware / mobile / network / incident | Settings screens | кнопки «сканировать» = TODO | **COMP** |

---

## 6. Системные блокеры (все 138)

1. **`protection.py`** — logger 500, no DB persist → **ломает все 100 toggles**
2. **Wildcard SFM** `3.0.0-mock-real-protection` → ломает неизвестные пути
3. **iOS `loadSettingsFromServer` stub** → вакуум настроек
4. **Schema mismatch** `enabledCategories` vs `categories`
5. **Original SFM not importable** on prod
6. **Functional-138 runner** passes on 404 — метрика «137 passed» **не = prod ready**

---

## 7. Приоритет доменов (как anti-fake)

| P | Домен | Почему |
|---|-------|--------|
| P0 | **SEC-INFRA** + **AF** | Фундамент + Premium promise |
| P0 | **DW** + **ID** + **DC** | Premium тарифы 2–4, Analytics modals |
| P1 | **COMP** + **AV** | cyberThreats + mobileThreats UI уже есть |
| P1 | **PC-MON** | Family trust |
| P1 | **IOT** + **MOB** | категории 10+10 функций |
| P2 | **EM** + **ELD** + **AI-CAT** | extras, не блокируют core |
| P2 | **LOC** | privacy premium |

---

## 8. «Наилучшее» для продакшена (не MVP)

1. **Один раз починить SEC-INFRA** — все категории выигрывают.
2. **Явные роутеры per domain** — не wildcard, не весь SFM.
3. **Единый verdict contract** — antifake, phishing URL, malware, fake doc.
4. **Async jobs** для тяжёлого ML.
5. **iOS: Hub per domain** (не 100 экранов) — Antifake, Identity, DarkWeb, DeviceScan.
6. **Честный copy** — только L3-ready features.
7. **Приёмка:** device TestFlight + prod smoke **с assert на verdict**, не на HTTP code.

---

## 9. Связанные файлы

- `.cursor/SECURITY_138_MASTER_TODO.md` — все задачи
- `.cursor/ANTIFAKE_PRODUCTION_TODO.md` — anti-fake (синхрон AF-*)
- `docs/ANTIFAKE_PRODUCTION_PLAN.md`
- `docs/audit/EXTENDED_138_CHECKLIST.md` — пересмотреть verify после L3
