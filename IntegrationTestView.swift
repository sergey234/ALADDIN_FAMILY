import SwiftUI

/**
 * 🧪 INTEGRATION TEST VIEW
 * Простой интерфейс для тестирования API
 */

struct IntegrationTestView: View {
    @StateObject private var viewModel = SimpleAPITestViewModel()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    Text("🧪 API ТЕСТИРОВАНИЕ")
                        .font(.title)
                        .fontWeight(.bold)
                        .padding()

                    Text("Тестирование 236 эндпоинтов ALADDIN")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)

                    // Прогресс
                    VStack(spacing: 10) {
                        ProgressView(value: viewModel.progress, total: 236)
                            .padding(.horizontal)

                        Text("\(Int(viewModel.progress))/236 API протестировано")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        HStack {
                            Text("✅ \(viewModel.successCount)")
                                .foregroundColor(.green)
                            Spacer()
                            Text("❌ \(viewModel.errorCount)")
                                .foregroundColor(.red)
                        }
                        .font(.caption)
                        .padding(.horizontal)
                    }

                    // Результаты
                    VStack(alignment: .leading, spacing: 10) {
                        Text("ПОСЛЕДНИЕ РЕЗУЛЬТАТЫ:")
                            .font(.headline)
                            .padding(.top)

                        ScrollView {
                            Text(viewModel.testResults)
                                .font(.system(.body, design: .monospaced))
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding()
                                .background(Color.gray.opacity(0.1))
                                .cornerRadius(8)
                        }
                        .frame(height: 300)
                    }

                    // Управление
                    VStack(spacing: 15) {
                        HStack(spacing: 10) {
                            Button("🎯 Полное тестирование") {
                                Task { await viewModel.runFullAPITest() }
                            }
                            .buttonStyle(.borderedProminent)

                            Button("🔄 Очистить") {
                                viewModel.clearResults()
                            }
                            .buttonStyle(.bordered)
                        }

                        HStack(spacing: 10) {
                            Button("📊 Категории") {
                                Task { await viewModel.testCategories() }
                            }
                            .buttonStyle(.bordered)

                            Button("⚡ Performance") {
                                Task { await viewModel.testPerformance() }
                            }
                            .buttonStyle(.bordered)

                            Button("🧪 Errors") {
                                Task { await viewModel.testErrorHandling() }
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                    .padding(.horizontal)

                    // Статистика
                    if viewModel.totalTests > 0 {
                        VStack(spacing: 5) {
                            Text("СТАТИСТИКА:")
                                .font(.headline)

                            HStack {
                                Text("Всего: \(viewModel.totalTests)")
                                Spacer()
                                Text("Успех: \(String(format: "%.1f", viewModel.successRate))%")
                            }
                            .font(.caption)

                            HStack {
                                Text("Среднее время: \(String(format: "%.2f", viewModel.averageResponseTime))s")
                                    .font(.caption)
                                    .foregroundColor(viewModel.averageResponseTime < 3 ? .green : .orange)
                            }
                        }
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                        .padding(.horizontal)
                    }
                }
                .padding()
            }
            .navigationTitle("API Tester")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}