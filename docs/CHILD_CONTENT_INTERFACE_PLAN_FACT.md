# Детский контент и интерфейс: план vs факт (краткий аудит)

**Для следующей ML-системы:** полный onboarding и индекс всех связанных файлов — **`docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md`**. Каталог **275** пунктов и статусы — **`docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`**.

Канонический трек: `NEXT_VERSION_IMPLEMENTATION_PLAN.md` (Track A, фазы 0–9). Длинный чат-список из «89 микрозадач» — это **roadmap и контент-объём**, а не построчный чеклист репозитория; ниже — как это соотносится с текущим кодом.

## Архитектура контента (фазы 1–3 в плане)

| Область | Статус | Где в коде |
| --- | --- | --- |
| ContentManager / sync / version / cache | Реализовано | `Core/Content/` |
| Локальное хранилище | **Персистентность v1 (JSON на диске)**, не CoreData | `ContentDatabase.swift` |
| Модели Item / Category / Progress / Metadata | Реализовано | `ContentModels.swift` и связанные типы |
| API + оффлайн | Реализовано (сеть + seed / last-known-good) | `ContentSyncManager`, `ContentSeedProvider`, клиенты API |
| Подпись манифеста | **Реальная проверка P-256**, fail-closed | `ContentValidator.verifySignature` |

## «190 единиц контента» по возрастам (чат-план)

| Сегмент | План в чате | Факт в приложении |
| --- | --- | --- |
| 1–6 / 7–12 / 13–22, сотни тематических единиц | Полный каталог | В плане зафиксирован как **roadmap v2+**; в клиенте — **MVP pipeline + seed/серверный контракт**, а не готовый каталог на все позиции чата |

## Детский UI

| Поверхность | Назначение |
| --- | --- |
| `08_ChildInterfaceScreen.swift` | Оболочка детского режима |
| `ChildContentScreen.swift` | Лента/категории контента |
| `ParentDashboardView.swift` | Зеркало для родителя |
| Награды / игры | `ChildRewardsScreen`, `RewardsModalView`, `RewardsQuickModal`, `GamesParentalControlScreen` |

## Родительский gate (обязательный in-app)

Чувствительные действия должны проходить `ParentSessionGate.confirmSensitiveAction` (биометрия при наличии; иначе — PIN-сессия в TTL после `verifyParentalPIN`). Статическая проверка wiring: `scripts/trackb_mandatory_parental_control_smoke.py`.

Остаётся продуктовый долг: **inline-редактирование** (тогглы ± в `RewardsModalView` без отдельного шага gate) — по смыслу то же окно уже только для родителя по роли; при ужесточении модели угроз можно обернуть и эти контролы.
