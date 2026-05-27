# Companion Platform — передача дел ML-системе (актуально)

**Дата handoff:** 2026-05-27  
**Предыдущий handoff:** [COMPANION_ML_HANDOFF_FULL.md](./COMPANION_ML_HANDOFF_FULL.md) (частично устарел по счётчикам)  
**Рабочий корень:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## 0. С чего начать (5 минут)

1. Прочитать **§1** (что строим) и **§2** (главный план — ссылки).  
2. Открыть **[COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)** — единый TODO-лист **102 задачи** с галочками.  
3. Текущий фокус: **HERO-3** (3 героя 2D Rive) — §6.  
4. Не трогать онбординг Figma `KvkUdyb5Ll31Z9FSzCbpNl` (read-only).  
5. Prod: не mock bypass — [.cursor/rules/prod-no-mock-bypass.mdc](../.cursor/rules/prod-no-mock-bypass.mdc).

**Прогресс:** **64 / 102 (63%)** · **HERO-3: 23 / 26** · **P0 ✅** · **P1 ✅** · **CX ✅** · **OPS ✅** · **10 deploy+verify ✅ 27.05** · **08b UI ⏳**

---

## 1. Что мы строим (одним абзацем)

**ALADDIN Companion** — детский/семейный AI-компаньон (аналог Grok для Kids): **3 героя** (единорог, Аладин-человек, джин), вход из **Kids/Игры**, экран **Hub + Conversation** с layout **56% герой / субтитр**, **12 эмоций + lip-sync**, голос WebSocket, trust, родительское согласие, память, threads. Визуал: **2D Rive** (не 3D) в стиле онбординга. Backend: FastAPI на `aladdin-ai.ru:8002`, SQLite P0.

---

## 2. Главный план (иерархия документов)

| Уровень | Документ | Роль |
|---------|----------|------|
| **Roadmap продукта** | [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md) | P0→P3, фазы, метрики, §11 чеклист |
| **3 героя Figma→Rive** | [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) | §1–11, Motion §2.2, Mimic §2.3, wireframes |
| **2D vs 3D (ADR)** | [COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md) | Утверждено: остаёмся на 2D Rive |
| **Спринтовые TODO (детали)** | [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) | Описание каждой задачи P0, P1, HERO-3… |
| **Ежедневный трекер** | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | **Главный TODO-лист** `[x]` / `[ ]` |
| **Матрица HERO-3** | [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md) | Spec / BE / iOS / .riv / QA по ID |
| **Верификация / GATE** | [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) | GATE-EMO, D10, device |
| **Grok parity** | [GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md) | API, UX §6.2 layout |
| **Матрица 102 фич** | [GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md) | Трассировка ID |

---

## 3. Полный TODO-лист (102 задачи)

**Источник истины:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)

| Блок | Готово | Всего | Статус |
|------|--------|-------|--------|
| P0 MVP | 19 | 19 | ✅ |
| P1 | 11 | 11 | ✅ |
| CX | 6 | 6 | ✅ |
| OPS | 4 | 4 | ✅ |
| **HERO-3** | **23** | **26** | см. §6 |
| P1+ | 0 | 12 | после HERO-3 |
| P2 | 1 | 17 | |
| P3 | 0 | 6 | |
| Adult | 0 | 3 | отдельный продукт |
| GATE | 0 | 12 | в конце |
| **Итого** | **64** | **102** | |

**Порядок HERO-3 (актуальный):**  
`17` `02` ✅ → **`07` art** + **`08` verify device** → **`09` Bible** → **`10` deploy** → **`11` QA** → GATE.

---

## 4. Индекс файлов (что открывать по задаче)

### 4.1 Документация (docs/)

| Файл | Когда читать |
|------|----------------|
| `COMPANION_PROGRESS_TRACKER.md` | Каждый день — галочки |
| `COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md` | HERO-3, Figma, Motion |
| `COMPANION_RIVE_EXPORT_CHECKLIST.md` | **HERO-3-07** export .riv |
| `COMPANION_RIVE_UNBLOCK.md` | SPM RiveRuntime, кэш Xcode |
| `COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md` | PO sign-off Motion/Mimic |
| `COMPANION_FIGMA_PRODUCT_DECISIONS.md` | Продуктовые решения |
| `COMPANION_DEPLOY_P0.md` | Деплой, env, nginx |
| `COMPANION_ML_HANDOFF_2026-05-27.md` | **Этот файл** |
| `COMPANION_ML_HANDOFF_FULL.md` | SSH, BE история (доп.) |
| `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | SSH `149.154.65.180` |

### 4.2 iOS — Companion UI / Rive

| Файл | Назначение |
|------|------------|
| `Screens/CompanionHubScreen.swift` | Выбор героя |
| `Screens/CompanionConversationScreen.swift` | Разговор 56% + субтитр |
| `UI/Companion/CompanionHeroLayout.swift` | Метрики 56%/28% |
| `UI/Companion/CompanionDialogueStrip.swift` | Субтитр Grok-style |
| `UI/Companion/CompanionHeroAvatarView.swift` | Rive vs fallback |
| `UI/Companion/CompanionHeroAnimatedView.swift` | Процедурная сцена |
| `UI/Companion/CompanionHeroRiveHost.swift` | RiveRuntime host |
| `UI/Companion/CompanionHeroEmotion+Timeline.swift` | Debounce 400ms |
| `Core/Services/CompanionAPIService.swift` | REST JWT |
| `Core/Models/CompanionModels.swift` | DTO + `CompanionHeroEmotion` |
| `Resources/Companion/*.riv` | unicorn, aladdin, genie (placeholder) |

### 4.3 iOS — проект / зависимости

| Файл | Назначение |
|------|------------|
| `ALADDIN.xcodeproj/project.pbxproj` | SPM `rive-ios` 6.20.5 exact |
| `Podfile` | `RiveRuntime ~> 6.0` (запасной путь) |
| `scripts/reset_rive_spm_cache.sh` | Починка кэша SPM / XCFramework |
| `scripts/companion_riv_size_gate.py` | Gate &lt;500KB ×3 |
| `scripts/deploy_companion_p0.sh` | Деплой BE |
| `scripts/verify_companion_p0_prod.sh` | Verify prod |

### 4.4 Backend

| Файл | Назначение |
|------|------------|
| `security/api/routers/ai_companion_router.py` | Companion API |
| `security/services/ai_platform/` | policy, persona, emotions |
| `Tests/test_companion_*.py` | Smoke / persona / emotions |

### 4.5 Figma (не править onboarding)

| Ресурс | ID / URL |
|--------|----------|
| **Companion** (3 героя) | `vwKcGPUUEZjgayEHNn0BJM` — `00_Spec`, `01_Unicorn`, `02_Aladdin_Human`, `03_Genie` |
| **Onboarding** (read-only) | `KvkUdyb5Ll31Z9FSzCbpNl` — OB_00–07 |

Env Figma: `docs/FIGMA_COMPANION.env` (если есть).

---

## 5. Сделано до 2026-05-27 (отметить в работе)

### 5.1 Продукт / архитектура ✅
- ADR 2D Rive, Grok-layout 56% + subtitle  
- Figma 3×12 wireframes (HERO-3-02)  
- Motion + Mimic sign-off PO (HERO-3-17)  
- BE: 3 persona, genie age_policy, cosmetics, emotions sync  

### 5.2 iOS инженерия ✅
- Hub 3 карточки, Conversation, API JWT (`CompanionAPIService` + `NetworkManager()` @MainActor)  
- Grok UI: `CompanionHeroLayout`, `CompanionDialogueStrip`  
- Эмоции 13, debounce 400ms, stream thinking, sad/comfort без playful  
- **Xcode project compiles** (2026-05-27): исправлены Rive SPM, iOS 15 `onChange`, `Color` vs RiveRuntime, `CompanionChatResponse.cosmeticUnlocked`, `ALADDINNavigationBar` companion cases  
- SPM **RiveRuntime 6.20.5**, `CompanionHeroRiveHost`, placeholder `.riv` ×3 в бандле  
- `companion_riv_size_gate.py` 3/3 OK  

### 5.3 ⏳ Не закрыто по DoD
- **HERO-3-07** production `.riv` от аниматора  
- **HERO-3-08** проверка на device: Rive vs emoji fallback  
- **HERO-3-09** Character Bible  
- **HERO-3-10** deploy verify 3 characters  
- **HERO-3-11** MOTION/MIMIC-Q, D10  
- TestFlight, GATE-EMO  

---

## 6. HERO-3-07 и HERO-3-08 — блокеры?

| ID | Инженерный блокер? | DoD закрыт? | Действие |
|----|-------------------|-------------|----------|
| **07** | **Нет** (placeholder + gate OK) | **Нет** | Аниматор: 3× `.riv` по [checklist](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| **08** | **Нет** (сборка OK) | **Почти** | 5 мин: симулятор → Companion → виден Rive |

**Скрипт если Rive SPM сломается снова:**
```bash
cd mobile_apps/ALADDIN_iOS
./scripts/reset_rive_spm_cache.sh
```

---

## 7. Оставшаяся работа — как делать (по приоритету)

### 7.1 Параллельно (без аниматора)

| # | ID | Что | Как |
|---|-----|-----|-----|
| 1 | **HERO-3-09** | Character Bible | Markdown в `docs/`, 3 героя: голос, табу, возраст, референсы OB |
| 2 | **HERO-3-10** | Deploy + verify | `./scripts/deploy_companion_p0.sh` + `verify_companion_p0_prod.sh`, 3 `character_id` |
| 3 | **HERO-3-22** | CI hook | GitHub Action: `python3 scripts/companion_riv_size_gate.py` |
| 4 | **P1-10** | Аналитика N1–N6 | События iOS + BE, без PII |
| 5 | **OPS-04** | LLM cost alert | Мониторинг на VPS |

### 7.2 Дизайн / анимация

| # | ID | Что | Как |
|---|-----|-----|-----|
| 6 | **HERO-3-07** | Production `.riv` | Rive Editor 360×480, SM: triggers `idle`…`excited`, Number `mouth_open` → `Resources/Companion/` |
| 7 | **HERO-3-02** | Final art в Figma | Страницы `01`–`03` в `vwKcGPUUEZjgayEHNn0BJM` |

### 7.3 После .riv + device

| # | ID | Что | Как |
|---|-----|-----|-----|
| 8 | **HERO-3-11** | QA | [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) D10, MOTION-Q, MIMIC-Q |
| 9 | GATE | GATE-HERO-3-IOS-α, GATE-EMO, GATE-EMO-EMPATHY | Device Kids |
| 10 | — | TestFlight | Трекер § «В конце» |

### 7.4 P1+ / P2 (после HERO-3)

См. [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) § P1+, P2, P3, Adult.

---

## 8. Правила для ML-системы

1. **Deployment target iOS 15.2** — не использовать `onChange(of:) { _, new in }` (iOS 17), не `NavigationStack` без `@available`, не `Locale.current.language` (iOS 16).  
2. **Не импортировать `RiveRuntime` в файлы со `SwiftUI.Color`** — конфликт типов `Color`; Rive только в `CompanionHeroRiveHost.swift`.  
3. **Новый экран** → добавить cases в `NavigationManager.ALADDINScreen` + `ALADDINNavigationBar.navigationLocalizationKey()`.  
4. **Companion только Kids/Игры** — genie не для child без policy.  
5. **Деплой** только `/opt/aladdin-backend`, не telegram-shop bot.  
6. **Обновлять** трекер + матрицу при закрытии задачи.  

---

## 9. Команды быстрого старта

```bash
ROOT=/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
cd "$ROOT"

# Gate .riv
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion

# BE smoke
PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py

# iOS (после открытия Xcode)
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 16' build

# Prod verify (нужен SSH)
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

---

## 10. Контакты / эскалация

- Prod issues: `COMPANION_DEPLOY_P0.md`, server guide  
- Figma Companion: file key `vwKcGPUUEZjgayEHNn0BJM`  
- При расхождении счётчиков — править **COMPANION_PROGRESS_TRACKER.md** первым  

---

*Документ подготовлен для передачи следующей ML-системе. Синхронизирован с трекером от 2026-05-27.*
