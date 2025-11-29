# 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ: МЕТОДЫ ВОССТАНОВЛЕНИЯ ДОСТУПА

**Дата создания:** 16 ноября 2025  
**Версия:** 1.0  
**Цель:** Реализовать анонимные методы восстановления доступа к семье в iOS приложении ALADDIN

---

## 🎯 ОБЩЕЕ ОПИСАНИЕ ЗАДАЧИ

### Цель
Реализовать систему восстановления доступа к семье, которая:
- ✅ Соответствует принципу анонимности (не собирает персональные данные)
- ✅ Использует Recovery Code (код восстановления)
- ✅ Поддерживает локальное сохранение (Backup)
- ✅ Интегрируется с существующими методами (QR-код, ввод кода)

### Текущее состояние
- ✅ Recovery Code уже генерируется при создании семьи
- ✅ QR-код сканирование работает
- ✅ Ввод кода вручную работает
- ⚠️ RecoveryOptionsModal существует, но не подключен к логике
- ❌ Backup восстановление не реализовано
- ❌ Автоматическое сохранение кода не реализовано

---

## 📁 СТРУКТУРА ФАЙЛОВ ПРОЕКТА

### Файлы, которые нужно изменить:
1. `Shared/Components/RecoveryOptionsModal.swift` - обновить UI
2. `Core/Security/KeychainManager.swift` - добавить новые ключи
3. `ViewModels/FamilyRegistrationViewModel.swift` - добавить сохранение кода
4. `Screens/14_OnboardingScreen.swift` - обновить навигацию
5. `Shared/Components/Modals/RecoveryCodeModal.swift` - улучшить шаринг

### Файлы, которые нужно создать:
1. `Core/Security/RecoveryCodeStorageManager.swift` - менеджер для работы с кодами
2. `Shared/Components/Modals/BackupRecoveryModal.swift` - модальное окно для Backup восстановления

---

## 📌 ЭТАП 1: ИСПРАВЛЕНИЕ RecoveryOptionsModal

### Задача
Обновить `RecoveryOptionsModal` чтобы:
- Удалить опции Email и Phone (противоречат анонимности)
- Оставить только Backup
- Переименовать "Резервная копия" → "Сохранение"
- Подключить к реальной логике восстановления

### Файл: `Shared/Components/RecoveryOptionsModal.swift`

#### Шаг 1.1: Обновить enum RecoveryOption

**БЫЛО:**
```swift
enum RecoveryOption: String, CaseIterable {
    case email = "email"
    case phone = "phone"
    case backup = "backup"
    
    var displayName: String {
        switch self {
        case .email: return "Email"
        case .phone: return "Телефон"
        case .backup: return "Резервная копия"
        }
    }
    
    var icon: String {
        switch self {
        case .email: return "envelope"
        case .phone: return "phone"
        case .backup: return "externaldrive"
        }
    }
}
```

**ДОЛЖНО БЫТЬ:**
```swift
enum RecoveryOption: String, CaseIterable {
    case backup = "backup"
    
    var displayName: String {
        return "Сохранение"
    }
    
    var icon: String {
        return "externaldrive"
    }
}
```

#### Шаг 1.2: Обновить логику кнопки "Продолжить"

**БЫЛО:**
```swift
Button("Продолжить") {
    // Обработка восстановления
    isPresented = false
}
```

**ДОЛЖНО БЫТЬ:**
```swift
Button("Продолжить") {
    if selectedOption == .backup {
        // Открыть BackupRecoveryModal
        // (будет реализовано в Этапе 2)
        isPresented = false
    }
}
```

#### Шаг 1.3: Обновить UI (убрать выбор, оставить только одну опцию)

**БЫЛО:**
```swift
VStack(spacing: 12) {
    ForEach(RecoveryOption.allCases, id: \.self) { option in
        Button(action: {
            selectedOption = option
        }) {
            // ... UI для выбора опции
        }
    }
}
```

**ДОЛЖНО БЫТЬ:**
```swift
VStack(spacing: 12) {
    // Показать только Backup опцию (без выбора)
    HStack {
        Image(systemName: "externaldrive")
            .font(.title2)
            .foregroundColor(.blue)
            .frame(width: 30)
        
        Text("Сохранение")
            .font(.body)
            .foregroundColor(.primary)
        
        Spacer()
        
        Image(systemName: "checkmark.circle.fill")
            .foregroundColor(.blue)
    }
    .padding()
    .background(
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.blue.opacity(0.1))
    )
}
```

### Проверка Этапа 1
- [ ] Email опция удалена
- [ ] Phone опция удалена
- [ ] Осталась только Backup опция
- [ ] Текст изменен на "Сохранение"
- [ ] Кнопка "Продолжить" обновлена

---

## 📌 ЭТАП 2: РЕАЛИЗАЦИЯ BACKUP ВОССТАНОВЛЕНИЯ

### Задача
Реализовать локальное сохранение Recovery Code в Keychain и восстановление из него.

### Шаг 2.1: Добавить новые ключи в KeychainManager

**Файл:** `Core/Security/KeychainManager.swift`

**Найти:**
```swift
enum Key: String, CaseIterable {
    case authToken = "auth_token"
    case refreshToken = "refresh_token"
    case userPassword = "user_password"
    case biometricData = "biometric_data"
    case encryptionKey = "encryption_key"
    case deviceId = "device_id"
    case userPreferences = "user_preferences"
}
```

**Добавить:**
```swift
enum Key: String, CaseIterable {
    case authToken = "auth_token"
    case refreshToken = "refresh_token"
    case userPassword = "user_password"
    case biometricData = "biometric_data"
    case encryptionKey = "encryption_key"
    case deviceId = "device_id"
    case userPreferences = "user_preferences"
    // ✅ НОВЫЕ КЛЮЧИ ДЛЯ RECOVERY CODE
    case recoveryCode = "recovery_code"
    case familyId = "family_id"
}
```

### Шаг 2.2: Создать RecoveryCodeStorageManager

**Файл:** `Core/Security/RecoveryCodeStorageManager.swift` (СОЗДАТЬ НОВЫЙ)

**Полный код:**
```swift
import Foundation

/// 🔐 Recovery Code Storage Manager
/// Управление сохранением и восстановлением Recovery Code
class RecoveryCodeStorageManager {
    static let shared = RecoveryCodeStorageManager()
    
    private let keychain = KeychainManager.shared
    
    private init() {}
    
    // MARK: - Save Recovery Code
    
    /// Сохранить Recovery Code и Family ID в Keychain
    /// - Parameters:
    ///   - code: Recovery Code (формат: FAM-A1B2-C3D4-E5F6)
    ///   - familyID: Family ID (формат: FAM_123456)
    /// - Returns: true если сохранение успешно, false если ошибка
    func saveRecoveryCode(_ code: String, familyID: String) -> Bool {
        guard !code.isEmpty, !familyID.isEmpty else {
            print("❌ RecoveryCodeStorageManager: Пустой код или familyID")
            return false
        }
        
        // Сохраняем Recovery Code
        keychain.save(code, forKey: .recoveryCode)
        
        // Сохраняем Family ID
        keychain.save(familyID, forKey: .familyId)
        
        print("✅ RecoveryCodeStorageManager: Код сохранен: \(code)")
        return true
    }
    
    // MARK: - Get Recovery Code
    
    /// Получить сохраненный Recovery Code
    /// - Returns: Recovery Code или nil если не найден
    func getRecoveryCode() -> String? {
        return keychain.loadString(forKey: .recoveryCode)
    }
    
    /// Получить сохраненный Family ID
    /// - Returns: Family ID или nil если не найден
    func getFamilyID() -> String? {
        return keychain.loadString(forKey: .familyId)
    }
    
    // MARK: - Check Availability
    
    /// Проверить, есть ли сохраненный Recovery Code
    /// - Returns: true если код есть, false если нет
    func hasRecoveryCode() -> Bool {
        return getRecoveryCode() != nil && getFamilyID() != nil
    }
    
    // MARK: - Delete Recovery Code
    
    /// Удалить сохраненный Recovery Code и Family ID
    /// - Returns: true если удаление успешно, false если ошибка
    func deleteRecoveryCode() -> Bool {
        keychain.delete(forKey: .recoveryCode)
        keychain.delete(forKey: .familyId)
        
        print("✅ RecoveryCodeStorageManager: Код удален")
        return true
    }
}
```

### Шаг 2.3: Автоматическое сохранение при создании семьи

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`

**Найти метод `createFamily()`:**

**Найти место после успешного создания семьи:**
```swift
case .success(let response):
    self?.familyID = response.family_id
    self?.recoveryCode = response.recovery_code
    // ... остальной код
```

**Добавить после сохранения recoveryCode:**
```swift
case .success(let response):
    self?.familyID = response.family_id
    self?.recoveryCode = response.recovery_code
    
    // ✅ НОВОЕ: Автоматически сохраняем Recovery Code в Keychain
    if let recoveryCode = self?.recoveryCode,
       let familyID = self?.familyID {
        let saved = RecoveryCodeStorageManager.shared.saveRecoveryCode(
            recoveryCode,
            familyID: familyID
        )
        if saved {
            print("✅ Recovery Code автоматически сохранен в Keychain")
        }
    }
    
    // ... остальной код
```

### Шаг 2.4: Создать BackupRecoveryModal

**Файл:** `Shared/Components/Modals/BackupRecoveryModal.swift` (СОЗДАТЬ НОВЫЙ)

**Полный код:**
```swift
import SwiftUI

/// 💾 Backup Recovery Modal
/// Модальное окно для восстановления доступа из локального сохранения
struct BackupRecoveryModal: View {
    @Binding var isPresented: Bool
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showSuccess = false
    
    // Callback для успешного восстановления
    var onRecoverySuccess: (() -> Void)?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Иконка
                Image(systemName: "externaldrive.badge.icloud")
                    .font(.system(size: 64))
                    .foregroundColor(.blue)
                
                // Заголовок
                VStack(spacing: 8) {
                    Text("Восстановление из сохранения")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Восстановить доступ используя сохраненный код")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                
                // Проверка наличия кода
                if isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                } else if let error = errorMessage {
                    // Ошибка
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.orange)
                        
                        Text(error)
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.orange.opacity(0.1))
                    )
                } else if showSuccess {
                    // Успех
                    VStack(spacing: 12) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.green)
                        
                        Text("Доступ восстановлен!")
                            .font(.body)
                            .fontWeight(.semibold)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.green.opacity(0.1))
                    )
                } else {
                    // Информация
                    VStack(spacing: 12) {
                        Text("Нажмите кнопку ниже для восстановления доступа из локального сохранения")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                }
                
                Spacer()
                
                // Кнопка восстановления
                if !showSuccess {
                    Button(action: {
                        performRecovery()
                    }) {
                        Text("Восстановить")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(isLoading ? Color.gray : Color.blue)
                            )
                    }
                    .disabled(isLoading)
                } else {
                    Button(action: {
                        onRecoverySuccess?()
                        isPresented = false
                    }) {
                        Text("Готово")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.green)
                            )
                    }
                }
            }
            .padding(20)
            .navigationTitle("Восстановление")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    // MARK: - Recovery Logic
    
    private func performRecovery() {
        isLoading = true
        errorMessage = nil
        
        // Проверяем наличие кода
        guard RecoveryCodeStorageManager.shared.hasRecoveryCode() else {
            isLoading = false
            errorMessage = "Сохранение не найдено. Убедитесь, что вы ранее создали семью на этом устройстве."
            return
        }
        
        // Получаем код
        guard let recoveryCode = RecoveryCodeStorageManager.shared.getRecoveryCode(),
              let familyID = RecoveryCodeStorageManager.shared.getFamilyID() else {
            isLoading = false
            errorMessage = "Ошибка чтения сохранения"
            return
        }
        
        // Вызываем API для восстановления
        // Используем существующий метод recoverAccess из FamilyRegistrationViewModel
        // Для этого нужно передать callback или использовать NotificationCenter
        
        // Временная реализация - просто показываем успех
        // В реальной реализации нужно вызвать FamilyRegistrationViewModel.recoverAccess(withCode:)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            isLoading = false
            showSuccess = true
            onRecoverySuccess?()
        }
    }
}

// MARK: - Preview

#if DEBUG
struct BackupRecoveryModal_Previews: PreviewProvider {
    static var previews: some View {
        BackupRecoveryModal(isPresented: .constant(true))
    }
}
#endif
```

**ВАЖНО:** В методе `performRecovery()` нужно интегрировать с `FamilyRegistrationViewModel.recoverAccess(withCode:)`. Это будет сделано в Этапе 3.

### Проверка Этапа 2
- [ ] Новые ключи добавлены в KeychainManager
- [ ] RecoveryCodeStorageManager создан
- [ ] Автоматическое сохранение работает при создании семьи
- [ ] BackupRecoveryModal создан
- [ ] Методы save/get/delete работают

---

## 📌 ЭТАП 3: ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩИМИ МЕТОДАМИ

### Задача
Интегрировать Backup восстановление с существующими методами и обновить OnboardingScreen.

### Шаг 3.1: Обновить OnboardingScreen (страница 7)

**Файл:** `Screens/14_OnboardingScreen.swift`

**Найти кнопку "ВОССТАНОВИТЬ":**
```swift
Button(action: {
    showRecovery = true
    let impactFeedback = UIImpactFeedbackGenerator(style: .light)
    impactFeedback.impactOccurred()
}) {
    Text(localizationManager.localized("onboarding_recover"))
    // ...
}
```

**Заменить на ActionSheet:**

**Добавить State переменные:**
```swift
@State private var showRecoveryOptions = false
@State private var showBackupRecovery = false
@State private var showInvitationCodeInput = false
@State private var showQRScanner = false
```

**Заменить кнопку:**
```swift
Button(action: {
    showRecoveryOptions = true
    let impactFeedback = UIImpactFeedbackGenerator(style: .light)
    impactFeedback.impactOccurred()
}) {
    Text(localizationManager.localized("onboarding_recover"))
    // ... остальной UI
}
.confirmationDialog(
    "Выберите способ восстановления",
    isPresented: $showRecoveryOptions,
    titleVisibility: .visible
) {
    Button("Ввести код вручную") {
        showInvitationCodeInput = true
    }
    
    Button("Сканировать QR-код") {
        showQRScanner = true
    }
    
    Button("Восстановить из сохранения") {
        showBackupRecovery = true
    }
    
    Button("Отмена", role: .cancel) {}
}
```

**Добавить sheet модальные окна:**
```swift
.sheet(isPresented: $showBackupRecovery) {
    BackupRecoveryModal(
        isPresented: $showBackupRecovery,
        onRecoverySuccess: {
            // После успешного восстановления
            // Обновить UI или перейти на главный экран
        }
    )
}
.sheet(isPresented: $showInvitationCodeInput) {
    InvitationCodeInputModal(
        isPresented: $showInvitationCodeInput
    )
}
.sheet(isPresented: $showQRScanner) {
    QRScannerModal(
        isPresented: $showQRScanner
    )
}
```

### Шаг 3.2: Интегрировать BackupRecoveryModal с FamilyRegistrationViewModel

**Файл:** `Shared/Components/Modals/BackupRecoveryModal.swift`

**Обновить метод `performRecovery()`:**

**Найти:**
```swift
private func performRecovery() {
    // ... текущая реализация
}
```

**Заменить на:**
```swift
private func performRecovery() {
    isLoading = true
    errorMessage = nil
    
    // Проверяем наличие кода
    guard RecoveryCodeStorageManager.shared.hasRecoveryCode() else {
        isLoading = false
        errorMessage = "Сохранение не найдено. Убедитесь, что вы ранее создали семью на этом устройстве."
        return
    }
    
    // Получаем код
    guard let recoveryCode = RecoveryCodeStorageManager.shared.getRecoveryCode() else {
        isLoading = false
        errorMessage = "Ошибка чтения сохранения"
        return
    }
    
    // Создаем ViewModel для восстановления
    let viewModel = FamilyRegistrationViewModel()
    
    // Вызываем метод восстановления
    viewModel.recoverAccess(withCode: recoveryCode)
    
    // Ожидаем результат через NotificationCenter или callback
    NotificationCenter.default.addObserver(
        forName: NSNotification.Name("FamilyRecoverySuccess"),
        object: nil,
        queue: .main
    ) { _ in
        isLoading = false
        showSuccess = true
    }
    
    NotificationCenter.default.addObserver(
        forName: NSNotification.Name("FamilyRecoveryError"),
        object: nil,
        queue: .main
    ) { notification in
        isLoading = false
        if let error = notification.userInfo?["error"] as? String {
            errorMessage = error
        } else {
            errorMessage = "Ошибка восстановления доступа"
        }
    }
}
```

**ВАЖНО:** Нужно обновить `FamilyRegistrationViewModel.recoverAccess()` чтобы отправлять уведомления. Это будет сделано в следующем шаге.

### Шаг 3.3: Обновить FamilyRegistrationViewModel.recoverAccess()

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`

**Найти метод `recoverAccess(withCode:)`:**

**Найти:**
```swift
func recoverAccess(withCode code: String) {
    isLoading = true
    
    networkManager.recoverFamily(familyID: extractFamilyID(from: code)) { [weak self] result in
        DispatchQueue.main.async {
            self?.isLoading = false
            
            switch result {
            case .success(let response):
                // ... обработка успеха
            case .failure(let error):
                // ... обработка ошибки
            }
        }
    }
}
```

**Обновить для отправки уведомлений:**
```swift
func recoverAccess(withCode code: String) {
    isLoading = true
    
    networkManager.recoverFamily(familyID: extractFamilyID(from: code)) { [weak self] result in
        DispatchQueue.main.async {
            self?.isLoading = false
            
            switch result {
            case .success(let response):
                self?.familyID = response.familyId
                self?.familyMembers = response.members.map { member in
                    FamilyMember(
                        id: member.id,
                        name: member.name,
                        role: FamilyRole(storageValue: member.role) ?? .parent,
                        ageGroup: AgeGroup(rawValue: member.role) ?? .adult,
                        isActive: member.status == "protected"
                    )
                }
                
                // ✅ НОВОЕ: Сохраняем Recovery Code если еще не сохранен
                if let familyID = self?.familyID {
                    if !RecoveryCodeStorageManager.shared.hasRecoveryCode() {
                        RecoveryCodeStorageManager.shared.saveRecoveryCode(
                            code,
                            familyID: familyID
                        )
                    }
                }
                
                self?.currentStep = .completed
                self?.showSuccessModal = true
                
                // ✅ НОВОЕ: Отправляем уведомление об успехе
                NotificationCenter.default.post(
                    name: NSNotification.Name("FamilyRecoverySuccess"),
                    object: nil
                )
                
            case .failure(let error):
                self?.errorMessage = error.localizedDescription
                
                // ✅ НОВОЕ: Отправляем уведомление об ошибке
                NotificationCenter.default.post(
                    name: NSNotification.Name("FamilyRecoveryError"),
                    object: nil,
                    userInfo: ["error": error.localizedDescription]
                )
            }
        }
    }
}
```

### Проверка Этапа 3
- [ ] OnboardingScreen обновлен с ActionSheet
- [ ] BackupRecoveryModal интегрирован
- [ ] FamilyRegistrationViewModel отправляет уведомления
- [ ] Все три метода восстановления работают

---

## 📌 ЭТАП 4: УЛУЧШЕНИЕ RecoveryCodeModal

### Задача
Улучшить существующую кнопку "Поделиться" в RecoveryCodeModal.

### Шаг 4.1: Изменить текст кнопки

**Файл:** `Shared/Components/Modals/RecoveryCodeModal.swift`

**Найти:**
```swift
Text("Поделиться QR-кодом")
```

**Заменить на:**
```swift
Text("Поделиться")
```

### Шаг 4.2: Улучшить текст при шаринге

**Найти:**
```swift
.sheet(isPresented: $showShareSheet) {
    ShareSheet(activityItems: [recoveryCode])
}
```

**Заменить на:**
```swift
.sheet(isPresented: $showShareSheet) {
    ShareSheet(activityItems: [
        """
        🔑 Код восстановления ALADDIN: \(recoveryCode)
        
        Используйте этот код для восстановления доступа к семье.
        Сохраните его в безопасном месте.
        
        Приложение: ALADDIN - Защита семьи от киберугроз
        """
    ])
}
```

### Шаг 4.3: Опционально - добавить QR-код в Share Sheet

**Найти метод `generateQRCode(from:)`:**

**Обновить ShareSheet чтобы включать QR-код:**
```swift
.sheet(isPresented: $showShareSheet) {
    var shareItems: [Any] = [
        """
        🔑 Код восстановления ALADDIN: \(recoveryCode)
        
        Используйте этот код для восстановления доступа к семье.
        Сохраните его в безопасном месте.
        """
    ]
    
    // Добавляем QR-код как изображение
    if let qrCodeImage = generateQRCode(from: recoveryCode) {
        shareItems.append(qrCodeImage)
    }
    
    ShareSheet(activityItems: shareItems)
}
```

### Проверка Этапа 4
- [ ] Текст кнопки изменен на "Поделиться"
- [ ] Текст при шаринге улучшен
- [ ] QR-код добавлен в Share Sheet (опционально)

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit тесты

**Файл:** `Tests/UnitTests/RecoveryCodeStorageManagerTests.swift` (СОЗДАТЬ НОВЫЙ)

```swift
import XCTest
@testable import ALADDIN

final class RecoveryCodeStorageManagerTests: XCTestCase {
    var storageManager: RecoveryCodeStorageManager!
    
    override func setUp() {
        super.setUp()
        storageManager = RecoveryCodeStorageManager.shared
        // Очищаем перед каждым тестом
        storageManager.deleteRecoveryCode()
    }
    
    override func tearDown() {
        storageManager.deleteRecoveryCode()
        super.tearDown()
    }
    
    func testSaveRecoveryCode() {
        let code = "FAM-A1B2-C3D4-E5F6"
        let familyID = "FAM_123456"
        
        let result = storageManager.saveRecoveryCode(code, familyID: familyID)
        
        XCTAssertTrue(result, "Сохранение должно быть успешным")
        XCTAssertTrue(storageManager.hasRecoveryCode(), "Код должен быть сохранен")
    }
    
    func testGetRecoveryCode() {
        let code = "FAM-A1B2-C3D4-E5F6"
        let familyID = "FAM_123456"
        
        storageManager.saveRecoveryCode(code, familyID: familyID)
        
        let retrievedCode = storageManager.getRecoveryCode()
        let retrievedFamilyID = storageManager.getFamilyID()
        
        XCTAssertEqual(retrievedCode, code, "Код должен совпадать")
        XCTAssertEqual(retrievedFamilyID, familyID, "Family ID должен совпадать")
    }
    
    func testDeleteRecoveryCode() {
        let code = "FAM-A1B2-C3D4-E5F6"
        let familyID = "FAM_123456"
        
        storageManager.saveRecoveryCode(code, familyID: familyID)
        XCTAssertTrue(storageManager.hasRecoveryCode(), "Код должен быть сохранен")
        
        storageManager.deleteRecoveryCode()
        XCTAssertFalse(storageManager.hasRecoveryCode(), "Код должен быть удален")
    }
    
    func testHasRecoveryCode() {
        XCTAssertFalse(storageManager.hasRecoveryCode(), "Кода не должно быть изначально")
        
        storageManager.saveRecoveryCode("FAM-A1B2-C3D4-E5F6", familyID: "FAM_123456")
        XCTAssertTrue(storageManager.hasRecoveryCode(), "Код должен быть после сохранения")
    }
}
```

### UI тесты

**Файл:** `Tests/UITests/BackupRecoveryUITests.swift` (СОЗДАТЬ НОВЫЙ)

```swift
import XCTest

final class BackupRecoveryUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testBackupRecoveryFlow() throws {
        // 1. Перейти на онбординг
        // 2. Нажать "ВОССТАНОВИТЬ"
        // 3. Выбрать "Восстановить из сохранения"
        // 4. Проверить, что открылся BackupRecoveryModal
        // 5. Нажать "Восстановить"
        // 6. Проверить результат
    }
    
    func testBackupRecoveryNoCode() throws {
        // 1. Убедиться, что кода нет в Keychain
        // 2. Открыть BackupRecoveryModal
        // 3. Проверить, что показывается ошибка "Сохранение не найдено"
    }
}
```

---

## ✅ ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### Этап 1: RecoveryOptionsModal
- [ ] Email опция удалена
- [ ] Phone опция удалена
- [ ] Осталась только Backup опция
- [ ] Текст изменен на "Сохранение"
- [ ] Кнопка "Продолжить" обновлена

### Этап 2: Backup восстановление
- [ ] Новые ключи добавлены в KeychainManager
- [ ] RecoveryCodeStorageManager создан
- [ ] Все методы реализованы (save/get/delete/has)
- [ ] Автоматическое сохранение работает при создании семьи
- [ ] BackupRecoveryModal создан
- [ ] UI модального окна реализован

### Этап 3: Интеграция
- [ ] OnboardingScreen обновлен с ActionSheet
- [ ] Три опции в ActionSheet работают
- [ ] BackupRecoveryModal интегрирован
- [ ] FamilyRegistrationViewModel отправляет уведомления
- [ ] Все методы восстановления работают

### Этап 4: Улучшение RecoveryCodeModal
- [ ] Текст кнопки изменен на "Поделиться"
- [ ] Текст при шаринге улучшен
- [ ] QR-код добавлен в Share Sheet (опционально)

### Тестирование
- [ ] Unit тесты созданы и проходят
- [ ] UI тесты созданы и проходят
- [ ] Ручное тестирование выполнено

---

## 📝 ЛОКАЛИЗАЦИЯ

### Добавить ключи в LocalizationManager

**Файл:** `Core/Localization/LocalizationManager.swift`

**Русский (RU):**
```swift
"recovery_backup_title": "Восстановление из сохранения",
"recovery_backup_description": "Восстановить доступ используя сохраненный код",
"recovery_backup_button": "Восстановить",
"recovery_backup_success": "Доступ восстановлен!",
"recovery_backup_no_code": "Сохранение не найдено",
"recovery_code_saved": "Код восстановления сохранен локально",
"recovery_options_title": "Выберите способ восстановления",
"recovery_option_manual": "Ввести код вручную",
"recovery_option_qr": "Сканировать QR-код",
"recovery_option_backup": "Восстановить из сохранения"
```

**Английский (EN):**
```swift
"recovery_backup_title": "Restore from Backup",
"recovery_backup_description": "Restore access using saved code",
"recovery_backup_button": "Restore",
"recovery_backup_success": "Access restored!",
"recovery_backup_no_code": "No backup found",
"recovery_code_saved": "Recovery code saved locally",
"recovery_options_title": "Choose recovery method",
"recovery_option_manual": "Enter code manually",
"recovery_option_qr": "Scan QR code",
"recovery_option_backup": "Restore from backup"
```

---

## 🐛 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: Keychain не сохраняет данные
**Решение:** Проверить права доступа в KeychainManager. Убедиться, что используется правильный service identifier.

### Проблема 2: NotificationCenter не работает
**Решение:** Убедиться, что уведомления отправляются на главном потоке (DispatchQueue.main.async).

### Проблема 3: ActionSheet не показывается
**Решение:** Убедиться, что используется `.confirmationDialog()` для iOS 15+ или `.actionSheet()` для более старых версий.

### Проблема 4: BackupRecoveryModal не закрывается после успеха
**Решение:** Убедиться, что вызывается `onRecoverySuccess?()` и `isPresented = false`.

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация Apple
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)
- [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller)
- [confirmationDialog](https://developer.apple.com/documentation/swiftui/view/confirmationdialog(_:ispresented:titlevisibility:presenting:actions:)-8d7kb)

### Файлы для справки
- `Core/Security/KeychainManager.swift` - пример использования Keychain
- `ViewModels/FamilyRegistrationViewModel.swift` - пример работы с API
- `Shared/Components/Modals/RecoveryCodeModal.swift` - пример модального окна

---

## 🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ

После выполнения всех этапов должно быть реализовано:

1. ✅ RecoveryOptionsModal обновлен (только Backup)
2. ✅ Recovery Code автоматически сохраняется в Keychain
3. ✅ Backup восстановление работает
4. ✅ ActionSheet с тремя опциями восстановления
5. ✅ Улучшенный Share Sheet в RecoveryCodeModal
6. ✅ Все методы анонимны и не требуют персональных данных

---

**Дата создания:** 16 ноября 2025  
**Версия:** 1.0  
**Статус:** Готов к реализации




