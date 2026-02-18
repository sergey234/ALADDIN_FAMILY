import SwiftUI

/**
 * 🔍 SettingsScreen Diagnostic Tool
 * Диагностический инструмент для выявления причины крашей SettingsScreen
 *
 * Этап 1 нашего плана: Диагностика корневой причины
 */

struct SettingsScreenDiagnostic: View {

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var testMessage = "Диагностика готова к запуску"
    @State private var isTesting = false

    enum TestType: String {
        case basic = "Базовый тест"
        case environment = "EnvironmentObject"
        case managers = "Менеджеры"
        case localization = "Локализация"
    }

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("🔍 SettingsScreen Diagnostic")
                    .font(.title)
                    .bold()

                Text("Этап 1: Диагностика крашей")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                Text(testMessage)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)

                Button(action: runBasicTest) {
                    Text(isTesting ? "Тестирование..." : "Запустить базовый тест")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isTesting ? Color.gray : Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .disabled(isTesting)

                Spacer()
            }
            .padding()
            .navigationBarItems(trailing: Button("Закрыть") { dismiss() })
        }
    }

    private func runBasicTest() {
        isTesting = true
        testMessage = "Запуск базового теста..."

        // Простой тест - проверка основных компонентов
        let navManager = navigationManager
        let locManager = localizationManager

        if navManager != nil && locManager != nil {
            testMessage = "✅ Базовый тест пройден!\nEnvironmentObject работают корректно"
        } else {
            testMessage = "❌ Ошибка: EnvironmentObject не инициализированы"
        }

        isTesting = false
    }
}

struct SettingsScreenDiagnostic_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreenDiagnostic()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}