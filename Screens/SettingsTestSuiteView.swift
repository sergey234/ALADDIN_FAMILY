import SwiftUI

/**
 * 🚨 [PHASE 8] SETTINGS TEST SUITE VIEW
 * Полное тестирование всех сценариев SettingsScreen
 * Для выявления точной точки краша
 */
struct SettingsTestSuiteView: View {
    // ✅ [REVERT] Возвращаем @EnvironmentObject для совместимости
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(spacing: 20) {
            Text("🚨 SETTINGS TEST SUITE")
                .font(.title)
                .foregroundColor(.red)

            Text("Последовательное тестирование всех компонентов")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)

            ScrollView {
                VStack(spacing: 15) {
                    testSection("Тест 1: Базовый View", "Простой VStack") {
                        basicViewTest()
                    }

                    testSection("Тест 2: EnvironmentObjects", "Проверка доступности") {
                        environmentObjectsTest()
                    }

                    testSection("Тест 3: Computed Properties", "Тестирование всех properties") {
                        computedPropertiesTest()
                    }

                    testSection("Тест 4: Navigation Header", "Тестирование заголовка") {
                        navigationHeaderTest()
                    }

                    testSection("Тест 5: Profile Section", "Тестирование профиля") {
                        profileSectionTest()
                    }

                    testSection("Тест 6: Полный SettingsScreen", "Все компоненты вместе") {
                        fullSettingsScreenTest()
                    }
                }
                .padding()
            }

            Button("Назад к Onboarding") {
                navigationManager.navigateTo(.onboarding)
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
        .navigationBarTitle("Settings Test Suite", displayMode: .inline)
        .onAppear {
            print("🚨 [TEST_SUITE] SettingsTestSuiteView appeared")
        }
    }

    private func testSection(_ title: String, _ subtitle: String, content: () -> AnyView) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundColor(.primary)

            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)

            content()
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
        }
    }

    private func basicViewTest() -> AnyView {
        AnyView(VStack {
            Text("✅ Базовый View работает")
                .foregroundColor(.green)
            Text("Если вы видите это - базовое создание View OK")
                .font(.caption)
        })
    }

    private func environmentObjectsTest() -> AnyView {
        AnyView(VStack(alignment: .leading) {
            HStack {
                Text("NavigationManager:")
                Text(navigationManager as AnyObject? != nil ? "✅" : "❌")
                    .foregroundColor(navigationManager as AnyObject? != nil ? .green : .red)
            }

            HStack {
                Text("LocalizationManager:")
                Text(localizationManager as AnyObject? != nil ? "✅" : "❌")
                    .foregroundColor(localizationManager as AnyObject? != nil ? .green : .red)
            }

            Text("Если оба зеленые - EnvironmentObjects доступны")
                .font(.caption)
                .foregroundColor(.secondary)
        })
    }

    private func computedPropertiesTest() -> AnyView {
        AnyView(VStack(alignment: .leading) {
            // ✅ [REVERT] Создаем временный SettingsScreen с EnvironmentObject
            let tempSettings = SettingsScreen()
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)

            Text("Создание SettingsScreen: \(tempSettings as AnyObject? != nil ? "✅" : "❌")")
                .foregroundColor(tempSettings as AnyObject? != nil ? .green : .red)
        })
    }

    private func navigationHeaderTest() -> AnyView {
        AnyView(VStack {
            Text("Если вы видите этот текст - NavigationHeader работает")
                .foregroundColor(.green)
                .multilineTextAlignment(.center)
        })
    }

    private func profileSectionTest() -> AnyView {
        AnyView(VStack {
            Text("Если вы видите этот текст - ProfileSection работает")
                .foregroundColor(.green)
                .multilineTextAlignment(.center)
        })
    }

    private func fullSettingsScreenTest() -> AnyView {
        AnyView(VStack {
            Text("⚠️ Этот тест может вызвать краш")
                .foregroundColor(.red)

            Button("Запустить полный тест SettingsScreen") {
                print("🚨 [TEST_SUITE] Запуск полного теста SettingsScreen")
                // ✅ [FIX 5] Thread-safe навигация
                Task { @MainActor in
                    navigationManager.navigateTo(.settingsTest)
                }
            }
            .padding()
            .background(Color.red.opacity(0.2))
            .foregroundColor(.red)
            .cornerRadius(8)
        })
    }
}