import Foundation
import Combine

/// Загружает `/api/ai/companion/capabilities` — UI без хардкода mic/trust.
@MainActor
final class CompanionCapabilitiesService: ObservableObject {
    static let shared = CompanionCapabilitiesService()

    @Published private(set) var payload: CompanionCapabilitiesPayload?
    @Published private(set) var isLoading = false
    @Published private(set) var lastError: String?

    private let api = CompanionAPIService.shared

    private init() {}

    var voiceRealtimeEnabled: Bool {
        uiFlag(module: "voice_realtime", key: "mic_button")
    }

    var companionEnabled: Bool {
        featureEnabled("companion")
    }

    func refresh() async {
        isLoading = true
        lastError = nil
        defer { isLoading = false }

        do {
            payload = try await api.fetchCapabilities()
        } catch {
            lastError = error.localizedDescription
        }
    }

    private func featureEnabled(_ name: String) -> Bool {
        payload?.features?[name]?.enabled ?? true
    }

    private func uiFlag(module: String, key: String) -> Bool {
        payload?.features?[module]?.ui?[key] ?? true
    }
}
