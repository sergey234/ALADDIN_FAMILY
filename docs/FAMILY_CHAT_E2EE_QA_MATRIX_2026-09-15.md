# Family Chat E2EE — QA matrix (CHAT-5)

**Дата:** 2026-09-15  
**Цель:** один телефон на TF может писать; видео Report/Restrict без алерта «not ready».

## Автоматические фиксы в билде

| ID | Что сделано |
|----|-------------|
| CHAT-1 | Логи `🔐 FamilyE2EE.bootstrap` / `ensureKey` / `orphan recovery` / `recreate` |
| CHAT-2 | Send / + меню disabled пока `!e2eeManager.isReady` + баннер |
| CHAT-3 | Single-device create key (как было) |
| CHAT-4 | Пустые sender keys при «чужих» device id → auto create+distribute; кнопка **Пересоздать защиту чата** |

## Чеклист владельца

### A. Simulator — 1 device
- [ ] Открыть Family Chat
- [ ] Баннер setup исчезает ≤15 с (или сразу ready)
- [ ] Отправить текст → OK
- [ ] Report / Restrict / Delete own видны на чужом / своём сообщении

### B. TestFlight — 1 device (главный для видео)
- [ ] Открыть Family Chat на физическом iPhone
- [ ] Дождаться ready (баннер ушёл, Send активен)
- [ ] Если Send серый и есть ошибка → **Пересоздать защиту чата** → снова ready
- [ ] Отправить сообщение
- [ ] Показать Report + Restrict на видео
- [ ] В Console (Mac ↔ device): строки `FamilyE2EE.bootstrap END ready=true`

### C. TestFlight — 2 devices (регресс, не блокер видео)
- [ ] Устройство A пишет → B читает (после открытия чата на обоих)
- [ ] Новый join: A раздаёт ключ, B получает после bootstrap

## PASS для App Review видео

**B** полностью зелёный = можно снимать чат.  
**C** — желательно до релиза, не блокер письма ASC.
