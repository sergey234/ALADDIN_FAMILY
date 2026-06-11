# Anti-Fake Production Plan — 100% deepfakes category

**Версия:** 1.0 · **2026-06-09**  
**Трекер:** `.cursor/ANTIFAKE_PRODUCTION_TODO.md` (72 задачи, 13 батчей)  
**Не MVP:** все 8 под-угроз категории `deepfakes` + Premium gate + метрики + без mock.

---

## 1. Проблема (аудит прода)

| Наблюдение | Влияние |
|------------|---------|
| Wildcard отдаёт `3.0.0-mock-real-protection`, `result: ""` | Ложная защита, нарушение prod policy |
| `protection/enable` → HTTP 500 (`logger` undefined) | Toggle deepfakes не работает |
| `protection/settings` POST OK, GET — всё false | Нет персистенции |
| iOS не вызывает antifake API | Нет user-visible value |
| SFM original не импортируется | Агенты не исполняются |
| `fake_news` agent: `No module named 'cv2'` | Даже прямой Python падает |
| FAQ/onboarding обещают real-time звонки | App Store / trust risk |

---

## 2. Принципы продакшена

1. **Явные роутеры** в OpenAPI — никакого wildcard для antifake.
2. **Единый verdict contract** на все check-API.
3. **Premium enforced на сервере** — UI toggle недостаточен.
4. **Media не храним** — temp disk + hash в job row, TTL 15 min.
5. **Sync text/url** · **async audio/video/document/call** — из-за CPU/RAM.
6. **Не поднимать весь SFM** — registry из 4 агентов + workers.
7. **Честный copy** — только то, что в билде (CallKit = post-call / screening, не «слушаем все звонки»).

---

## 3. Канонические category IDs

Единый список для iOS `ThreatProtectionCategory`, `protection.py`, БД:

| ID | iOS сегодня | Server `ALL_CATEGORIES` | Решение |
|----|-------------|-------------------------|---------|
| `cyberThreats` | ✅ | ✅ | keep |
| `fraud` | ✅ | — | keep, add server |
| `childThreats` | ✅ | — | keep, add server |
| `dataLeaks` | ✅ | ✅ | keep |
| `deepfakes` | ✅ | ✅ | keep |
| `internetThreats` | ✅ | — | keep |
| `mobileThreats` | ✅ | — | keep |
| `familyThreats` | ✅ | — | keep |
| `iotThreats` | ✅ | — | keep |
| `networkThreats` | — | ✅ | map → `internetThreats` alias server-side |
| `deviceProtection` | — | ✅ | map → `mobileThreats` |
| `dataProtection` | — | ✅ | map → `dataLeaks` |
| `identityProtection` | — | ✅ | keep as separate or merge fraud |
| `socialEngineering` | — | ✅ | map → `fraud` |
| `advancedThreats` | — | ✅ | map → `cyberThreats` |

**iOS POST body (новый адаптер):**

```json
{
  "categories": {
    "deepfakes": true,
    "cyberThreats": false
  },
  "globalLevel": 95
}
```

Внутри iOS `ProtectionSettings` может оставаться `enabledCategories` — маппинг только в `APIService`.

---

## 4. API спецификация

### 4.1 `POST /api/antifake/check/text`

**Auth:** Bearer JWT · **Premium:** required  
**Body:** `{ "text": string, "mode"?: "news" | "message" | "email" | "profile" }`  
**Response 200:** unified verdict (sync).

### 4.2 `POST /api/antifake/check/url`

**Body:** `{ "url": string }`  
**Agents:** phishing rules + redirect analysis.

### 4.3 `POST /api/antifake/check/audio|video|document`

**Content-Type:** `multipart/form-data`  
**Response 202:** `{ "job_id": "uuid", "status": "queued" }`

### 4.4 `GET /api/antifake/jobs/{job_id}`

**Response:** `{ "status": "queued|processing|completed|failed", ...verdict }`

### 4.5 `POST /api/antifake/call/analyze`

**Body:** multipart audio (m4a/wav) + optional `{ "caller_id": string, "display_name": string }`  
**Response:** 202 job_id — покрывает угрозы 3 (spoof) + 2 (voice).

### 4.6 `GET /api/antifake/metrics`

**Response:**

```json
{
  "checks_total": 0,
  "fake_detected": 0,
  "by_type": { "text": 0, "audio": 0, "video": 0, "call": 0 },
  "latency_p95_ms": 0
}
```

---

## 5. База данных

```sql
CREATE TABLE user_protection_settings (
  user_id BIGINT PRIMARY KEY,
  categories JSONB NOT NULL DEFAULT '{}',
  global_level INT NOT NULL DEFAULT 95,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE antifake_jobs (
  id UUID PRIMARY KEY,
  user_id BIGINT NOT NULL,
  job_type TEXT NOT NULL, -- text|url|audio|video|document|call
  status TEXT NOT NULL,
  input_hash TEXT,
  verdict JSONB,
  latency_ms INT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_antifake_jobs_user_created ON antifake_jobs(user_id, created_at DESC);
```

---

## 6. iOS экраны

| Экран | Назначение |
|-------|------------|
| `AntifakeHubScreen` | Entry из deepfakes category |
| `AntifakeTextCheckView` | Новости, сообщения, email paste |
| `AntifakeAudioCheckView` | Голосовые, VoiceNotes export |
| `AntifakeVideoCheckView` | Галерея / файлы |
| `AntifakeCallCheckView` | Импорт записи + CallKit hook |
| Share Extension | Safari / Telegram share sheet |

**Навигация:** `ThreatProtectionCategory.deepfakes.settingsScreen` → `.antifakeHub` (новый case в `NavigationManager`).

---

## 7. Звонки (реалистичный prod scope)

| Обещание в UI | Техническая реализация |
|---------------|------------------------|
| «Проверьте подозрительный звонок» | Post-call upload + analyze |
| «Подозрительный номер» | Call Directory block list + heuristics |
| «Голос не похож на знакомого» | Audio job на фрагменте записи |

**Не обещаем:** прослушивание всех звонков в фоне без действия пользователя (iOS restriction).

---

## 8. Деплой

1. Миграция SQL на prod (`aladdin_db`).
2. `pip install` в `/opt/aladdin-backend/venv`.
3. RQ worker systemd unit.
4. nginx `client_max_body_size` + timeouts для `/api/antifake/`.
5. `include_router(antifake)` в `main.py`.
6. `test_antifake_prod_smoke.py` — gate.

---

## 9. Acceptance (100% готовность)

- [ ] Все 8 угроз из `tariffs_threat_deepfake_*` имеют рабочий user path в Hub.
- [ ] Premium free user → 403 на check API.
- [ ] Нет mock в ответах antifake (automated grep).
- [ ] Settings deepfakes persist cross-device (same user).
- [ ] Share Extension работает из Safari.
- [ ] AI Assistant tool возвращает verdict в чате.
- [ ] Metrics отражают реальные проверки.
- [ ] App Store build с демо всех 4 типов проверки.

---

## 10. Связанные файлы (старт правок)

**Server:** `app/routers/protection.py`, `app/routers/antifake.py` (new), `main.py`, `security/ai_agents/*`  
**iOS:** `ProtectionSettingsManager.swift`, `APIService.swift`, `AppConfig.swift`, `ThreatProtectionCategory.swift`, `NavigationManager.swift`  
**Copy:** `LocalizationManager.swift`, `14_OnboardingScreen.swift`, `13_SupportScreen.swift`
