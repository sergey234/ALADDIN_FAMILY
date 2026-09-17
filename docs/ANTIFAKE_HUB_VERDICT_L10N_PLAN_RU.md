# Antifake Hub — локализация вердикта (EN ↔ RU)

**Дата:** 2026-09-18  
**Статус:** план зафиксирован; правки — по одной задаче (`afl10n-*`), без массовых diff.  
**Симптом:** UI приложения EN, `summary_human` / `reasons_human` с сервера RU.

## SSOT правило

Язык **в приложении** (`LocalizationManager.currentLanguage`) = язык динамического вердикта.  
Не использовать `Locale.preferredLanguages` устройства для Antifake.

| App language | Headers | Human copy |
|--------------|---------|------------|
| English | `X-Aladdin-Lang: en`, `Accept-Language: en` | EN only, 0 кириллицы |
| Русский | `X-Aladdin-Lang: ru`, `Accept-Language: ru` | RU |

Серверный SSOT human: `attach_human_reasons` / `_client_verdict` в `app/routers/antifake.py`.

## Корневые причины (аудит)

1. Text/URL через `NetworkManager` — **нет** lang headers → сервер default `ru`.
2. Media upload / job poll в `APIService` — lang из **device** locale, не in-app.
3. Sync media `completed` return — **без** `_client_verdict` → hardcode `lang="ru"` в `_build_response`.
4. `REASON_I18N` EN missing → silent fallback на RU.

## Чеклист поверхностей

| ID | Поверхность | DoD |
|----|-------------|-----|
| A1 | Disclaimer / табы | UI keys EN/RU |
| A2 | Hint, Paste, Check, Done | UI keys |
| A3 | Verdict title / risk / source badge | UI / presentation |
| A4 | `summary_human` | язык приложения |
| A5 | `reasons_human` | язык приложения |
| A6 | What to do next / Verify | UI keys |
| A7–A8 | Share chrome + body | body = human с сервера |
| A9 | Feedback / was_scam | UI keys |
| A10 | Premium / errors | UI keys |
| B | Text / Link / Contact | A4–A5 |
| C | Voice / Video / Document | headers + `_client_verdict` |
| D | Call analyze | то же |
| E | History | P2 re-humanize |
| F–H | Family / assistant / empty | UI keys |

## План задач (Cursor TODO)

| Todo id | Фаза | Задача |
|---------|------|--------|
| `afl10n-meta` | meta | Этот документ + TODO |
| `afl10n-p0-01-nm-headers` | P0 | NetworkManager: lang headers из LocalizationManager |
| `afl10n-p0-02-api-headers` | P0 | APIService multipart + poll: убрать preferredLanguages |
| `afl10n-p0-03-smoke-en` | P0 | Smoke EN text check (headers + no Cyrillic human) |
| `afl10n-p0-04-sync-media` | P0 | Sync media return → `_client_verdict` |
| `afl10n-p0-05-build-response` | P0 | `_build_response` без hardcode `lang="ru"` |
| `afl10n-p0-06-reason-i18n` | P0 | Аудит REASON_I18N EN / no silent RU fallback |
| `afl10n-p1-07-backend-test` | P1 | Backend тест X-Aladdin-Lang: en |
| `afl10n-p1-08-ios-unit` | P1 | iOS unit headers from currentLanguage |
| `afl10n-p1-09-verify-script` | P1 | verify / golden: EN без `[А-Яа-яЁё]` |
| `afl10n-p1-10-device-qa` | P1 | Device QA чеклист B–D EN+RU |
| `afl10n-p2-11-history` | P2 | History re-humanize |
| `afl10n-p2-12-share-smoke` | P2 | Share sheet smoke |
| `afl10n-deploy-main` | deploy | GO владельца → 🇷🇺 MAIN FirstVDS (`…180`) |

## Порядок работы

1. Одна задача = один маленький diff.  
2. После каждой — smoke / тест по DoD задачи.  
3. MAIN deploy только по явному GO.  
4. Не смешивать с bot / VPN / secrets.

## Прогресс

| Todo | Статус |
|------|--------|
| `afl10n-meta` | ✅ документ сохранён |
| `afl10n-p0-01-nm-headers` | ✅ `NetworkManager.performRequest` → `X-Aladdin-Lang` + `Accept-Language` из `LocalizationManager` |
| `afl10n-p0-02-api-headers` | ✅ `APIService` multipart upload + job poll → `aladdinUILangCode()` из in-app language |
| `afl10n-p0-03-smoke-en` | ✅ Text EN human (device) |
| `afl10n-p0-04-sync-media` | ✅ sync media `completed` → `_client_verdict(request)` (локально; MAIN — после GO) |
| `afl10n-p0-05-build-response` | ✅ `_build_response` без hardcode `lang="ru"` (локально; MAIN — после GO) |
| `afl10n-p0-06-reason-i18n` | ✅ 128/128 EN+RU; lookup без silent RU→EN (локально; MAIN — после GO) |
| `afl10n-p1-07`…`p2-12`, deploy | pending (по одной) |

**Смежная тема (не afl10n):** Trial UX на тарифах — `docs/TRIAL_TARIFFS_UX_PLAN_RU.md` (`trial-ux-*`).
