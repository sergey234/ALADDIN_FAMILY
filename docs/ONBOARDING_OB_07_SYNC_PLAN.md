# OB_07 — план синхронизации Figma ↔ iOS

**Дата:** 2026-05-23 · **Figma:** `122:53` `OB_07_Invite_393x852` · **Build:** 202+

## Проблема

- Текст «Мы собираем…» и ссылки **не видны** на устройстве (уезжают за экран / сжимаются в `HStack`).
- Логотип, заголовок и описание — **ScrollView**, не фиксированные Y из Figma.
- Legal-блок не совпадает с `BLOCK_final_legal` в `CHROME_bottom`.

## План реализации

| # | Задача | Figma | iOS |
|---|--------|-------|-----|
| 1 | `OnboardingFigmaAnchor` **case 6** | wordmark 7,374 · title 12,470 · desc 12,508 | `forContentIndex(6)` |
| 2 | Layout mode **ob07Final** | chrome h=304, без «Пропустить» | `tabTopY` без skipBand, design height 548 |
| 3 | Scrim под текст | y≈480 | gradient + stops |
| 4 | Типографика | title 24 Semibold · desc 16 @ 75% · legal 11/12 | `OnboardingOB07Style` |
| 5 | Логотип | 361×104 @ y=374 | `OnboardingLogoV2View(fixedHeight: 104)` |
| 6 | Legal-блок | `BLOCK_final_legal` @ screen y=654 | `OnboardingOB07LegalBlock` — 4 строки столбиком |
| 7 | Политика | info + ссылка в одной строке (перенос) | `Text` + `Text` underline |
| 8 | Соглашение | отдельная строка-ссылка + чекбокс | как Figma `ROW_terms_link` + `ROW_terms_consent` |
| 9 | QA | симулятор `-OnboardingPage7` | визуально ≈ Figma |

## Эталон Y (screen 393×852)

| Элемент | y | Примечание |
|---------|---|------------|
| Hero | 24 | фон |
| WORDMARK | 374 | TabView, anchored |
| Title | 470 | 24pt Semibold |
| Desc | 508 | 16pt, white 75% |
| CHROME | 556 | под TabView |
| Legal block | 654 | в chrome |
| Secondary buttons | 788 | «Код» / «Восстановить» |

## Статус

- [x] План
- [x] Код case 6 + OB07 legal + typography
- [x] Build 202 Debug — OK
- [ ] SYNC-D пользователь «принято» (симулятор `-OnboardingPage7`)
