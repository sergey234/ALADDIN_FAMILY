# HERO-3-11b — сессия device QA (заполнить на iPhone)

**Статус:** ⏳ открыто · **Build:** 210+ · **`.riv`:** placeholder OK  
**Чеклист:** [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md)  
**После PASS:** поставить `[x]` на **11b** в [TRACKER](./COMPANION_PROGRESS_TRACKER.md) → шаг к **GATE-P0**

---

## Протокол

| Поле | Значение |
|------|----------|
| Дата | |
| Тестер | |
| Устройство | |
| iOS | |
| Build | |
| Итог **11b** | PASS / FAIL |

**Навигация:** Kids → Игры → **Мир героев** → **Главное** · genie только teen/parent.

---

## D10 (4 реплики × герой)

| # | Реплика | unicorn | aladdin | genie |
|---|---------|---------|---------|-------|
| 1 | «Ура, я получил пятёрку!» | ✅/❌ | ✅/❌ | ✅/❌ |
| 2 | «Мне грустно сегодня» | ✅/❌ | ✅/❌ | ✅/❌ |
| 3 | «Расскажи анекдот!» | ✅/❌ | ✅/❌ | ✅/❌ |
| 4 | «Подозрительное письмо со ссылкой» | ✅/❌ | ✅/❌ | ✅/❌ |

---

## MOTION-Q

| ID | PASS |
|----|------|
| MOTION-Q1 listening &lt;300 ms | ✅/❌ |
| MOTION-Q2 speaking + рот ≥1 s | ✅/❌ |
| MOTION-Q3 грусть без playful | ✅/❌ |
| MOTION-Q4 герои различимы | ✅/❌ |
| MOTION-Q5 D10 на каждом герое | ✅/❌ |

---

## MIMIC-Q (placeholder — state меняется)

| ID | PASS |
|----|------|
| MIMIC-Q1 happy/sad/playful/alert разные | ✅/❌ |
| MIMIC-Q6 нет ✨ на sad/comfort | ✅/❌ |

---

## SPEECH-Q6

| Проверка | PASS |
|----------|------|
| Текст в чат → TTS слышен («Озвучивать ответы» вкл.) | ✅/❌ |

---

## Заметки / баги

```
(скриншоты, краши, шаги воспроизведения)
```

---

## Закрытие

При **PASS** всех критичных строк выше:

1. `[x]` **11b** в `COMPANION_PROGRESS_TRACKER.md`
2. Обновить протокол в `COMPANION_HERO3_11_QA_CHECKLIST.md` § «Протокол»
3. **GATE-P0** — после 11b (07 ещё ⏳)

*Pixel-perfect MIMIC → **11c** после production `.riv` (HERO-3-07).*
