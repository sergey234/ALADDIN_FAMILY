# Critical Alerts → regen APP profile → secret

**Team:** B3WGHSWL79 · App ID `ai.aladdin` · Request **`VX53USXWCJ`**

## Шаг 1 — capability на App ID (~3 мин)

1. https://developer.apple.com/account/resources/identifiers/list  
2. Клик **ALADDIN** · `ai.aladdin`  
3. **Edit**  
4. Найдите **Critical Alerts** → галочка **On**  
   - Если кнопки/галочки нет (только Request / серое) → Apple ещё **не Assigned** `VX53USXWCJ`.  
     Тогда **не** жмите Save наугад: напишите агенту «Critical Alerts ещё не Assigned» и стоп.  
5. **Save** / Continue → Save  

## Шаг 2 — пересоздать App Store profile (~5 мин)

1. https://developer.apple.com/account/resources/profiles/list  
2. **ALADDIN AI App Store** (может стать Invalid)  
3. **Edit** → Generate → **Download**  
   или Delete + `+` → App Store → `ai.aladdin` → Generate → Download  
4. Файл вроде `ALADDIN_AI_App_Store (5).mobileprovision`  

## Шаг 3 — агенту

Напишите: **«main profile с Critical Alerts скачан»** (+ имя файла).

Агент: проверит entitlement `critical-alerts` в профиле → `gh secret set PROVISIONING_PROFILE_APP` →
вернёт `com.apple.developer.usernotifications.critical-alerts` в `ALADDIN.entitlements` →
`allowsCriticalAlerts = true` (обе ветки в `Core/Config/AppConfig.swift`) + `XCTAssertTrue` в `AppConfigTests`.

До Assigned entitlement в коде **нет** (иначе CI-подпись падает), toggle скрыт.

## После secret

Нужен **GO на commit** (если ещё не закоммичен UI pack) и отдельно **GO на push** для CI.
