# Tailscale шаг 1 Mac — итог 2026-09-21

## Почему .pkg «не открывался»

По диагностике файл **целый и легальный** (Notarized Developer ID Tailscale Inc.).  
Частая причина на форумах Apple/StackOverflow: двойной клик блокирует Gatekeeper → нужно **ПКМ → Открыть** или **Privacy & Security → Open Anyway**.  
На Sequoia Installer иногда «молча» не стартует — обход: установка через `installer` с правами админа (GUI-пароль).

Источники: [Apple/StackOverflow unverified pkg](https://stackoverflow.com/questions/65085341/how-can-i-open-an-unverified-pkg-file-on-mac), [Tailscale macOS variants](https://tailscale.com/docs/concepts/macos-variants), [GitHub #13670](https://github.com/tailscale/tailscale/issues/13670) (другое: extension после install).

## Что сделали

| Действие | Результат |
|----------|-----------|
| `installer -pkg … -target /` (через osascript + ваш пароль) | **INSTALL_OK** |
| `/Applications/Tailscale.app` | ✅ установлен |
| Открыли приложение | ✅ |
| MAIN / Brain | не трогали |

Запасной файл: `~/Downloads/Tailscale-1.102.4-macos.zip` → уже распакован в `~/Downloads/Tailscale-unzip/Tailscale.app`.

## Что сделать вам сейчас

1. В меню-баре иконка Tailscale → **Log in** (Google/GitHub).  
2. Разрешить VPN / Network Extension в System Settings, если спросит.  
3. Написать: `Tailscale Mac: logged in`
