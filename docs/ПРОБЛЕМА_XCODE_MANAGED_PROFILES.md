# ⚠️ ПРОБЛЕМА: Xcode Managed Profiles

## Проблема

Provisioning profiles, которые мы используем, являются **"Xcode managed"** (автоматически управляемыми), а для **Manual signing** нужны **"manually managed"** (ручно управляемые) профили.

## Ошибки

```
Provisioning profile "iOS Team Store Provisioning Profile: family.aladdin.ios" is Xcode managed, 
but signing settings require a manually managed profile.
```

## Решение

### Вариант 1: Использовать Automatic signing (рекомендуется)

Для Automatic signing на GitHub Actions нужен авторизованный Apple ID, но его нет на runner.

### Вариант 2: Скачать manually managed profiles

1. Откройте https://developer.apple.com/account/resources/profiles/list
2. Найдите профили для `family.aladdin.ios` и `family.aladdin.ios.packetTunnel`
3. Убедитесь, что они **не** "Xcode Managed"
4. Скачайте их
5. Закодируйте в base64 и добавьте в GitHub Secrets

### Вариант 3: Использовать сертификат подписи

1. Экспортируйте сертификат из Keychain Access
2. Закодируйте в base64
3. Добавьте в GitHub Secrets:
   - `IOS_DISTRIBUTION_CERTIFICATE`
   - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`

## Текущий статус

Workflow пытается использовать Manual signing, но профили являются Xcode managed, поэтому сборка не проходит.

## Следующие шаги

1. Проверить профили в App Store Connect
2. Если они Xcode managed - скачать manually managed версии
3. Или добавить сертификат подписи в GitHub Secrets

