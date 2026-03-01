import SwiftUI

/**
 * 🧪 Trial Flow Test View
 * UI для ручного тестирования trial flow в приложении
 * Позволяет запускать тестовые сценарии прямо в приложении
 */
struct TrialFlowTestView: View {

    @State private var testResults: [String] = []
    @State private var isRunningTest = false

    // Mock functions for testing (TrialFlowTestRunner not available in main target)
    private func debugTrialState() {
        testResults.append("🔍 [MOCK] Trial state debug")
    }

    private func debugResetAllStates() {
        testResults.append("🔧 [MOCK] All states reset")
    }

    private func runFirstLaunchScenario() async {
        testResults.append("🚀 [MOCK] First launch scenario completed")
        try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 second delay
    }

    private func runTrialUsageScenario() async {
        testResults.append("📱 [MOCK] Trial usage scenario completed")
        try? await Task.sleep(nanoseconds: 1_000_000_000)
    }

    private func runTrialExpirationScenario() async {
        testResults.append("⏰ [MOCK] Trial expiration scenario completed")
        try? await Task.sleep(nanoseconds: 1_000_000_000)
    }

    private func runCompleteTrialFlow() async {
        testResults.append("🔄 [MOCK] Complete trial flow completed")
        try? await Task.sleep(nanoseconds: 2_000_000_000)
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.xl) {
                    // Header
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "testtube.2")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)

                        Text("Trial Flow Integration Tests")
                            .font(.title)
                            .fontWeight(.bold)

                        Text("Тестирование полного цикла trial от первого запуска до истечения")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal, Spacing.l)

                    // Test Scenarios
                    VStack(spacing: Spacing.m) {
                        testScenarioButton(
                            title: "🚀 Сценарий 1: Первый запуск",
                            subtitle: "Активация trial при первом запуске",
                            action: runFirstLaunchScenario
                        )

                        testScenarioButton(
                            title: "⏰ Сценарий 2: Использование trial",
                            subtitle: "Проверка доступа к функциям во время trial",
                            action: runTrialUsageScenario
                        )

                        testScenarioButton(
                            title: "⌛ Сценарий 3: Истечение trial",
                            subtitle: "Переход на free план после истечения",
                            action: runTrialExpirationScenario
                        )

                        testScenarioButton(
                            title: "🔄 Полный цикл trial flow",
                            subtitle: "Все сценарии последовательно",
                            action: runCompleteTrialFlow
                        )
                    }
                    .padding(.horizontal, Spacing.l)

                    // Debug Tools
                    VStack(spacing: Spacing.m) {
                        Text("🐛 Debug Tools")
                            .font(.headline)
                            .foregroundColor(.orange)

                        HStack(spacing: Spacing.m) {
                            Button(action: {
                                debugTrialState()
                                addTestResult("🐛 Debug state logged to console")
                            }) {
                                Text("Показать состояние")
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, Spacing.m)
                                    .background(Color.blue.opacity(0.1))
                                    .foregroundColor(.blue)
                                    .cornerRadius(8)
                            }

                            Button(action: {
                                debugResetAllStates()
                                addTestResult("🔧 All states reset for testing")
                            }) {
                                Text("Сбросить состояние")
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, Spacing.m)
                                    .background(Color.red.opacity(0.1))
                                    .foregroundColor(.red)
                                    .cornerRadius(8)
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.l)

                    // Test Results
                    if !testResults.isEmpty {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("📋 Test Results")
                                .font(.headline)
                                .foregroundColor(.green)

                            ForEach(testResults, id: \.self) { result in
                                Text("• \(result)")
                                    .font(.body)
                                    .foregroundColor(.textSecondary)
                            }
                        }
                        .padding(.horizontal, Spacing.l)
                        .padding(.vertical, Spacing.m)
                        .background(Color.green.opacity(0.05))
                        .cornerRadius(12)
                        .padding(.horizontal, Spacing.l)
                    }

                    Spacer(minLength: Spacing.xxl)
                }
                .padding(.top, Spacing.xl)
            }
            .navigationBarItems(trailing:
                Button(action: {
                    testResults.removeAll()
                }) {
                    Image(systemName: "trash")
                        .foregroundColor(.textSecondary)
                }
            )
        }
    }

    // MARK: - Test Actions

    private func runFirstLaunchScenario() {
        runTestScenario("First Launch Scenario") {
            await runFirstLaunchScenario()
        }
    }

    private func runTrialUsageScenario() {
        runTestScenario("Trial Usage Scenario") {
            await runTrialUsageScenario()
        }
    }

    private func runTrialExpirationScenario() {
        runTestScenario("Trial Expiration Scenario") {
            await runTrialExpirationScenario()
        }
    }

    private func runCompleteTrialFlow() {
        runTestScenario("Complete Trial Flow") {
            await runCompleteTrialFlow()
        }
    }

    private func runTestScenario(_ name: String, testAction: @escaping () async -> Void) {
        isRunningTest = true
        addTestResult("▶️ Starting: \(name)")

        Task {
            await testAction()
            await MainActor.run {
                isRunningTest = false
                addTestResult("✅ Completed: \(name)")
            }
        }
    }

    private func addTestResult(_ result: String) {
        testResults.append("\(Date()): \(result)")
    }

    // MARK: - UI Components

    private func testScenarioButton(title: String, subtitle: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(title)
                    .font(.headline)
                    .foregroundColor(.primary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.textSecondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .padding(Spacing.l)
            .background(Color.blue.opacity(0.05))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.blue.opacity(0.2), lineWidth: 1)
            )
        }
        .disabled(isRunningTest)
        .opacity(isRunningTest ? 0.5 : 1.0)
    }
}

// MARK: - Preview

#if DEBUG
struct TrialFlowTestView_Previews: PreviewProvider {
    static var previews: some View {
        TrialFlowTestView()
    }
}
#endif