# ADR: подпись манифеста контента fail-closed (G3)

**Статус:** accepted (поэтапное внедрение)  
**Дата:** 2026-04-27  
**Связь:** `docs/GAP_CLOSURE_PLAN_PHASES_1_8_ML_HANDOFF.md` (G3), `Core/Content/Sync/ContentSyncManager.swift`, `Core/Config/AppConfig.swift`

## Контекст

- На клиенте есть `ContentValidator.verifySignature`, `ContentManifestSigning`, флаг `AppConfig.contentManifestRequireValidSignature` и путь `validateManifestSignatureIfNeeded` в `ContentSyncManager.applyManifest`.
- В gap зафиксировано: **fail-closed по подписи** как единственный прод-путь требует явной политики сервера + ключа в приложении + регресса.

## Решение

**Фаза A (текущий допустимый прод):** подпись **может быть выключена** (`requireManifestSignature = false`), пока бэкенд не гарантирует стабильный канон подписи и ключ в `AppConfig.contentManifestSigningPublicKeyBase64` не задеплоен во все сборки.

**Фаза B (целевой прод):** при включении `requireManifestSignature = true`:
1. Сервер подписывает **каноническое** тело манифеста (как в `ContentManifestSigning.canonicalSigningData`).
2. В приложении задан непустой публичный ключ; при отсутствии подписи или невалидной подписи — **откат** к предыдущему сохранённому манифесту (поведение уже в `applyManifest` try/catch) и **ошибка** наружу для телеметрии.
3. Релизный чеклист: смоук `scripts/content_contract_smoke.py` + ручной negative case (подпись сломана → клиент не принимает).

**Запрещено:** включать fail-closed на клиенте без одновременной выкладки подписывающего контура на `/api/content/manifest` (и дельты, если она несёт те же гарантии).

## Последствия

- Backend: ответственность за ключи ротации и версионирование манифеста.  
- iOS: при смене ключа — скоординированный релиз приложения.  
- G3 считается **инженерно закрытым по политике** после принятия ADR; **операционно закрыт** после выполнения Фазы B на проде (отдельный тикет/релиз).
