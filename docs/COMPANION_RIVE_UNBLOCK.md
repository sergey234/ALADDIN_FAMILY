# Companion Rive — снятие блокеров 07 / 08 (простым языком)

**Статус 2026-05-27:** **08** — Xcode build ✅ · **07** — placeholder 3/3, production art ⏳ · Handoff: [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md)

## Что было «блокером»

| Блокер | Простым языком | Что сделали |
|--------|----------------|-------------|
| **07 файлы** | В приложении должны лежать 3 анимации `.riv` | ✅ `unicorn` + `aladdin` + **`genie.riv`** (пока placeholder ~15 KB) |
| **07 «красивый арт»** | Нужны финальные 2D-лица как в онбординге | ⏳ **отдельный трек дизайна** — файлы меняются без правок Swift |
| **08 RiveRuntime** | Библиотека, которая **проигрывает** `.riv` (без неё — emoji) | ✅ **Swift Package** в `ALADDIN.xcodeproj` + Podfile |

## Два слоя (важно)

1. **Инженерия (разблокировано)** — 3 файла в бандле, Rive подключён, сцена 56% + субтитр.  
2. **Дизайн (параллельно)** — заменить placeholder на art 360×480 из Figma/Rive ([чеклист](./COMPANION_RIVE_EXPORT_CHECKLIST.md)).

## Ошибка Xcode: `There is no XCFramework found at .../RiveRuntime.xcframework`

После очистки кэша `xcodebuild -resolvePackageDependencies` **не всегда распаковывает** zip — в `DerivedData` остаётся пустая папка `artifacts/extract/rive-ios`.

**Исправление:** тот же скрипт (ниже) — он скачивает zip и кладёт `RiveRuntime.xcframework` в  
`DerivedData/ALADDIN-*/SourcePackages/artifacts/rive-ios/RiveRuntime/`.

## Ошибка Xcode: `already exists in file system` (RiveRuntime.zip)

Типичный баг **SwiftPM**: в кэше остался **битый** или **пустой** файл `RiveRuntime.xcframework.zip`, повторная загрузка падает с `fatalError`.

**Исправление (1 команда):**

```bash
cd mobile_apps/ALADDIN_iOS
chmod +x scripts/reset_rive_spm_cache.sh
./scripts/reset_rive_spm_cache.sh
```

Скрипт: удаляет артефакт в `~/Library/Caches/org.swift.swiftpm/artifacts/` и `DerivedData/.../SourcePackages/artifacts/rive-ios`, скачивает zip с GitHub, проверяет checksum, вызывает `xcodebuild -resolvePackageDependencies`.

Вручную в Xcode (после закрытия проекта): **File → Packages → Reset Package Caches** → **Resolve Package Versions**.

## Один раз в Xcode (если пакет не подтянулся)

1. Открыть **`ALADDIN.xcodeproj`** (или `.xcworkspace` если используете CocoaPods).  
2. **File → Packages → Resolve Package Versions** (должен подтянуть `rive-ios` **6.20.5**).  
3. **Product → Clean** → **Build** на симуляторе.  
4. Companion → **Мир героев** → **Главное**: на **реальном iPhone** — **Rive**; симулятор **iOS 15.x** — Rive выключен (нет краша), 08b PASS только на device ([08b](./COMPANION_08B_DEVICE_CHECKLIST.md)).

### Альтернатива: CocoaPods

```bash
cd mobile_apps/ALADDIN_iOS
pod install
open ALADDIN.xcworkspace
```

В `Podfile` уже есть `pod 'RiveRuntime', '~> 6.0'`.

## Проверка

```bash
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
# OK ×3

python3 scripts/companion_riv_size_gate.py --dir Resources/Companion  # exit 0
```

## ADR

[COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md) — остаёмся на **2D Rive**, не 3D.
