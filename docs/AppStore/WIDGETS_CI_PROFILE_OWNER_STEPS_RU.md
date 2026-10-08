# ALADDIN Widgets — профиль для CI (сборка 5)

**Зачем:** CI упал: `ALADDINWidgets requires a provisioning profile with the App Groups feature`.  
**Bundle ID:** `ai.aladdin.widgets`  
**App Group:** `group.ai.aladdin`  
**Team:** `B3WGHSWL79` (SAUDAPAYDI)  
**Секрет GitHub:** `PROVISIONING_PROFILE_WIDGETS`  
**Bump не нужен** — номер сборки остаётся **5**.

Код CI уже готов в репо (workflow + Fastlane). Вам — только Apple + вставить секрет.

---

## Шаг 1. App ID виджета (если ещё нет)

Откройте: [Identifiers](https://developer.apple.com/account/resources/identifiers/list)

1. **+** → **App IDs** → Continue  
2. Description: `ALADDIN AI Widgets`  
3. Bundle ID → **Explicit** → `ai.aladdin.widgets`  
4. Capabilities: включите **App Groups**  
5. Register → Edit → App Groups → Configure → выберите **`group.ai.aladdin`** → Save

Проверка App Groups: [Application Groups](https://developer.apple.com/account/resources/identifiers/list/applicationGroup) — должен быть `group.ai.aladdin`.

---

## Шаг 2. Профиль App Store

Откройте: [Profiles](https://developer.apple.com/account/resources/profiles/list)

1. **+** → **App Store** (Distribution) → Continue  
2. App ID: **`ai.aladdin.widgets`** → Continue  
3. Certificate: ваш **Apple Distribution** (тот же, что для app) → Continue  
4. Profile Name: `ALADDIN AI Widgets App Store` → Generate  
5. **Download** → файл `.mobileprovision` в Загрузки

---

## Шаг 3. Одна строка base64

В Terminal (из корня `ALADDIN_iOS`):

```bash
chmod +x scripts/encode_widgets_profile_for_github.sh
./scripts/encode_widgets_profile_for_github.sh ~/Downloads/*.mobileprovision
```

(подставьте точное имя скачанного файла, если glob не один)

Скрипт проверит `group.ai.aladdin` + `ai.aladdin.widgets` и напечатает **одну длинную строку**.

---

## Шаг 4. Вставить в GitHub Secret

Откройте: [Actions secrets — ALADDIN_FAMILY](https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions)

1. **New repository secret** (или Edit, если уже есть)  
2. Name: **`PROVISIONING_PROFILE_WIDGETS`**  
3. Value: вставьте строку base64 из шага 3 (без пробелов/переносов)  
4. Save

---

## Шаг 5. Запустить CI снова

1. Убедитесь, что коммит с правками CI уже на `master` (push).  
2. [Actions](https://github.com/sergey234/ALADDIN_FAMILY/actions) → **Build and Upload to App Store** → **Run workflow** (или Re-run failed).  
3. Ждите зелёный Archive + Upload → TestFlight **build 5**.

---

## Что уже сделано в коде (агент)

- Decode/encode scripts для Widgets  
- Fastlane + `check-secrets.yml` → `ALADDINWidgets_*` в xcconfig + ExportOptions  
- Widgets добавлен в Embed App Extensions  
- Канон Bundle ID в `docs/APPLE_ORG_COMPANY_IDS_CANON.md`

Без секрета CI **отключит** Widgets (как Call Directory без профиля) — архив может пройти, но виджетов в IPA не будет. Для полного билда с виджетами секрет **обязателен**.
