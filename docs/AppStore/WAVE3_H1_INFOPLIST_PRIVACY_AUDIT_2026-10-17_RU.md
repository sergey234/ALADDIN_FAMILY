# WAVE3 · H1 — Info.plist privacy audit

**ID:** `cap-H1` · **Дата:** 2026-10-17  
**Правило:** ключ usage description есть ⇒ в продукте есть реальный вызов API.

## Удалено (нет кода в Core/Screens/Shared/Companion)

| Ключ | Было | Почему |
|------|------|--------|
| `NSAppleMusicUsageDescription` | music entertainment | нет MediaPlayer/MusicKit |
| `NSBluetoothAlwaysUsageDescription` | proximity | нет CoreBluetooth |
| `NSBluetoothPeripheralUsageDescription` | proximity | нет CoreBluetooth |
| `NSHomeKitUsageDescription` | smart home | нет HomeKit |
| `NSLocalNetworkUsageDescription` | device comm | нет NWBrowser; «Bonjour» только в тексте песни |
| `NSRemindersUsageDescription` | reminders | EventKit только **events**, не Reminders |
| `NSSiriUsageDescription` | Siri commands | нет Intents/SiriKit |

Также убраны из `ru.lproj` / `en.lproj` `InfoPlist.strings`.

## Оставлено (есть код)

| Ключ | Зачем |
|------|--------|
| Location WhenInUse / Always | геозоны + SOS |
| Camera / Photo / Mic / Speech | companion + безопасность |
| Contacts | чат / calls hub |
| Face ID | auth |
| Motion | crash/fall |
| Calendars (+ FullAccess iOS 17) | sync семейных привычек в календарь |
| User Notifications | семейные алерты |

## Отложено до фазы G

| Ключ | Когда |
|------|--------|
| `NSHealthShareUsageDescription` / Update | `cap-G1` при включении HealthKit fall |

## Verify

```bash
rg -n 'NSHomeKit|NSBluetooth|NSAppleMusic|NSSiri|NSLocalNetwork|NSReminders' Info.plist ru.lproj/InfoPlist.strings en.lproj/InfoPlist.strings
# ожидаемо: пусто
```
