# 🔌 Dependency Injection - План Реализации

## 🎯 **ЧТО ЭТО ТАКОЕ?**
**Dependency Injection** - это способ управления зависимостями в приложении. Вместо создания объектов внутри классов, мы "впрыскиваем" их извне. Это как заказывать готовую еду вместо готовки дома - все компоненты уже готовы и правильно настроены.

## ⚠️ **ЗАЧЕМ НУЖНО?**
- **Упрощение тестирования** - легко подменить зависимости
- **Гибкость архитектуры** - легко менять реализации
- **Уменьшение связанности** - классы не зависят от конкретных реализаций
- **Улучшение читаемости** - зависимости видны явно

## 📱 **РЕАЛИЗАЦИЯ ДЛЯ iOS (Swinject)**

### Шаг 1: Установка Swinject
```swift
// Podfile
pod 'Swinject', '~> 2.8'
pod 'SwinjectAutoregistration', '~> 2.8'
```

### Шаг 2: Создание Container
```swift
// mobile/ios/DependencyInjection/ALADDINContainer.swift
import Swinject
import SwinjectAutoregistration

class ALADDINContainer {
    static let shared = Container()
    
    static func configure() {
        // Регистрация сервисов
        shared.register(NetworkManagerProtocol.self) { _ in
            ALADDINNetworkManager()
        }.inObjectScope(.container)
        
        // Регистрация AI помощника
        shared.register(AIAssistantProtocol.self) { _ in
            UnifiedSupportAPI()
        }.inObjectScope(.container)
        
        // Регистрация Security Manager
        shared.register(SecurityManagerProtocol.self) { _ in
            ALADDINSecurityManager()
        }.inObjectScope(.container)
        
        // Регистрация VPN клиента
        shared.register(VPNClientProtocol.self) { _ in
            ALADDINVPNClient()
        }.inObjectScope(.container)
        
        // Регистрация ViewModels
        shared.register(MainViewModel.self) { resolver in
            MainViewModel(
                networkManager: resolver.resolve(NetworkManagerProtocol.self)!,
                aiAssistant: resolver.resolve(AIAssistantProtocol.self)!,
                securityManager: resolver.resolve(SecurityManagerProtocol.self)!
            )
        }
        
        // Регистрация ViewControllers
        shared.register(ViewController.self) { resolver in
            let storyboard = UIStoryboard(name: "Main", bundle: nil)
            let viewController = storyboard.instantiateViewController(withIdentifier: "ViewController") as! ViewController
            viewController.viewModel = resolver.resolve(MainViewModel.self)!
            return viewController
        }
    }
}
```

### Шаг 3: Использование в ViewModel
```swift
// mobile/ios/ViewModels/MainViewModel.swift
class MainViewModel {
    private let networkManager: NetworkManagerProtocol
    private let aiAssistant: AIAssistantProtocol
    private let securityManager: SecurityManagerProtocol
    
    // Инъекция зависимостей через конструктор
    init(
        networkManager: NetworkManagerProtocol,
        aiAssistant: AIAssistantProtocol,
        securityManager: SecurityManagerProtocol
    ) {
        self.networkManager = networkManager
        self.aiAssistant = aiAssistant
        self.securityManager = securityManager
    }
    
    func loadData() {
        // Используем инжектированные зависимости
        networkManager.fetchData { [weak self] result in
            // Обработка результата
        }
    }
}
```

## 🤖 **РЕАЛИЗАЦИЯ ДЛЯ ANDROID (Koin)**

### Шаг 1: Установка Koin
```kotlin
// build.gradle
implementation "org.koin:koin-android:3.4.0"
implementation "org.koin:koin-androidx-viewmodel:3.4.0"
```

### Шаг 2: Создание Modules
```kotlin
// mobile/android/DI/ALADDINModules.kt
import org.koin.androidx.viewmodel.dsl.viewModel
import org.koin.dsl.module

val networkModule = module {
    single<NetworkManager> { ALADDINNetworkManager() }
    single<AIAssistant> { UnifiedSupportAPI() }
    single<SecurityManager> { ALADDINSecurityManager(get()) }
    single<VPNClient> { ALADDINVPNClient() }
}

val viewModelModule = module {
    viewModel { MainViewModel(get(), get(), get()) }
    viewModel { SecurityViewModel(get()) }
    viewModel { VPNViewModel(get()) }
}

val repositoryModule = module {
    single<DataRepository> { DataRepositoryImpl(get()) }
    single<SettingsRepository> { SettingsRepositoryImpl() }
}

val allModules = listOf(
    networkModule,
    viewModelModule,
    repositoryModule
)
```

### Шаг 3: Инициализация Koin
```kotlin
// mobile/android/ALADDINApplication.kt
class ALADDINApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        startKoin {
            androidContext(this@ALADDINApplication)
            modules(allModules)
        }
    }
}
```

### Шаг 4: Использование в Activity
```kotlin
// mobile/android/MainActivity.kt
class MainActivity : AppCompatActivity() {
    
    private val viewModel: MainViewModel by viewModel()
    private val networkManager: NetworkManager by inject()
    private val securityManager: SecurityManager by inject()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Используем инжектированные зависимости
        viewModel.loadData()
        securityManager.performSecurityChecks()
    }
}
```

## 📋 **ПЛАН ВНЕДРЕНИЯ (1 неделя)**

### День 1-2: Подготовка
- [ ] Установить Swinject для iOS
- [ ] Установить Koin для Android
- [ ] Создать протоколы/интерфейсы

### День 3-4: Реализация
- [ ] Создать Container для iOS
- [ ] Создать Modules для Android
- [ ] Рефакторить существующие классы

### День 5-7: Интеграция
- [ ] Интегрировать в ViewModels
- [ ] Обновить ViewControllers/Activities
- [ ] Написать тесты

## 🧪 **ТЕСТИРОВАНИЕ С DI**

### iOS тесты
```swift
// mobile/ios/Tests/MainViewModelTests.swift
class MainViewModelTests: XCTestCase {
    var container: Container!
    var viewModel: MainViewModel!
    
    override func setUp() {
        super.setUp()
        
        container = Container()
        container.register(NetworkManagerProtocol.self) { _ in
            MockNetworkManager()
        }
        container.register(AIAssistantProtocol.self) { _ in
            MockAIAssistant()
        }
        
        viewModel = container.resolve(MainViewModel.self)!
    }
    
    func testLoadData() {
        // Тест с мок-объектами
        viewModel.loadData()
        // Проверки...
    }
}
```

### Android тесты
```kotlin
// mobile/android/Tests/MainViewModelTest.kt
class MainViewModelTest : KoinTest {
    
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<NetworkManager> { MockNetworkManager() }
                single<AIAssistant> { MockAIAssistant() }
            }
        )
    }
    
    @Test
    fun testLoadData() {
        val viewModel = MainViewModel(get(), get(), get())
        viewModel.loadData()
        // Проверки...
    }
}
```

## ⚠️ **ВАЖНЫЕ МОМЕНТЫ**

### ✅ **ПЛЮСЫ:**
- Упрощение тестирования
- Гибкость архитектуры
- Уменьшение связанности
- Лучшая читаемость кода

### ⚠️ **МИНУСЫ:**
- Дополнительная сложность
- Больше кода для настройки
- Необходимость изучения фреймворков
- Потенциальные проблемы с производительностью

## 📊 **МЕТРИКИ УСПЕХА**
- [ ] 100% покрытие тестами
- [ ] Упрощение тестирования на 50%
- [ ] Уменьшение связанности на 30%
- [ ] Улучшение читаемости кода

---

*Значительно улучшает архитектуру и упрощает тестирование!*

