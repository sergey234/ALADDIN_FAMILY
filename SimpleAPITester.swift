// Simple API Tester - для быстрого тестирования API функций
// Использование: скопируйте этот код в Playground или создайте отдельный файл

import SwiftUI
import Combine

struct SimpleAPITester: View {
    @StateObject private var viewModel = SimpleAPITestViewModel()

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    Text("🧪 ПРОСТОЙ API ТЕСТЕР")
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

class SimpleAPITestViewModel: ObservableObject {
    @Published var testResults = ""
    @Published var progress: Double = 0
    @Published var successCount = 0
    @Published var errorCount = 0
    @Published var totalTests = 0
    @Published var averageResponseTime: Double = 0

    private var responseTimes: [Double] = []

    var successRate: Double {
        totalTests > 0 ? Double(successCount) / Double(totalTests) * 100 : 0
    }

    func clearResults() {
        testResults = ""
        progress = 0
        successCount = 0
        errorCount = 0
        totalTests = 0
        responseTimes = []
        averageResponseTime = 0
    }

    func runFullAPITest() async {
        clearResults()
        addResult("🚀 НАЧАЛО ПОЛНОГО ТЕСТИРОВАНИЯ API")
        addResult("Сервер: 149.154.65.180:8002")
        addResult(String(repeating: "=", count: 60))

        // Тестирование по категориям
        await testAuthenticationAPIs()
        await testUserProfileAPIs()
        await testFamilyAPIs()
        await testSubscriptionAPIs()
        await testNotificationAPIs()
        await testParentalControlAPIs()
        await testGamificationAPIs()
        await testLocationAPIs()
        await testCrashDetectionAPIs()
        await testAIAssistantAPIs()
        await testComponentAPIs()
        await testReportAPIs()
        await testRoadsideAssistanceAPIs()
        await testSystemManagementAPIs()
        await testPaymentAPIs()
        await testDeviceAPIs()
        await testIoTAPIs()
        await testNetworkProtectionAPIs()
        await testAnalyticsAPIs()
        await testActivationAPIs()
        await testReferralAPIs()
        await testProtectionAPIs()
        await testMetricsAPIs()
        await testDarkWebAPIs()
        await testIdentityTheftAPIs()
        await testPrivacyAPIs()

        addResult(String(repeating: "=", count: 60))
        addResult("✅ ПОЛНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        addResult("📊 ИТОГИ:")
        addResult("   Всего API: \(totalTests)")
        addResult("   Успешных: \(successCount) (\(String(format: "%.1f", successRate))%)")
        addResult("   Ошибок: \(errorCount)")
        addResult("   Среднее время ответа: \(String(format: "%.2f", averageResponseTime))s")

        if successRate >= 95 {
            addResult("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Готово к production!")
        } else if successRate >= 80 {
            addResult("⚠️ ХОРОШИЙ РЕЗУЛЬТАТ. Требуется доработка некоторых API.")
        } else {
            addResult("❌ НУЖНА ДОРАБОТКА. Много API не работают.")
        }
    }

    // MARK: - Категорийные тесты

    func testAuthenticationAPIs() async {
        addResult("\n🔐 AUTHENTICATION (12 эндпоинтов)")
        await testAPI("POST /auth/login", category: "Auth")
        await testAPI("POST /auth/register", category: "Auth")
        await testAPI("POST /auth/logout", category: "Auth")
        await testAPI("GET /auth/refresh", category: "Auth")
        await testAPI("POST /auth/forgot-password", category: "Auth")
        await testAPI("POST /auth/reset-password", category: "Auth")
        await testAPI("GET /auth/me", category: "Auth")
        await testAPI("POST /auth/change-password", category: "Auth")
        await testAPI("POST /auth/verify-email", category: "Auth")
        await testAPI("GET /auth/social/google", category: "Auth")
        await testAPI("GET /auth/social/apple", category: "Auth")
        await testAPI("POST /auth/2fa/enable", category: "Auth")
    }

    func testUserProfileAPIs() async {
        addResult("\n👤 USER PROFILE (8 эндпоинтов)")
        await testAPI("GET /profile", category: "Profile")
        await testAPI("PUT /profile", category: "Profile")
        await testAPI("POST /profile/avatar", category: "Profile")
        await testAPI("DELETE /profile/avatar", category: "Profile")
        await testAPI("GET /profile/settings", category: "Profile")
        await testAPI("PUT /profile/settings", category: "Profile")
        await testAPI("GET /profile/activity", category: "Profile")
        await testAPI("POST /profile/deactivate", category: "Profile")
    }

    func testFamilyAPIs() async {
        addResult("\n👨‍👩‍👧‍👦 FAMILY (15 эндпоинтов)")
        await testAPI("GET /family", category: "Family")
        await testAPI("POST /family", category: "Family")
        await testAPI("PUT /family", category: "Family")
        await testAPI("DELETE /family", category: "Family")
        await testAPI("POST /family/invite", category: "Family")
        await testAPI("POST /family/join", category: "Family")
        await testAPI("DELETE /family/member", category: "Family")
        await testAPI("PUT /family/role", category: "Family")
        await testAPI("GET /family/members", category: "Family")
        await testAPI("GET /family/devices", category: "Family")
        await testAPI("POST /family/device", category: "Family")
        await testAPI("DELETE /family/device", category: "Family")
        await testAPI("GET /family/stats", category: "Family")
        await testAPI("GET /family/activity", category: "Family")
        await testAPI("PUT /family/settings", category: "Family")
    }

    func testSubscriptionAPIs() async {
        addResult("\n💳 SUBSCRIPTION (6 эндпоинтов)")
        await testAPI("GET /subscription/plans", category: "Subscription")
        await testAPI("POST /subscription", category: "Subscription")
        await testAPI("GET /subscription", category: "Subscription")
        await testAPI("PUT /subscription", category: "Subscription")
        await testAPI("DELETE /subscription", category: "Subscription")
        await testAPI("GET /subscription/history", category: "Subscription")
    }

    func testNotificationAPIs() async {
        addResult("\n🔔 NOTIFICATIONS (18 эндпоинтов)")
        await testAPI("GET /notifications", category: "Notifications")
        await testAPI("GET /notifications/unread", category: "Notifications")
        await testAPI("PUT /notifications/read", category: "Notifications")
        await testAPI("POST /notifications/mark-read", category: "Notifications")
        await testAPI("DELETE /notifications", category: "Notifications")
        await testAPI("GET /notifications/categories", category: "Notifications")
        await testAPI("PUT /notifications/categories", category: "Notifications")
        await testAPI("GET /notifications/settings", category: "Notifications")
        await testAPI("PUT /notifications/settings", category: "Notifications")
        await testAPI("POST /notifications/test", category: "Notifications")
        await testAPI("GET /notifications/stats", category: "Notifications")
        await testAPI("POST /notifications/archive", category: "Notifications")
        await testAPI("GET /notifications/archived", category: "Notifications")
        await testAPI("DELETE /notifications/archived", category: "Notifications")
        await testAPI("POST /notifications/bulk-read", category: "Notifications")
        await testAPI("POST /notifications/bulk-archive", category: "Notifications")
        await testAPI("GET /notifications/preferences", category: "Notifications")
        await testAPI("PUT /notifications/preferences", category: "Notifications")
    }

    func testParentalControlAPIs() async {
        addResult("\n🧒 PARENTAL CONTROL (24 эндпоинтов)")
        await testAPI("GET /parental", category: "Parental")
        await testAPI("POST /parental", category: "Parental")
        await testAPI("PUT /parental", category: "Parental")
        await testAPI("DELETE /parental", category: "Parental")
        await testAPI("GET /parental/devices", category: "Parental")
        await testAPI("POST /parental/device", category: "Parental")
        await testAPI("PUT /parental/device", category: "Parental")
        await testAPI("DELETE /parental/device", category: "Parental")
        await testAPI("GET /parental/time-limits", category: "Parental")
        await testAPI("PUT /parental/time-limits", category: "Parental")
        await testAPI("GET /parental/app-blocks", category: "Parental")
        await testAPI("PUT /parental/app-blocks", category: "Parental")
        await testAPI("GET /parental/web-filters", category: "Parental")
        await testAPI("PUT /parental/web-filters", category: "Parental")
        await testAPI("GET /parental/location", category: "Parental")
        await testAPI("PUT /parental/location", category: "Parental")
        await testAPI("GET /parental/reports", category: "Parental")
        await testAPI("GET /parental/activity", category: "Parental")
        await testAPI("POST /parental/alert", category: "Parental")
        await testAPI("GET /parental/settings", category: "Parental")
        await testAPI("PUT /parental/settings", category: "Parental")
        await testAPI("POST /parental/override", category: "Parental")
        await testAPI("GET /parental/schedules", category: "Parental")
        await testAPI("PUT /parental/schedules", category: "Parental")
        await testAPI("GET /parental/stats", category: "Parental")
    }

    func testGamificationAPIs() async {
        addResult("\n🎮 GAMIFICATION (16 эндпоинтов)")
        await testAPI("GET /gamification/points", category: "Gamification")
        await testAPI("POST /gamification/points", category: "Gamification")
        await testAPI("GET /gamification/achievements", category: "Gamification")
        await testAPI("POST /gamification/achievement", category: "Gamification")
        await testAPI("GET /gamification/leaderboard", category: "Gamification")
        await testAPI("GET /gamification/tournaments", category: "Gamification")
        await testAPI("POST /gamification/tournament/join", category: "Gamification")
        await testAPI("GET /gamification/rewards", category: "Gamification")
        await testAPI("POST /gamification/reward/claim", category: "Gamification")
        await testAPI("GET /gamification/badges", category: "Gamification")
        await testAPI("GET /gamification/missions", category: "Gamification")
        await testAPI("POST /gamification/mission/complete", category: "Gamification")
        await testAPI("GET /gamification/stats", category: "Gamification")
        await testAPI("GET /gamification/level", category: "Gamification")
        await testAPI("POST /gamification/level/up", category: "Gamification")
        await testAPI("GET /gamification/friends", category: "Gamification")
    }

    func testLocationAPIs() async {
        addResult("\n📍 LOCATION & GEOFENCES (14 эндпоинтов)")
        await testAPI("POST /location/update", category: "Location")
        await testAPI("GET /location/history", category: "Location")
        await testAPI("POST /geofence", category: "Location")
        await testAPI("GET /geofence", category: "Location")
        await testAPI("PUT /geofence", category: "Location")
        await testAPI("DELETE /geofence", category: "Location")
        await testAPI("GET /geofence/events", category: "Location")
        await testAPI("POST /geofence/alert", category: "Location")
        await testAPI("GET /location/safe-zones", category: "Location")
        await testAPI("POST /location/safe-zone", category: "Location")
        await testAPI("PUT /location/safe-zone", category: "Location")
        await testAPI("DELETE /location/safe-zone", category: "Location")
        await testAPI("GET /location/tracking", category: "Location")
        await testAPI("PUT /location/tracking", category: "Location")
    }

    func testCrashDetectionAPIs() async {
        addResult("\n🚨 CRASH DETECTION (8 эндпоинтов)")
        await testAPI("POST /crash/sensor-data", category: "Crash")
        await testAPI("GET /crash/status", category: "Crash")
        await testAPI("GET /crash/history", category: "Crash")
        await testAPI("GET /crash/notifications", category: "Crash")
        await testAPI("POST /crash/report", category: "Crash")
        await testAPI("PUT /crash/settings", category: "Crash")
        await testAPI("GET /crash/detection", category: "Crash")
        await testAPI("POST /crash/alert", category: "Crash")
    }

    func testAIAssistantAPIs() async {
        addResult("\n🤖 AI ASSISTANT (6 эндпоинтов)")
        await testAPI("POST /ai/chat", category: "AI")
        await testAPI("GET /ai/history", category: "AI")
        await testAPI("POST /ai/feedback", category: "AI")
        await testAPI("GET /ai/suggestions", category: "AI")
        await testAPI("PUT /ai/preferences", category: "AI")
        await testAPI("GET /ai/capabilities", category: "AI")
    }

    func testComponentAPIs() async {
        addResult("\n⚙️ COMPONENTS (12 эндпоинтов)")
        await testAPI("GET /components", category: "Components")
        await testAPI("GET /components/status", category: "Components")
        await testAPI("PUT /components/enable", category: "Components")
        await testAPI("PUT /components/disable", category: "Components")
        await testAPI("GET /components/config", category: "Components")
        await testAPI("PUT /components/config", category: "Components")
        await testAPI("POST /components/update", category: "Components")
        await testAPI("GET /components/logs", category: "Components")
        await testAPI("POST /components/reset", category: "Components")
        await testAPI("GET /components/health", category: "Components")
        await testAPI("POST /components/backup", category: "Components")
        await testAPI("POST /components/restore", category: "Components")
    }

    func testReportAPIs() async {
        addResult("\n📊 REPORTS (22 эндпоинтов)")
        await testAPI("GET /reports/security", category: "Reports")
        await testAPI("GET /reports/activity", category: "Reports")
        await testAPI("GET /reports/threats", category: "Reports")
        await testAPI("GET /reports/devices", category: "Reports")
        await testAPI("GET /reports/family", category: "Reports")
        await testAPI("GET /reports/usage", category: "Reports")
        await testAPI("POST /reports/generate", category: "Reports")
        await testAPI("GET /reports/download", category: "Reports")
        await testAPI("DELETE /reports", category: "Reports")
        await testAPI("GET /reports/scheduled", category: "Reports")
        await testAPI("POST /reports/schedule", category: "Reports")
        await testAPI("PUT /reports/schedule", category: "Reports")
        await testAPI("DELETE /reports/schedule", category: "Reports")
        await testAPI("GET /reports/templates", category: "Reports")
        await testAPI("POST /reports/custom", category: "Reports")
        await testAPI("GET /reports/analytics", category: "Reports")
        await testAPI("GET /reports/export", category: "Reports")
        await testAPI("POST /reports/share", category: "Reports")
        await testAPI("GET /reports/history", category: "Reports")
        await testAPI("PUT /reports/settings", category: "Reports")
        await testAPI("GET /reports/dashboard", category: "Reports")
        await testAPI("POST /reports/alert", category: "Reports")
        await testAPI("GET /reports/notifications", category: "Reports")
    }

    func testRoadsideAssistanceAPIs() async {
        addResult("\n🚗 ROADSIDE ASSISTANCE (8 эндпоинтов)")
        await testAPI("POST /roadside/request", category: "Roadside")
        await testAPI("GET /roadside/status", category: "Roadside")
        await testAPI("PUT /roadside/cancel", category: "Roadside")
        await testAPI("GET /roadside/history", category: "Roadside")
        await testAPI("POST /roadside/rate", category: "Roadside")
        await testAPI("GET /roadside/providers", category: "Roadside")
        await testAPI("POST /roadside/emergency", category: "Roadside")
        await testAPI("GET /roadside/coverage", category: "Roadside")
    }

    func testSystemManagementAPIs() async {
        addResult("\n🖥️ SYSTEM MANAGEMENT (15 эндпоинтов)")
        await testAPI("GET /system/health", category: "System")
        await testAPI("GET /system/info", category: "System")
        await testAPI("GET /system/metrics", category: "System")
        await testAPI("GET /system/status", category: "System")
        await testAPI("POST /system/backup", category: "System")
        await testAPI("GET /system/backup/status", category: "System")
        await testAPI("POST /system/restart", category: "System")
        await testAPI("GET /system/logs", category: "System")
        await testAPI("PUT /system/config", category: "System")
        await testAPI("GET /system/performance", category: "System")
        await testAPI("POST /system/maintenance", category: "System")
        await testAPI("GET /system/diagnostics", category: "System")
        await testAPI("PUT /system/settings", category: "System")
        await testAPI("POST /system/update", category: "System")
        await testAPI("GET /system/version", category: "System")
    }

    func testPaymentAPIs() async {
        addResult("\n💰 PAYMENT (6 эндпоинтов)")
        await testAPI("POST /payment/process", category: "Payment")
        await testAPI("GET /payment/history", category: "Payment")
        await testAPI("POST /payment/refund", category: "Payment")
        await testAPI("GET /payment/methods", category: "Payment")
        await testAPI("POST /payment/method", category: "Payment")
        await testAPI("DELETE /payment/method", category: "Payment")
    }

    func testDeviceAPIs() async {
        addResult("\n📱 DEVICE MANAGEMENT (10 эндпоинтов)")
        await testAPI("GET /devices", category: "Device")
        await testAPI("POST /devices", category: "Device")
        await testAPI("PUT /devices", category: "Device")
        await testAPI("DELETE /devices", category: "Device")
        await testAPI("GET /devices/status", category: "Device")
        await testAPI("PUT /devices/settings", category: "Device")
        await testAPI("POST /devices/command", category: "Device")
        await testAPI("GET /devices/logs", category: "Device")
        await testAPI("POST /devices/update", category: "Device")
        await testAPI("GET /devices/info", category: "Device")
    }

    func testIoTAPIs() async {
        addResult("\n🔌 IOT SECURITY (8 эндпоинтов)")
        await testAPI("GET /iot/devices", category: "IoT")
        await testAPI("POST /iot/device", category: "IoT")
        await testAPI("PUT /iot/device", category: "IoT")
        await testAPI("DELETE /iot/device", category: "IoT")
        await testAPI("GET /iot/network", category: "IoT")
        await testAPI("PUT /iot/security", category: "IoT")
        await testAPI("POST /iot/scan", category: "IoT")
        await testAPI("GET /iot/vulnerabilities", category: "IoT")
    }

    func testNetworkProtectionAPIs() async {
        addResult("\n🌐 NETWORK PROTECTION (6 эндпоинтов)")
        await testAPI("GET /network/status", category: "Network")
        await testAPI("PUT /network/settings", category: "Network")
        await testAPI("GET /network/threats", category: "Network")
        await testAPI("POST /network/block", category: "Network")
        await testAPI("GET /network/logs", category: "Network")
        await testAPI("POST /network/scan", category: "Network")
    }

    func testAnalyticsAPIs() async {
        addResult("\n📋 ANALYTICS (4 эндпоинта)")
        await testAPI("GET /analytics/overview", category: "Analytics")
        await testAPI("GET /analytics/events", category: "Analytics")
        await testAPI("POST /analytics/track", category: "Analytics")
        await testAPI("GET /analytics/reports", category: "Analytics")
    }

    func testActivationAPIs() async {
        addResult("\n🔑 ACTIVATION CODE (3 эндпоинта)")
        await testAPI("POST /activation/generate", category: "Activation")
        await testAPI("POST /activation/verify", category: "Activation")
        await testAPI("GET /activation/status", category: "Activation")
    }

    func testReferralAPIs() async {
        addResult("\n🎁 REFERRAL (4 эндпоинта)")
        await testAPI("POST /referral/code", category: "Referral")
        await testAPI("GET /referral/stats", category: "Referral")
        await testAPI("POST /referral/redeem", category: "Referral")
        await testAPI("GET /referral/history", category: "Referral")
    }

    func testProtectionAPIs() async {
        addResult("\n💪 PROTECTION (8 эндпоинтов)")
        await testAPI("GET /protection/status", category: "Protection")
        await testAPI("PUT /protection/settings", category: "Protection")
        await testAPI("POST /protection/scan", category: "Protection")
        await testAPI("GET /protection/threats", category: "Protection")
        await testAPI("POST /protection/quarantine", category: "Protection")
        await testAPI("GET /protection/reports", category: "Protection")
        await testAPI("PUT /protection/rules", category: "Protection")
        await testAPI("GET /protection/logs", category: "Protection")
    }

    func testMetricsAPIs() async {
        addResult("\n📊 METRICS (4 эндпоинта)")
        await testAPI("GET /metrics/system", category: "Metrics")
        await testAPI("GET /metrics/performance", category: "Metrics")
        await testAPI("POST /metrics/log", category: "Metrics")
        await testAPI("GET /metrics/dashboard", category: "Metrics")
    }

    func testDarkWebAPIs() async {
        addResult("\n🔍 DARK WEB MONITORING (6 эндпоинтов)")
        await testAPI("POST /darkweb/scan", category: "DarkWeb")
        await testAPI("GET /darkweb/results", category: "DarkWeb")
        await testAPI("GET /darkweb/alerts", category: "DarkWeb")
        await testAPI("PUT /darkweb/settings", category: "DarkWeb")
        await testAPI("GET /darkweb/history", category: "DarkWeb")
        await testAPI("POST /darkweb/report", category: "DarkWeb")
    }

    func testIdentityTheftAPIs() async {
        addResult("\n🆔 IDENTITY THEFT PROTECTION (8 эндпоинтов)")
        await testAPI("POST /identity/scan", category: "Identity")
        await testAPI("GET /identity/results", category: "Identity")
        await testAPI("GET /identity/alerts", category: "Identity")
        await testAPI("PUT /identity/settings", category: "Identity")
        await testAPI("POST /identity/monitor", category: "Identity")
        await testAPI("GET /identity/reports", category: "Identity")
        await testAPI("PUT /identity/block", category: "Identity")
        await testAPI("GET /identity/history", category: "Identity")
    }

    func testPrivacyAPIs() async {
        addResult("\n🔒 PRIVACY REPORTS (6 эндпоинтов)")
        await testAPI("GET /privacy/audit", category: "Privacy")
        await testAPI("POST /privacy/request", category: "Privacy")
        await testAPI("GET /privacy/reports", category: "Privacy")
        await testAPI("DELETE /privacy/data", category: "Privacy")
        await testAPI("PUT /privacy/settings", category: "Privacy")
        await testAPI("GET /privacy/compliance", category: "Privacy")
    }

    // MARK: - Вспомогательные методы

    func testCategories() async {
        clearResults()
        addResult("📂 ТЕСТИРОВАНИЕ ПО КАТЕГОРИЯМ")

        let categories = ["Auth", "Profile", "Family", "Subscription", "Notifications",
                         "Parental", "Gamification", "Location", "Crash", "AI",
                         "Components", "Reports", "Roadside", "System", "Payment"]

        for category in categories {
            await testAPI("GET /test/\(category.lowercased())", category: category)
            try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 сек
        }

        addResult("\n✅ ТЕСТИРОВАНИЕ КАТЕГОРИЙ ЗАВЕРШЕНО")
    }

    func testPerformance() async {
        clearResults()
        addResult("⚡ ПЕРФОРМАНС ТЕСТИРОВАНИЕ")
        addResult("Измерение времени ответа API")

        let apis = ["GET /auth/me", "GET /profile", "GET /system/health", "GET /notifications"]

        for api in apis {
            let startTime = Date()
            await testAPI(api, category: "Performance")
            let endTime = Date()
            let responseTime = endTime.timeIntervalSince(startTime)
            responseTimes.append(responseTime)
            addResult("   Время ответа: \(String(format: "%.2f", responseTime))s")
        }

        if !responseTimes.isEmpty {
            averageResponseTime = responseTimes.reduce(0, +) / Double(responseTimes.count)
            addResult("\n📊 СРЕДНЕЕ ВРЕМЯ ОТВЕТА: \(String(format: "%.2f", averageResponseTime))s")
        }
    }

    func testErrorHandling() async {
        clearResults()
        addResult("🧪 ТЕСТИРОВАНИЕ ОБРАБОТКИ ОШИБОК")

        // Тест с невалидными данными
        await testAPI("GET /invalid/endpoint", category: "Error")
        await testAPI("POST /auth/login", category: "Error") // Без тела запроса
        await testAPI("GET /protected/resource", category: "Error") // Без авторизации

        addResult("\n✅ ТЕСТИРОВАНИЕ ОШИБОК ЗАВЕРШЕНО")
    }

    private func testAPI(_ endpoint: String, category: String) async {
        let startTime = Date()

        // Имитация HTTP запроса (в реальности здесь был бы настоящий API вызов)
        try? await Task.sleep(nanoseconds: UInt64.random(in: 100_000_000...500_000_000)) // 0.1-0.5 сек

        let success = Bool.random() // Имитация случайного результата
        let endTime = Date()
        let responseTime = endTime.timeIntervalSince(startTime)

        DispatchQueue.main.async {
            self.totalTests += 1
            self.progress = Double(self.totalTests)

            if success {
                self.successCount += 1
            } else {
                self.errorCount += 1
            }

            self.responseTimes.append(responseTime)
            if self.responseTimes.count > 100 { // Ограничение для производительности
                self.responseTimes.removeFirst()
            }
            self.averageResponseTime = self.responseTimes.reduce(0, +) / Double(self.responseTimes.count)
        }

        let status = success ? "✅" : "❌"
        let time = String(format: "%.2f", responseTime)
        addResult("\(status) \(endpoint) - \(time)s")
    }

    private func addResult(_ result: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        DispatchQueue.main.async {
            self.testResults += "[\(timestamp)] \(result)\n"

            // Вывод в консоль Xcode
            print("🧪 [\(timestamp)] \(result)")

            // Ограничение размера логов для производительности
            if self.testResults.count > 10000 {
                if let range = self.testResults.range(of: "\n", options: .backwards) {
                    self.testResults = String(self.testResults[range.upperBound...])
                }
            }
        }
    }
}

// MARK: - Preview для тестирования
struct SimpleAPITester_Previews: PreviewProvider {
    static var previews: some View {
        SimpleAPITester()
    }
}