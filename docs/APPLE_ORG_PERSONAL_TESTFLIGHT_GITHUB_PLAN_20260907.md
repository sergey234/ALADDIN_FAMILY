# План: TestFlight с личного аккаунта через GitHub (Cursor)

**Дата:** 2026-09-07  
**Цель:** на iPhone владельца — тестовая сборка ALADDIN из **личного** App Store Connect / TestFlight.  
**Канал доставки:** GitHub Actions (workflow App Store / TestFlight), не «ручной Transfer на компанию».

Связанный handoff для другой ML: `docs/APPLE_ORG_ML_HANDOFF_TWO_PATHS_20260907.md`.

---

## Важно одной фразой

Сейчас Bundle `family.aladdin.ios` живёт на **личном** ASC → для TestFlight на телефон грузим билд, подписанный **личным** Team **`6CJVBBUGSN`**.  
Team компании **`B3WGHSWL79`** для этой задачи **не** использовать (его вернём после Transfer).

---

## Что уже успели поменять в коде (до этого плана)

| Изменение | Статус | Нужно для личного TF? |
|-----------|--------|------------------------|
| `DEVELOPMENT_TEAM` ×12 → `B3WGHSWL79` в `project.pbxproj` | сделано локально | **Нет — мешает.** Вернуть `6CJVBBUGSN` |
| Скрипты `ios_set_development_team.sh`, `ios_verify_signing_targets.sh` | новые | полезны |
| Docs `APPLE_ORG_*` | новые | для миграции, не блокируют TF |
| `ALADDIN/StoreKit/ALADDINSubscriptions.storekit` | новый | опционально в коммит |
| Bundle / App Group / Product ID / Swift UI | **не** трогали | — |

Build в проекте: **248** (канон bump с 247), version **1.0.0**.

---

## Шаги (порядок строгий)

### 1) Вернуть личный Team в Xcode-проекте

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/ios_set_development_team.sh 6CJVBBUGSN
./scripts/ios_verify_signing_targets.sh
# Ожидание: DEVELOPMENT_TEAM = 6CJVBBUGSN (единственный)
```

В Xcode: Signing & Capabilities → Team = личный аккаунт (тот же, что владеет TestFlight).

### 2) Поднять build number (если 247 уже в TestFlight)

Если 247 уже залита — bump до **248** (или следующий свободный) во всех targets.  
Иначе Apple отклонит duplicate build.

### 3) Узкий iOS-коммит (без бота и секретов)

В staging **только** то, что нужно для TF:

- `ALADDIN.xcodeproj/project.pbxproj` (личный Team + build)
- при желании: `scripts/ios_*.sh`, docs `APPLE_ORG_*` (не обязательно для самого upload)
- **НЕ** `telegram_stars_shop_bot/`
- **НЕ** `.env`, сертификаты с секретами, VPN handoff §32
- **НЕ** тысячи файлов из `BACKUPS/` если они случайно в diff

Перед коммитом:

```bash
git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$' && echo STOP || echo OK
```

Коммит — **только по явному GO владельца**.

### 4) Push в GitHub

```bash
git push origin master   # или рабочая ветка, если так принято
```

### 5) Запустить workflow App Store / TestFlight

- Файл: `.github/workflows/appstore.yml` (обычно `workflow_dispatch`)
- Secrets в GitHub должны быть от **личного** ASC:
  - `APP_STORE_CONNECT_API_KEY`
  - `APP_STORE_CONNECT_ISSUER_ID`
  - `APP_STORE_CONNECT_API_KEY_ID`
- Дождаться зелёных шагов: Archive → Export IPA → **Upload** (не archive-only)

Если upload skipped — билд **не** появится в TestFlight (см. fail-step в workflow).

### 6) App Store Connect (личный)

1. My Apps → ALADDIN → TestFlight  
2. Дождаться Processing → Ready to Test  
3. Добавить себя как Internal/External tester (как уже настроено)  
4. На iPhone: TestFlight → Install / Update  

### 7) Smoke на телефоне

- Запуск, логин, главный экран  
- VPN/семейные экраны по smoke-чеклисту владельца  
- Нет падения на старте  

### 8) После успешного TF — не забыть про миграцию

Личный TF ≠ миграция на компанию. Дальше по handoff: минимальный Store → Transfer → снова `B3WGHSWL79`.

---

## Что открыть локально

```bash
open ALADDIN.xcodeproj
```

Проверить Signing: Team = личный (`6CJVBBUGSN`), Bundle = `family.aladdin.ios`.

---

## Cursor TODO (id для агента)

См. задачи `tf-pers-*` в Cursor TODO этой сессии.

---

## Стоп-условия

- В pbxproj всё ещё `B3WGHSWL79` → **не** пушить для личного TF  
- В коммите есть `telegram_stars_shop_bot` или `.env` → **STOP**  
- GitHub secrets от компании, а app на личном → upload fail  
- Duplicate build number → bump и перезапуск  

**Конец плана личного TestFlight.**
