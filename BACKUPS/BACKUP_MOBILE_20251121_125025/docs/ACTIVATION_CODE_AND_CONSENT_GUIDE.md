# 📱 Где находится страница активации кода и согласие ПДн

**Дата:** 19 ноября 2025

---

## 🔍 1. СТРАНИЦА АКТИВАЦИИ КОДА

### 📍 Где находится экран активации?

**Файл:** `Screens/26_ActivationCodeScreen.swift`

**Экран:** `ActivationCodeScreen`

**Навигация:** `.activationCode` в `NavigationManager.ALADDINScreen`

---

### 🚪 Как пользователи попадают на экран активации?

**Сейчас экран активации НЕ подключен к навигации!**

Нужно добавить кнопку/ссылку в одном из мест:

#### Вариант 1: В экране Тарифов (TariffsScreen)
После оплаты через QR пользователь должен иметь возможность активировать код.

**Где добавить:**
- `Screens/10_TariffsScreen.swift`
- После успешной оплаты или в разделе "Управление подпиской"

#### Вариант 2: В экране Настроек (SettingsScreen)
В разделе подписки добавить кнопку "Активировать код".

**Где добавить:**
- `Screens/05_SettingsScreen.swift`
- В секции `profileSection` или `appSection`

#### Вариант 3: В экране Профиля (ProfileScreen)
В разделе подписки добавить кнопку "Активировать код".

**Где добавить:**
- `Screens/11_ProfileScreen.swift`
- В секции с информацией о подписке

---

### 💡 РЕКОМЕНДУЕМЫЙ ПУТЬ ДЛЯ ПОЛЬЗОВАТЕЛЯ:

```
1. Пользователь выбирает тариф на экране "Тарифы"
   ↓
2. Нажимает "ОПЛАТИТЬ ЧЕРЕЗ QR"
   ↓
3. Открывается лендинг с формой оплаты
   ↓
4. После оплаты получает код активации
   ↓
5. Возвращается в приложение
   ↓
6. Переходит в "Настройки" → "Активировать код"
   ИЛИ
   "Профиль" → "Активировать код"
   ↓
7. Вводит код и активирует подписку
```

---

## ✅ 2. СОГЛАСИЕ НА ОБРАБОТКУ ПДн — ГДЕ ПОСМОТРЕТЬ

### 📍 Что было сделано:

#### 1. ЭКРАН АКТИВАЦИИ КОДА (`ActivationCodeScreen`)

**Файл:** `Screens/26_ActivationCodeScreen.swift`

**Что добавлено:**

```193:272:Screens/26_ActivationCodeScreen.swift
// MARK: - Consent Card (152-ФЗ)

private var consentCard: some View {
    VStack(alignment: .leading, spacing: Spacing.s) {
        HStack(alignment: .top, spacing: Spacing.s) {
            Button(action: {
                HapticFeedback.impact(.light)
                withAnimation {
                    consentAccepted.toggle()
                }
            }) {
                Image(systemName: consentAccepted ? "checkmark.square.fill" : "square")
                    .font(.system(size: 20))
                    .foregroundColor(consentAccepted ? .primaryBlue : .textSecondary)
            }
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("Согласие на обработку персональных данных")
                    .font(.subheadline.bold())
                    .foregroundColor(.textPrimary)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Нажимая «Активировать», я даю согласие на обработку персональных данных в соответствии с:")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    HStack(spacing: 4) {
                        Button(action: {
                            URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/consent.html", tariffId: nil)
                        }) {
                            Text("Согласием на обработку персональных данных")
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                                .underline()
                        }
                        
                        Text("и")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Button(action: {
                            URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/privacy.html", tariffId: nil)
                        }) {
                            Text("Политикой конфиденциальности")
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                                .underline()
                        }
                        
                        Text(".")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
        
        if !consentAccepted && !viewModel.code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            Text("⚠️ Для активации кода необходимо дать согласие на обработку персональных данных")
                .font(.caption)
                .foregroundColor(.orange)
                .padding(.leading, 28)
        }
    }
    .padding(Spacing.m)
    .background(
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.white.opacity(0.08))
    )
    .overlay(
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .stroke(consentAccepted ? Color.primaryBlue.opacity(0.3) : Color.white.opacity(0.12), lineWidth: 1)
    )
    .padding(.horizontal, Spacing.screenPadding)
    .onAppear {
        // ✅ Восстанавливаем сохраненное согласие
        if savedConsentAccepted {
            consentAccepted = true
        }
    }
}
```

**Что делает:**
- ✅ Показывает чекбокс согласия
- ✅ Ссылки на `consent.html` и `privacy.html`
- ✅ Кнопка "Активировать" неактивна без согласия (строка 124)
- ✅ Сохраняет согласие в `@AppStorage`

**Переменные состояния:**
```10:13:Screens/26_ActivationCodeScreen.swift
// ✅ Согласие на обработку ПДн (152-ФЗ)
@State private var consentAccepted: Bool = false
@AppStorage("personal_data_consent_accepted") private var savedConsentAccepted: Bool = false
@AppStorage("personal_data_consent_date") private var consentDate: String = ""
```

**Кнопка активации:**
```124:124:Screens/26_ActivationCodeScreen.swift
.disabled(viewModel.isLoading || viewModel.code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !consentAccepted)
```

---

#### 2. ЭКРАН ПРОФИЛЯ (`ProfileScreen`)

**Файл:** `Screens/11_ProfileScreen.swift`

**Что добавлено:**

```298:428:Screens/11_ProfileScreen.swift
// MARK: - Consent Section (152-ФЗ)

private var consentSection: some View {
    VStack(alignment: .leading, spacing: Spacing.s) {
        sectionTitle("Согласие на обработку персональных данных")
        
        VStack(spacing: Spacing.s) {
            // Статус согласия
            HStack(spacing: Spacing.m) {
                Image(systemName: consentAccepted ? "checkmark.circle.fill" : "xmark.circle.fill")
                    .font(.system(size: 24))
                    .foregroundColor(consentAccepted ? .green : .red)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(consentAccepted ? "Согласие предоставлено" : "Согласие не предоставлено")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    if consentAccepted, !consentDate.isEmpty {
                        Text("Дата: \(formatConsentDate(consentDate))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            
            // Кнопки действий
            if consentAccepted {
                // Просмотр документов
                Button(action: {
                    URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/consent.html", tariffId: nil)
                }) {
                    HStack(spacing: Spacing.m) {
                        Image(systemName: "doc.text")
                            .font(.system(size: 18))
                            .foregroundColor(.primaryBlue)
                        
                        Text("Просмотреть согласие")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 14))
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                
                Button(action: {
                    URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/privacy.html", tariffId: nil)
                }) {
                    HStack(spacing: Spacing.m) {
                        Image(systemName: "lock.shield")
                            .font(.system(size: 18))
                            .foregroundColor(.primaryBlue)
                        
                        Text("Политика конфиденциальности")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 14))
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                
                // Отзыв согласия
                Button(action: {
                    showConsentRevokeAlert = true
                }) {
                    HStack(spacing: Spacing.m) {
                        Image(systemName: "xmark.circle")
                            .font(.system(size: 18))
                            .foregroundColor(.red)
                        
                        Text("Отозвать согласие")
                            .font(.body)
                            .foregroundColor(.red)
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.red.opacity(0.1))
                    )
                }
            } else {
                Text("Согласие на обработку персональных данных необходимо для использования приложения. Вы можете предоставить его при активации кода подписки.")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    .alert("Отозвать согласие?", isPresented: $showConsentRevokeAlert) {
        Button("Отменить", role: .cancel) {}
        Button("Отозвать", role: .destructive) {
            consentAccepted = false
            consentDate = ""
            // TODO: Отправить запрос на сервер об отзыве согласия
        }
    } message: {
        Text("Отзыв согласия может привести к невозможности использования некоторых функций приложения. Вы уверены?")
    }
}

private func formatConsentDate(_ dateString: String) -> String {
    let formatter = ISO8601DateFormatter()
    if let date = formatter.date(from: dateString) {
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .medium
        displayFormatter.timeStyle = .short
        displayFormatter.locale = Locale(identifier: "ru_RU")
        return displayFormatter.string(from: date)
    }
    return dateString
}
```

**Что делает:**
- ✅ Показывает статус согласия (предоставлено/не предоставлено)
- ✅ Показывает дату согласия (если есть)
- ✅ Кнопки для просмотра документов
- ✅ Кнопка для отзыва согласия
- ✅ Alert для подтверждения отзыва

**Переменные состояния:**
```27:30:Screens/11_ProfileScreen.swift
// ✅ Согласие на обработку ПДн (152-ФЗ)
@AppStorage("personal_data_consent_accepted") private var consentAccepted: Bool = false
@AppStorage("personal_data_consent_date") private var consentDate: String = ""
@State private var showConsentRevokeAlert: Bool = false
```

**Где отображается:**
```83:87:Screens/11_ProfileScreen.swift
// Безопасность
securitySection

// Согласие на обработку ПДн (152-ФЗ)
consentSection

// Реферальная программа
referralSection
```

---

## 📋 ИТОГОВЫЙ СПИСОК: Где посмотреть согласие ПДн

### ✅ В КОДЕ:

1. **Экран активации кода:**
   - Файл: `Screens/26_ActivationCodeScreen.swift`
   - Строки: 193-272 (блок `consentCard`)
   - Строка: 124 (кнопка неактивна без согласия)
   - Строки: 10-13 (переменные состояния)

2. **Экран профиля:**
   - Файл: `Screens/11_ProfileScreen.swift`
   - Строки: 298-428 (блок `consentSection`)
   - Строки: 27-30 (переменные состояния)
   - Строки: 83-87 (где отображается в UI)

3. **Документы на сервере:**
   - `https://aladdin-ai.ru/consent.html` — Согласие на обработку ПДн
   - `https://aladdin-ai.ru/privacy.html` — Политика конфиденциальности
   - `https://aladdin-ai.ru/terms.html` — Публичная оферта

---

## 🎯 ЧТО НУЖНО ДОБАВИТЬ

### ⚠️ КРИТИЧНО: Добавить навигацию к экрану активации

**Вариант 1: В Настройках (рекомендуется)**

Добавить в `Screens/05_SettingsScreen.swift` в секцию `appSection`:

```swift
// Кнопка активации кода
Button(action: {
    navigationManager.navigateTo(.activationCode)
}) {
    HStack(spacing: Spacing.m) {
        Image(systemName: "key.fill")
            .font(.system(size: 18))
            .foregroundColor(.primaryBlue)
        
        Text("Активировать код подписки")
            .font(.body)
            .foregroundColor(.textPrimary)
        
        Spacer()
        
        Image(systemName: "chevron.right")
            .font(.system(size: 14))
            .foregroundColor(.textSecondary)
    }
    .padding(Spacing.m)
    .background(
        RoundedRectangle(cornerRadius: CornerRadius.medium)
            .fill(Color.backgroundMedium.opacity(0.3))
    )
}
```

**Вариант 2: В Профиле**

Добавить в `Screens/11_ProfileScreen.swift` в секцию с подпиской.

---

## 📱 КАК ПРОТЕСТИРОВАТЬ

1. **Запустите приложение на симуляторе**
2. **Перейдите в "Настройки" или "Профиль"**
3. **Найдите кнопку "Активировать код"** (если добавлена)
4. **Или перейдите напрямую через код:**
   ```swift
   navigationManager.navigateTo(.activationCode)
   ```
5. **Проверьте:**
   - ✅ Чекбокс согласия отображается
   - ✅ Кнопка "Активировать" неактивна без согласия
   - ✅ Ссылки на документы открываются
   - ✅ После согласия кнопка становится активной

---

**Дата:** 19 ноября 2025  
**Статус:** ✅ Согласие ПДн реализовано, но навигация к экрану активации не добавлена

