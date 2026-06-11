# ALADDIN Security — единый план 100% (138 функций)

**Версия:** 2.0 · **2026-06-09**  
**Статус:** согласованный продуктовый путь · реализация не начата  
**Трекеры:** `.cursor/SECURITY_138_MASTER_TODO.md` · `.cursor/SECURITY_100_PERCENT_ROADMAP_TODO.md` · `.cursor/ANTIFAKE_PRODUCTION_TODO.md`

**Жёсткое правило:** **онбординг не меняем** до Фазы 7 (COPY). Только аудит `copy-01-audit`.

---

## 1. Подтверждение: мы идём правильным путём

| Решение | Почему верно |
|---------|--------------|
| **Фаза 0 SEC-INFRA первой** | Прод-тест 09.06: toggle не persist, enable 500, sync → mock. Без крыши Hub'ы снова разъедутся. |
| **5 Hub'ов вместо 100 экранов** | Parental/VPN уже сильные; остальное — доменные центры действия. |
| **Явные FastAPI-роутеры, не wildcard** | Неизвестный URL сейчас = `status:success` (ложь). |
| **SFM-WIRE + SFM Truth** | Код **есть** (`app/security/`). Wire runtime + `GET /api/sfm/status` чтобы ML не путались. См. `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md` |
| **После restore: explicit routers** | Mobile идёт через Hub API; SFM execute — backend; wildcard = 503 |
| **138 verify = L3 на TestFlight** | HTTP 200/404 ≠ готовность. |
| **Онбординг заморожен** | Меняем FAQ/тарифы только в Фазе 7 после L3. |

**Итог:** архитектура Hub + SEC-INFRA + постепенная регистрация агентов — **наилучшее продуктовое решение** для 100% без повторного краха монолита.

---

## 2. SFM — что тестировали, что на проде, почему падает

### 2.1 Что такое SFM в ALADDIN

```
iOS / FastAPI router
        │
        ├─► Явный роутер (parental, VPN, protection)     ← целевой путь
        │
        └─► wildcard_handler → SFMAdapter → HTTP :8003/api/execute
                    │
                    └─► SafeFunctionManager (монолит ~1000+ handlers)
                            или OptimizedSFM mock (4–101 fn)
                            или start_sfm_core_http fallback {"status":"success"}
```

SFM задуман как **оркестратор**: `execute_function(name, params)` → агент → результат.  
Protection toggles, components, reports, antifake — всё **должно** сходиться здесь или в **явных роутерах** того же агента.

### 2.2 Что работало при тестах (март–июнь 2026)

| Тест | Результат | Что это значило |
|------|-----------|-----------------|
| `test_sfm_execute_function.py` | ✅ после фикса формата Tuple/dict | Скрипт совместим с разными return types |
| `GET /api/components/batch/status` | 200 | **Роутер FastAPI**, не SFM |
| `POST /api/components/status/*` без JWT | 403 | Auth работает |
| `POST :8003/api/execute` `get_darkweb_stats` | `{"status":"success"}` | **Soft mock** — не L3 |
| Локальный `safe_function_manager.py` (репо) | 1000+ функций | **Не задеплоен на VPS** |
| Build 122 SFM plan | регистрация агентов | Скрипты есть, prod не синхронизирован |

**Вывод:** ML-система была права, что **инфраструктура отвечает**. Ошибка — считать `status:success` за L3.

### 2.3 Состояние на проде сейчас (проверено SSH 09.06.2026)

| Компонент | Статус |
|-----------|--------|
| `/opt/aladdin-backend/security/safe_function_manager.py` | **ОТСУТСТВУЕТ** |
| `from security.safe_function_manager import SafeFunctionManager` | **ImportError** |
| `security/sfm_singleton.py` → `get_sfm()` | **Circular import** (`security/types` vs stdlib `types`) |
| `start_sfm_core_http.py` :8003 | **Работает**, но `sfm=None`; AI-хендлеры захардкожены; остальное → `status:success` |
| `health` на :8003 | Врёт: `functions_count: 1074` |
| Gunicorn `main:app` :8002 | Работает; wildcard → SFMAdapter → :8003 |
| `protection.py` enable | **`logger` не импортирован** → 500 с валидным JWT |
| `get_protection_settings_from_db` | **Stub** — всегда `false` |

### 2.4 Почему «поднять весь SFM» падал и будет падать снова

1. **Файл не на сервере** — монолит живёт в репо/tmp_push146, не в `/opt/aladdin-backend`.
2. **Circular import** — пакет `security/types/` конфликтует с Python `types`.
3. **Тяжёлые deps** — `cv2`, transformers, Redis — OOM / 30s cold start на VPS.
4. **Три несовместимых API** — `Tuple[bool,Any,str]` vs `dict` vs HTTP envelope.
5. **OptimizedSFM** — `3.0.0-mock-real-protection`, 4 функции в `__init__`, остальное не подключено.
6. **Wildcard маскирует** — любой путь получает 200.

### 2.5 Наилучшее постоянное решение для SFM

**Не возвращать монолит целиком.** Внедрить **SFM Agent Registry** (Фаза 0, блок SFM):

```
┌─────────────────────────────────────────────────────────┐
│  SFM Agent Registry (port 8003 или in-process)          │
│  ├─ REGISTERED_AGENTS: dict[name → AgentHandle]         │
│  ├─ execute(name): known → lazy_load(agent).run()      │
│  │                 unknown → 503 AGENT_NOT_REGISTERED    │
│  ├─ NO generic {"status":"success"}                    │
│  └─ health: real_count = len(REGISTERED_AGENTS)        │
└─────────────────────────────────────────────────────────┘
         ▲ register per phase (AF, DW, ID, AV…)
         │
  FastAPI explicit routers (primary for mobile)
```

| Шаг | Задача | ID |
|-----|--------|-----|
| 1 | Переименовать `security/types/` → `security/security_types/` (убрать circular import) | `sfm-01` |
| 2 | Деплой `AgentRegistry` вместо fake health 1074 | `sfm-02` |
| 3 | Удалить `OptimizedSFM` mock path из prod `get_sfm()` | `sfm-03` |
| 4 | `start_sfm_core_http.py`: unknown function → 503 | `sfm-04` |
| 5 | `SFMAdapter`: не маскировать 503; пробрасывать в API | `sfm-05` |
| 6 | `main.py` wildcard: security paths → 404 до SFM | `sec-04` |
| 7 | Маппинг `categoryId` → список agent names для enable/disable | `sfm-06` |
| 8 | По фазам: register_agent() для каждого домена | `sfm-07…12` |
| 9 | Опционально позже: chunked deploy `safe_function_manager` **только** как библиотека handlers в registry | `sfm-12` |

**Связь с protection:**  
`POST /protection/enable` → UPSERT DB → `registry.activate_agents_for_category(categoryId)` → агенты реально включаются.

---

## 3. Каждая проблема → отдельное решение → задача

| # | Проблема | Решение | Задачи |
|---|----------|---------|--------|
| P1 | Сервер забывает настройки | PostgreSQL `user_protection_settings` UPSERT | `sec-02`, `af-0-02/03` |
| P2 | enable → 500 | `import logging; logger = logging.getLogger(__name__)` | `sec-01`, `af-0-01` |
| P3 | iOS не тянет settings | Включить `loadSettingsFromServer()` + merge | `sync-01`, `R0-G4` |
| P4 | Schema mismatch 9 vs 11 categories | Канон iOS 9 в server + migration alias | `sec-03`, `af-0-04` |
| P5 | Wildcard mock | Blocklist + explicit routers | `sec-04/05/06`, `af-0-05/06` |
| P6 | SFM fake success | Agent Registry + 503 | `sfm-02…05`, `sec-07` |
| P7 | deepfake/fake-news пустой result | Antifake Hub explicit API | `af-2-*`, `R1-*` |
| P8 | Dark Web stats без scan | DW router + worker | `dw-01…08`, `R2-G1` |
| P9 | Identity stats ≠ detect | Identity Hub detect API | `id-01…08`, `R3-*` |
| P10 | cleanup/start mock | data_cleanup_agent router | `dc-01…06` |
| P11 | Antivirus scan TODO UI | Wire Malware screen + real scan job | `av-01…08`, `R4-G1` |
| P12 | Component scan buttons TODO | comp routers + iOS wire | `comp-01…10` |
| P13 | IoT fix threat TODO | IoT scan API | `iot-01…07` |
| P14 | parental monitoring mock envelope | FastAPI-only route | `pc-01…02` |
| P15 | 138 checklist ложный ok | L3 criterion + TestFlight | `sec-08`, `R8-*` |
| P16 | Онбординг vs реальность | **Не трогать**; аудит только | `copy-01-audit` |
| P17 | Premium без server gate | 403 на check/scan без tier | per-hub `*-07` |
| P18 | Offline settings conflict | Queue + last-write-wins | `sync-05` |

---

## 4. Девять категорий × L1/L2/L3 × план до 100%

Текущая оценка → целевая после всех фаз.

### 4.1 cyberThreats (10 угроз) · сейчас ~25% → 100%

| Уровень | Сейчас | Решение | Задачи |
|---------|--------|---------|--------|
| L1 | ⚠️ каталог, scan TODO | Device Hub карточка cyber | `R4-G5`, `comp-10` |
| L2 | ❌ protection stub | SEC-INFRA + `cyberThreats` toggle | `sec-*`, `R0-G8` |
| L3 | ❌ | Antivirus + malware + phishing scan | `av-01…08`, `comp-01/02`, `R4-G1/G2` |

**Пер-угроза L3 (10):** virus, trojan, ransomware, spyware, adware, rootkit, keylogger, backdoor, worm, fileless → единый `POST /api/device/scan` + typed `threatKind` в ответе.

| ID | Угроза | L3 критерий |
|----|--------|-------------|
| `cyb-01` | Вирусы | EICAR/test → quarantine UI |
| `cyb-02` | Трояны | threats[] с severity |
| `cyb-03` | Ransomware | heuristic + block advice |
| `cyb-04` | Spyware | app permission risk |
| `cyb-05` | Adware | detection in scan |
| `cyb-06` | Rootkit | jailbreak/root flag |
| `cyb-07` | Keylogger | behavioral hint |
| `cyb-08` | Backdoor | network anomaly |
| `cyb-09` | Черви | propagation check |
| `cyb-10` | Fileless | memory/script heuristic |

---

### 4.2 fraud (12) · ~30% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1 | Identity Hub | `R3-G3` |
| L2 | fraud toggle → agents | `id-06`, `sfm-06` |
| L3 | SNILS/credit/phishing fraud detect | `id-01…05`, `R3-G1/G2` |

| ID | Угроза | L3 |
|----|--------|-----|
| `frd-01` | Кража личности | detect API verdict |
| `frd-02` | Фишинг финансовый | text pipeline (AF link) |
| `frd-03` | Мошенничество с картами | transaction pattern |
| `frd-04` | Соц. инженерия звонок | call analyze (AF) |
| `frd-05` | Поддельные сайты | url check |
| `frd-06` | Скимминг | education + detect hook |
| `frd-07` | Кредитное мошенничество | credit monitor |
| `frd-08` | SIM-swap | carrier alert stub→real |
| `frd-09` | Поддельные маркетплейсы | url/text |
| `frd-10` | Инвест. пирамиды | text ML |
| `frd-11` | Вишинг | AF text |
| `frd-12` | Смishing | mob-04 + AF |

---

### 4.3 childThreats (17) · ~90% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1 | ✅ | — |
| L2 | ✅ parental | regression |
| L3 | ⚠️ monitoring detail | `pc-01…06`, `R5-G1…G3` |

| ID | Gap | Задача |
|----|-----|--------|
| `chd-01` | monitoring/detail mock envelope | `pc-01`, `pc-02` |
| `chd-02` | messages/calls modals | `pc-03` |
| `chd-03` | PDF reports TODO | `pc-04`, `pc-05` |
| `chd-04` | geofence geocode | `loc-04` |
| `chd-05…17` | regression pass | `R5-G5` |

---

### 4.4 dataLeaks (12) · ~35% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1 | Analytics modals | `R2-G4/G5` Privacy Hub |
| L2 | protection + agents | `sec-*`, `dc-04`, `dw-*` |
| L3 | DW scan + cleanup + location | `dw-*`, `dc-*`, `loc-*`, `R2-*` |

| ID | Угроза | L3 |
|----|--------|-----|
| `dlk-01` | Email breach | DW scan → breaches[] |
| `dlk-02` | Phone leak | DW phone ingest |
| `dlk-03` | Password reuse | HIBP-style check |
| `dlk-04` | Dark web mention | scan job |
| `dlk-05` | Broker data | cleanup agent |
| `dlk-06` | EXIF leak | comp-08 |
| `dlk-07` | Tracker leak | anti-tracker |
| `dlk-08` | Location leak | location bubble |
| `dlk-09` | Cloud misconfig | device audit |
| `dlk-10` | Screenshot leak | education + hub tip |
| `dlk-11` | Metadata | cleanup record |
| `dlk-12` | Public profile | DW social scan |

---

### 4.5 deepfakes (8) · ~15% → 100%

Полный трекер: `ANTIFAKE_PRODUCTION_TODO.md` (72 задачи).

| Уровень | Решение |
|---------|---------|
| L1 | Antifake Hub 4 вкладки (`af-6-*`) — **не онбординг** |
| L2 | SEC-INFRA |
| L3 | `/api/antifake/check/*` + jobs (`af-2-*`, `af-3-*`) |

| ID | Угроза | L3 |
|----|--------|-----|
| `dfk-01` | Fake video | video job verdict |
| `dfk-02` | Fake audio/voice | audio job |
| `dfk-03` | Fake news | text check |
| `dfk-04` | Fake document | document job |
| `dfk-05` | Spoofed call | call/analyze |
| `dfk-06` | Fake URL/media | url check |
| `dfk-07` | AI-generated image | image pipeline |
| `dfk-08` | Voice clone | audio + call |

---

### 4.6 internetThreats (6) · ~95% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1–L3 | VPN/Network уже сильные | `R6-G5` regression smoke |
| Gap | DNS/filter stats в ProtectionStats | `av-05` real numbers |

---

### 4.7 mobileThreats (10) · ~20% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1 | Device Hub mobile section | `R4-G5`, `mob-03` |
| L2 | mobileThreats toggle | `mob-05`, `sfm-06` |
| L3 | mobile_security_agent | `mob-01…02`, `R4-G4` |

---

### 4.8 familyThreats (15) · ~85% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L3 gaps | Family modals API, rewards sync | `pc-03`, gamification regression |
| | Emergency contacts real | family API audit |

---

### 4.9 iotThreats (10) · ~20% → 100%

| Уровень | Решение | Задачи |
|---------|---------|--------|
| L1 | IoT screen | `iot-03` fix threat wire |
| L2 | iotThreats toggle | `iot-05` |
| L3 | home scan API | `iot-01…02`, `R4-G3` |

---

## 5. Удаление всех mock (инвентарь)

| Mock | Где | Замена | Задача |
|------|-----|--------|--------|
| `3.0.0-mock-real-protection` | wildcard envelope | 404/503 | `sec-05` |
| `OptimizedSFM` 4 functions | sfm_singleton.py | Agent Registry | `sfm-03` |
| `status:success` fallback | start_sfm_core_http.py | 503 | `sfm-04` |
| `functions_count:1074` | :8003 health | real registry count | `sfm-02` |
| protection DB stub | protection.py | PostgreSQL | `sec-02` |
| `loadSettingsFromServer` stub | iOS | real GET | `sync-01` |
| Settings scan TODO buttons | Malware/Phishing/IoT | API wire | `comp-01…04`, `iot-03` |
| Elderly mockData | 09_ElderlyInterfaceScreen | API | `eld-01` |
| ios-functional-138 pass on 404 | runner | fail on 404/mock | `sec-08` |
| EXTENDED_138 all ok | checklist | L3 criterion | `R8-G1` |

---

## 6. Фазы (сводка)

| Фаза | Нед | Фокус | Gate |
|------|-----|-------|------|
| **0** SEC-INFRA + SFM Registry | 1–2 | L2 всех 9 toggles; no mock | `R0-G1…G8`, `sfm-01…06` |
| **1** Antifake Hub | 3–4 | deepfakes L3 | `R1-G1…G10` |
| **2** Privacy Hub | 3 | dataLeaks L3 | `R2-G1…G8` |
| **3** Identity Hub | 2–3 | fraud L3 | `R3-G1…G6` |
| **4** Device Hub | 4–5 | cyber+mobile+iot L3 | `R4-G1…G9` |
| **5** Family polish | 1–2 | child L3 100% | `R5-G1…G5` |
| **6** Extras | 2 | crash/roadside/elderly | `R6-*` |
| **7** COPY | 1 | FAQ/tariffs **не онбординг** | `R7-G2…G5` |
| **8** QA 138 | 1+ | TestFlight L3 sign-off | `R8-*` |

**Оценка:** 14–18 недель · 2 backend + 2 iOS.

---

## 7. Счёт задач (обновлённый)

| Секция | Задач |
|--------|-------|
| SEC | 10 |
| SFM | 12 |
| AF | 72 |
| DW+ID+DC+LOC | 28 |
| AV+COMP+IOT+MOB | 31 |
| PC-MON+EM+ELD | 16 |
| SYNC+COPY | 10 |
| CAT per-threat IDs | 58 |
| Roadmap gates | 47 |
| **Итого уникальных** | **~210** (с перекрытием gate/master) |

---

## 8. Критерий «100% готово»

Для **каждой** из 138 функций:

1. **L1** — видна в каталоге/Hub (онбординг не трогаем).
2. **L2** — toggle persist после kill app + server reload.
3. **L3** — TestFlight: действие → осмысленный результат, `source: real_agent`, не пустой `result`.
4. Prod logs 24h: **ноль** `mock-real-protection` на security paths.

---

*Документ объединяет SECURITY_100_PERCENT_MASTER_PLAN, gap analysis и prod audit 09.06.2026.*
