# Голос: AI Помощник + Диктофон — единый план (100%)

Дата: 2026-05-20  
Статус: **закрыто по критериям эталона Apple HIG + Telegram/WhatsApp Voice**

---

## 1. Архитектура

| Поток | Запись | STT | Хранение | UI |
|-------|--------|-----|----------|-----|
| **AI Помощник** | `SpeechManager` + `AVAudioEngine` | Apple `SFSpeechRecognizer` on-device → Siri cloud | Текст в чат (Hermes) | `06_AIAssistantScreen` |
| **Диктофон** | `VoiceNotesRecorderService` (m4a) | `VoiceNotesTranscriptionService` + cloud fallback | `VoiceNotesStore` локально | `VoiceNotesScreen` |
| **Семейный чат** | `VoiceMessageRecorder` | Нет | Сервер | `VoiceRecordingView` |

**Координатор:** `VoiceAudioSessionCoordinator` — mutex AI / Notes / Family.

---

## 2. Финальная таблица: ALADDIN vs эталон (100%)

| Критерий | Эталон (Telegram/WhatsApp/Apple HIG) | ALADDIN |
|----------|--------------------------------------|---------|
| Pre-flight check | Mic disabled + подсказка | ✅ AI: chip + disabled mic; Диктофон: speech hint в баннере |
| Permission UX | Settings deep link в alert | ✅ Mic + Speech alerts с «Открыть Настройки» (AI + Диктофон) |
| Stop semantics | endAudio + финализация | ✅ |
| False «service unavailable» | Не показывать на cancel | ✅ |
| Interruption (звонок) | Pause/stop + сообщение | ✅ AI: toast; Диктофон: autosave + toast |
| Live caption | Видно при записи | ✅ AI partial transcript |
| Max duration | AI 30–60 с; notes 5–15 мин | ✅ AI 60 с; Диктофон 10 мин + предупреждение за 30 с |
| Audio format tap | Явный format | ✅ `validTapFormat` |
| Real level meter | Да | ✅ RMS tap / AVAudioRecorder metering |
| Privacy disclosure | Cloud/off-device понятно | ✅ plist + баннер on-device/Siri + chip «Через Siri» |
| Automated tests | Speech path covered | ✅ `SpeechPathTests` (+ durations, interruption name, waveform) |
| Multi-locale STT | Fallback chain | ✅ |
| On-device first + cloud | Да | ✅ `SpeechRecognizerFactory` |
| Session coordinator | Один менеджер | ✅ |
| Hold-to-record | Да | ✅ + slide-to-cancel (← отпустите) |
| Haptic start/stop | Да | ✅ `HapticFeedback` |
| Playback / share | Да | ✅ m4a + `UIActivityViewController` |
| Waveform | Реальная или честная | ✅ `VoiceNoteWaveformSampler` из m4a |
| Send note → AI | — | ✅ «В AI Помощник» |

**Оценка:** против «среднего App Store» — **отлично**; против «лучший в мире» — **~100% по заявленным критериям** (E2E UI-тесты — ручной TestFlight чеклист).

---

## 3. План реализации (выполнен)

### Фаза A — P0 ✅
- Mic disabled, Settings alerts, live caption, 60 с, tap format, interruption stop
- Диктофон: STT cloud fallback, QuickRecorderBar, Call Assistant collapse, no demo seed

### Фаза B — P1 ✅
- Real audio level, 10 min + warning, session coordinator, split permission alerts, unit tests

### Фаза C — P2/P3 ✅ (2026-05-20)
- Interruption toast (AI + Notes)
- Speech permission alert (Диктофон)
- Privacy STT disclaimer
- Haptic on record start/stop
- Slide-to-cancel (hold + drag left)
- Real waveform from m4a
- Расширенные `SpeechPathTests`

---

## 4. Проверка (TestFlight)

| # | Сценарий | Ожидание |
|---|----------|----------|
| 1 | AI: tap mic, говорить, tap stop | Текст в поле → send |
| 2 | AI: hold mic, свайп влево, отпустить | Отмена, без send |
| 3 | AI: входящий звонок во время записи | Toast «Запись прервана…» |
| 4 | Диктофон: запись → стоп | Карточка + waveform + транскрипт |
| 5 | Диктофон: звонок во время записи | Autosave + toast |
| 6 | Отказ Speech → alert → Settings | Deep link работает |
| 7 | iPhone ru-RU, Siri вкл., язык загружен | On-device или chip «Через Siri» |

**Симулятор:** STT 4099 / Required assets — ожидаемо; cloud path для smoke OK.

---

## 5. Команды CI / локально

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINTests/SpeechPathTests CODE_SIGNING_ALLOWED=NO build test
```

---

## 6. Метод 6 шляп — итог

| Шляпа | Вывод |
|-------|--------|
| ⚪ Факты | Два стека, Apple Speech, локальные заметки, единый координатор |
| 🔴 Риски | Simulator ≠ device для ru-RU on-device |
| ⚫ Провал | Без Siri/lang pack — cloud fallback + понятные alerts |
| 🟡 Плюсы | Privacy, hold+cancel, real waveform, tests |
| 🟢 Рост | E2E XCUITest — опционально post-100% |
| 🔵 Решение | **Критерии таблицы закрыты — релиз TestFlight на iPhone** |
