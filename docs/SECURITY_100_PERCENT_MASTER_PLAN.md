# ALADDIN Security — план доработки на 100% (L1 + L2 + L3)

**Версия:** 1.0 · **2026-06-09**  
**Цель:** каждая из **138 функций** и каждое **маркетинговое обещание** работает на трёх уровнях.  
**Связанные трекеры (позже объединим в один):**
- `.cursor/SECURITY_138_MASTER_TODO.md` — реестр задач по доменам
- `.cursor/ANTIFAKE_PRODUCTION_TODO.md` — детальный anti-fake
- `.cursor/SECURITY_100_PERCENT_ROADMAP_TODO.md` — **этот план** по фазам L1/L2/L3

**Анализ разрывов:** `docs/SECURITY_138_GAP_ANALYSIS.md`

---

## 1. Три уровня — что значит «100%»

| Уровень | Вопрос | Критерий готовности | Кто проверяет |
|---------|--------|---------------------|---------------|
| **L1 Продукт** | Пользователь **видит** функцию? | Текст в тарифе, onboarding, FAQ, экран/Hub, Premium lock понятен | Дизайн + copy |
| **L2 Система** | Настройка **доходит до сервера** и **сохраняется**? | Toggle → API 200 → reload → то же состояние; JWT; Premium на сервере | Backend + iOS sync |
| **L3 Действие** | Пользователь **получает результат**? | Скан / вердикт / блок / уведомление с реальными данными; не пустой `result` | TestFlight + prod smoke |

**100% для ALADDIN** = по каждой заявленной функции **L1 + L2 + L3**.  
Переключатель без результата = максимум **40%** (L1+L2 без L3).

---

## 2. Фундамент SEC-INFRA — «крыша дома» (Фаза 0)

Пока не сделано — **ни один Hub не считается готовым**, даже если экран красивый.

### Что сломано сегодня (проверено на проде)

| # | Проблема | Простыми словами | Целевое состояние |
|---|----------|------------------|-------------------|
| S1 | `protection/enable` → 500 | Нажал «включить» — ошибка | Всегда 200, категория включена |
| S2 | settings POST OK, GET — false | Сервер «забывает» | UPSERT в PostgreSQL |
| S3 | iOS не грузит settings с сервера | Телефон живёт сам по себе | `loadSettingsFromServer` при старте |
| S4 | JSON schema mismatch | Телефон и сервер говорят на разных языках | Один формат `categories` |
| S5 | Wildcard mock | Любой URL — пустой «фейковый» ответ | Только явные роутеры; иначе 404/503 |
| S6 | SFM singleton mock | «Мозг» безопасности — заглушка на 4 функции | Registry агентов per domain |
| S7 | Чеклист 138 = HTTP code | «Работает» на 404 | Приёмка только с L3 на устройстве |

### Фаза 0 — deliverables

1. Миграция `user_protection_settings`
2. Починка `protection.py` (logger, persist, тесты)
3. iOS adapter `ProtectionSettings` ↔ server
4. `main.py`: blocklist wildcard для security paths
5. Gateway guard: reject `mock-real-protection` + empty `result`
6. `test_security_prod_smoke.py` — assert L2/L3
7. Документ **канонических category IDs**

**После Фазы 0:** все 9 переключателей категорий = честный **L2** для 100 угроз.

---

## 3. Архитектура «идеально» — 5 Security Hubs

Вместо 100 экранов — **5 центров действия** + parental (уже сильный) + VPN (уже сильный).

```
┌─────────────────────────────────────────────────────────────┐
│  SEC-INFRA (фаза 0) — toggles, sync, no mock                │
└─────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼          ▼          ▼
 Antifake  Identity   Privacy    Device     Family
  Hub       Hub        Hub        Hub        (готов ~90%)
 8 угроз   fraud+ID   DW+DC+LOC  AV+MOB+IOT  parental 32
```

| Hub | Категории / функции | L3 «что видит пользователь» |
|-----|---------------------|------------------------------|
| **Antifake** | deepfakes 8 | «Фейк 87%» / «Похоже на правду» |
| **Identity** | fraud 12 (часть) | «Попытка кражи личности» / мониторинг СНИЛС |
| **Privacy** | dataLeaks 12 | «Email найден в 3 утечках» / «Данные удалены с брокера» |
| **Device** | cyber 10 + mobile 10 + iot 10 | «Найден троян» / «Умная камера уязвима» |
| **Family** | child 17 + family 15 | Уже: блокировки, гео, отчёты — добить monitoring L3 |

**Internet 6** → VPN Hub (уже L3).  
**Parental 32** → Family Hub (добить PC-MON).

---

## 4. Доменный анализ (как anti-fake)

### 4.1 ANTIFAKE — deepfakes (8 угроз) · Приоритет P0

| | Сейчас | Нужно для 100% |
|---|--------|----------------|
| **L1** | ✅ Тарифы, FAQ, toggle, onboarding | Hub-экран, 4 вкладки |
| **L2** | ❌ enable 500, no persist | SEC-INFRA + category `deepfakes` |
| **L3** | ❌ API пустой mock | `/api/antifake/check/*` + jobs + verdict |

**L3 по каждой угрозе:**

| # | Угроза | L3 действие |
|---|--------|-------------|
| 1 | Deepfake-видео | Загрузил видео → вердикт |
| 2 | Поддельные голоса | Загрузил аудио / голосовое → вердикт |
| 3 | Спуфинг номера | Post-call + caller ID heuristics |
| 4 | Поддельные сайты | URL check + Share Extension |
| 5 | Фейковые новости | Text check |
| 6 | Поддельные документы | Фото документа → job |
| 7 | Фейковые профили | Text + фото |
| 8 | Email spoofing | Text mode email |

**Трекер:** `ANTIFAKE_PRODUCTION_TODO.md` (72 задачи).

---

### 4.2 PRIVACY HUB — dataLeaks (12 угроз) · P0

#### Dark Web (угроза #34 и др.)

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Modal в Analytics, Advanced toggle | Scan CTA, история утечек |
| **L2** | ⚠️ stats user-scoped после фикса E-batch | scan/start persist, premium gate |
| **L3** | ⚠️ «0 утечек» без реального scan flow | Email check → список breaches или честное «не найдено» |

**Как сделать:** `dw-01…08`, router без wildcard, agent `dark_web_monitoring_agent`, iOS poll job.

#### Personal Data Cleanup

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Sheet в Advanced Protection | Progress + список брокеров |
| **L2** | ⚠️ toggle локальный | `POST cleanup/start` + status |
| **L3** | ❌ нет результата | «Запрос на удаление отправлен» / отчёт |

#### Location / EXIF / trackers (часть dataLeaks)

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Location bubble toggle | Карта bubble vs точная точка |
| **L2** | ❌ | API settings persist |
| **L3** | ❌ | `generate` bubble + privacy stats из reports |

**Трекер:** MASTER `DW`, `DC`, `LOC`.

---

### 4.3 IDENTITY HUB — fraud (12 угроз) · P0

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Identity modal, tariff fraud list | Формы мониторинга, история попыток |
| **L2** | ⚠️ reports stats only | SNILS/credit/fraud endpoints + toggle→agent |
| **L3** | ❌ | «Обнаружена попытка» / «Чисто» с датой |

**Покрывает угрозы:** телефонное мошенничество, банки, карты, vishing, smishing (частично через antifake text), романтические аферы.

**Как сделать:** `id-01…08`, `russian_identity_theft_protection_agent`, единый verdict, **не путать** stats с detect.

---

### 4.4 DEVICE HUB — cyberThreats (10) + mobileThreats (10) + iotThreats (10) · P1

#### Antivirus / Malware (cyber)

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Network screen antivirus section, malware settings | Scan button активна |
| **L2** | ⚠️ AntivirusManager локально | `/api/antivirus/scan`, threats sync |
| **L3** | ❌ TODO на кнопках | EICAR test → quarantine → уведомление |

#### Component screens (phishing, network, mobile, incident)

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Экраны настроек | — |
| **L2** | ⚠️ ComponentStatusService | Explicit `/api/components/*` |
| **L3** | ❌ «Запустить скан» = TODO | Реальный scan + отчёт |

#### IoT

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ IoTSecurityScreen | Список устройств дома |
| **L2** | ❌ `home_default` | homeId из family |
| **L3** | ❌ fix threat TODO | Scan → уязвимости с severity |

#### Mobile

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Device detail | Mobile threats section |
| **L2** | ❌ | mobile_security_agent API |
| **L3** | ❌ | App risk / smishing via text hub |

**Трекер:** `AV`, `COMP`, `IOT`, `MOB`.

---

### 4.5 FAMILY HUB — childThreats (17) + familyThreats (15) · P1 добивка

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Parental Control, Family | — |
| **L2** | ✅ ~95% API | monitoring/detail без mock |
| **L3** | ⚠️ ~85% | Реальные messages/calls в FamilyModals; PDF reports |

**Единственный сегмент близок к 100%** — инвестиции точечные (PC-MON).

---

### 4.6 INTERNET — internetThreats (6) · уже ~95%

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ VPN screen | — |
| **L2** | ✅ settings sync | — |
| **L3** | ✅ connect/disconnect/stats | Safari Content Blocker отдельный трек |

**Действие:** regression smoke only; не блокирует общий план.

---

### 4.7 EXTRAS — 6 функций · P2

| Extra | L1 | L2 | L3 | Действие |
|-------|----|----|-----|----------|
| VPN | ✅ | ✅ | ✅ | maintain |
| AI Assistant | ✅ | ✅ | ✅ | tool integrations |
| Family | ✅ | ✅ | ✅ | — |
| Analytics | ✅ | ⚠️ | ⚠️ | modals → hubs |
| Elderly | ✅ | ⚠️ | ❌ mock calendar | ELD batch |
| Voice control | ⚠️ | ⚠️ | ⚠️ | component API |

#### Emergency (crash + roadside)

| | Сейчас | 100% |
|---|--------|------|
| **L1** | ✅ Crash alert UI, roadside sheet | Settings modal |
| **L2** | ❌ | API start/call/cancel |
| **L3** | ❌ | Реальный вызов помощи / crash log |

---

## 5. Единый шаблон домена (копировать на каждый Hub)

Для **каждого** домена (AF, DW, ID, …) одинаковые 7 шагов:

```
1. SEC-INFRA готов (L2 для категории)
2. Backend: explicit router в OpenAPI
3. Backend: agent/worker, NO wildcard mock
4. Contract: verdict + confidence + reasons
5. Premium gate server-side
6. iOS: Hub screen + history + AI tool (опционально)
7. QA: TestFlight L3 script + update checklist verify
```

---

## 6. Фазы объединённого плана (для слияния с anti-fake)

| Фаза | Название | Срок* | L-уровень | Трекеры |
|------|----------|-------|-----------|---------|
| **0** | SEC-INFRA «крыша» | 1–2 нед | L2 всех 100 | sec-01…10, af-0-* |
| **1** | Antifake Hub | 3–4 нед | L1+L2+L3 ×8 | AF-0…12 |
| **2** | Privacy Hub (DW+DC+LOC) | 3 нед | L3 dataLeaks 12 | DW, DC, LOC |
| **3** | Identity Hub | 2–3 нед | L3 fraud 12 | ID |
| **4** | Device Hub (AV+COMP+IOT+MOB) | 4–5 нед | L3 cyber+mobile+iot 30 | AV, COMP, IOT, MOB |
| **5** | Family polish | 1–2 нед | L3 monitoring | PC-MON |
| **6** | Extras (EM, ELD) | 2 нед | L3 extras | EM, ELD |
| **7** | COPY + QA gate | 1 нед | L1 честность | COPY, all smoke |
| **8** | 138 checklist rewrite | 3 дня | verify=L3 only | checklist regen |

*При 2 backend + 2 iOS параллельно ≈ **14–18 недель** до полного 100%.

---

## 7. Приёмка «идеально 100%»

Перед App Store submit:

- [ ] **9 категорий:** toggle → reload → same state (L2)
- [ ] **5 Hubs:** демо-видео L3 для каждого
- [ ] **138 строк** checklist: каждая с `verify=ok` только после TestFlight L3
- [ ] **0** ответов `mock-real-protection` в security paths (grep 24h logs)
- [ ] Onboarding/FAQ/tariffs = subset of L3-ready features only
- [ ] Premium free user: 403 на все check/scan API

---

## 8. Как соединить два плана позже

```
SECURITY_100_PERCENT_ROADMAP_TODO.md  (фазы 0–8, L1/L2/L3 gates)
           +
SECURITY_138_MASTER_TODO.md         (156 задач по ID)
           +
ANTIFAKE_PRODUCTION_TODO.md         (72 детальных AF)
           ═══════════════════════════════════════════
           →  SECURITY_UNIFIED_IMPLEMENTATION.md (будущий)
```

На этапе слияния: один файл, фазы 0→8, внутри каждой фазы — полный список task ID без дубликатов.

---

## 9. Заключение — наилучший путь

1. **Сначала крыша (Фаза 0)** — иначе любая «100%» функция снова сломается при sync.
2. **Потом Hubs с L3** — Antifake первый (самое громкое обещание Premium), затем Privacy и Identity (уже есть modals), затем Device (самый большой объём ML).
3. **Family не переписывать** — только monitoring и отчёты.
4. **VPN не трогать** — regression only.
5. **Один verdict contract** на все проверки — проще iOS, проще QA.
6. **Не SFM монолит** — 4–5 агентов с explicit routers.
7. **Честный L1** только после L3 готов — иначе App Store и семьи.

Это единственный путь к **реальным 100%**, а не к «138 галочек в таблице».
