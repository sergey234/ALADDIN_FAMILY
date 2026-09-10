# Релизный промпт ALADDIN iOS (Path B / компания `ai.aladdin`)

## Для ML-системы (читать первым)

1. **Не использовать** старые номера вроде 247/248/237/226 как инструкцию.
   Они относились к **другому** приложению (`family.aladdin.ios`, личный TF).
   Текущее App Store приложение: **`ai.aladdin` / ALADDIN AI**, нумерация Path B **с 1**.

2. **Как узнать, какую сборку поднимать (SSOT):**
   ```bash
   # PREV_BUILD = фактический номер сейчас
   /usr/bin/grep -A1 'CFBundleVersion' Info.plist | /usr/bin/tail -1
   /usr/bin/grep 'buildNumber =' Core/Config/AppConfig.swift
   /usr/bin/grep 'CURRENT_PROJECT_VERSION' ALADDIN.xcodeproj/project.pbxproj | /usr/bin/sort -u
   ```
   - Все эти значения должны совпадать → это **PREV_BUILD**.
   - **NEXT_BUILD = PREV_BUILD + 1** (только +1; понижать запрещено).
   - Пример: если везде `5` → поднимать на `6`. Если везде `1` → поднимать на `2`.

3. **После успешного bump** обязательно обновить пару ниже в этом файле:
   `PREV_BUILD` = только что выпущенный номер, `NEXT_BUILD` = +1 к нему.

4. Пока владелец не дал **GO на bump**, документ только хранит актуальную пару; код не трогать.

---

## Актуальная пара (обновлять после каждого bump)

```text
PREV_BUILD = 2
NEXT_BUILD = 3
```

Смысл сейчас: в рабочих файлах Xcode/git фактическая сборка = **2**.
Следующая релизная сборка после успешного push = **3** (когда будет GO).

```text
Задача при GO на bump:
1) Поднять номер сборки с PREV_BUILD на NEXT_BUILD во всех нужных местах.
2) Проверить, что все фиксы/дополнения этой сборки в git (включая файлы из pbxproj).
3) Закоммитить только необходимое для релиза.
4) Обновить в этом файле пару PREV_BUILD/NEXT_BUILD (после bump: PREV=NEXT_старый, NEXT=PREV+1).
5) Запушить строго по правилам ниже (только после явного GO на push).
```

> **Путь B / компания:** нумерация с **1** для ASC app `ai.aladdin`.
> Личный TF (`family.aladdin.ios`) имел свою линейку до 248 — **не продолжать** те номера в Path B.

════════════════════════════════════
КАНОН (не менять)
════════════════════════════════════
Путь: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
Ветка: `master`
Remote: `origin = git@github.com:sergey234/ALADDIN_FAMILY.git`

════════════════════════════════════
ДО ЛЮБОЙ РАБОТЫ (показать вывод)
════════════════════════════════════
```bash
git remote -v
git branch --show-current
git log --oneline -n 3
```
Если remote/ветка/путь не канон → СТОП и спросить.

Дополнительно перед bump показать фактический PREV:
```bash
/usr/bin/grep -A1 'CFBundleVersion' Info.plist
/usr/bin/grep 'static let buildNumber' Core/Config/AppConfig.swift
/usr/bin/grep 'CURRENT_PROJECT_VERSION' ALADDIN.xcodeproj/project.pbxproj | /usr/bin/sort | /usr/bin/uniq -c
```

════════════════════════════════════
НОМЕР СБОРКИ — обязательные файлы
════════════════════════════════════
| Файл | Что менять | Мест |
|------|------------|------|
| `Info.plist` | `CFBundleVersion` → NEXT_BUILD | 1 |
| `ALADDIN.xcodeproj/project.pbxproj` | `CURRENT_PROJECT_VERSION = NEXT_BUILD;` | все (~8–12) |
| `Core/Config/AppConfig.swift` | `buildNumber` + `minimumClientBuildForApiContract` | 2 |
| `Tests/UnitTests/AppConfigTests.swift` | assert `buildNumber` / contract = NEXT_BUILD | обычно 1–2 |

**Дополнительно (часто забывают → TestFlight «не видит» новую сборку / reject extensions):**
| Файл | Что |
|------|-----|
| `ALADDINCallDirectory/Info.plist` | `CFBundleVersion` = NEXT_BUILD (не оставлять старый hardcoded) |
| `ALADDINWidgets/Info.plist` | обычно `$(CURRENT_PROJECT_VERSION)` — ок, если pbx обновлён |

После правки:
- в этих файлах нет PREV_BUILD;
- все targets/extensions согласованы на NEXT_BUILD;
- `NEXT_BUILD == PREV_BUILD + 1` (**понижать запрещено**; не вставлять номера из старых шаблонов/личных TF).

════════════════════════════════════
ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА ПЕРЕД КОММИТОМ (урок CI 243)
════════════════════════════════════
Archive падает, если файл есть в `project.pbxproj`, но не в git.

1. `git status` — нет нужных `??` / незастейдженных релизных файлов.
2. Все новые `.swift` из pbxproj Sources есть в `git ls-files`.
3. Не коммитить: `.env`, ключи, сертификаты, секреты, BACKUPS, локальный мусор, `telegram_stars_shop_bot/**` в iOS-релиз.
4. Яндекс/API ключи в чат можно, в git — **НИКОГДА**.

════════════════════════════════════
КОММИТ → PUSH
════════════════════════════════════
Перед push:
```bash
git merge-base HEAD origin/master
```
Если hash нет → СТОП, не пушить, спросить.

Порядок:
1. проверить build number в файлах выше
2. обновить пару PREV/NEXT в этом документе
3. `commit` (только релизные изменения) — **только если владелец просил commit**
4. `git push origin master` — **только после явного GO на push**
5. показать hash и строку `… master -> master`

Запрещено: копия с другим `.git`, rebase без разрешения, force-push в `master`, смена `git config`.
Если push не fast-forward → СТОП, спросить.

════════════════════════════════════
АНТИПАТТЕРНЫ
════════════════════════════════════
- Брать «пример 247→248» как реальные PREV/NEXT.
- Несколько разных номеров в одном запросе.
- Поднимать сразу на +2/+10 без причины.
- «После 225 сделай 226», если фактический PREV уже другой.
- Всегда сначала **прочитать файлы**, потом пара `PREV_BUILD → NEXT_BUILD`.
- Локальный Archive в Xcode ≠ появление в TestFlight: нужен **успешный CI upload** с **уникальным CFBundleVersion** выше последней загруженной.

════════════════════════════════════
TESTFLIGHT: ПОЧЕМУ «GITHUB ЗЕЛЁНЫЙ», А НА ТЕЛЕФОНЕ НЕТ (урок 243/244)
════════════════════════════════════

**Какой workflow реально грузит в ASC:**
`.github/workflows/check-secrets.yml`
имя в UI: **Build and Upload to App Store**
(триггер: `workflow_dispatch` **и** `push` на `master`).

**Не путать** с legacy `.github/workflows/appstore.yml` (Manual Only, урезанный ExportOptions без Antifake/CallDirectory).

**Что смотреть в логах CI (по шагам):**
1. `Build Archive with Fastlane` — зелёный
2. Export IPA / `xcodebuild -exportArchive` — зелёный
3. **Upload to App Store Connect** (`apple-actions/upload-testflight-build`) — зелёный
Если зелёный только archive, а upload skipped/failed → в TestFlight **не появится**.

**После upload:** App Store Connect → Activity / TestFlight → Processing (часто 10–60+ мин).
Проверить email от Apple (ITMS rejection). Билд должен быть в нужной TestFlight группе.

**Файлы номера (канон):** `Info.plist` + `project.pbxproj` (все `CURRENT_PROJECT_VERSION`) + `AppConfig` ×2 + `AppConfigTests` + `ALADDINCallDirectory/Info.plist`.
Extensions ContentBlocker/AntifakeShare: `GENERATE_INFOPLIST_FILE=YES` → версия из `CURRENT_PROJECT_VERSION` в pbx.
