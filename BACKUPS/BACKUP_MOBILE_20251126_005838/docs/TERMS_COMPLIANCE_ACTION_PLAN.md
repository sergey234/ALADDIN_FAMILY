# 📋 ПЛАН ДЕЙСТВИЙ: ПРИВЕДЕНИЕ В СООТВЕТСТВИЕ С TERMS OF SERVICE

**Дата создания:** 14 ноября 2025  
**Версия:** 1.0  
**Статус:** В работе

---

## 🎯 ЦЕЛЬ

Привести приложение ALADDIN в полное соответствие с Terms of Service (100%) для успешной публикации в App Store.

**Текущее соответствие:** 85%  
**Целевое соответствие:** 100%

---

## 📊 ОБЩАЯ СТРУКТУРА ПЛАНА

### Критические задачи (блокируют публикацию):
1. ⚠️ **Обновление Terms of Service** (раздел 8 - Платежи)
2. ⚠️ **Добавление функции удаления аккаунта**
3. ⚠️ **Подтверждение NO-LOGS политики**

### Важные задачи (рекомендуется):
4. ⚠️ **Проверка анонимности регистрации**

---

# 🔴 ЗАДАЧА 1: ОБНОВЛЕНИЕ TERMS OF SERVICE (РАЗДЕЛ 8)

## 📌 Проблема
В Terms of Service раздел 8 "Платежи и подписки" не отражает реальную систему оплаты:
- Не упомянута QR-оплата для российских пользователей
- Не указано, что автопродление работает только для IAP
- Не указано, что уведомление за 24 часа работает только для IAP

## 🎯 Цель
Обновить Terms of Service, чтобы они точно отражали реальную систему оплаты.

## 📝 План действий

### Шаг 1.1: Обновить HTML версию Terms of Service
**Файл:** `20_terms_of_service.html`  
**Приоритет:** 🔴 Критический  
**Время:** 15 минут

**Действия:**
1. Открыть файл `20_terms_of_service.html`
2. Найти раздел "8. Платежи и подписки"
3. Заменить содержимое на:

```html
<!-- 8. Платежи и подписки -->
<div class="accordion-header" onclick="toggleAccordion(this)">
    <span style="font-size: 13px; font-weight: 600;">💳 8. Платежи и подписки</span>
    <span style="font-size: 18px;">▼</span>
</div>
<div class="accordion-content">
    <div class="section">
        <div class="subsection-title">Оплата подписки</div>
        
        <div class="highlight" style="margin-bottom: 15px;">
            <strong>🇷🇺 Для пользователей в России:</strong><br>
            • Оплата через QR-код (СБП, SberPay, Universal QR)<br>
            • Подписка НЕ продлевается автоматически<br>
            • Необходимо продлевать подписку вручную<br>
            • Уведомления о приближающемся окончании подписки отправляются через приложение
        </div>
        
        <div class="highlight" style="margin-bottom: 15px;">
            <strong>🌍 Для пользователей вне России:</strong><br>
            • Оплата через App Store (In-App Purchase)<br>
            • Подписка продлевается автоматически<br>
            • Уведомление за 24 часа до списания (через App Store)<br>
            • Отмена подписки через настройки Apple ID
        </div>
        
        <div class="list-item">• Возврат средств по правилам App Store (только для IAP)</div>
        <div class="list-item">• Для QR-оплаты возврат средств по запросу в поддержку</div>
        <div class="list-item">• Все платежи обрабатываются через защищенные платежные системы</div>
    </div>
</div>
```

**Чек-лист:**
- [ ] Файл обновлен
- [ ] Проверено отображение в браузере
- [ ] Проверена корректность форматирования

---

### Шаг 1.2: Обновить Swift версию Terms of Service
**Файл:** `Screens/19_TermsOfServiceScreen.swift`  
**Приоритет:** 🔴 Критический  
**Время:** 20 минут

**Действия:**
1. Открыть файл `Screens/19_TermsOfServiceScreen.swift`
2. Найти enum `TermsSection` → case `.payments`
3. Обновить метод `content` для case `.payments`:

```swift
case .payments:
    return [
        "Для пользователей в России: оплата через QR-код (СБП, SberPay)",
        "Для пользователей вне России: оплата через App Store (IAP)",
        "Автопродление работает только для IAP",
        "Уведомление за 24 часа работает только для IAP",
        "Возврат средств по правилам App Store (для IAP) или по запросу (для QR)"
    ]
```

4. Обновить локализацию в `LocalizationManager.swift`:
   - Найти ключи `terms_section_payments_content_*`
   - Обновить тексты для RU и EN

**Чек-лист:**
- [ ] Swift код обновлен
- [ ] Локализация обновлена (RU)
- [ ] Локализация обновлена (EN)
- [ ] Проверено в симуляторе

---

### Шаг 1.3: Обновить MD версию (для документации)
**Файл:** `docs/PRIVACY_POLICY_FULL_152FZ.md` (если есть Terms там)  
**Приоритет:** 🟡 Средний  
**Время:** 10 минут

**Действия:**
1. Если Terms of Service есть в MD файле, обновить раздел 8
2. Создать отдельный файл `docs/TERMS_OF_SERVICE_FULL.md` (опционально)

**Чек-лист:**
- [ ] MD версия обновлена (если есть)

---

### Шаг 1.4: Публикация обновленных Terms на сайте
**Приоритет:** 🔴 Критический (перед публикацией в App Store)  
**Время:** 30 минут

**Действия:**
1. Загрузить обновленный `20_terms_of_service.html` на сайт
2. Убедиться, что URL доступен публично
3. Проверить, что URL указан в App Store Connect

**Чек-лист:**
- [ ] Terms опубликованы на сайте
- [ ] URL доступен публично
- [ ] URL указан в App Store Connect

---

## ✅ Критерии завершения задачи 1:
- [ ] HTML версия обновлена
- [ ] Swift версия обновлена
- [ ] Локализация обновлена
- [ ] Terms опубликованы на сайте
- [ ] URL указан в App Store Connect

**Общее время:** ~1.5 часа  
**Приоритет:** 🔴 Критический

---

# 🔴 ЗАДАЧА 2: ДОБАВЛЕНИЕ ФУНКЦИИ УДАЛЕНИЯ АККАУНТА

## 📌 Проблема
В Terms of Service указано: "Вы можете удалить аккаунт в любой момент", но в приложении нет такой функции.

## 🎯 Цель
Добавить полную функциональность удаления аккаунта с подтверждением и удалением всех данных.

## 📝 План действий

### Шаг 2.1: Создать API endpoint на backend
**Приоритет:** 🔴 Критический  
**Время:** 2-3 часа (backend разработка)

**Действия:**
1. Создать endpoint: `DELETE /user/delete-account`
2. Реализовать удаление:
   - Всех данных пользователя
   - Связей с семьей
   - Подписок
   - Истории активности
   - VPN сессий
3. Добавить подтверждение через токен/код
4. Логировать удаление (для аудита)

**API спецификация:**
```python
DELETE /api/user/delete-account
Headers:
  Authorization: Bearer {token}
Body:
  {
    "confirmation_code": "DELETE_ACCOUNT_2025",  # Защита от случайного удаления
    "reason": "optional"  # Опциональная причина
  }
Response:
  {
    "success": true,
    "message": "Account deleted successfully",
    "deleted_at": "2025-11-14T12:00:00Z"
  }
```

**Чек-лист:**
- [ ] Endpoint создан
- [ ] Удаление всех данных реализовано
- [ ] Добавлена защита от случайного удаления
- [ ] Протестировано на staging

---

### Шаг 2.2: Добавить метод в APIService
**Файл:** `Core/Network/APIService.swift`  
**Приоритет:** 🔴 Критический  
**Время:** 30 минут

**Действия:**
1. Добавить метод `deleteAccount(confirmationCode:completion:)`:

```swift
// MARK: - Account Deletion

struct DeleteAccountRequest: Codable {
    let confirmationCode: String
    let reason: String?
}

struct DeleteAccountResponse: Codable {
    let success: Bool
    let message: String
    let deletedAt: String?
}

func deleteAccount(
    confirmationCode: String,
    reason: String? = nil,
    completion: @escaping (Result<DeleteAccountResponse, Error>) -> Void
) {
    let request = DeleteAccountRequest(
        confirmationCode: confirmationCode,
        reason: reason
    )
    networkManager.delete(
        endpoint: "/user/delete-account",
        body: request,
        completion: completion
    )
}
```

2. Добавить endpoint в `AppConfig.Endpoint`:
```swift
static let deleteAccount = "/user/delete-account"
```

**Чек-лист:**
- [ ] Метод добавлен в APIService
- [ ] Endpoint добавлен в AppConfig
- [ ] Протестировано подключение к API

---

### Шаг 2.3: Создать ViewModel для удаления аккаунта
**Файл:** `ViewModels/DeleteAccountViewModel.swift` (новый)  
**Приоритет:** 🔴 Критический  
**Время:** 1 час

**Действия:**
1. Создать новый файл `ViewModels/DeleteAccountViewModel.swift`:

```swift
import SwiftUI
import Combine

class DeleteAccountViewModel: ObservableObject {
    @Published var isDeleting: Bool = false
    @Published var errorMessage: String?
    @Published var confirmationCode: String = ""
    @Published var reason: String = ""
    @Published var showConfirmation: Bool = false
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    // Константа для подтверждения (можно сделать динамической)
    private let requiredConfirmationCode = "УДАЛИТЬ"
    
    var canDelete: Bool {
        confirmationCode.uppercased() == requiredConfirmationCode.uppercased()
    }
    
    func deleteAccount() {
        guard canDelete else {
            errorMessage = "Введите правильный код подтверждения"
            return
        }
        
        isDeleting = true
        errorMessage = nil
        
        apiService.deleteAccount(
            confirmationCode: confirmationCode,
            reason: reason.isEmpty ? nil : reason
        ) { [weak self] result in
            DispatchQueue.main.async {
                self?.isDeleting = false
                
                switch result {
                case .success:
                    // Очистить локальные данные
                    self?.clearLocalData()
                    // Показать успешное сообщение
                    self?.showConfirmation = true
                case .failure(let error):
                    self?.errorMessage = "Ошибка удаления: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func clearLocalData() {
        // Очистить все локальные данные
        StorageManager.shared.clearAllData()
        KeychainManager.shared.clearAll()
        
        // Очистить UserDefaults
        let domain = Bundle.main.bundleIdentifier!
        UserDefaults.standard.removePersistentDomain(forName: domain)
        
        // Сбросить onboarding
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
    }
}
```

**Чек-лист:**
- [ ] ViewModel создан
- [ ] Логика удаления реализована
- [ ] Очистка локальных данных реализована
- [ ] Обработка ошибок добавлена

---

### Шаг 2.4: Создать UI для удаления аккаунта
**Файл:** `Screens/DeleteAccountScreen.swift` (новый)  
**Приоритет:** 🔴 Критический  
**Время:** 1.5 часа

**Действия:**
1. Создать новый экран `Screens/DeleteAccountScreen.swift`:

```swift
import SwiftUI

struct DeleteAccountScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = DeleteAccountViewModel()
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    VStack(spacing: Spacing.s) {
                        Text("🗑️")
                            .font(.system(size: 60))
                        
                        Text("Удаление аккаунта")
                            .font(.h1)
                            .foregroundColor(.textPrimary)
                        
                        Text("Это действие необратимо")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(.top, Spacing.xl)
                    
                    // Предупреждение
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("⚠️ Внимание!")
                            .font(.bodyBold)
                            .foregroundColor(.red)
                        
                        Text("При удалении аккаунта будут удалены:")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("• Все ваши данные")
                            Text("• История активности")
                            Text("• Подписки")
                            Text("• Связи с семьей")
                        }
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.red.opacity(0.1))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .stroke(Color.red.opacity(0.3), lineWidth: 1)
                            )
                    )
                    
                    // Код подтверждения
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Для подтверждения введите:")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        Text("УДАЛИТЬ")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(Color.backgroundMedium)
                            )
                        
                        ALADDINTextField(
                            text: $viewModel.confirmationCode,
                            placeholder: "Введите код подтверждения",
                            isSecure: false
                        )
                    }
                    
                    // Причина (опционально)
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Причина удаления (необязательно):")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        TextEditor(text: $viewModel.reason)
                            .frame(height: 100)
                            .padding(Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(Color.backgroundMedium)
                            )
                    }
                    
                    // Кнопка удаления
                    PrimaryButton(
                        title: "Удалить аккаунт",
                        isEnabled: viewModel.canDelete && !viewModel.isDeleting,
                        isLoading: viewModel.isDeleting,
                        action: {
                            viewModel.deleteAccount()
                        }
                    )
                    .padding(.top, Spacing.m)
                    
                    // Ошибка
                    if let error = viewModel.errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding()
                    }
                }
                .padding(Spacing.screenPadding)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Отмена") {
                    dismiss()
                }
            }
        }
        .alert("Аккаунт удален", isPresented: $viewModel.showConfirmation) {
            Button("OK") {
                // Вернуться на экран онбординга
                UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                // Перезапустить приложение (или показать онбординг)
            }
        } message: {
            Text("Ваш аккаунт успешно удален. Все данные были удалены.")
        }
    }
}
```

**Чек-лист:**
- [ ] Экран создан
- [ ] UI соответствует дизайну приложения
- [ ] Добавлены предупреждения
- [ ] Добавлена валидация кода подтверждения
- [ ] Добавлена обработка ошибок

---

### Шаг 2.5: Добавить кнопку в ProfileScreen
**Файл:** `Screens/11_ProfileScreen.swift`  
**Приоритет:** 🔴 Критический  
**Время:** 30 минут

**Действия:**
1. Добавить кнопку "Удалить аккаунт" в секцию настроек:

```swift
// В секции настроек профиля
SettingsSection(title: "Опасная зона") {
    Button(action: {
        // Показать подтверждение перед переходом
        showDeleteAccountConfirmation = true
    }) {
        HStack {
            Text("🗑️")
                .font(.title3)
            Text("Удалить аккаунт")
                .font(.body)
                .foregroundColor(.red)
            Spacer()
            Image(systemName: "chevron.right")
                .foregroundColor(.textTertiary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.red.opacity(0.1))
        )
    }
    .buttonStyle(PlainButtonStyle())
}
```

2. Добавить state и sheet:

```swift
@State private var showDeleteAccountConfirmation: Bool = false
@State private var showDeleteAccountScreen: Bool = false

// В body добавить:
.sheet(isPresented: $showDeleteAccountScreen) {
    DeleteAccountScreen()
}
.alert("Удалить аккаунт?", isPresented: $showDeleteAccountConfirmation) {
    Button("Отмена", role: .cancel) { }
    Button("Удалить", role: .destructive) {
        showDeleteAccountScreen = true
    }
} message: {
    Text("Это действие необратимо. Все ваши данные будут удалены.")
}
```

**Чек-лист:**
- [ ] Кнопка добавлена в ProfileScreen
- [ ] Добавлено подтверждение перед переходом
- [ ] Sheet для DeleteAccountScreen настроен
- [ ] Протестировано в симуляторе

---

### Шаг 2.6: Добавить локализацию
**Файл:** `Core/Localization/LocalizationManager.swift`  
**Приоритет:** 🟡 Средний  
**Время:** 20 минут

**Действия:**
1. Добавить ключи локализации для RU и EN:

```swift
// RU
"delete_account": "Удалить аккаунт",
"delete_account_title": "Удаление аккаунта",
"delete_account_warning": "Это действие необратимо",
"delete_account_confirmation_code": "Введите код подтверждения",
"delete_account_reason": "Причина удаления (необязательно)",
"delete_account_success": "Аккаунт успешно удален",
"delete_account_error": "Ошибка удаления аккаунта",

// EN
"delete_account": "Delete Account",
"delete_account_title": "Delete Account",
"delete_account_warning": "This action is irreversible",
...
```

**Чек-лист:**
- [ ] Локализация добавлена (RU)
- [ ] Локализация добавлена (EN)
- [ ] Все тексты переведены

---

## ✅ Критерии завершения задачи 2:
- [ ] API endpoint создан и протестирован
- [ ] APIService обновлен
- [ ] ViewModel создан
- [ ] UI экран создан
- [ ] Кнопка добавлена в ProfileScreen
- [ ] Локализация добавлена
- [ ] Полный flow протестирован

**Общее время:** ~6-7 часов  
**Приоритет:** 🔴 Критический

---

# 🔴 ЗАДАЧА 3: ПОДТВЕРЖДЕНИЕ NO-LOGS ПОЛИТИКИ

## 📌 Проблема
В Terms of Service заявлено: "Мы не храним историю ваших посещений (NO-LOGS)", но это нужно подтвердить на backend.

## 🎯 Цель
Подтвердить и задокументировать NO-LOGS политику на backend.

## 📝 План действий

### Шаг 3.1: Аудит backend кода
**Приоритет:** 🔴 Критический  
**Время:** 2-3 часа (backend аудит)

**Действия:**
1. Проверить все места, где может происходить логирование VPN трафика:
   - VPN серверы
   - Прокси серверы
   - DNS серверы
   - Логи подключений
   - Базы данных

2. Проверить наличие:
   - Логирования URL запросов
   - Логирования IP адресов назначения
   - Логирования DNS запросов
   - Хранения истории подключений
   - Аналитики трафика

3. Создать отчет о найденных проблемах (если есть)

**Чек-лист:**
- [ ] Проверены VPN серверы
- [ ] Проверены прокси серверы
- [ ] Проверены DNS серверы
- [ ] Проверены логи подключений
- [ ] Проверены базы данных
- [ ] Создан отчет

---

### Шаг 3.2: Удаление логирования (если найдено)
**Приоритет:** 🔴 Критический  
**Время:** 2-4 часа (в зависимости от найденного)

**Действия:**
1. Удалить все логирование VPN трафика
2. Удалить хранение истории подключений
3. Удалить аналитику трафика (если есть)
4. Оставить только:
   - Технические логи (ошибки, производительность)
   - Агрегированную статистику (без привязки к пользователям)

**Чек-лист:**
- [ ] Логирование удалено
- [ ] История подключений удалена
- [ ] Аналитика трафика удалена
- [ ] Технические логи оставлены
- [ ] Протестировано

---

### Шаг 3.3: Добавить документацию NO-LOGS
**Приоритет:** 🔴 Критический  
**Время:** 1 час

**Действия:**
1. Создать документ `docs/NO_LOGS_POLICY.md`:

```markdown
# 🔒 NO-LOGS POLICY - ALADDIN VPN

## Принцип
ALADDIN VPN не ведет логи о:
- Посещенных сайтах
- IP адресах назначения
- DNS запросах
- Содержимом трафика
- Времени подключения (с привязкой к пользователю)

## Что мы НЕ логируем:
- ❌ URL запросов
- ❌ IP адреса назначения
- ❌ DNS запросы
- ❌ Содержимое пакетов
- ❌ История подключений (с привязкой к пользователю)

## Что мы логируем (только техническое):
- ✅ Ошибки подключения (без привязки к пользователю)
- ✅ Производительность серверов
- ✅ Агрегированная статистика (без персональных данных)
```

2. Добавить комментарии в код backend

**Чек-лист:**
- [ ] Документация создана
- [ ] Комментарии добавлены в код
- [ ] Документация доступна команде

---

### Шаг 3.4: Добавить проверку в CI/CD
**Приоритет:** 🟡 Средний  
**Время:** 1 час

**Действия:**
1. Создать скрипт проверки на наличие логирования VPN трафика
2. Добавить в CI/CD pipeline
3. Настроить автоматическую проверку при каждом коммите

**Чек-лист:**
- [ ] Скрипт проверки создан
- [ ] Добавлен в CI/CD
- [ ] Протестирован

---

### Шаг 3.5: Обновить Privacy Policy
**Приоритет:** 🟡 Средний  
**Время:** 30 минут

**Действия:**
1. Убедиться, что NO-LOGS политика четко описана в Privacy Policy
2. Добавить ссылку на документацию (если нужно)

**Чек-лист:**
- [ ] Privacy Policy обновлена
- [ ] NO-LOGS политика четко описана

---

## ✅ Критерии завершения задачи 3:
- [ ] Backend код проверен
- [ ] Логирование удалено (если было)
- [ ] Документация создана
- [ ] CI/CD проверка добавлена (опционально)
- [ ] Privacy Policy обновлена

**Общее время:** ~5-8 часов  
**Приоритет:** 🔴 Критический

---

# 🟡 ЗАДАЧА 4: ПРОВЕРКА АНОНИМНОСТИ РЕГИСТРАЦИИ

## 📌 Проблема
Нужно убедиться, что регистрация действительно анонимная и backend не требует обязательных имен.

## 🎯 Цель
Подтвердить, что регистрация полностью анонимная.

## 📝 План действий

### Шаг 4.1: Проверить API регистрации
**Приоритет:** 🟡 Средний  
**Время:** 1 час

**Действия:**
1. Проверить endpoint регистрации: `POST /family/create`
2. Убедиться, что поле `name` опциональное (не обязательное)
3. Проверить, что можно создать пользователя без имени

**API проверка:**
```python
# Должно работать:
POST /api/family/create
{
    "role": "parent",
    "age_group": "adult",
    "letter": "A"
    # name отсутствует - должно работать
}
```

**Чек-лист:**
- [ ] API проверен
- [ ] Поле name опциональное
- [ ] Регистрация без имени работает

---

### Шаг 4.2: Обновить клиентский код (если нужно)
**Приоритет:** 🟡 Средний  
**Время:** 30 минут

**Действия:**
1. Убедиться, что в `FamilyRegistrationViewModel` не отправляется имя
2. Если имя отправляется, сделать его опциональным
3. Добавить проверку: если имя не указано, использовать анонимный идентификатор

**Чек-лист:**
- [ ] Клиентский код проверен
- [ ] Имя не отправляется (или опциональное)
- [ ] Анонимный идентификатор используется

---

### Шаг 4.3: Добавить тесты
**Приоритет:** 🟢 Низкий  
**Время:** 1 час

**Действия:**
1. Создать unit тест для регистрации без имени
2. Создать integration тест для проверки анонимности

**Чек-лист:**
- [ ] Unit тесты созданы
- [ ] Integration тесты созданы
- [ ] Тесты проходят

---

## ✅ Критерии завершения задачи 4:
- [ ] API проверен
- [ ] Клиентский код обновлен (если нужно)
- [ ] Тесты добавлены (опционально)

**Общее время:** ~2-3 часа  
**Приоритет:** 🟡 Средний

---

# 📊 ОБЩИЙ ПЛАН ВЫПОЛНЕНИЯ

## Приоритеты и сроки

### Неделя 1 (Критические задачи):
- [ ] **День 1-2:** Задача 1 - Обновление Terms of Service (1.5 часа)
- [ ] **День 2-4:** Задача 2 - Удаление аккаунта (6-7 часов)
- [ ] **День 4-5:** Задача 3 - NO-LOGS политика (5-8 часов)

### Неделя 2 (Важные задачи):
- [ ] **День 1:** Задача 4 - Проверка анонимности (2-3 часа)
- [ ] **День 2-3:** Тестирование всех изменений
- [ ] **День 4-5:** Финальная проверка и подготовка к публикации

---

## 📋 ОБЩИЙ ЧЕК-ЛИСТ

### Критические задачи:
- [ ] Terms of Service обновлены (HTML, Swift, локализация)
- [ ] Terms опубликованы на сайте
- [ ] API endpoint удаления аккаунта создан
- [ ] UI удаления аккаунта реализован
- [ ] Backend NO-LOGS политика подтверждена
- [ ] Документация NO-LOGS создана

### Важные задачи:
- [ ] Анонимность регистрации подтверждена
- [ ] Все изменения протестированы
- [ ] Локализация обновлена

### Финальная проверка:
- [ ] Все задачи выполнены
- [ ] Приложение протестировано
- [ ] Документация обновлена
- [ ] Готово к публикации в App Store

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ

**Общее время:** ~15-20 часов работы

- Задача 1: 1.5 часа
- Задача 2: 6-7 часов
- Задача 3: 5-8 часов
- Задача 4: 2-3 часа
- Тестирование: 2-3 часа

---

## 🎯 РЕЗУЛЬТАТ

После выполнения всех задач:
- ✅ **Соответствие Terms of Service: 100%**
- ✅ **Готовность к публикации в App Store: 100%**
- ✅ **Все юридические требования выполнены**

---

**Дата создания плана:** 14 ноября 2025  
**Статус:** Готов к выполнению  
**Последнее обновление:** 14 ноября 2025




