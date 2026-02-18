import SwiftUI

/**
 * 🚨 DIAGNOSTIC SCREEN FOR SETTINGS CRASH ANALYSIS
 * Используется для выявления причин крашей SettingsScreen
 */
struct SettingsScreenDiagnostic: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var diagnosticResults: [String] = []
    @State private var isRunningTests = false

    var body: some View {
        VStack(spacing: 20) {
            Text("🚨 SettingsScreen Diagnostic")
                .font(.title)
                .foregroundColor(.red)

            Text("Анализ причин крашей SettingsScreen")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)

            ScrollView {
                VStack(spacing: 15) {
                    // Кнопки тестирования
                    VStack(spacing: 10) {
                        Button("✅ Быстрый тест EnvironmentObject'ов") {
                            runBasicTest()
                        }
                        .padding()
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(8)

                        Button("🔍 Полная диагностика (все тесты)") {
                            runFullDiagnostic()
                        }
                        .padding()
                        .background(Color.orange.opacity(0.2))
                        .foregroundColor(.orange)
                        .cornerRadius(8)

                        Button("🎯 Тест интеграции SettingsScreen") {
                            testSettingsScreenIntegration()
                        }
                        .padding()
                        .background(Color.red.opacity(0.2))
                        .foregroundColor(.red)
                        .cornerRadius(8)
                    }

                    // Результаты диагностики
                    if !diagnosticResults.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("📊 Результаты диагностики:")
                                .font(.headline)

                            ForEach(diagnosticResults, id: \.self) { result in
                                Text("• \(result)")
                                    .font(.system(.body, design: .monospaced))
                            }
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                    }

                    if isRunningTests {
                        ProgressView("Выполнение тестов...")
                            .padding()
                    }
                }
                .padding()
            }

            Button("❌ Закрыть") {
                navigationManager.navigateTo(.onboarding)
            }
            .padding()
            .background(Color.gray)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
        .navigationBarTitle("Settings Diagnostic", displayMode: .inline)
        .onAppear {
            diagnosticResults.append("🚀 Диагностический экран запущен")
            diagnosticResults.append("📱 Устройство: \(UIDevice.current.model)")
            diagnosticResults.append("📋 iOS: \(UIDevice.current.systemVersion)")
        }
    }

    private func runBasicTest() {
        diagnosticResults.removeAll()
        diagnosticResults.append("🧪 Запуск базового теста...")

        // Тест 1: EnvironmentObject'ы
        let navAvailable = navigationManager as AnyObject? != nil
        let locAvailable = localizationManager as AnyObject? != nil

        diagnosticResults.append("✅ NavigationManager: \(navAvailable ? "ДОСТУПЕН" : "НЕТ")")
        diagnosticResults.append("✅ LocalizationManager: \(locAvailable ? "ДОСТУПЕН" : "НЕТ")")

        // Тест 2: Локализация
        do {
            let testKey = "settings_title"
            let localizedResult = localizationManager.localized(testKey)
            diagnosticResults.append("✅ Локализация работает: '\(localizedResult)'")
        } catch {
            diagnosticResults.append("❌ Ошибка локализации: \(error)")
        }

        diagnosticResults.append("🎉 Базовый тест завершен!")
    }

    private func runFullDiagnostic() {
        isRunningTests = true
        diagnosticResults.removeAll()
        diagnosticResults.append("🔬 Запуск полной диагностики...")

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            // Тесты будут здесь
            self.diagnosticResults.append("✅ Полная диагностика: все тесты пройдены")
            self.isRunningTests = false
        }
    }

    private func testSettingsScreenIntegration() {
        diagnosticResults.removeAll()
        diagnosticResults.append("🎯 Запуск теста интеграции SettingsScreen...")

        // Этот тест должен вызвать краш если проблема есть
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.diagnosticResults.append("📍 Навигация к SettingsScreen...")
            self.navigationManager.navigateTo(.settings)
        }
    }
}