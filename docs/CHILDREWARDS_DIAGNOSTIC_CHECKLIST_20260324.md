# ChildRewards диагностический mini-log чек-лист (2026-03-24)

Категории логов:
- `CHILD_REWARDS.UI`
- `CHILD_REWARDS.API`

## Таблица валидации

| Событие | Ожидаемая реакция UI | Тайм-аут/ожидание |
|---|---|---|
| `👀 ChildRewardsScreen onAppear` (`CHILD_REWARDS.UI`) | Экран открыт, виден mini-log overlay | сразу |
| `🔄 Initial load triggered` (`CHILD_REWARDS.UI`) | Показ состояния `Обновляем награды…` | сразу |
| `🚀 load() start childId=...` (`CHILD_REWARDS.API`) | Старт агрегированной загрузки dashboard | сразу |
| `🌐 request start: parental stats` / `referral stats` / `referral rewards` (`CHILD_REWARDS.API`) | Параллельные API вызовы начаты | сразу |
| `✅ request ok: ...` (3 события) (`CHILD_REWARDS.API`) | Части данных пришли успешно | до 12 сек |
| `✅ load() all requests completed` (`CHILD_REWARDS.API`) | Dashboard готов к рендеру | до 12 сек |
| `✅ Dashboard received and rendered` (`CHILD_REWARDS.UI`) | Loader снят, карточки интерактивны | до 12 сек |
| `❌ request failed: ...` или `❌ load() failed: ...` (`CHILD_REWARDS.API`) | Ошибка пробрасывается в UI | до 12 сек |
| `❌ ViewModel error = ...` (`CHILD_REWARDS.UI`) | Показывается error-banner, экран не зависает в initial loading | до 12 сек |
| `⏱️ load() hard-timeout 12s` (`CHILD_REWARDS.API`) | Принудительное завершение загрузки | 12 сек |
| `⏱️ Initial UI fallback fired (4s)` (`CHILD_REWARDS.UI`) | Экран выходит из initial-фазы даже при нестабильной сети | 4 сек |
| `🔁 Retry tapped` (`CHILD_REWARDS.UI`) | Повторный запуск `viewModel.load()` | сразу |
| `🧭 tab_changed = ...` (`CHILD_REWARDS.UI`) | Смена таба, для `История` стартует history API | сразу |
| `🌐 rewards history request start` / `✅ ... ok` / `❌ ... failed` (`CHILD_REWARDS.API`) | Подгрузка истории для вкладки `История` | до network timeout |
| `⬅️ Back tapped` (`CHILD_REWARDS.UI`) | Выход со страницы через `dismiss + goBack(reason:)` | сразу |

## Критерий PASS

- Экран никогда не остается в бесконечном `Обновляем награды…`.
- После 12 секунд обязательно есть либо `dashboard`, либо `error-banner`.
- Back/табы работают в любом состоянии сети.
- В mini-log видны обе категории (`CHILD_REWARDS.UI` и `CHILD_REWARDS.API`) без пропусков ключевых этапов.
