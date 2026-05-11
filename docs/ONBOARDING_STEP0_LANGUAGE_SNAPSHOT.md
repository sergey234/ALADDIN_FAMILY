# Снимок шага 0 онбординга (выбор языка)

**Назначение:** зафиксировать поведение и разметку **страницы 0** до дальнейшей визуальной доработки (7 контентных слайдов + Main). Источник правды в коде — `Screens/14_OnboardingScreen.swift`; при расхождении править сначала код, этот файл обновлять опционально.

**Связь с героем:** поверх экрана в `body` уже может отображаться `HeroAmbientLayerView(slot: .onboardingLanguage)` (ассет `OnboardingHero_00` когда появится в каталоге). Содержимое **самого шага 0** ниже — без изменений смысла.

---

## Вспомогательные строки (не LocalizationManager — намеренно минимальный набор)

Кнопка «Продолжить» на шаге 0 и заголовок шага заданы локально по enum языка, чтобы шаг не зависел от тяжёлого словаря.

---

## Код (копия на момент фиксации)

Фрагмент из `OnboardingScreen`: `languageStepContinueTitle`, `languageStepTitle`, `languageStepView`.

```swift
    private func languageStepContinueTitle(for language: LocalizationManager.Language) -> String {
        switch language {
        case .russian: return "Продолжить"
        case .english: return "Continue"
        case .chinese: return "继续"
        case .arabic: return "متابعة"
        }
    }

    private func languageStepTitle(for language: LocalizationManager.Language) -> String {
        switch language {
        case .russian: return "Язык приложения"
        case .english: return "App language"
        case .chinese: return "应用语言"
        case .arabic: return "لغة التطبيق"
        }
    }

    @ViewBuilder
    private func languageStepView() -> some View {
        VStack(spacing: Spacing.xl) {
            Spacer(minLength: 12)

            Text("🌐")
                .font(.system(size: 56))

            Text(languageStepTitle(for: selectedLanguageForOnboarding))
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
                .padding(.horizontal, Spacing.l)

            VStack(spacing: Spacing.m) {
                ForEach(LocalizationManager.Language.userSelectableLanguages, id: \.rawValue) { lang in
                    Button {
                        selectedLanguageForOnboarding = lang
                        localizationManager.changeLanguage(to: lang)
                        loadPages()
                        HapticFeedback.selection()
                    } label: {
                        HStack(spacing: Spacing.m) {
                            Text(lang.flag)
                                .font(.system(size: 28))
                            Text(lang.displayName)
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(.white)
                            Spacer()
                            if selectedLanguageForOnboarding == lang {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.primaryBlue)
                            }
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.white.opacity(selectedLanguageForOnboarding == lang ? 0.22 : 0.12))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(
                                            selectedLanguageForOnboarding == lang ? Color.primaryBlue : Color.white.opacity(0.2),
                                            lineWidth: selectedLanguageForOnboarding == lang ? 2 : 1
                                        )
                                )
                        )
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("\(lang.displayName)")
                }
            }
            .padding(.horizontal, Spacing.screenPadding)

            Spacer(minLength: 12)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Выбор языка приложения")
    }
```

---

## Кнопка «Продолжить» на шаге 0

Реализована **вне** `languageStepView`, в `mainOnboardingContent` (нижний блок кнопок): при `currentPage == 0` вызывается `languageStepContinueTitle(for:)`. Логику перехода `0 → 1` не менять без согласования с `hasChosenLanguageOnce` / `loadPages()`.
