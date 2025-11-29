# 📋 ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ ALADDIN iOS
## От 75% до 100% готовности

### 🔴 КРИТИЧЕСКИЕ ЗАДАЧИ (НЕМЕДЛЕННО)

#### 1. ✅ СОХРАНЕНИЕ РЕЗЕРВНОЙ КОПИИ - ВЫПОЛНЕНО
- Создана резервная копия: `project.pbxproj.backup_before_fixes_20251019_205409`

#### 2. 🔧 УДАЛЕНИЕ ДУБЛИРУЮЩИХ ФАЙЛОВ (СЛЕДУЮЩИЙ ШАГ)
**Проблема:** 
```
warning: Skipping duplicate build file in Compile Sources:
- Core/Config/AppConfig.swift
- Core/Models/APIModels.swift  
- Core/Network/APIService.swift
```

**Решение:**
1. Открыть Xcode
2. Target ALADDIN → Build Phases → Compile Sources
3. Найти дубликаты и удалить
4. Тест сборки

**Команда для проверки:**
```bash
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN build 2>&1 | grep "duplicate"
```

#### 3. 🗑️ УДАЛЕНИЕ ОТСУТСТВУЮЩЕГО SECURITYMANAGER.SWIFT
**Проблема:** Файл не существует, но ссылка в проекте есть

**Решение:**
```bash
# Удалить все упоминания SecurityManager из project.pbxproj
sed -i '' '/SecurityManager/d' ALADDIN.xcodeproj/project.pbxproj
```

**Тест:**
```bash
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN build 2>&1 | grep "SecurityManager"
```

#### 4. 🔐 НАСТРОЙКА DEVELOPER TEAM ID
**Решение через Xcode:**
1. Открыть ALADDIN.xcodeproj
2. Select target ALADDIN
3. Signing & Capabilities
4. Team: выбрать Apple ID

**Или создать Personal Team:**
```bash
# Xcode автоматически создаст Personal Team при первом запуске
```

---

### 🟠 ВАЖНЫЕ ЗАДАЧИ (ДО РЕЛИЗА)

#### 5. 🔒 SSL PINNING

**Создать файл:** `Core/Network/SSLPinningManager.swift`

```swift
import Foundation

class SSLPinningManager: NSObject, URLSessionDelegate {
    
    static let shared = SSLPinningManager()
    
    // Сертификаты для pinning
    private let certificates: [SecCertificate] = {
        var certs: [SecCertificate] = []
        
        if let certPath = Bundle.main.path(forResource: "api-certificate", ofType: "cer"),
           let certData = try? Data(contentsOf: URL(fileURLWithPath: certPath)),
           let cert = SecCertificateCreateWithData(nil, certData as CFData) {
            certs.append(cert)
        }
        
        return certs
    }()
    
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // Проверка сертификата
        let policies = [SecPolicyCreateSSL(true, challenge.protectionSpace.host as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFTypeRef)
        
        var secResult = SecTrustResultType.invalid
        let status = SecTrustEvaluate(serverTrust, &secResult)
        
        guard status == errSecSuccess else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // Проверка pinned сертификатов
        let serverCertificatesCount = SecTrustGetCertificateCount(serverTrust)
        
        for i in 0..<serverCertificatesCount {
            if let serverCertificate = SecTrustGetCertificateAtIndex(serverTrust, i) {
                let serverCertificateData = SecCertificateCopyData(serverCertificate) as Data
                
                for pinnedCertificate in certificates {
                    let pinnedCertificateData = SecCertificateCopyData(pinnedCertificate) as Data
                    
                    if serverCertificateData == pinnedCertificateData {
                        completionHandler(.useCredential, URLCredential(trust: serverTrust))
                        return
                    }
                }
            }
        }
        
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}
```

**Обновить NetworkManager:**
```swift
class NetworkManager: ObservableObject {
    private let session: URLSession
    
    init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        
        // Добавить SSL Pinning
        self.session = URLSession(
            configuration: configuration,
            delegate: SSLPinningManager.shared,
            delegateQueue: nil
        )
    }
}
```

**Тест:**
```bash
# Проверить компиляцию
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN build
```

#### 6. 🔑 KEYCHAIN MANAGER

**Создать файл:** `Core/Storage/KeychainManager.swift`

```swift
import Foundation
import Security

class KeychainManager {
    
    static let shared = KeychainManager()
    
    private init() {}
    
    // MARK: - Save
    
    func save(_ value: String, forKey key: String) -> Bool {
        guard let data = value.data(using: .utf8) else { return false }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        
        return status == errSecSuccess
    }
    
    // MARK: - Load
    
    func load(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return value
    }
    
    // MARK: - Delete
    
    func delete(forKey key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess
    }
    
    // MARK: - Token Management
    
    func saveToken(_ token: String) -> Bool {
        save(token, forKey: "auth_token")
    }
    
    func loadToken() -> String? {
        load(forKey: "auth_token")
    }
    
    func deleteToken() -> Bool {
        delete(forKey: "auth_token")
    }
}
```

**Тест:**
```swift
// Тест сохранения токена
let success = KeychainManager.shared.saveToken("test_token_123")
print("Token saved: \(success)")

// Тест загрузки токена
if let token = KeychainManager.shared.loadToken() {
    print("Token loaded: \(token)")
}
```

#### 7. 📦 REPOSITORY PATTERN

**Создать файл:** `Core/Repositories/FamilyRepository.swift`

```swift
import Foundation
import Combine

protocol FamilyRepository {
    func getFamily() async throws -> Family
    func addMember(_ member: FamilyMember) async throws -> FamilyMember
    func removeMember(_ memberId: String) async throws
}

class FamilyRepositoryImpl: FamilyRepository {
    
    private let networkManager: NetworkManager
    private let storageManager: StorageManager
    
    init(networkManager: NetworkManager = NetworkManager(),
         storageManager: StorageManager = StorageManager.shared) {
        self.networkManager = networkManager
        self.storageManager = storageManager
    }
    
    func getFamily() async throws -> Family {
        // Сначала попытка загрузить из кэша
        if let cachedFamily = storageManager.loadFamily() {
            return cachedFamily
        }
        
        // Загрузка из сети
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.get(endpoint: "/family") { (result: Result<Family, Error>) in
                switch result {
                case .success(let family):
                    self.storageManager.saveFamily(family)
                    continuation.resume(returning: family)
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    func addMember(_ member: FamilyMember) async throws -> FamilyMember {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.post(endpoint: "/family/members", body: member) { (result: Result<FamilyMember, Error>) in
                switch result {
                case .success(let member):
                    continuation.resume(returning: member)
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    func removeMember(_ memberId: String) async throws {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.delete(endpoint: "/family/members/\(memberId)") { (result: Result<Void, Error>) in
                switch result {
                case .success:
                    continuation.resume()
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
}
```

**Обновить FamilyViewModel:**
```swift
class FamilyViewModel: ObservableObject {
    
    @Published var family: Family?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let repository: FamilyRepository
    
    init(repository: FamilyRepository = FamilyRepositoryImpl()) {
        self.repository = repository
    }
    
    func loadFamily() {
        isLoading = true
        
        Task {
            do {
                let family = try await repository.getFamily()
                await MainActor.run {
                    self.family = family
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
}
```

---

### 🟡 ЖЕЛАТЕЛЬНЫЕ ЗАДАЧИ (ПОСЛЕ РЕЛИЗА)

#### 8. ✅ UNIT TESTS

**Создать файл:** `Tests/UnitTests/MainViewModelTests.swift`

```swift
import XCTest
@testable import ALADDIN

class MainViewModelTests: XCTestCase {
    
    var viewModel: MainViewModel!
    
    override func setUp() {
        super.setUp()
        viewModel = MainViewModel()
    }
    
    override func tearDown() {
        viewModel = nil
        super.tearDown()
    }
    
    func testInitialState() {
        XCTAssertTrue(viewModel.isVPNEnabled)
        XCTAssertEqual(viewModel.familyMembers, 4)
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testToggleVPN() {
        let initialState = viewModel.isVPNEnabled
        viewModel.toggleVPN()
        XCTAssertNotEqual(viewModel.isVPNEnabled, initialState)
    }
    
    func testLoadDashboardData() {
        let expectation = XCTestExpectation(description: "Load dashboard data")
        
        viewModel.loadDashboardData()
        XCTAssertTrue(viewModel.isLoading)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            XCTAssertFalse(self.viewModel.isLoading)
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 2)
    }
}
```

#### 9. 🎨 UI TESTS

**Создать файл:** `Tests/UITests/MainScreenUITests.swift`

```swift
import XCTest

class MainScreenUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testMainScreenAppears() {
        XCTAssertTrue(app.isDisplayingMainScreen)
    }
    
    func testVPNToggle() {
        let vpnToggle = app.switches["VPN Toggle"]
        XCTAssertTrue(vpnToggle.exists)
        
        let initialValue = vpnToggle.value as? String
        vpnToggle.tap()
        
        let newValue = vpnToggle.value as? String
        XCTAssertNotEqual(initialValue, newValue)
    }
    
    func testNavigationToProfile() {
        let profileButton = app.buttons["Profile"]
        XCTAssertTrue(profileButton.exists)
        
        profileButton.tap()
        XCTAssertTrue(app.isDisplayingProfileScreen)
    }
}

extension XCUIApplication {
    var isDisplayingMainScreen: Bool {
        return otherElements["MainScreen"].exists
    }
    
    var isDisplayingProfileScreen: Bool {
        return otherElements["ProfileScreen"].exists
    }
}
```

#### 10. 🤖 CI/CD SETUP

**Создать файл:** `.github/workflows/ios-build.yml`

```yaml
name: iOS Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Select Xcode version
      run: sudo xcode-select -s /Applications/Xcode_14.2.app
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/Library/Developer/Xcode/DerivedData
        key: ${{ runner.os }}-xcode-${{ hashFiles('**/project.pbxproj') }}
    
    - name: Build
      run: |
        cd mobile_apps/ALADDIN_iOS
        xcodebuild -project ALADDIN.xcodeproj \
          -scheme ALADDIN \
          -destination 'platform=iOS Simulator,name=iPhone 14' \
          build
    
    - name: Run tests
      run: |
        cd mobile_apps/ALADDIN_iOS
        xcodebuild test \
          -project ALADDIN.xcodeproj \
          -scheme ALADDIN \
          -destination 'platform=iOS Simulator,name=iPhone 14'
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

---

## 📊 ПРОГРЕСС ТРЕКЕР

### Текущий статус: 75% → 100%

| Задача | Приоритет | Статус | Прогресс |
|--------|-----------|--------|----------|
| 1. Резервная копия | �� | ✅ Выполнено | 100% |
| 2. Дублирующие файлы | 🔴 | 🔄 В работе | 0% |
| 3. SecurityManager | 🔴 | ⏳ Ожидает | 0% |
| 4. Developer Team | 🔴 | ⏳ Ожидает | 0% |
| 5. SSL Pinning | 🟠 | ⏳ Ожидает | 0% |
| 6. Keychain Manager | 🟠 | ⏳ Ожидает | 0% |
| 7. Repository Layer | 🟠 | ⏳ Ожидает | 0% |
| 8. Unit Tests | 🟡 | ⏳ Ожидает | 0% |
| 9. UI Tests | 🟡 | ⏳ Ожидает | 0% |
| 10. CI/CD | 🟡 | ⏳ Ожидает | 0% |

---

## ✅ DEFINITION OF DONE

### Критические задачи:
- [ ] Сборка без warnings
- [ ] Все файлы в правильных местах
- [ ] Developer Team настроен
- [ ] SSL Pinning работает

### Важные задачи:
- [ ] Keychain используется для токенов
- [ ] Repository pattern внедрен
- [ ] Error handling добавлен
- [ ] Code coverage > 60%

### Финальная проверка:
- [ ] TestFlight build успешен
- [ ] App Store Connect готов
- [ ] Документация обновлена
- [ ] CI/CD настроен

---

**Создано:** 19 октября 2025  
**Автор:** Senior iOS Developer  
**Цель:** Довести проект от 75% до 100% готовности

