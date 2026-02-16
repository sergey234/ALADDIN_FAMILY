import SwiftUI
import os.log
#if !targetEnvironment(simulator)
import Darwin
#endif

/// 🩺 Settings Screen Diagnostic - МИНИМАЛЬНЫЙ ТЕСТОВЫЙ VIEW
/// Создан для выявления реальной причины краша Settings Screen
/// Если этот View работает - проблема в компонентах основного экрана
struct SettingsScreenDiagnostic: View {

    // MARK: - Environment Objects (Тестируем по одному)

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    // @EnvironmentObject private var localizationManager: LocalizationManager // Пока отключен

    // MARK: - State (Минимальный набор)

    @State private var testCounter: Int = 0

    // MARK: - Body

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("🩺 Settings Screen - Diagnostic Mode")
                    .font(.title)
                    .foregroundColor(.red)

                Text("Если это видно - базовый SwiftUI View работает!")
                    .foregroundColor(.green)

                Divider()

                // 🔥 КРИТИЧЕСКОЕ: Логируем начало каждого теста
                Text("Текущий тест: проверка базовых компонентов...")
                    .font(.caption)
                    .foregroundColor(.blue)

                // ТЕСТ 1: Базовые компоненты SwiftUI
                testBasicSwiftUI()

                Divider()

                // ТЕСТ 2: Environment Objects
                testEnvironmentObjects()

                Divider()

                // ТЕСТ 3: State и модификаторы
                testStateAndModifiers()

                Divider()

                // ТЕСТ 4: Singleton менеджеры (если предыдущие работают)
                testSingletonManagers()

                Divider()

                // ТЕСТ 4.5: @Published свойства - КРИТИЧЕСКОЕ!
                testPublishedProperties()

                Divider()

                // ТЕСТ 5: Localization (если все работает)
                testLocalization()

                Divider()

                // 🔥 ТЕСТ 6: CRASH LOGS - КРИТИЧЕСКОЕ
                testCrashLogs()

                Spacer()
            }
            .padding()
        }
        .navigationTitle("Settings Diagnostic")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            crashLog("🩺 DIAGNOSTIC: SettingsScreenDiagnostic onAppear вызван")
            crashLog("🩺 DIAGNOSTIC: Thread.isMainThread = \(Thread.isMainThread)")
            crashLog("🩺 DIAGNOSTIC: Базовый тест прошел - SwiftUI работает")
            print("🩺 DIAGNOSTIC: onAppear вызван - базовый тест прошел")
            print("🩺 DIAGNOSTIC: Thread.isMainThread = \(Thread.isMainThread)")
        }
    }

    // MARK: - Тестовые функции

    @ViewBuilder
    private func testBasicSwiftUI() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🧪 ТЕСТ 1: Базовые компоненты SwiftUI")
                .font(.headline)

            Text("✅ Text работает")
            Button("✅ Button работает") {
                crashLog("🧪 ТЕСТ 1: Button нажат, counter = \(testCounter + 1)")
                testCounter += 1
                print("🩺 DIAGNOSTIC: Button нажат, counter = \(testCounter)")
            }
            Text("Counter: \(testCounter)")
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
        .onAppear {
            crashLog("🧪 ТЕСТ 1: testBasicSwiftUI появился на экране")
        }
    }

    @ViewBuilder
    private func testEnvironmentObjects() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🧪 ТЕСТ 2: Environment Objects")
                .font(.headline)

            Text("✅ dismiss Environment работает")

            Button("✅ navigationManager Environment") {
                crashLog("🧪 ТЕСТ 2: Проверка navigationManager")
                let nm = navigationManager
                crashLog("🧪 navigationManager OK: \(nm)")
                print("🩺 DIAGNOSTIC: navigationManager = \(navigationManager)")
            }
        }
        .padding()
        .background(Color.blue.opacity(0.1))
        .cornerRadius(8)
        .onAppear {
            crashLog("🧪 ТЕСТ 2: testEnvironmentObjects появился на экране")
        }
    }

    @ViewBuilder
    private func testStateAndModifiers() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🧪 ТЕСТ 3: State и модификаторы")
                .font(.headline)

            Text("✅ @State работает")
            Text("✅ .padding() работает")
            Text("✅ .background() работает")
            Text("✅ .cornerRadius() работает")
        }
        .padding()
        .background(Color.green.opacity(0.1))
        .cornerRadius(8)
    }

    @ViewBuilder
    private func testSingletonManagers() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🧪 ТЕСТ 4: Singleton менеджеры")
                .font(.headline)

            Button("✅ NotificationManager.shared") {
                let manager = NotificationManager.shared
                print("🩺 DIAGNOSTIC: NotificationManager.shared = \(manager)")
            }

            Button("✅ SecurityManager.shared") {
                let manager = SecurityManager.shared
                print("🩺 DIAGNOSTIC: SecurityManager.shared = \(manager)")
            }

            Button("✅ TariffManager.shared") {
                let manager = TariffManager.shared
                print("🩺 DIAGNOSTIC: TariffManager.shared = \(manager)")
            }
        }
        .padding()
        .background(Color.orange.opacity(0.1))
        .cornerRadius(8)
    }

    @ViewBuilder
    private func testPublishedProperties() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🎯 ТЕСТ 4.5: @Published свойства - КРИТИЧЕСКОЕ!")
                .font(.headline)

            Button("🔍 NotificationManager @Published") {
                crashLog("🧪 TEST: Проверка NotificationManager @Published свойств")
                let nm = NotificationManager.shared
                crashLog("🧪 NotificationManager OK: \(nm)")

                // 🔥 КРИТИЧЕСКОЕ: Проверяем доступ к @Published на main thread
                let settings = nm.notificationSettings
                crashLog("🧪 notificationSettings OK: \(settings)")
                crashLog("🧪 securityEnabled: \(settings.securityEnabled)")
                crashLog("🧪 soundEnabled: \(settings.soundEnabled)")
            }

            Button("🔍 TariffManager @Published") {
                crashLog("🧪 TEST: Проверка TariffManager @Published свойств")
                let tm = TariffManager.shared
                crashLog("🧪 TariffManager OK: \(tm)")

                let tariff = tm.currentTariff
                crashLog("🧪 currentTariff OK: \(tariff)")
            }

            Button("🔍 Thread safety test") {
                crashLog("🧪 TEST: Проверка Thread.isMainThread = \(Thread.isMainThread)")

                // Имитируем доступ не на main thread
                DispatchQueue.global().async {
                    crashLog("🧪 BACKGROUND THREAD: Thread.isMainThread = \(Thread.isMainThread)")
                    // НЕ пытаемся обращаться к @Published здесь - это может крашить
                }
            }
        }
        .padding()
        .background(Color.yellow.opacity(0.1))
        .cornerRadius(8)
    }

    @ViewBuilder
    private func testLocalization() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🧪 ТЕСТ 5: LocalizationManager")
                .font(.headline)

            Button("✅ LocalizationManager EnvironmentObject") {
                // Этот тест будет добавлен если базовые работают
                print("🩺 DIAGNOSTIC: Localization тест пока отключен")
            }
        }
        .padding()
        .background(Color.purple.opacity(0.1))
        .cornerRadius(8)
    }

    @ViewBuilder
    private func testCrashLogs() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("🔥 ТЕСТ 6: CRASH LOGS - КРИТИЧЕСКОЕ")
                .font(.headline)

            Button("📋 Показать последние логи крашей") {
                let logs = getCrashLogs()
                print("🔥 CRASH LOGS: Найдено \(logs.count) логов")
                logs.forEach { print("🔥 LOG: \($0)") }
            }

            Button("📄 Показать последний лог краша") {
                if let lastLog = getLastCrashLog() {
                    print("🔥 LAST CRASH LOG: \(lastLog)")
                } else {
                    print("🔥 NO CRASH LOGS FOUND")
                }
            }

            Button("🔄 Очистить логи крашей") {
                UserDefaults.standard.removeObject(forKey: "crash_logs_array")
                UserDefaults.standard.removeObject(forKey: "last_crash_log")
                UserDefaults.standard.synchronize()
                print("🔥 CRASH LOGS CLEARED")
            }

            Button("🚨 Тестировать crash logging") {
                crashLog("🧪 TEST CRASH LOG: Диагностический тест логов")
                print("🧪 CRASH LOG TEST: Лог должен быть записан")
            }
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(8)
    }
}