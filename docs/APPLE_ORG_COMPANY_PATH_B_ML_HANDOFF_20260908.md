# ALADDIN iOS — Handoff для другой ML-системы  
## Корпоративный ASC / путь B / состояние на 2026-09-08

**Рабочий корень:**  
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  

**Ветка:** `master`  
**Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git`  
**Локальный kit (артефакты + этот отчёт):**  
`~/Downloads/ALADDIN_COMPANY_ASC_SETUP_20260908/`  

> Секреты (`.p8`, `.p12`, пароли, base64 профилей) **не коммитить** в git. Живут в Загрузках / kit. В чат не вставлять.

---

## 0) Как пришли к решению (зачем путь B)

### Проблема
- Личный Apple: приложение `family.aladdin.ios`, **только TestFlight** (build **248** уже на телефоне владельца).
- Компания: **SAUDAPAYDI, TOO**, Team **`B3WGHSWL79`**, Account Holder **`aladdin.ai@tuta.io`**.
- Bundle `family.aladdin.ios` **занят личным** аккаунтом → компания не может создать тот же Bundle.
- Кнопки **Transfer App** в личном ASC **нет** (нет версии в App Store) → Transfer сейчас недоступен.

### Варианты
| Путь | Суть | Решение владельца |
|------|------|-------------------|
| A / C | Минимальный Store с личного → Transfer → компания | Отложен |
| **B** | Личный TF оставить; на компании **новое** app | **Выбран** |

### Выбранные ID компании
| Роль | ID |
|------|-----|
| ASC app name | **ALADDIN AI** |
| App Bundle | **`ai.aladdin`** |
| Content Blocker | `ai.aladdin.ContentBlocker` |
| Antifake Share | `ai.aladdin.AntifakeShare` |
| Call Directory | `ai.aladdin.CallDirectory` |
| App Group | **`group.ai.aladdin`** |
| Team | **`B3WGHSWL79`** |

Канон в репо: `docs/APPLE_ORG_COMPANY_IDS_CANON.md`.

---

## 1) Чеклист: что сделали и для чего

### A. Стратегия и документы
| # | Сделано | Зачем |
|---|---------|--------|
| A1 | Отказались от Transfer «прямо сейчас» | Кнопки Transfer нет без Store-релиза |
| A2 | Зафиксирован путь B | Личный TF не ломаем; компания — отдельное app |
| A3 | Handoff двух путей / Gate0 / IAP docs | Память для людей и ML |
| A4 | Этот файл + kit в Downloads | Единая точка входа для следующей ML |

### B. Apple Developer / ASC (компания)
| # | Сделано | Зачем |
|---|---------|--------|
| B1 | App Group `group.ai.aladdin` | Общие данные app ↔ extensions |
| B2 | App ID `ai.aladdin` + capabilities (Groups, Domains, IAP, Push) | Главное приложение |
| B3 | 3 App ID расширений + App Groups | Content Blocker / Antifake Share / Call Directory |
| B4 | New App в ASC: **ALADDIN AI** / Bundle `ai.aladdin` | Карточка для TestFlight/Store компании |
| B5 | ASC API Key (Team), Key ID `PR42M5Z4Z8`, `.p8` в Downloads | Upload IPA из GitHub Actions |
| B6 | CSR + Apple Distribution + `.p12` | Подпись IPA на CI |
| B7 | 4× App Store provisioning profiles | Manual signing всех targets в CI |
| B8 | iPhone зарегистрирован в Team компании; Xcode Signing = SAUDAPAYDI | Локальная подпись без «no devices» |

### C. Код / репозиторий (локально, **ещё не обязательно закоммичено** на момент handoff — проверить `git status`)
| # | Сделано | Зачем |
|---|---------|--------|
| C1 | `DEVELOPMENT_TEAM` → `B3WGHSWL79` (12 мест) | Сборки от компании |
| C2 | Bundles → `ai.aladdin` + extensions | Совпадение с Identifiers |
| C3 | Entitlements / код → `group.ai.aladdin` | App Group |
| C4 | StoreKit / `StoreManager` Product IDs → `ai.aladdin.subscription.*` | IAP под новым Bundle |
| C5 | Обновлены CI workflows (`check-secrets.yml`, `appstore.yml`, …) | CI знает новые Bundle/group |
| C6 | `scripts/ios_verify_signing_targets.sh` обновлён | Автопроверка канона |
| C7 | Личный TF 248 ранее: Team временно личный → push → TF | Рабочий билд на телефоне с личного |
| C8 | Потом снова код под компанию (C1–C5) | Готовность к TF компании |

### D. GitHub Secrets (личный repo `sergey234/ALADDIN_FAMILY`)
| Secret | Назначение | Статус (по сессии) |
|--------|------------|-------------------|
| `APP_STORE_CONNECT_API_KEY` | текст `.p8` | ✅ владелец вставил |
| `APP_STORE_CONNECT_API_KEY_ID` | `PR42M5Z4Z8` | ✅ |
| `APP_STORE_CONNECT_ISSUER_ID` | Issuer со страницы ASC | ✅ |
| `APPLE_TEAM_ID` | `B3WGHSWL79` | ✅ |
| `IOS_DISTRIBUTION_CERTIFICATE` | base64 `.p12` | ✅ |
| `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD` | пароль `.p12` | ✅ |
| `PROVISIONING_PROFILE_APP` | base64 профиля `ai.aladdin` | ✅ |
| `PROVISIONING_PROFILE_EXTENSION` | Content Blocker | ✅ |
| `PROVISIONING_PROFILE_ANTIFAKE_SHARE` | Antifake Share | ✅ |
| `PROVISIONING_PROFILE_CALL_DIRECTORY` | Call Directory (новый secret; раньше мог отсутствовать) | ✅ создать/вставить |

**Не трогали (legacy, CI не использует):** `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD` — старый altool; можно оставить.

**GitHub = личный** — нормально. Apple = компания через Secrets.

---

## 2) Где что лежит (карта файлов)

### В репозитории (без секретов)
| Путь | Содержание |
|------|------------|
| `docs/APPLE_ORG_COMPANY_IDS_CANON.md` | Канон Bundle / group / IAP компании |
| `docs/APPLE_ORG_ML_HANDOFF_TWO_PATHS_20260907.md` | Разбор Transfer vs New App |
| `docs/APPLE_ORG_PERSONAL_TESTFLIGHT_GITHUB_PLAN_20260907.md` | План личного TF 248 |
| `docs/APPLE_ORG_MIGRATION_RUNBOOK.md` | Старый runbook (часть про Transfer устарела для текущего выбора B) |
| `docs/APPLE_ORG_MIGRATION_GATE0_WORKSHEET.md` | Факты Gate0 + пометка путь B |
| `docs/APPLE_ORG_IAP_PRODUCT_IDS.md` | Product IDs (после правки — префикс `ai.aladdin`) |
| `docs/RELEASE_BUILD_PROMPT.md` | Канон bump build для push |
| `docs/APPLE_ORG_COMPANY_PATH_B_ML_HANDOFF_20260908.md` | **Этот файл** |
| `scripts/ios_set_development_team.sh` | Смена Team в pbx |
| `scripts/ios_verify_signing_targets.sh` | Проверка Team/bundles/group |
| `ALADDIN.xcodeproj/project.pbxproj` | Team + bundles компании |
| `*.entitlements` | `group.ai.aladdin` |
| `Core/Store/StoreManager.swift` | Product IDs компании |
| `.github/workflows/check-secrets.yml` | CI upload SSOT |

### Локальный kit (одно место)
**Папка:** `~/Downloads/ALADDIN_COMPANY_ASC_SETUP_20260908/`

Туда скопированы/лежат копии отчёта и индекс. Секретные исходники — в `~/Downloads/` (см. ниже).

### Секреты и артефакты в `~/Downloads/` (НЕ в git)
| Файл | Зачем |
|------|--------|
| `AuthKey_PR42M5Z4Z8.p8` | ASC API private key |
| `ALADDIN_Company_Dist.certSigningRequest` | CSR |
| `ALADDIN_Company_Dist.key` | private key к CSR/Distribution |
| `distribution (5).cer` | скачанный Distribution cert |
| `ALADDIN_Company_Dist.p12` | для CI |
| `ALADDIN_Company_Dist_p12_PASSWORD.txt` | пароль p12 |
| `ALADDIN_Company_Dist_BASE64.txt` | base64 p12 |
| `ALADDIN_AI_App_Store.mobileprovision` | профиль app |
| `ALADDIN_AI_ContentBlocker_App_Store.mobileprovision` | | 
| `ALADDIN_AI_AntifakeShare_App_Store.mobileprovision` | |
| `ALADDIN_AI_CallDirectory_App_Store.mobileprovision` | |
| `PROVISIONING_PROFILE_*_BASE64.txt` | готовые вставки в GitHub |

---

## 3) Что осталось (следующая ML / владелец)

| # | Задача | Кто | Блокер? |
|---|--------|-----|---------|
| 1 | Подтвердить все 10 company secrets в GitHub Actions | владелец | да для CI |
| 2 | **`GO коммит+push ai.aladdin`** — закоммитить смену Bundle/Team/CI и запушить | владелец → агент | да для TF компании |
| 3 | Дождаться CI: Archive + Export + **Upload** зелёные | авто | |
| 4 | ASC компании → ALADDIN AI → TestFlight → Processing → Install | владелец | |
| 5 | Smoke на iPhone (это **другое** app, рядом с личным TF) | владелец | |
| 6 | Paid Apps Active (отложено владельцем) | владелец | для IAP продаж |
| 7 | Создать Subscriptions в ASC с ID `ai.aladdin.subscription.*` | владелец | для покупок |
| 8 | Карточка Store + Submit (позже) | владелец | |
| 9 | Не путать: push с **личными** ASC secrets снова сломает company TF | все | |

### Важно для следующей ML
- После path B **master** ориентирован на **компанию** (`ai.aladdin` / `B3WGHSWL79`). Личный `family.aladdin.ios` в коде больше не канон.
- Личный TestFlight **248** остаётся на старом Bundle в ASC личного аккаунта; новый билд = отдельное приложение.
- `PROVISIONING_PROFILE_CALL_DIRECTORY` обязателен: 4-е расширение в IPA; раньше secret мог отсутствовать на личном пайплайне.
- Не открывать Environment secrets в GitHub — только **Repository secrets**.
- `gh` на машине владельца может быть **не залогинен** — secrets вставляли вручную.

### Команды проверки
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/ios_verify_signing_targets.sh
git status --short
git log -3 --oneline
```

Ожидание verify: Team `B3WGHSWL79`, bundles `ai.aladdin*`, group `group.ai.aladdin`.

---

## 4) Краткая хронология решений

1. Нужен Store/TF от компании + Bundle занят личным → сравнение Transfer vs New App.  
2. Transfer недоступен (нет Store-версии) → владелец: **оставить личный TF, делать на компании**.  
3. Выбран Bundle `ai.aladdin` / group `group.ai.aladdin`.  
4. Identifiers + New App **ALADDIN AI**.  
5. Код переведён на company IDs.  
6. Xcode: аккаунт SAUDAPAYDI, device registered, Signing ok.  
7. GitHub: API + cert + 4 profiles (company).  
8. **Следующий явный шаг владельца:** GO на commit+push → CI → TestFlight ALADDIN AI.

---

## 5) Связанные URL (без секретов)

- ASC API keys: https://appstoreconnect.apple.com/access/integrations/api  
- Certificates: https://developer.apple.com/account/resources/certificates/list  
- Profiles: https://developer.apple.com/account/resources/profiles/list  
- GitHub secrets: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions  
- CI workflow SSOT: `.github/workflows/check-secrets.yml` (UI name: Build and Upload to App Store)

---

**Конец handoff 2026-09-08.**  
Следующая система: не начинать Transfer; не возвращать Team на личный без явного GO; следующий deliverable — commit+push company code → TF **ALADDIN AI**.
