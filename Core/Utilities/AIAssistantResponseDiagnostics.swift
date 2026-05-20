import Foundation

/// Классификация источника ответа AI Assistant для логов и QA (Build 198).
enum AIAssistantResponseSource: String {
    case faqLocal = "faq_local"
    case cloudAPI = "cloud_api"
    case cloudAPIProbableMock = "cloud_api_probable_mock"
    case cloudDisabled = "cloud_disabled"
}

enum AIAssistantResponseDiagnostics {
    /// Типичные маркеры SFM/mock-ответа на проде (не Hermes на устройстве).
    private static let probableMockMarkers: [String] = [
        "реальный ai aladdin",
        "1074 функц",
        "sfm_mock",
        "sfm_fallback",
        "mock_fallback"
    ]

    static func classifyServerResponse(_ text: String) -> AIAssistantResponseSource {
        let lower = text.lowercased()
        for marker in probableMockMarkers where lower.contains(marker) {
            return .cloudAPIProbableMock
        }
        return .cloudAPI
    }

    static func logDelivery(
        source: AIAssistantResponseSource,
        context: String,
        responseLength: Int,
        grounded: Bool?,
        toolsUsed: [String]?,
        preview: String
    ) {
        let groundedLabel = grounded.map { String($0) } ?? "nil"
        let toolsLabel = (toolsUsed ?? []).joined(separator: ",")
        let snippet = preview.prefix(80)
        print(
            "🤖 AI source=\(source.rawValue) context=\(context) len=\(responseLength) grounded=\(groundedLabel) tools=[\(toolsLabel)] preview=\"\(snippet)\""
        )
        MasterLogger.shared.business(
            "🤖 AI delivery source=\(source.rawValue) context=\(context) len=\(responseLength) grounded=\(groundedLabel)"
        )
    }
}
