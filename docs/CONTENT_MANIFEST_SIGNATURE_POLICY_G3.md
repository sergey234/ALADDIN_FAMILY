# Политика подписи контент-манифеста (G3)

**Связь:** `docs/GAP_CLOSURE_PLAN_PHASES_1_8_ML_HANDOFF.md` (G3, W0-2, W1-3), `Core/Content/Validation/ContentValidator.swift`  
**Алгоритм:** ECDSA P-256 (реализация `ContentValidator.verifySignature`).

## Режимы

| Сборка / окружение | Подпись обязательна для применения манифеста | Поведение при отсутствии/невалидной подписи |
|---|:---:|---|
| **Debug** (локальная разработка) | **Нет** (по умолчанию) | Разрешена структурная валидация `validateManifest` без крипто-гейта; dev-сборки могут принимать `signature == nil` на усмотрение W1-3. |
| **Release** (TestFlight / App Store) | **Да** (после внедрения W1-3 в `ContentSyncManager`) | Манифест **не** применяется: откат на last-known-good, пользователю безопасное сообщение (ключи локализации, W-LOC-6). |
| **Staging** | Как **Release**, если используется релизная конфигурация; иначе согласовать с командой. | Аналогично Release, если включён флаг `AppConfig.contentManifestRequireValidSignature`. |

## Канонические байты (для согласования с бэкендом)

- Реализация на клиенте: `ContentManifestSigning.canonicalSigningData(for:)` → UTF-8 JSON объекта **без** поля `signature`, с полями верхнего уровня в кодировке `JSONEncoder`: `outputFormatting = [.sortedKeys, .withoutEscapingSlashes]`, `dateEncodingStrategy = .iso8601`; массивы `categories` и `items` **отсортированы по `id`** перед кодированием.  
- Текущее iOS-API: `verifySignature(payload: Data, signatureBase64: publicKeyBase64:)` — байты `payload` должны **точно** совпадать с тем, что подписал **приватный** ключ на сервере.  
- Публичный ключ: **32-byte raw** `P256` в **Base64**; ключ в бандле: `Info.plist` → `CONTENT_MANIFEST_SIGNING_PUBLIC_KEY_BASE64` (читает `AppConfig.contentManifestSigningPublicKeyBase64`).

## Соответствие коду (Wave 0)

- `AppConfig.contentManifestRequireValidSignature` — **документированная** настройка «в релизе требуем крипто-гейта»; фактическое **блокирование** `applyManifest` без подписи — в `ContentSyncManager` (W1-3); при ошибке применения — откат версии и повторное сохранение предыдущего манифеста (W1-4).
- `ContentValidator.verifySignature` — unit-тесты: валидная подпись / битая подпись / изменённый payload.

## Proof

- Этот документ + `Tests/UnitTests/ContentValidatorTests.swift` + `ContentManifestSigningTests.swift` + `ContentSyncManagerApplyTests.swift` (подпись / откат с инжектом флага в DEBUG).
