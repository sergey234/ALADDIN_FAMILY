import SwiftUI
import Foundation

// ✅ Глобальные флаги для защиты от рекурсии SessionExpired
// ✅ BUILD 114: Используем принципы из ПОЛНАЯ_ИСТОРИЯ_ИСПРАВЛЕНИЙ_BUILD_77_99.md
// - Глобальный флаг виден всем экземплярам View
// - Флаг обрабатывается на MainActor-потоке UI
// - Синхронный сброс в defer предотвращает race condition
private var isHandlingSessionExpiredGlobal: Bool = false

private enum MagicAuthLinkParser {
    private static let tokenKeys = ["magic_token", "token", "auth_token", "code"]

    static func extractToken(from url: URL) -> String? {
        let path = url.path.lowercased()
        let host = url.host?.lowercased() ?? ""
        let looksLikeAuthLink = path.contains("magic") || path.contains("auth") || host.contains("auth")
        guard looksLikeAuthLink else { return nil }

        if let components = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            for item in components.queryItems ?? [] {
                let name = item.name.lowercased()
                guard tokenKeys.contains(name),
                      let value = item.value?.trimmingCharacters(in: .whitespacesAndNewlines),
                      !value.isEmpty else { continue }
                return value
            }
        }
        return nil
    }
}

/// 👤 User Profile Manager
/// Singleton класс для управления профилем пользователя
/// Предоставляет быстрый доступ к данным пользователя из кеша
@MainActor
class UserProfileManager {
    static let shared = UserProfileManager()

    private let apiService: APIService
    private let userDefaults = UserDefaults.standard

    private let displayNameKey = "user_display_name"
    private let profileNameKey = "user_profile_name"
    private let emailKey = "user_email"
    private let lastUpdateKey = "user_profile_last_update"

    private init() {
        self.apiService = APIService.shared
        // Загружаем профиль при инициализации
        loadProfileInBackground()
    }

    // MARK: - Public Methods

    /// Получить отображаемое имя пользователя
    var displayName: String {
        if let cachedName = userDefaults.string(forKey: displayNameKey),
           !cachedName.isEmpty {
            return cachedName
        }
        return NSLocalizedString("child_interface_default_name", comment: "Default user name")
    }

    /// Получить email пользователя
    var email: String? {
        return userDefaults.string(forKey: emailKey)
    }

    /// Проверить, загружен ли профиль
    var isProfileLoaded: Bool {
        return userDefaults.string(forKey: displayNameKey) != nil
    }

    /// Получить время последнего обновления профиля
    var lastUpdateTime: Date? {
        if let timestamp = userDefaults.double(forKey: lastUpdateKey) as Double?, timestamp > 0 {
            return Date(timeIntervalSince1970: timestamp)
        }
        return nil
    }

    /// Загрузить профиль из API и сохранить в кеш
    func loadProfile(completion: ((Bool) -> Void)? = nil) {
        apiService.getUserProfile { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case .success(let profile):
                    // Сохраняем данные в кеш
                    self.saveProfileToCache(profile)
                    print("✅ User profile loaded and cached: \(profile.name)")
                    completion?(true)

                case .failure(let error):
                    print("⚠️ Failed to load user profile: \(error.localizedDescription)")
                    completion?(false)
                }
            }
        }
    }

    /// Очистить кеш профиля
    func clearProfileCache() {
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        userDefaults.synchronize()
        print("🗑️ User profile cache cleared")
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        // ✅ BUILD 122: НЕ загружаем профиль на онбординге
        let hasCompletedOnboarding = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        guard hasCompletedOnboarding else {
            print("ℹ️ UserProfileManager: Онбординг не завершен - пропускаем загрузку профиля")
            return
        }
        
        // Загружаем профиль в фоне при инициализации
        // Если профиль старше 24 часов, обновляем
        if shouldRefreshProfile() {
            DispatchQueue.global(qos: .background).async { [weak self] in
                self?.loadProfile()
            }
        }
    }

    private func shouldRefreshProfile() -> Bool {
        guard let lastUpdate = lastUpdateTime else {
            return true // Нет данных, нужно загрузить
        }

        let twentyFourHours: TimeInterval = 24 * 60 * 60
        return Date().timeIntervalSince(lastUpdate) > twentyFourHours
    }

    private func saveProfileToCache(_ profile: UserProfile) {
        let priorUserId = userDefaults.string(forKey: "user_id")
        userDefaults.set(profile.name, forKey: displayNameKey)
        userDefaults.set(profile.name, forKey: profileNameKey) // Для совместимости
        userDefaults.set(profile.email, forKey: emailKey)
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        let uid = profile.id.trimmingCharacters(in: .whitespacesAndNewlines)
        if !uid.isEmpty {
            if profile.safeIsGuest {
                let existing = (userDefaults.string(forKey: "user_id") ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                let hasRealUser = !existing.isEmpty && existing != "anonymous" && !existing.lowercased().hasPrefix("guest_")
                if !hasRealUser { userDefaults.set(uid, forKey: "user_id") }
            } else {
                userDefaults.set(uid, forKey: "user_id")
            }
            let newUserId = userDefaults.string(forKey: "user_id")
            if priorUserId != newUserId {
                NotificationCenter.default.post(name: .aladdinUserIdentityDidUpdate, object: nil)
            }
        }
        userDefaults.synchronize()
    }
}

/// Сброс онбординга до `NavigationManager()` (см. `appStartLogger` выше по порядку полей в `ALADDINApp`).
private enum EarlyOnboardingLaunchReset {
    /// Handles legacy scheme typo `RESET_ONBOARDING ` (trailing space) and any key that trims to `RESET_ONBOARDING`.
    private static func resetOnboardingEnvironmentValue(from env: [String: String]) -> String? {
        if let v = env["RESET_ONBOARDING"] { return v }
        if let v = env["RESET_ONBOARDING "] { return v }
        for (key, value) in env where key.trimmingCharacters(in: .whitespacesAndNewlines) == "RESET_ONBOARDING" {
            return value
        }
        return nil
    }

    static func applyIfRequested() {
        let pi = ProcessInfo.processInfo
        let rawEnv = resetOnboardingEnvironmentValue(from: pi.environment)
        let trimmed = rawEnv?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let lowered = trimmed.lowercased()
        let fromEnv = (trimmed == "1" || lowered == "true" || lowered == "yes")
        let argv = pi.arguments
        let fromArgv = argv.contains("-RESET_ONBOARDING") || argv.contains("-ResetOnboarding")

        #if DEBUG
        let envForLog = rawEnv.map { "\"\($0)\"" } ?? "<unset>"
        print("🔧 ONBOARDING_LAUNCH: RESET_ONBOARDING env=\(envForLog) | -RESET_ONBOARDING in argv=\(argv.contains("-RESET_ONBOARDING"))")
        #endif

        guard fromEnv || fromArgv else { return }

        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        UserDefaults.standard.synchronize()
        #if DEBUG
        print("🌍 ONBOARDING_LAUNCH: hasCompletedOnboarding сброшен (env=\(fromEnv), argv=\(fromArgv))")
        #endif
    }
}

@main
struct ALADDINApp: App {
    private enum LifecycleKeys {
        static let lastScenePhase = "lifecycle_last_scene_phase"
        static let gracefulTerminateMarker = "lifecycle_graceful_terminate"
        static let lastLaunchTimestamp = "lifecycle_last_launch_ts"
    }

    // 🔍 ТЕСТОВОЕ ЛОГИРОВАНИЕ - проверяем работу при старте приложения
    private let appStartLogger: Void = {
        // RESET_ONBOARDING / -RESET_ONBOARDING must run BEFORE `@StateObject NavigationManager()` reads UserDefaults.
        EarlyOnboardingLaunchReset.applyIfRequested()
        // W4-1 UI tests: must run before `NavigationManager()` reads onboarding defaults.
        if ProcessInfo.processInfo.arguments.contains("-UITestSkipOnboarding") {
            UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            UserDefaults.standard.synchronize()
        }
        if ProcessInfo.processInfo.arguments.contains("-UITestCompanionSmoke") {
            UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            UserDefaults.standard.set("child", forKey: "current_user_role")
            UserDefaults.standard.set("2026-05-26", forKey: "companion_legal_ack_version")
            UserDefaults.standard.set(true, forKey: "companion_mic_coach_seen")
            UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.aiDataSharingEnabled)
            UserDefaults.standard.synchronize()
        }
        print("🚀 ALADDIN_APP: Application starting...")
        print("🚀 ALADDIN_APP: Testing logger initialization...")
        return ()
    }()

    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    // ✅ BUILD 112: Используем Singleton для LocalizationManager
    @StateObject private var localizationManager = LocalizationManager.shared
    /// Единый источник статистики главной / профиля (семья, устройства, угрозы).
    @StateObject private var mainViewModel = MainViewModel()
    @AppStorage("selected_theme") private var selectedTheme: String = "light"
    // ✅ BUILD 95: Показ VisualLogger overlay в RELEASE/TestFlight по флагу
    @AppStorage("enable_visual_logging_release") private var enableVisualLoggingRelease: Bool = false
    // ✅ BUILD 95: Используем @AppStorage вместо UserDefaults для предотвращения рекурсии
    @AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false
    // ✅ BUILD 96: Используем @AppStorage вместо UserDefaults для предотвращения рекурсии
    @AppStorage("auto_login_enabled") private var autoLoginEnabled: Bool = false

    // ✅ ИСПРАВЛЕНИЕ: Отслеживаем состояние приложения для предотвращения сброса навигации
    @Environment(\.scenePhase) private var scenePhase
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    // ✅ Состояние навигации
    @State private var navigationInitialized: Bool = false
    @State private var didRunDeferredBootstrap: Bool = false
    @State private var isConsumingMagicLinkToken: Bool = false
    
    // ✅ BUILD 113: Защита от повторных вызовов onAppear
    // SwiftUI может вызывать onAppear несколько раз при пересоздании View
    private static var hasInitialized = false
    private static let initializationLock = NSLock()
    /// Однократная метка: первый вызов `mainAppContent()` (после LocalizationManager).
    private static var loggedMainAppContentFirstInvocation = false

    // MARK: - Theme Helper (light-only product policy)
    private var preferredColorScheme: ColorScheme? { .light }

    private static func enforceLightAppearance() {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows)
            .forEach { $0.overrideUserInterfaceStyle = .light }
    }
    
    init() {
        LaunchDiagnostics.appendStartupTrace("ALADDINApp.init BEGIN")
        LaunchDiagnostics.appendLifecycleTrace("ALADDINApp.init BEGIN")
        // 🔴 ГЛОБАЛЬНЫЙ EXCEPTION HANDLER - для диагностики крашей
        // ✅ BUILD 114: Временно отключаем кастомный перехватчик, чтобы вернуть системные логи iOS
        /*
        NSSetUncaughtExceptionHandler { exception in
            print("💥💥💥 GLOBAL CRASH DETECTED! 💥💥💥")
            print("💥 Exception Name: \(exception.name)")
            print("💥 Exception Reason: \(exception.reason ?? "No reason provided")")
            print("💥 Stack Trace:")
            for (index, symbol) in exception.callStackSymbols.enumerated() {
                print("💥   [\(index)] \(symbol)")
            }
            print("💥💥💥 END OF CRASH REPORT 💥💥💥")
        }
        */

        print("🚀🚀🚀 ALADDINApp.init() called - APP STARTING")
        print("🚀 ALADDINApp: Начало инициализации приложения")

        // One-time cleanup: legacy profile PIN field is removed from UI/flow.
        // Keep it out of UserDefaults to avoid user confusion.
        let profilePinCleanupMarkerKey = "migration_profile_pin_removed_v1"
        if !UserDefaults.standard.bool(forKey: profilePinCleanupMarkerKey) {
            UserDefaults.standard.removeObject(forKey: "profile_pin")
            UserDefaults.standard.set(true, forKey: profilePinCleanupMarkerKey)
        }
        
        // ✅ BUILD 115: Диагностика значения hasCompletedOnboarding при старте
        #if DEBUG
        let currentOnboardingValue = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        print("🔍 BUILD \(AppConfig.buildNumber): Значение hasCompletedOnboarding в UserDefaults при старте = \(currentOnboardingValue)")
        #endif

        // IMPORTANT: Keep init lightweight.
        // Heavy debug/token operations are moved to deferred bootstrap (.task) to avoid startup hangs
        // before onboarding/main screen appears.
        let defaults = UserDefaults.standard
        let lastPhase = defaults.string(forKey: LifecycleKeys.lastScenePhase) ?? "unknown"
        let terminatedGracefully = defaults.bool(forKey: LifecycleKeys.gracefulTerminateMarker)
        if !terminatedGracefully && (lastPhase == "active" || lastPhase == "inactive") {
            LaunchDiagnostics.appendLifecycleTrace("⚠️ Inferred previous unclean termination (likely kill/watchdog). lastPhase=\(lastPhase)")
        } else {
            LaunchDiagnostics.appendLifecycleTrace("Previous termination marker: graceful=\(terminatedGracefully), lastPhase=\(lastPhase)")
        }
        defaults.set(false, forKey: LifecycleKeys.gracefulTerminateMarker)
        defaults.set(Date().timeIntervalSince1970, forKey: LifecycleKeys.lastLaunchTimestamp)
        defaults.synchronize()
        ContentBackgroundSyncScheduler.shared.registerIfNeeded()
        ContentBackgroundSyncScheduler.shared.scheduleNextRefresh()

#if DEBUG
        print("ℹ️ ALADDINApp.init: Debug/token recovery deferred to runDeferredLaunchBootstrapIfNeeded()")
#endif
        LaunchDiagnostics.appendStartupTrace("ALADDINApp.init END")
        LaunchDiagnostics.appendLifecycleTrace("ALADDINApp.init END")
    }
    
    var body: some Scene {
        WindowGroup {
            // Показываем полноценный root-контент приложения.
            // Экран loading по-прежнему доступен через navigationManager.currentScreen == .loading.
            mainAppContent()
                .onAppear {
                    LaunchDiagnostics.appendStartupTrace("WindowGroup.onAppear BEGIN")
                    LaunchDiagnostics.appendLifecycleTrace("WindowGroup.onAppear")
                    // Ensure persisted visual logs are restored once per app launch.
                    VisualLogger.shared.loadLogsAsync()
                    selectedTheme = "light"
                    Self.enforceLightAppearance()
                    LaunchDiagnostics.appendStartupTrace("WindowGroup.onAppear after loadLogsAsync")
                    // Восстанавливаем первичную инициализацию навигации, иначе приложение
                    // застревает на статическом loading-экране и не доходит до onboarding.
                    let navManager = navigationManager
                    let locManager = localizationManager
                    LaunchDiagnostics.appendStartupTrace("initializeNavigation about to run")
                    Self.initializeNavigation(
                        navigationManager: navManager,
                        localizationManager: locManager,
                        hasCompletedOnboarding: hasCompletedOnboarding
                    )
                    if ProcessInfo.processInfo.arguments.contains("-UITestChildContentW4_4") {
                        navManager.currentScreen = .childContent
                    }
                    if ProcessInfo.processInfo.arguments.contains("-UITestChildInterface")
                        || (ProcessInfo.processInfo.arguments.contains("-UITestCompanionSmoke")
                            && !ProcessInfo.processInfo.arguments.contains("-UITestCompanionHome")) {
                        navManager.currentScreen = .childInterface
                    }
                    if ProcessInfo.processInfo.arguments.contains("-UITestCompanionHome") {
                        navManager.currentScreen = .companionHome
                    }
                    consumePendingMagicAuthTokenIfNeeded()
                    LaunchDiagnostics.appendStartupTrace("initializeNavigation finished; currentScreen=\(navigationManager.currentScreen.rawValue)")
                }
                .task {
                    LaunchDiagnostics.appendStartupTrace("WindowGroup.task BEGIN deferred bootstrap")
                    LaunchDiagnostics.appendLifecycleTrace("WindowGroup.task BEGIN deferred bootstrap")
                    await runDeferredLaunchBootstrapIfNeeded()
                    LaunchDiagnostics.appendStartupTrace("WindowGroup.task END deferred bootstrap")
                    LaunchDiagnostics.appendLifecycleTrace("WindowGroup.task END deferred bootstrap")
                }
                .onOpenURL { url in
                    if let token = DevicePairingLinkParser.extractToken(from: url)?.trimmingCharacters(in: .whitespacesAndNewlines),
                       !token.isEmpty {
                        PendingAuthTokenStore.saveDeviceBindToken(token)
                        if hasCompletedOnboarding {
                            navigationManager.pendingDeviceBindToken = token
                            navigationManager.navigateTo(.joinDevice)
                        }
                        return
                    }

                    if let token = MagicAuthLinkParser.extractToken(from: url)?.trimmingCharacters(in: .whitespacesAndNewlines),
                       !token.isEmpty {
                        PendingAuthTokenStore.saveMagicAuthToken(token)
                        consumePendingMagicAuthTokenIfNeeded()
                    }
                }
                .onChange(of: hasCompletedOnboarding) { completed in
                    guard completed else { return }
                    if let raw = PendingAuthTokenStore.loadDeviceBindToken() {
                        let token = DevicePairingLinkParser.extractToken(fromScannedString: raw)
                            ?? URL(string: raw).flatMap { DevicePairingLinkParser.extractToken(from: $0) }
                        if let token, !token.isEmpty {
                            navigationManager.pendingDeviceBindToken = token
                            navigationManager.navigateTo(.joinDevice)
                        }
                    }
                    consumePendingMagicAuthTokenIfNeeded()
                }
        }
    }

    @MainActor
    private func runDeferredLaunchBootstrapIfNeeded() async {
        guard !didRunDeferredBootstrap else { return }
        didRunDeferredBootstrap = true

        print("🚀 [Phase 1] runDeferredLaunchBootstrapIfNeeded() started")
        LaunchDiagnostics.appendStartupTrace("runDeferredLaunchBootstrapIfNeeded BEGIN")
        LaunchDiagnostics.appendLifecycleTrace("runDeferredLaunchBootstrapIfNeeded BEGIN")

#if DEBUG
        // Run heavy debug recovery here (after UI is already mounted), not in init().
        LaunchDiagnostics.appendStartupTrace("deferred: KeychainAutoRecoveryService.repairTokensIfNeeded BEGIN")
        KeychainAutoRecoveryService.repairTokensIfNeeded()
        LaunchDiagnostics.appendStartupTrace("deferred: KeychainAutoRecoveryService.repairTokensIfNeeded END")
#endif

        // ✅ PHASE 1 RESTORE: SubscriptionManager.initializeOnAppStart() теперь ОБЯЗАТЕЛЕН
        // Это критично для JWT, family members, component status и предотвращения 404
        print("📡 Initializing SubscriptionManager (DEFENSIVE JWT)...")
        LaunchDiagnostics.appendStartupTrace("deferred: SubscriptionManager.initializeOnAppStart BEGIN")
        await SubscriptionManager.shared.initializeOnAppStart()
        print("✅ SubscriptionManager.initializeOnAppStart() completed successfully")
        LaunchDiagnostics.appendStartupTrace("deferred: SubscriptionManager.initializeOnAppStart END")

        LaunchDiagnostics.appendStartupTrace("deferred: FamilyReconcileService.reconcileIfNeeded BEGIN")
        await FamilyReconcileService.shared.reconcileIfNeeded(reason: "app_start", force: true)
        LaunchDiagnostics.appendStartupTrace("deferred: FamilyReconcileService.reconcileIfNeeded END")

#if DEBUG
        // Debug-only heavy operations (token seeding, auto-login diagnostics)
        let skipDebugTokensRaw = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
        let skipDebugTokens = skipDebugTokensRaw.trimmingCharacters(in: .whitespacesAndNewlines) == "1"
        let hasAutoLogin = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"] != nil &&
            !(ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"] ?? "").isEmpty
        let shouldSkipDebugTokens = skipDebugTokens || hasAutoLogin

        if !shouldSkipDebugTokens {
            LaunchDiagnostics.appendStartupTrace("deferred: DebugAuthTokenSeeder.seedIfNeeded BEGIN")
            DebugAuthTokenSeeder.seedIfNeeded()
            LaunchDiagnostics.appendStartupTrace("deferred: DebugAuthTokenSeeder.seedIfNeeded END")
        } else {
            if skipDebugTokens {
                print("⚠️ DEBUG: Пропущено создание debug токенов (SKIP_DEBUG_TOKENS=1)")
            } else if hasAutoLogin {
                print("⚠️ DEBUG: Пропущено создание debug токенов (настроен автоматический логин)")
            }
            print("   Для получения валидных токенов используйте performRealLogin() в Debug Console")
        }

        print("ℹ️ SAFE_LAUNCH: Heavy debug operations completed in deferred bootstrap")
        
        let isAutoLoginEnabled = autoLoginEnabled
        DispatchQueue.global(qos: .utility).async {
            let email = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"]
            let password = ProcessInfo.processInfo.environment["AUTO_LOGIN_PASSWORD"]
            let savedEmail = UserDefaults.standard.string(forKey: "saved_login_email")
            let savedPassword = KeychainManager.shared.loadString(forKey: .userPassword)

            print("🔍 ALADDINApp: Проверка переменных окружения...")
            let skipDebugTokensValue = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
            let skipDebugTokensTrimmed = skipDebugTokensValue.trimmingCharacters(in: .whitespacesAndNewlines)
            let skipDebugTokensIsSet = skipDebugTokensTrimmed == "1"
            print("   - AUTO_LOGIN_EMAIL: \(email != nil ? "✅ установлен (\(email?.prefix(3) ?? "")...)" : "❌ не установлен")")
            print("   - AUTO_LOGIN_PASSWORD: \(password != nil ? "✅ установлен (\(password?.count ?? 0) символов)" : "❌ не установлен")")
            print("   - SKIP_DEBUG_TOKENS: \(skipDebugTokensValue.isEmpty ? "❌ НЕ УСТАНОВЛЕН" : "✅ установлен = '\(skipDebugTokensTrimmed)' (\(skipDebugTokensIsSet ? "активен" : "не активен"))")")

            let allEnvVars = ProcessInfo.processInfo.environment
            let relevantVars = allEnvVars.keys.filter { $0.hasPrefix("AUTO_") || $0.hasPrefix("SKIP_") }
            if !relevantVars.isEmpty {
                print("   - Все найденные переменные: \(relevantVars.joined(separator: ", "))")
                for varName in relevantVars {
                    let value = allEnvVars[varName] ?? ""
                    if varName.contains("PASSWORD") {
                        print("     • \(varName) = '\(value.count) символов'")
                    } else {
                        print("     • \(varName) = '\(value)'")
                    }
                }
            } else {
                print("   - ⚠️ ВНИМАНИЕ: Не найдено ни одной переменной окружения с префиксом AUTO_ или SKIP_!")
                print("   - Проверьте, что переменные установлены в правильной схеме (Run)")
            }

            let hasValidEnvCredentials = (email != nil && password != nil && !(email?.isEmpty ?? true) && !(password?.isEmpty ?? true))
            let hasSavedCredentials = isAutoLoginEnabled && savedEmail != nil && savedPassword != nil
            let shouldAutoLogin = hasValidEnvCredentials || hasSavedCredentials

            if shouldAutoLogin {
                let loginEmail = email ?? savedEmail!
                print("🔐 ALADDINApp: Автоматический логин...")
                print("   - Email: \(loginEmail)")
                print("   - Тип: \(email != nil ? "переменные окружения" : "сохраненные credentials")")
                print("ℹ️ ALADDINApp: Автоматический логин пропущен в deferred bootstrap для стабильности")
            } else {
                if email == nil || password == nil || (email?.isEmpty ?? true) || (password?.isEmpty ?? true) {
                    print("⚠️ ALADDINApp: Переменные окружения для автоматического логина не установлены")
                    print("   - Установите AUTO_LOGIN_EMAIL и AUTO_LOGIN_PASSWORD в Scheme → Run → Arguments → Environment Variables")
                }
                print("ℹ️ ALADDINApp: Автоматический логин не настроен - пользователь должен войти вручную")
            }
        }
#endif
        LaunchDiagnostics.appendStartupTrace("runDeferredLaunchBootstrapIfNeeded END")
        LaunchDiagnostics.appendLifecycleTrace("runDeferredLaunchBootstrapIfNeeded END")
    }

    @MainActor
    private func consumePendingMagicAuthTokenIfNeeded() {
        guard hasCompletedOnboarding else { return }
        guard !isConsumingMagicLinkToken else { return }
        guard let token = PendingAuthTokenStore.loadMagicAuthToken() else { return }

        isConsumingMagicLinkToken = true
        APIService.shared.consumeMagicLink(token: token) { result in
            DispatchQueue.main.async {
                defer { isConsumingMagicLinkToken = false }
                switch result {
                case .success(let session):
                    AppConfig.authToken = session.token
                    if let refresh = session.refreshToken, !refresh.isEmpty {
                        KeychainManager.shared.save(refresh, forKey: .refreshToken)
                    }
                    if let userId = session.userId, !userId.isEmpty {
                        UserDefaults.standard.set(userId, forKey: "user_id")
                    }
                    PendingAuthTokenStore.clearMagicAuthToken()
                    navigationManager.currentScreen = .main
                case .failure(let error):
                    print("⚠️ Magic-link auth failed: \(error.localizedDescription)")
                }
            }
        }
    }

    /// Общие `environmentObject`, тема, сцена и оверлеи — и для регистрации (вне `NavigationView`), и для основного стека.
    @ViewBuilder
    private func applyRootChrome<Content: View>(_ content: Content) -> some View {
        content
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
            .environmentObject(FeedbackSystem.shared)
            .environmentObject(SubscriptionManager.shared)
            .environmentObject(mainViewModel)
            .environment(\.locale, localizationManager.locale)
            .id("nav_\(navigationManager.currentScreen.rawValue)")
            .onAppear {
                // ✅ BUILD 114: Убрано дублирование вызова initializeNavigation
                // Этот вызов уже происходит в основном WindowGroup.onAppear (линия 315)
                /*
                let navManager = navigationManager
                let locManager = localizationManager
                Self.initializeNavigation(navigationManager: navManager, localizationManager: locManager, hasCompletedOnboarding: hasCompletedOnboarding)
                */
            }
            .onChange(of: scenePhase) { newPhase in
                UserDefaults.standard.set(newPhase == .active ? "active" : newPhase == .inactive ? "inactive" : "background", forKey: LifecycleKeys.lastScenePhase)
                LaunchDiagnostics.appendLifecycleTrace("scenePhase changed -> \(newPhase)")
                if newPhase == .active {
                    print("🔄 Возврат из фона: приложение активно, экран = \(navigationManager.currentScreen)")
                    Task { @MainActor in
                        await SubscriptionManager.shared.performThrottledTrialExpiryCheckIfNeeded()
                    }
                    ContentBackgroundSyncScheduler.shared.triggerForegroundRefresh()
                } else if newPhase == .background {
                    ContentBackgroundSyncScheduler.shared.scheduleNextRefresh()
                }
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.willTerminateNotification)) { _ in
                UserDefaults.standard.set(true, forKey: LifecycleKeys.gracefulTerminateMarker)
                UserDefaults.standard.synchronize()
                LaunchDiagnostics.appendLifecycleTrace("UIApplication.willTerminateNotification received -> graceful terminate marker set")
            }
            .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("SessionExpired"))) { notification in
                guard !isHandlingSessionExpiredGlobal else {
                    #if DEBUG
                    print("⚠️ ALADDINApp: SessionExpired уже обрабатывается, пропускаем")
                    #endif
                    return
                }
                isHandlingSessionExpiredGlobal = true
                Task { @MainActor in
                    defer {
                        isHandlingSessionExpiredGlobal = false
                    }
                    let message = notification.userInfo?["message"] as? String ?? "Сессия истекла. Пожалуйста, войдите снова."
                    #if DEBUG
                    let stackTrace = Thread.callStackSymbols.prefix(10).joined(separator: "\n")
                    print("⚠️ ALADDINApp: Получено уведомление SessionExpired: \(message)")
                    print("   - Call stack (отправитель):")
                    print(stackTrace)
                    VisualLogger.shared.log("⚠️ ALADDINApp: SessionExpired получено: \(message)", level: .warning, category: "SESSION")
                    MasterLogger.shared.log(.warn, category: .business, message: "⚠️ ALADDINApp: SessionExpired notification received: \(message)")
                    #endif
                    let tokenStatus = TokenValidator.validateCurrentToken()
                    if case .valid = tokenStatus {
                        #if DEBUG
                        print("⚠️ ALADDINApp: SessionExpired получено, но токен валиден - НЕ удаляем токен")
                        VisualLogger.shared.log("⚠️ ALADDINApp: SessionExpired игнорировано - токен валиден", level: .warning, category: "SESSION")
                        MasterLogger.shared.log(.warn, category: .business, message: "⚠️ ALADDINApp: SessionExpired ignored - token is valid")
                        #endif
                        return
                    }
                    #if DEBUG
                    print("⚠️ ALADDINApp: Токен действительно невалиден - удаляем токены")
                    #endif
                    Task { @MainActor in
                        KeychainManager.shared.delete(forKey: .authToken)
                        KeychainManager.shared.delete(forKey: .refreshToken)
                    }
                    navigationManager.navigateToRoot(.onboarding)
                }
            }
            .preferredColorScheme(preferredColorScheme)
            .overlay(alignment: .bottomTrailing) {
                Group {
                    #if DEBUG
                    visualLoggerOverlay()
                    #else
                    if enableVisualLoggingRelease {
                        visualLoggerOverlay()
                    }
                    #endif
                }
            }
            .overlay {
                FeedbackParticleOverlay()
            }
    }

    // ✅ НОВОЕ: Основное содержимое приложения
    private func mainAppContent() -> some View {
        if !Self.loggedMainAppContentFirstInvocation {
            Self.loggedMainAppContentFirstInvocation = true
            LaunchDiagnostics.appendStartupTrace("mainAppContent() FIRST invocation; currentScreen=\(navigationManager.currentScreen.rawValue) hasCompletedOnboarding=\(hasCompletedOnboarding)")
        }
        if navigationManager.currentScreen == .mainWithRegistration {
            return AnyView(applyRootChrome(
                MainScreenWithRegistration(registrationVM: FamilyRegistrationViewModel())
                    .id("mainWithRegistration")
                    .onDisappear {
                        print("🔄 MainScreenWithRegistration disappeared — registration flow completed")
                    }
            ))
        }
        // КРИТИЧНО: NavigationView для основного приложения (регистрация показывается отдельным корнем выше)
        return AnyView(applyRootChrome(
        NavigationView {
                // ✅ КРИТИЧНО: Используем AnyView для каждого case - это заставит SwiftUI пересчитать
                Group {
                    switch navigationManager.currentScreen {
                    case .loading:
                        AnyView(AppLoadingView().id("loading"))
                    case .main:
                        AnyView(
                            MainScreen()
                                .id("main")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_01_MainScreen")
                        )
                    case .family:
                        AnyView(
                            FamilyScreen()
                                .id("family")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_02_FamilyScreen")
                        )
                    case .networkProtection:
                        AnyView(
                            NetworkProtectionScreen()
                                .id("network_protection")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_03_NetworkProtectionScreen")
                        )
                    case .analytics:
                        AnyView(AnalyticsScreen().id("analytics").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .settings:
                        AnyView(SettingsScreen()
                            .id("settings")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)) // ✅ Добавляем LocalizationManager
                    case .aiAssistant:
                        AnyView(
                            AIAssistantScreen()
                                .id("aiAssistant")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_06_AIAssistantScreen")
                        )
                    case .parentalControl:
                        AnyView(ParentalControlScreen()
                            .id("parentalControl")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ParentalControlScreen отображён")
                                #endif
                            })
                    case .childInterface:
                        AnyView(ChildInterfaceScreen()
                            .id("childInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ChildInterfaceScreen отображён")
                                #endif
                            })
                    case .securityEducation:
                        AnyView(SecurityEducationScreen()
                            .id("securityEducation")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: SecurityEducationScreen отображён")
                                #endif
                            })
                    case .elderlyInterface:
                        AnyView(ElderlyInterfaceScreen()
                            .id("elderlyInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ElderlyInterfaceScreen отображён")
                                #endif
                            })
                    case .tariffs:
                        AnyView(
                            TariffsScreen()
                                .id("tariffs")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_10_TariffsScreen")
                        )
#if !APP_STORE_BUILD
                    case .paymentQR:
                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем AnyView для отложенного создания View
                        // Это предотвращает попытку SwiftUI вычислить body до готовности данных
                        if let tariff = navigationManager.selectedTariffForPayment {
                            // ✅ Дополнительная проверка валидности тарифа
                            if !tariff.id.isEmpty && !tariff.title.isEmpty {
                                // ✅ Обертка в AnyView для безопасности инициализации
                                AnyView(
                                    PaymentQRScreen(tariff: tariff) {
                                        print("🔍 ALADDINApp: onPaymentCompleted вызван")
                                        navigationManager.beginManualPaymentQRClose()
                                        navigationManager.goBack(reason: "PaymentQR.onPaymentCompleted")
                                        navigationManager.selectedTariffForPayment = nil
                                    }
                                    .id("paymentQR")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                    .onAppear { 
                                        print("🚨 PaymentQRScreen открыт через NavigationLink!")
                                        print("🚨 Tariff ID: \(tariff.id)")
                                    }
                                )
                            } else {
                                // ✅ Fallback если тариф невалиден
                                AnyView(
                                    VStack(spacing: 20) {
                                        Text("Ошибка: тариф невалиден")
                                            .font(.headline)
                                        Text("ID: \(tariff.id.isEmpty ? "пусто" : tariff.id)")
                                        Text("Title: \(tariff.title.isEmpty ? "пусто" : tariff.title)")
                                        Button("Назад") {
                                                navigationManager.beginManualPaymentQRClose()
                                                navigationManager.goBack(reason: "PaymentQR.invalidTariffFallback")
                                            navigationManager.selectedTariffForPayment = nil
                                        }
                                    }
                                    .padding()
                                    .id("paymentQR_error_invalid")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                )
                            }
                        } else {
                            // ✅ Fallback если тариф не передан
                            AnyView(
                                VStack(spacing: 20) {
                                    Text("Ошибка: тариф не выбран")
                                        .font(.headline)
                                    Button("Назад") {
                                            navigationManager.beginManualPaymentQRClose()
                                            navigationManager.goBack(reason: "PaymentQR.nilTariffFallback")
                                    }
                                }
                                .padding()
                                .id("paymentQR_error_nil")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                            )
                        }
#endif
                    case .activationCode:
                        AnyView(
                            ActivationCodeScreen()
                                .id("activationCode")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .profile:
                        AnyView(
                            ProfileScreen()
                                .id("profile")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .accessibilityIdentifier("aladdin_root_11_ProfileScreen")
                                .onAppear {
                                    print("🔍 DEBUG ALADDINApp: ProfileScreen отображён!")
                                    print("🔍 DEBUG ALADDINApp: currentScreen = \(navigationManager.currentScreen)")
                                }
                        )
                    case .notifications:
                        AnyView(NotificationsScreen().id("notifications").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .privacyPolicy:
                        AnyView(PrivacyPolicyScreen().id("privacyPolicy").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .termsOfService:
                        AnyView(TermsOfServiceScreen().id("termsOfService").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .onboarding:
                        AnyView(
                            OnboardingScreen()
                                .id("onboarding")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                                .onAppear {
                                    LaunchDiagnostics.appendStartupTrace("OnboardingScreen.onAppear")
                                }
                        )
                    case .devices:
                        AnyView(DevicesScreen().id("devices").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .referral:
                        AnyView(ReferralScreen().id("referral").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .deviceDetail:
                        AnyView(DeviceDetailScreen(
                            device: Device(
                                id: "routing-preview",
                                name: "iPhone 13",
                                owner: "Пользователь",
                                type: .iphone,
                                status: .protected,
                                lastActive: "Только что"
                            )
                        )
                        .id("deviceDetail")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .familyChat:
                        AnyView(FamilyChatScreen().id("familyChat").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .support:
                        AnyView(SupportScreen().id("support").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .addMemberOptions:
                        AnyView(AddMemberOptionsScreen().id("addMemberOptions").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childRewards:
                        AnyView(ChildRewardsScreen().id("childRewards").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .companionHome:
                        AnyView(CompanionHomeScreen()
                            .id("companionHome")
                            .accessibilityIdentifier("aladdin_root_companion_home")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .companionHub:
                        AnyView(CompanionHomeScreen(initialTab: .heroes)
                            .id("companionHub_legacy")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .companionConversation:
                        AnyView(CompanionHomeScreen(initialTab: .main)
                            .id("companionConversation_legacy")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessConsent:
                        AnyView(WellnessConsentScreen()
                            .id("wellnessConsent")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessHub:
                        AnyView(WellnessHubScreen()
                            .id("wellnessHub")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessCheckin:
                        AnyView(WellnessCheckinScreen()
                            .id("wellnessCheckin")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessTrust:
                        AnyView(WellnessTrustCenterScreen()
                            .id("wellnessTrust")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessPhqLite:
                        AnyView(WellnessAssessmentFlowScreen(kind: .phqLite)
                            .id("wellnessPhqLite")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessAssessmentsHub:
                        AnyView(WellnessAssessmentsHubScreen()
                            .id("wellnessAssessmentsHub")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessAssessmentFlow:
                        AnyView(WellnessAssessmentFlowScreen(kind: .fromStore())
                            .id("wellnessAssessmentFlow")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessExercise:
                        AnyView(WellnessExerciseScreen()
                            .id("wellnessExercise")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessTimeline:
                        AnyView(WellnessTimelineScreen()
                            .id("wellnessTimeline")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessDreamJournal:
                        AnyView(WellnessDreamJournalScreen()
                            .id("wellnessDreamJournal")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessReflective:
                        AnyView(WellnessReflectiveModeScreen()
                            .id("wellnessReflective")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .wellnessTogether:
                        AnyView(WellnessTogetherModeScreen()
                            .id("wellnessTogether")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .familyTournament:
                        AnyView(FamilyTournamentView().id("familyTournament").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .unicornPet:
                        AnyView(UnicornPetView().id("unicornPet").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .youngDefender:
                        AnyView(YoungDefenderView().id("youngDefender").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .familyProtector:
                        AnyView(FamilyProtectorView().id("familyProtector").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childGoalEditor:
                        AnyView(ChildGoalEditorView().id("childGoalEditor").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .gamesParentalControl:
                        AnyView(GamesParentalControlView().id("gamesParentalControl").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .languageSettings:
                        AnyView(LanguageSettingsScreen()
                            .id("languageSettings")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .notificationSettings:
                        AnyView(NotificationSettingsScreen().id("notificationSettings").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .widgetConfiguration:
                        AnyView(WidgetConfigurationScreen().id("widgetConfiguration").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .mainWithRegistration:
                        AnyView(EmptyView())
                    case .childContent:
                        AnyView(ChildContentScreen(
                            category: ChildCategoryKey.games,
                            ageGroup: .school
                        )
                        .id("childContent")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsModal:
                        AnyView(RewardsModalView(
                            unicornBalance: .constant(245),
                            weeklyRewarded: .constant(128),
                            weeklyPunished: .constant(45)
                        )
                        .id("rewardsModal")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsQuickModal:
                        AnyView(RewardsQuickModal(unicornBalance: .constant(245))
                            .id("rewardsQuickModal")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .threatProtection:
                        AnyView(
                            ThreatProtectionScreen()
                                .id("threatProtection")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .threatProtectionSettings:
                        AnyView(
                            ThreatProtectionSettingsScreen()
                                .id("threatProtectionSettings")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .iotSecurity:
                        // Экран IoT‑защиты умного дома
                        AnyView(
                            IoTSecurityScreen()
                                .id("iotSecurity")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .advancedProtection:
                        AnyView(AdvancedProtectionSettingsScreen().id("advancedProtection").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .qrCode:
                        AnyView(QRScannerModal(onCodeScanned: { _ in }).id("qrCode").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .invitationCode:
                        AnyView(InvitationCodeInputModal(isPresented: .constant(true)).id("invitationCode").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .joinDevice:
                        AnyView(
                            JoinDeviceScreen()
                                .id("joinDevice")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    default:
                        AnyView(
                            VStack(spacing: 20) {
                                Text("🚧")
                                    .font(.system(size: 60))
                                Text("Экран в разработке")
                                    .font(.title)
                                    .fontWeight(.bold)
                                Text(navigationManager.currentScreen.rawValue)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(LinearGradient.backgroundGradient)
                            .id("default_screen")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                        )
                    }
                }
                .appContentTransition(reduceMotion ? .fade : .slideTrailing, value: navigationManager.currentScreen)
                .id("screen_\(navigationManager.currentScreen.rawValue)")
                .navigationBarHidden(true)
                // Visual logger: только `applyRootChrome` → `visualLoggerOverlay()` (без дубля `.withVisualLogger()`, иначе два виджета и перехват касаний).
            }
            .navigationViewStyle(StackNavigationViewStyle())
        ))
    }

    // MARK: - Visual Logger Overlay
    @ViewBuilder
    private func visualLoggerOverlay() -> some View {
        // Только размер виджета — без Spacer на весь экран (иначе перехватываются касания по всему экрану).
        MasterLogger.shared.visualLogView
            .frame(maxWidth: 280)
            .padding(.trailing, 16)
            .padding(.bottom, 120)
    }

}

// MARK: - Static Helper Functions

extension ALADDINApp {
    // MARK: - Static Properties
    private static var hasInitializedNavigation = false
    

    // MARK: - Navigation Initialization
    // ✅ BUILD 95: Добавлен параметр hasCompletedOnboarding для предотвращения рекурсии
    private static func initializeNavigation(navigationManager: NavigationManager, localizationManager: LocalizationManager, hasCompletedOnboarding: Bool? = nil) {
        // 📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ: Замер времени инициализации
        let startTime = Date()

        // ✅ Используем статический флаг для предотвращения повторной инициализации
        if ALADDINApp.hasInitializedNavigation {
            print("🛠️ [ALADDINApp.initializeNavigation] Уже инициализировано, пропускаем")
            return
        }

        ALADDINApp.hasInitializedNavigation = true
        print("🛠️ [ALADDINApp.initializeNavigation] Начинаем инициализацию...")
        LaunchDiagnostics.appendStartupTrace("initializeNavigation BEGIN")

        // ✅ Активируем бесплатный тариф при первом запуске
        let storeManager = StoreManager()
        if !storeManager.hasFreeTariff && !storeManager.hasActiveSubscription() {
            storeManager.activateFreeTariff()
            print("✅ First launch: Free tariff activated automatically")
        }

        // ✅ ЗАГРУЖАЕМ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
        // UserProfileManager инициализируется автоматически при первом обращении
        // и загружает профиль в фоне
        _ = UserProfileManager.shared
        print("✅ UserProfileManager initialized and profile loading started")
        _ = ProfileManager.shared

        // 🔔 ИНИЦИАЛИЗИРУЕМ PUSH УВЕДОМЛЕНИЯ
        // NotificationManager инициализируется для обработки push уведомлений
        _ = NotificationManager.shared
        // ✅ BUILD 113: Убрано логирование для абсолютной тишины на старте навигации

        // Запрашиваем разрешение на push уведомления (асинхронно, не блокирует UI)
        Task {
            _ = await NotificationManager.shared.requestAuthorization()
        }

        // Истина — persisted `UserDefaults`: `@AppStorage` в WindowGroup.onAppear может отставать
        // после `RESET_ONBOARDING` в `appStartLogger`; чтение `bool(forKey:)` здесь безопасно (без записи).
        var onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        #if DEBUG
        if let passed = hasCompletedOnboarding, passed != onboardingDone {
            print("⚠️ initializeNavigation: @AppStorage snapshot (\(passed)) ≠ UserDefaults (\(onboardingDone)) — используем UserDefaults")
        }
        #endif
#if targetEnvironment(simulator)
        // Keep simulator auth/onboarding flow on stable runtimes (e.g. iOS 15.2).
        // Apply bypass only for problematic 18.4 simulator runtime.
        let runtime = ProcessInfo.processInfo.environment["SIMULATOR_RUNTIME_VERSION"] ?? ""
        if runtime.hasPrefix("18.4") {
            onboardingDone = true
            print("🟡 Simulator onboarding bypass enabled for runtime \(runtime)")
        }
#endif
        print("🛠️ [ALADDINApp.initializeNavigation] onboardingDone = \(onboardingDone)")
        print("🛠️ [ALADDINApp.initializeNavigation] Текущий экран ДО проверки: \(navigationManager.currentScreen)")

        // ✅ ИСПРАВЛЕНИЕ: NavigationManager всегда стартует с .onboarding по умолчанию.
        // Нельзя трактовать «уже .onboarding» как «пользователь должен остаться на онбординге» —
        // иначе при hasCompletedOnboarding=true мы никогда не перейдём на .main (синий/залипший старт).
        if !onboardingDone {
            print("🔴 ONBOARDING: Показываем онбординг")
            navigationManager.currentScreen = .onboarding
        } else {
            print("🟢 ONBOARDING: Пройден (UserDefaults) — переходим на главный экран")
            navigationManager.currentScreen = .main
        }

        print("🛠️ [ALADDINApp.initializeNavigation] Текущий экран ПОСЛЕ проверки: \(navigationManager.currentScreen)")
        LaunchDiagnostics.appendStartupTrace("initializeNavigation END currentScreen=\(navigationManager.currentScreen.rawValue)")

        // 📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ: Логируем время инициализации
        let initTime = Date().timeIntervalSince(startTime)
        // ✅ BUILD 113: Убрано логирование MasterLogger для разгрузки стека
        print("🚀 App initialization completed in \(String(format: "%.2f", initTime)) seconds")
    }

    /// Автоматически проверяет и удаляет debug токены при запуске
    /// Возвращает true, если были обнаружены и удалены debug токены
    static func autoFixDebugTokensIfNeeded() -> Bool {
        let keychain = KeychainManager.shared

        // Проверяем access token
        var isDebugToken = false
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let accessToken = keychain.loadString(forKey: .authToken) {
            // Проверяем признаки debug токена
            if accessToken.contains(".debugsignature") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (содержит .debugsignature)")
            } else if accessToken.count == 140 && accessToken.contains("eyJhbGciOi") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (длина 140)")
            }
        }

        // Проверяем refresh token
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let refreshToken = keychain.loadString(forKey: .refreshToken) {
            if refreshToken == "debug-refresh-token" {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug refresh token")
            }
        }

        // Если обнаружены debug токены - удаляем их
        if isDebugToken {
            print("🔧 ALADDINApp: Автоматически удаляем debug токены...")
            keychain.delete(forKey: .authToken)
            keychain.delete(forKey: .refreshToken)
            AppConfig.authToken = nil
            UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
            print("✅ ALADDINApp: Debug токены удалены!")
            print("⚠️ ALADDINApp: ВАЖНО! Выполните реальный логин через Debug Console:")
            print("   performRealLogin(email: \"ваш_email\", password: \"ваш_пароль\") { _ in }")
            return true
        } else {
            print("✅ ALADDINApp: Debug токены не обнаружены")
            return false
        }
    }

    
}

#if DEBUG
private enum DebugAuthTokenSeeder {
    // ✅ ИСПРАВЛЕНИЕ: Убираем debug токены, которые не принимает сервер
    // Вместо этого приложение будет работать в демо режиме
    private static let demoAccessToken = ""
    private static let demoRefreshToken = ""
    
    static func seedIfNeeded() {
        // ✅ ИСПРАВЛЕНИЕ: Не создаем debug токены - приложение работает в демо режиме
        #if DEBUG
        print("ℹ️ DEBUG: Debug токены отключены - приложение работает в демо режиме")
        print("ℹ️ DEBUG: Для тестирования API используйте performRealLogin() в Debug Console")
        #endif
    }
}
#endif

#if DEBUG
// MARK: - Debug Console Functions

func clearDebugTokens() -> Bool {
    let keychain = KeychainManager.shared
    keychain.delete(forKey: .authToken)
    keychain.delete(forKey: .refreshToken)
    AppConfig.authToken = nil
    UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
    print("✅ Debug токены удалены. Выполните реальный логин.")
    return true
}

func performRealLogin(email: String, password: String, completion: @escaping (Bool) -> Void) {
    print("🔐 Выполняем логин для \(email)...")
    print("   - Endpoint: \(AppConfig.Endpoint.login)")
    print("   - Base URL: \(AppConfig.apiBaseURL)")
    print("   - Full URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
    
    Task { @MainActor in
        APIService.shared.login(email: email, password: password) { result in
        switch result {
        case .success(_):
            print("✅ Логин успешен! Токены сохранены в Keychain.")
            
            // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
            let keychain = KeychainManager.shared
            var tokensSaved = true
            
            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
            if let accessToken = keychain.loadString(forKey: .authToken) {
                print("   - Access token сохранен (длина: \(accessToken.count))")
            } else {
                print("   - ⚠️ Access token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if let refreshToken = keychain.loadString(forKey: .refreshToken) {
                print("   - Refresh token сохранен (длина: \(refreshToken.count))")
            } else {
                print("   - ⚠️ Refresh token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if tokensSaved {
                print("✅ Теперь тумблеры должны работать!")

                // 🔄 Синхронизация демо-настроек после логина
                syncDemoSettingsToServer()

                completion(true)
            } else {
                print("❌ Токены не были сохранены в Keychain!")
                completion(false)
            }
        case .failure(let error):
            print("❌ Ошибка логина: \(error.localizedDescription)")
            
            // ✅ ДЕТАЛЬНАЯ ДИАГНОСТИКА ОШИБКИ
            if let networkError = error as? NetworkError {
                switch networkError {
                case .invalidStatusCode(let code):
                    print("   - HTTP Status: \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .httpError(let code):
                    print("   - HTTP Error \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .notFound(let message):
                    print("   - ⚠️ Endpoint не найден: \(message ?? "Not Found")")
                    print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                case .unauthorized(let message):
                    print("   - ⚠️ Неверные credentials: \(message ?? "Unauthorized")")
                case .forbidden(let message):
                    print("   - ⚠️ Доступ запрещен: \(message ?? "Forbidden")")
                case .invalidURL:
                    print("   - ⚠️ Неверный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                default:
                    print("   - Тип ошибки: \(networkError)")
                }
            }
            
            print("⚠️ Проверьте:")
            print("   1. Правильность email и password")
            print("   2. Доступность сервера: \(AppConfig.apiBaseURL)")
            print("   3. Правильность endpoint: \(AppConfig.Endpoint.login)")
            print("   4. Полный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
            
            completion(false)
        }
        }
    }
}

/// Проверяет, являются ли текущие токены debug токенами
/// Использование в Debug Console: checkIfTokensAreDebug()
func checkIfTokensAreDebug() -> Bool {
    let keychain = KeychainManager.shared
    var isDebug = false
    
    // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
    if let accessToken = keychain.loadString(forKey: .authToken) {
        if accessToken.contains(".debugsignature") || (accessToken.count == 140 && accessToken.contains("eyJhbGciOi")) {
            print("⚠️ Обнаружен debug access token")
            isDebug = true
        }
    }
    
    if let refreshToken = keychain.loadString(forKey: .refreshToken) {
        if refreshToken == "debug-refresh-token" {
            print("⚠️ Обнаружен debug refresh token")
            isDebug = true
        }
    }
    
    if isDebug {
        print("❌ Токены являются debug токенами. Выполните: clearDebugTokens() и затем performRealLogin()")
    } else {
        print("✅ Токены не являются debug токенами")
    }
    
    return isDebug
}
#endif

// MARK: - Crash Logs Functions (Available in Release for CrashLogsView)

// ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
private let crashTimeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .full
    formatter.timeStyle = .full
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
    return formatter
}()

/// 🔍 ПОЛУЧИТЬ ЛОГИ КРАШЕЙ
/// Использование в Debug Console: getCrashLogs()
/// Возвращает все доступные логи крашей из UserDefaults
func getCrashLogs() -> String {
    var result = "=== 🔍 CRASH LOGS ===\n\n"
    
    // 1. Основной лог краша из AppDelegate
    if let crashLog = UserDefaults.standard.string(forKey: "last_crash_log") {
        result += "🚨 LAST CRASH LOG:\n\(crashLog)\n\n"
    } else {
        result += "✅ No crash log found in UserDefaults[\"last_crash_log\"]\n\n"
    }
    
    // 2. Время краша
    let timestamp = UserDefaults.standard.double(forKey: "crash_timestamp")
    if timestamp > 0 {
        let date = Date(timeIntervalSince1970: timestamp)
        // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
        result += "⏰ CRASH TIME: \(crashTimeFormatter.string(from: date))\n"
        result += "   Timestamp: \(timestamp)\n\n"
    } else {
        result += "✅ No crash timestamp found\n\n"
    }
    
    // 3. VisualLogger логи
    if let data = UserDefaults.standard.data(forKey: "visual_logger_logs") {
        do {
            let logs = try JSONDecoder().decode([VisualLogger.LogEntry].self, from: data)
            result += "📋 VISUAL LOGGER LOGS (\(logs.count) entries):\n"
            if logs.isEmpty {
                result += "   No logs found\n\n"
            } else {
                // Последние 30 логов
                for log in logs.suffix(30) {
                    result += "   [\(log.formattedTime)] \(log.level.rawValue) \(log.message)\n"
                    if log.file != "" {
                        result += "      📁 \(log.file):\(log.line)\n"
                    }
                }
                result += "\n"
            }
        } catch {
            result += "❌ Failed to decode visual_logger_logs: \(error.localizedDescription)\n\n"
        }
    } else {
        result += "✅ No visual_logger_logs found in UserDefaults\n\n"
    }
    
    // 4. Информация о текущем состоянии
    result += "📱 CURRENT DEVICE INFO:\n"
    result += "   Model: \(UIDevice.current.model)\n"
    result += "   iOS: \(UIDevice.current.systemVersion)\n"
    result += "   App Version: \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown")\n"
    result += "   Build: \(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown")\n"
    
    print(result)
    return result
}

/// 🧹 ОЧИСТИТЬ ЛОГИ КРАШЕЙ
/// Использование в Debug Console: clearCrashLogs()
func clearCrashLogs() -> Bool {
    UserDefaults.standard.removeObject(forKey: "last_crash_log")
    UserDefaults.standard.removeObject(forKey: "crash_timestamp")
    UserDefaults.standard.removeObject(forKey: "last_crash_stack_trace")
    VisualLogger.shared.clearSavedLogs()
    print("✅ Crash logs cleared from UserDefaults")
    return true
}

/// 📁 ПОЛУЧИТЬ ЛОГИ ИЗ ФАЙЛОВ (для TestFlight)
/// Использование в Debug Console: getCrashLogsFromFiles()
/// Возвращает логи из файлов, сохраненных в Documents directory
func getCrashLogsFromFiles() -> String {
    var result = "=== 📁 CRASH LOGS FROM FILES ===\n\n"
    
    guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
        result += "❌ Documents directory not found\n"
        print(result)
        return result
    }
    
    // 1. Основной лог краша
    let crashLogFile = documentsPath.appendingPathComponent("crash_log.txt")
    if let crashLog = try? String(contentsOf: crashLogFile, encoding: .utf8) {
        result += "🚨 CRASH LOG FILE:\n\(crashLog)\n\n"
    } else {
        result += "✅ No crash_log.txt found\n\n"
    }
    
    // 2. Stack trace файл
    let stackTraceFile = documentsPath.appendingPathComponent("crash_stack_trace.txt")
    if let stackTrace = try? String(contentsOf: stackTraceFile, encoding: .utf8) {
        result += "📋 STACK TRACE FILE:\n\(stackTrace)\n\n"
    } else {
        result += "✅ No crash_stack_trace.txt found\n\n"
    }
    
    // 3. MainScreen debug log
    let mainScreenLogFile = documentsPath.appendingPathComponent("main_screen_debug_log.txt")
    if let mainScreenLog = try? String(contentsOf: mainScreenLogFile, encoding: .utf8) {
        result += "📱 MAIN SCREEN DEBUG LOG:\n\(mainScreenLog)\n\n"
    } else {
        result += "✅ No main_screen_debug_log.txt found\n\n"
    }
    
    // 4. Список всех файлов в Documents
    result += "📂 ALL FILES IN DOCUMENTS:\n"
    if let files = try? FileManager.default.contentsOfDirectory(at: documentsPath, includingPropertiesForKeys: nil) {
        for file in files {
            result += "   - \(file.lastPathComponent)\n"
        }
    }
    
    print(result)
    return result
}

/// 📊 ПОЛУЧИТЬ ВСЕ ЛОГИ (UserDefaults + файлы)
/// Использование в Debug Console: getAllCrashLogs()
func getAllCrashLogs() -> String {
    var result = "=== 🔍 ALL CRASH LOGS ===\n\n"
    
    // Логи из UserDefaults
    result += getCrashLogs()
    result += "\n\n"
    
    // Логи из файлов
    result += getCrashLogsFromFiles()
    
    return result
}

#if DEBUG
// MARK: - Debug Console Functions (DEBUG only)
extension ALADDINApp {
    private static var preCrashStateTimer: Timer?
    
    func startPreCrashStateMonitoring() {
        // Останавливаем предыдущий таймер если есть
        Self.preCrashStateTimer?.invalidate()
        
        // Сохраняем состояние каждые 5 секунд
        Self.preCrashStateTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            if let appDelegate = UIApplication.shared.delegate as? AppDelegate {
                appDelegate.savePreCrashState()
            }
        }
        
        // Сохраняем состояние сразу при запуске
        if let appDelegate = UIApplication.shared.delegate as? AppDelegate {
            appDelegate.savePreCrashState()
        }
    }
}

/// 🔄 Синхронизация демо-настроек на сервер после авторизации
func syncDemoSettingsToServer() {
    print("🔄 Начинаем синхронизацию демо-настроек на сервер...")

    let demoComponentIds = [
        "crash_detection_agent",
        "roadside_assistance_agent",
        "incident_response_agent",
        "emergency_response_bot",
        "emergency_event_manager",
        "phishing_protection_agent",
        "malware_detection_agent",
        "mobile_security_agent",
        "network_security_agent",
        "password_security_agent"
    ]

    Task {
        for componentId in demoComponentIds {
            let demoKey = "demo_\(componentId)"
            if let demoValue = UserDefaults.standard.object(forKey: demoKey) as? Bool {
                print("   📤 Синхронизируем \(componentId): \(demoValue)")

                do {
                    try await APIService.shared.updateComponentStatus(
                        componentId: componentId,
                        isEnabled: demoValue
                    )
                    print("   ✅ \(componentId) синхронизирован")

                    // Удаляем демо-настройку после успешной синхронизации
                    UserDefaults.standard.removeObject(forKey: demoKey)
                } catch {
                    print("   ❌ Ошибка синхронизации \(componentId): \(error.localizedDescription)")
                }
            } else {
                print("   ⏭️ Нет демо-настройки для \(componentId)")
            }
        }

        print("✅ Синхронизация демо-настроек завершена")
    }
}
#endif

// MARK: - Loading View

/// ✅ НОВОЕ: View для отображения загрузки приложения
struct AppLoadingView: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.primaryBlue.opacity(0.8), Color.secondaryBlue.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: Spacing.xl) {
                Spacer()

                // Логотип или иконка приложения
                ZStack {
                    Circle()
                        .fill(Color.secondaryGold.opacity(0.2))
                        .frame(width: 120, height: 120)

                    Text("🦄")
                        .font(.system(size: 60))
                }

                // Текст загрузки
                Text("ALADDIN")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.secondaryGold)
                    .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)

                Text("Подготовка приложения...")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))

                // Анимация загрузки
                ProgressView()
                    .scaleEffect(1.2)
                    .tint(.secondaryGold)
                    .padding(.top, Spacing.m)

                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
}
