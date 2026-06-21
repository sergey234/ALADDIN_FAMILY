# Rive Apple Runtime — справка для ALADDIN iOS (запомнить)

**Индекс доков Rive:** https://uat.rive.app/docs/llms.txt  
**Apple runtime:** https://rive.app/docs/runtimes/apple  
**GitHub:** https://github.com/rive-app/rive-ios  
**SPM:** `https://github.com/rive-app/rive-ios` (from `6.13.0+`)

---

## ALADDIN iOS — что используем сейчас

| Параметр | Значение в проекте |
|----------|-------------------|
| API | **Legacy Runtime** — `RiveViewModel`, не новый `Rive` + `Worker` + `File` |
| Import | `import RiveRuntime` |
| Хост | `UI/Companion/CompanionHeroRiveHost.swift` |
| Artboard | **`Hero360`** (360×480) |
| State Machine | **`HeroSM`** |
| Inputs | 13 triggers (`idle`, `listening`, …) + Number **`mouth_open`** 0…1 |
| Файлы | `Resources/Companion/{unicorn,aladdin,genie}.riv` в бандле |
| Мин. размер | ≥ 25 KB (`productionRivMinBytes`) — иначе PNG fallback |

**Не мигрировать на New Runtime** без отдельной задачи — Companion завязан на `RiveViewModel`.

---

## Legacy vs New Runtime (из официальной доки)

### Legacy (наш путь)

```swift
import RiveRuntime

RiveViewModel(fileName: "unicorn").view()  // SwiftUI
// artboard + stateMachine задаются в CompanionHeroRiveHost.makeRiveViewModel
```

- Один поток — **main thread**
- `viewModel.triggerInput("idle")`, `setInput("mouth_open", value:)`

### New Runtime (справочно, не в проде ALADDIN)

```swift
let worker = try await Worker()
let file = try await File(source: .local("unicorn", Bundle.main), worker: worker)
let rive = try await Rive(file: file)  // default artboard + SM если заданы в editor
```

- `@MainActor` на API
- Data Binding / ViewModelInstance — опционально; Companion использует **triggers + mouth_open**

---

## Default artboard (почему warning в Editor)

Если в `.riv` не задан default artboard, Rive Editor показывает warning.  
iOS **явно** указывает `Hero360` в `CompanionHeroRiveHost` — export всё равно лучше с default = Hero360.

---

## Export workflow (отдельно от runtime)

1. Editor source: `unicorn_golden_amp.rev` (cloud: `editor.rive.app/file/unicorn_golden_amprev/2319314`)
2. **Export → For runtime** → `Resources/Companion/unicorn.riv`
3. Verify: `python3 scripts/companion_07_verify_unicorn_riv.py unicorn`
4. **Только unicorn OK** → patch aladdin/genie (`companion_07_patch_riv_hero_image.py`)

---

## QA

- Rive на **реальном iPhone iOS 16+** (не iOS 15.2 Simulator — Metal issues)
- Console filter: `[CompanionHero]`
- Примеры Apple: `Example-iOS` в rive-ios repo (Marty, QuickStart, Player)

---

## Связанные файлы

- `docs/COMPANION_RIVE_EXPORT_CHECKLIST.md`
- `docs/COMPANION_RIVE_EDITOR_5_STEPS.md`
- `docs/HERO_PREBUILD_RIVE_EXPORT_GUIDE.html`
- `docs/LOG_ANALYSIS_ML_HANDOFF.md` (hero-prebuild-*)
