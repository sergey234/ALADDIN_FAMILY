# Релизный промпт ALADDIN iOS (актуально после build 245)

**Копировать и подставить ТОЛЬКО одно число.**

```text
PREV_BUILD = 245
NEXT_BUILD = 246

Задача:
1) Поднять номер сборки с PREV_BUILD на NEXT_BUILD во всех нужных местах.
2) Проверить, что все фиксы/дополнения этой сборки в git (включая файлы из pbxproj).
3) Закоммитить только необходимое для релиза.
4) Запушить строго по правилам ниже.
```

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

════════════════════════════════════
НОМЕР СБОРКИ — обязательные файлы
════════════════════════════════════
| Файл | Что менять | Мест |
|------|------------|------|
| `Info.plist` | `CFBundleVersion` → NEXT_BUILD | 1 |
| `ALADDIN.xcodeproj/project.pbxproj` | `CURRENT_PROJECT_VERSION = NEXT_BUILD;` | все (~8–12) |
| `Core/Config/AppConfig.swift` | `buildNumber` + `minimumClientBuildForApiContract` | 2 |

**Дополнительно (часто забывают → TestFlight «не видит» новую сборку / reject extensions):**
| Файл | Что |
|------|-----|
| `ALADDINCallDirectory/Info.plist` | `CFBundleVersion` = NEXT_BUILD (не оставлять старый hardcoded) |
| `ALADDINWidgets/Info.plist` | обычно `$(CURRENT_PROJECT_VERSION)` — ок, если pbx обновлён |

После правки:
- в этих файлах нет PREV_BUILD;
- `NEXT_BUILD > PREV_BUILD` (**понижать запрещено**; не вставлять 237/226 из старых шаблонов).

════════════════════════════════════
ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА ПЕРЕД КОММИТОМ (урок CI 243)
════════════════════════════════════
Archive падает, если файл есть в `project.pbxproj`, но не в git.

1. `git status` — нет нужных `??` / незастейдженных релизных файлов.  
2. Все новые `.swift` из pbxproj Sources есть в `git ls-files`.  
3. Не коммитить: `.env`, ключи, сертификаты, секреты, BACKUPS, локальный мусор.  
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
2. `commit` (только релизные изменения)  
3. `git push origin master`  
4. показать hash и строку `… master -> master`

Запрещено: копия с другим `.git`, rebase без разрешения, force-push в `master`, смена `git config`.  
Если push не fast-forward → СТОП, спросить.

════════════════════════════════════
АНТИПАТТЕРНЫ
════════════════════════════════════
- Несколько разных номеров (237/226/225) в одном запросе.  
- «После 225 сделай 226», если актуальный PREV уже другой.  
- Всегда пара сверху: `PREV_BUILD → NEXT_BUILD`.  
- Локальный Archive в Xcode ≠ появление в TestFlight: нужен **успешный CI upload** с **уникальным CFBundleVersion** выше последней загруженной.

════════════════════════════════════
TESTFLIGHT: ПОЧЕМУ «GITHUB ЗЕЛЁНЫЙ», А НА ТЕЛЕФОНЕ НЕТ (урок 243/244)
════════════════════════════════════

**Какой workflow реально грузит в ASC:**  
`.github/workflows/check-secrets.yml`  
имя в UI: **Build and Upload to App Store**  
(триггер: `workflow_dispatch` **и** `push` на `master`).

**Не путать** с legacy `.github/workflows/appstore.yml` (Manual Only, урезанный ExportOptions без Antifake/CallDirectory).

**Сравнение с 242 (важно):**  
У успешного 242 в `ALADDINCallDirectory/Info.plist` тоже было **239**, а main — **242**.  
Значит «CallDirectory отстал» **не** объясняет, почему 242 попал в TestFlight, а 243/244 — нет.

**Что смотреть в логах CI (по шагам):**
1. `Build Archive with Fastlane` — зелёный  
2. Export IPA / `xcodebuild -exportArchive` — зелёный  
3. **Upload to App Store Connect** (`apple-actions/upload-testflight-build`) — зелёный  
Если зелёный только archive, а upload skipped/failed → в TestFlight **не появится**.

**После upload:** App Store Connect → Activity / TestFlight → Processing (часто 10–60+ мин).  
Проверить email от Apple (ITMS rejection). Билд должен быть в нужной TestFlight группе.

**Номера сейчас (канон):** `Info.plist` + `project.pbxproj` (все `CURRENT_PROJECT_VERSION`) + `AppConfig` ×2 + `ALADDINCallDirectory/Info.plist`.  
Extensions ContentBlocker/AntifakeShare: `GENERATE_INFOPLIST_FILE=YES` → версия из `CURRENT_PROJECT_VERSION` в pbx.
