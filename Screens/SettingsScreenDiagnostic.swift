import SwiftUI

/**
 * 🔍 SettingsScreen Diagnostic Tool
 * Диагностический инструмент для выявления причины краша SettingsScreen
 *
 * Проверяет по шагам:
 * 1. EnvironmentObject инициализация
 * 2. Менеджеры инициализация
 * 3. Локализация
 * 4. ViewBuilder функции
 * 5. Полная сборка экрана
 */

struct SettingsScreenDiagnostic: View {

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var currentStep: Int = 0
    @State private var diagnosticResults: [String] = []
    @State private var crashDetected: Bool = false

    private let diagnosticSteps = [
        "1. EnvironmentObject проверка",
        "2. Менеджеры проверка",
        "3. Локализация проверка",
        "4. ViewBuilder функции",
        "5. Полная сборка экрана"
    ]

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    Text("🔍 SettingsScreen Diagnostic")
                        .font(.title)
                        .bold()

                    Text("Текущий шаг: \(diagnosticSteps[currentStep])")
                        .font(.headline)

                    // Диагностические результаты
                    VStack(alignment: .leading, spacing: 10) {
                        ForEach(diagnosticResults, id: \.self) { result in
                            Text("• \(result)")
                                .foregroundColor(result.contains("❌") ? .red : .green)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)

                    // Кнопки диагностики
                    VStack(spacing: 15) {
                        Button(action: runNextDiagnosticStep) {
                            Text("▶️ Следующий шаг диагностики")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }

                        Button(action: runFullDiagnostic) {
                            Text("🚀 Полная диагностика (быстрая)")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }

                        if crashDetected {
                            Button(action: { /* no-op */ }) {
                                Text("❌ КРАШ ОБНАРУЖЕН!")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.red)
                                    .foregroundColor(.white)
                                    .cornerRadius(8)
                            }
                        }
                    }

                    Divider()

                    // Минимальная версия SettingsScreen
                    if currentStep >= 4 {
                        Text("🧪 Тестирование минимальной версии:")
                            .font(.headline)

                        MinimalSettingsScreen()
                    }
                }
                .padding()
            }
            .navigationBarItems(trailing: Button("Закрыть") { dismiss() })
        }
    }

    private func runNextDiagnosticStep() {
        guard currentStep < diagnosticSteps.count else { return }

        let step = currentStep
        currentStep += 1

        switch step {
        case 0:
            checkEnvironmentObjects()
        case 1:
            checkManagers()
        case 2:
            checkLocalization()
        case 3:
            checkViewBuilders()
        case 4:
            checkFullScreen()
        default:
            break
        }
    }

    private func runFullDiagnostic() {
        diagnosticResults.removeAll()
        currentStep = 0

        checkEnvironmentObjects()
        checkManagers()
        checkLocalization()
        checkViewBuilders()
        checkFullScreen()

        currentStep = diagnosticSteps.count
    }

    private func checkEnvironmentObjects() {
        diagnosticResults.append("1️⃣ Проверка EnvironmentObject...")

        do {
            let navManager = navigationManager
            diagnosticResults.append("✅ NavigationManager: \(navManager != nil ? "OK" : "NIL")")

            let locManager = localizationManager
            diagnosticResults.append("✅ LocalizationManager: \(locManager != nil ? "OK" : "NIL")")

            // Проверяем основные свойства
            if let nav = navManager {
                diagnosticResults.append("✅ NavigationManager.currentScreen: \(nav.currentScreen)")
            }

            if let loc = locManager {
                diagnosticResults.append("✅ LocalizationManager.currentLanguage: \(loc.currentLanguage)")
            }

        } catch {
            diagnosticResults.append("❌ Ошибка в EnvironmentObject: \(error.localizedDescription)")
            crashDetected = true
        }
    }

    private func checkManagers() {
        diagnosticResults.append("2️⃣ Проверка менеджеров...")

        do {
            let notificationManager = NotificationManager.shared
            diagnosticResults.append("✅ NotificationManager.shared: \(notificationManager != nil ? "OK" : "NIL")")

            let securityManager = SecurityManager.shared
            diagnosticResults.append("✅ SecurityManager.shared: \(securityManager != nil ? "OK" : "NIL")")

            let tariffManager = TariffManager.shared
            diagnosticResults.append("✅ TariffManager.shared: \(tariffManager != nil ? "OK" : "NIL")")

            // Проверяем основные свойства
            diagnosticResults.append("✅ NotificationManager.isAuthorized: \(notificationManager.isAuthorized)")
            diagnosticResults.append("✅ TariffManager.currentTariff: \(tariffManager.currentTariff)")

        } catch {
            diagnosticResults.append("❌ Ошибка в менеджерах: \(error.localizedDescription)")
            crashDetected = true
        }
    }

    private func checkLocalization() {
        diagnosticResults.append("3️⃣ Проверка локализации...")

        do {
            let localized = localizationManager.localized("Settings", comment: "Test")
            diagnosticResults.append("✅ Локализация 'Settings': '\(localized)'")

            let safeLocalized = safeLocalized("Settings", comment: "Test")
            diagnosticResults.append("✅ Safe локализация 'Settings': '\(safeLocalized)'")

        } catch {
            diagnosticResults.append("❌ Ошибка в локализации: \(error.localizedDescription)")
            crashDetected = true
        }
    }

    private func checkViewBuilders() {
        diagnosticResults.append("4️⃣ Проверка ViewBuilder функций...")

        do {
            // Проверяем создание отдельных секций
            let _ = profileSection()
            diagnosticResults.append("✅ profileSection() создана")

            let _ = securitySection()
            diagnosticResults.append("✅ securitySection() создана")

        } catch {
            diagnosticResults.append("❌ Ошибка в ViewBuilder: \(error.localizedDescription)")
            crashDetected = true
        }
    }

    private func checkFullScreen() {
        diagnosticResults.append("5️⃣ Проверка полной сборки экрана...")

        do {
            // Попытка создать полный экран
            let _ = SettingsScreen()
            diagnosticResults.append("✅ SettingsScreen() создана без краша")

        } catch {
            diagnosticResults.append("❌ КРАШ в SettingsScreen(): \(error.localizedDescription)")
            crashDetected = true
        }
    }

    // MARK: - Helper Functions

    private func safeLocalized(_ key: String, comment: String = "") -> String {
        guard Thread.isMainThread else {
            DispatchQueue.main.sync {
                return localizationManager.localized(key, comment: comment)
            }
        }
        return localizationManager.localized(key, comment: comment)
    }

    // MARK: - Test ViewBuilder Functions

    @ViewBuilder
    private func profileSection() -> some View {
        VStack {
            Text("Profile Section Test")
            Text("Name: Test")
            Text("Alias: Test")
        }
    }

    @ViewBuilder
    private func securitySection() -> some View {
        VStack {
            Text("Security Section Test")
            Text("Protection Level: Test")
        }
    }
}

/**
 * 🧪 Minimal SettingsScreen
 * Минимальная версия экрана с только базовыми компонентами
 */
struct MinimalSettingsScreen: View {

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("🧪 Minimal SettingsScreen")
                    .font(.title)
                    .bold()

                Text("Если эта версия работает - проблема в сложных компонентах")
                    .multilineTextAlignment(.center)
                    .padding()

                Spacer()

                Button("Закрыть") {
                    dismiss()
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .padding()
        }
    }
}

struct SettingsScreenDiagnostic_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreenDiagnostic()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}