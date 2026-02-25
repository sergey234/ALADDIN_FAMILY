import Foundation

/**
 * 🤖 АВТОМАТИЧЕСКИЙ API ТЕСТ АНАЛИЗАТОР
 *
 * Автоматически анализирует логи и создает отчет о состоянии всех API
 */

class APITestAnalyzer {

    struct APITestResult {
        let endpoint: String
        let method: String
        let statusCode: Int?
        let responseTime: Double?
        let success: Bool
        let error: String?
        let timestamp: Date?
    }

    struct APITestReport {
        var totalAPIs: Int = 0
        var successfulAPIs: Int = 0
        var failedAPIs: Int = 0
        var averageResponseTime: Double = 0
        var results: [APITestResult] = []
        var categories: [String: [APITestResult]] = [:]

        var successRate: Double {
            totalAPIs > 0 ? Double(successfulAPIs) / Double(totalAPIs) : 0
        }

        var coveragePercentage: Double {
            let totalExpected = 236 // Из server_openapi.json
            return Double(totalAPIs) / Double(totalExpected) * 100
        }

        func generateHTMLReport() -> String {
            let date = DateFormatter.localizedString(from: Date(), dateStyle: .medium, timeStyle: .medium)

            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>ALADDIN API Test Report - \(date)</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { background: #007AFF; color: white; padding: 20px; border-radius: 8px; }
                    .stats { display: flex; gap: 20px; margin: 20px 0; }
                    .stat { background: #f0f0f0; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }
                    .success { color: #28a745; }
                    .error { color: #dc3545; }
                    .warning { color: #ffc107; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
                    th { background: #f8f9fa; }
                    .category { margin: 30px 0; }
                    .category h3 { color: #007AFF; border-bottom: 2px solid #007AFF; padding-bottom: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 ALADDIN API Test Report</h1>
                    <p>Generated: \(date)</p>
                    <p>Server Coverage: \(String(format: "%.1f", coveragePercentage))% (236 endpoints)</p>
                </div>

                <div class="stats">
                    <div class="stat">
                        <h3>Total APIs</h3>
                        <p style="font-size: 24px;">\(totalAPIs)</p>
                    </div>
                    <div class="stat success">
                        <h3>Successful</h3>
                        <p style="font-size: 24px;">\(successfulAPIs)</p>
                    </div>
                    <div class="stat error">
                        <h3>Failed</h3>
                        <p style="font-size: 24px;">\(failedAPIs)</p>
                    </div>
                    <div class="stat">
                        <h3>Success Rate</h3>
                        <p style="font-size: 24px;">\(String(format: "%.1f", successRate * 100))%</p>
                    </div>
                    <div class="stat">
                        <h3>Avg Response</h3>
                        <p style="font-size: 24px;">\(String(format: "%.2f", averageResponseTime))s</p>
                    </div>
                </div>

                <h2>📊 Detailed Results</h2>
                <table>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Response Time</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                    \(results.map { result in
                        let statusClass = result.success ? "success" : "error"
                        let statusText = result.success ? "✅ Success" : "❌ Failed"
                        let statusCode = result.statusCode.map { String($0) } ?? "-"
                        let responseTime = result.responseTime.map { String(format: "%.2f", $0) + "s" } ?? "-"

                        return """
                        <tr>
                            <td>\(result.endpoint)</td>
                            <td>\(result.method)</td>
                            <td>\(statusCode)</td>
                            <td>\(responseTime)</td>
                            <td class="\(statusClass)">\(statusText)</td>
                            <td>\(result.error ?? "-")</td>
                        </tr>
                        """
                    }.joined())
                </table>

                <h2>📂 By Category</h2>
                \(categories.map { category, results in
                    let successCount = results.filter { $0.success }.count
                    let totalCount = results.count
                    let categorySuccessRate = Double(successCount) / Double(totalCount) * 100

                    return """
                    <div class="category">
                        <h3>\(category) (\(successCount)/\(totalCount) - \(String(format: "%.1f", categorySuccessRate))%)</h3>
                        <table>
                            <tr>
                                <th>Endpoint</th>
                                <th>Method</th>
                                <th>Status</th>
                                <th>Response Time</th>
                                <th>Status</th>
                            </tr>
                            \(results.map { result in
                                let statusClass = result.success ? "success" : "error"
                                let statusText = result.success ? "✅" : "❌"
                                let statusCode = result.statusCode.map { String($0) } ?? "-"
                                let responseTime = result.responseTime.map { String(format: "%.2f", $0) + "s" } ?? "-"

                                return """
                                <tr>
                                    <td>\(result.endpoint)</td>
                                    <td>\(result.method)</td>
                                    <td>\(statusCode)</td>
                                    <td>\(responseTime)</td>
                                    <td class="\(statusClass)">\(statusText)</td>
                                </tr>
                                """
                            }.joined())
                        </table>
                    </div>
                    """
                }.joined())

            </body>
            </html>
            """
        }
    }

    static func analyzeLogs(_ logsText: String) -> APITestReport {
        var report = APITestReport()
        let lines = logsText.components(separatedBy: "\n")

        for line in lines {
            if let result = parseLogLine(line) {
                report.results.append(result)
                report.totalAPIs += 1

                if result.success {
                    report.successfulAPIs += 1
                } else {
                    report.failedAPIs += 1
                }

                if let time = result.responseTime {
                    report.averageResponseTime += time
                }

                // Категоризация по endpoint
                let category = categorizeEndpoint(result.endpoint)
                if report.categories[category] == nil {
                    report.categories[category] = []
                }
                report.categories[category]?.append(result)
            }
        }

        if report.totalAPIs > 0 {
            report.averageResponseTime /= Double(report.totalAPIs)
        }

        return report
    }

    private static func parseLogLine(_ line: String) -> APITestResult? {
        // Парсинг строки лога в формате MasterLogger
        if line.contains("➡️") && line.contains("REQUEST") {
            return parseRequestLine(line)
        } else if line.contains("⬅️") && line.contains("RESPONSE") {
            return parseResponseLine(line)
        }

        return nil
    }

    private static func parseRequestLine(_ line: String) -> APITestResult? {
        // Пример: ➡️ REQUEST: GET https://aladdin-ai.ru/api/profile headers=[auth: <redacted>]
        let components = line.components(separatedBy: " ")
        guard components.count >= 4 else { return nil }

        let method = components[2]
        let url = components[3]

        let timestamp = parseTimestamp(from: line)

        return APITestResult(
            endpoint: extractEndpoint(url),
            method: method,
            statusCode: nil,
            responseTime: nil,
            success: true, // Запрос всегда успешный на этом этапе
            error: nil,
            timestamp: timestamp
        )
    }

    private static func parseResponseLine(_ line: String) -> APITestResult? {
        // Пример: ⬅️ RESPONSE: status=200 url=https://aladdin-ai.ru/api/profile time=1.23s body=<json-sanitized>
        guard let statusRange = line.range(of: "status="),
              let urlRange = line.range(of: "url=") else { return nil }

        let statusPart = line[statusRange.upperBound...]
        let statusComponents = statusPart.components(separatedBy: " ")
        guard let statusCode = Int(statusComponents[0]) else { return nil }

        let urlPart = line[urlRange.upperBound...]
        let urlComponents = urlPart.components(separatedBy: " ")
        let url = urlComponents[0]

        let timeRange = line.range(of: "time=")
        let responseTime: Double? = timeRange.flatMap { range in
            let timePart = line[range.upperBound...]
            let timeComponents = timePart.components(separatedBy: "s")
            return Double(timeComponents[0])
        }

        let success = (200...299).contains(statusCode)
        var error: String? = nil

        if !success {
            error = "HTTP \(statusCode)"
        }

        let timestamp = parseTimestamp(from: line)

        return APITestResult(
            endpoint: extractEndpoint(url),
            method: "GET", // Метод для response - обычно это ответ на GET запрос
            statusCode: statusCode,
            responseTime: responseTime,
            success: success,
            error: error,
            timestamp: timestamp
        )
    }

    private static func extractEndpoint(_ url: String) -> String {
        guard let urlComponents = URLComponents(string: url),
              let host = urlComponents.host else {
            return url
        }

        let path = urlComponents.path
        let query = urlComponents.query.map { "?\($0)" } ?? ""

        return "\(host)\(path)\(query)"
    }

    private static func categorizeEndpoint(_ endpoint: String) -> String {
        if endpoint.contains("/auth/") { return "Authentication" }
        if endpoint.contains("/profile/") { return "User Profile" }
        if endpoint.contains("/subscription/") { return "Subscription" }
        if endpoint.contains("/notification") { return "Notifications" }
        if endpoint.contains("/family/") { return "Family" }
        if endpoint.contains("/gamification/") { return "Gamification" }
        if endpoint.contains("/parental/") { return "Parental Control" }
        if endpoint.contains("/location/") { return "Location" }
        if endpoint.contains("/crash/") { return "Crash Detection" }
        if endpoint.contains("/system/") { return "System Management" }
        if endpoint.contains("/ai/") { return "AI Assistant" }
        if endpoint.contains("/component") { return "Components" }
        if endpoint.contains("/report") { return "Reports" }
        if endpoint.contains("/payment") { return "Payment" }
        if endpoint.contains("/device") { return "Device" }

        return "Other"
    }

    private static func parseTimestamp(from line: String) -> Date? {
        // Пример формата: [14:23:45]
        guard let startRange = line.range(of: "["),
              let endRange = line.range(of: "]", range: startRange.upperBound..<line.endIndex) else {
            return nil
        }

        let timeString = String(line[startRange.upperBound..<endRange.lowerBound])
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        formatter.timeZone = TimeZone.current

        guard let time = formatter.date(from: timeString) else { return nil }

        // Используем сегодняшнюю дату с распарсенным временем
        let calendar = Calendar.current
        let today = Date()
        let components = calendar.dateComponents([.year, .month, .day], from: today)
        let timeComponents = calendar.dateComponents([.hour, .minute, .second], from: time)

        var combinedComponents = components
        combinedComponents.hour = timeComponents.hour
        combinedComponents.minute = timeComponents.minute
        combinedComponents.second = timeComponents.second

        return calendar.date(from: combinedComponents)
    }
}