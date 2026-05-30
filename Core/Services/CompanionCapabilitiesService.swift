import Foundation
import Combine

/// Загружает `/api/ai/companion/capabilities` — UI без хардкода mic/trust.
@MainActor
final class CompanionCapabilitiesService: ObservableObject {
    static let shared = CompanionCapabilitiesService()
    static let defaultCompanionCharacters = ["unicorn", "aladdin", "genie"]

    @Published private(set) var payload: CompanionCapabilitiesPayload?
    @Published private(set) var isLoading = false
    @Published private(set) var lastError: String?

    private let api = CompanionAPIService.shared
    private var cacheFetchedAt: Date?
    private var refreshInFlight: Task<Void, Never>?
    private let cacheTTL: TimeInterval = 30

    private init() {}

    var voiceRealtimeEnabled: Bool {
        uiFlag(module: "voice_realtime", key: "mic_button")
    }

    /// Premium: ElevenLabs Flash через `/companion/tts`. Free/trial → AVSpeech на устройстве.
    var neuroTtsPremiumEnabled: Bool {
        uiFlag(module: "companion_neuro_tts", key: "neuro_tts_premium")
    }

    /// Server Whisper fallback when Apple STT returns empty (requires FEATURE_COMPANION_SERVER_STT on VPS).
    var serverSttFallbackEnabled: Bool {
        uiFlag(module: "companion_server_stt", key: "server_stt_fallback", defaultValue: false)
    }

    var companionEnabled: Bool {
        featureEnabled("companion")
    }

    var allowedCharactersFromCapabilities: [String] {
        guard let list = payload?.features?["companion"]?.ui?.characters, !list.isEmpty else {
            return Self.defaultCompanionCharacters
        }
        return list
    }

    /// TTL-кэш + coalescing параллельных вызовов (Home + Hub не дублируют сеть).
    func refresh(force: Bool = false) async {
        let now = Date()
        if !force,
           payload != nil,
           let fetchedAt = cacheFetchedAt,
           now.timeIntervalSince(fetchedAt) < cacheTTL {
            return
        }
        if let inflight = refreshInFlight {
            await inflight.value
            return
        }

        let task = Task<Void, Never> { [weak self] in
            guard let self else { return }
            self.isLoading = true
            self.lastError = nil
            defer { self.isLoading = false }

            do {
                let fetched = try await self.api.fetchCapabilities()
                self.payload = fetched
                self.cacheFetchedAt = Date()
            } catch {
                self.lastError = error.localizedDescription
            }
        }
        refreshInFlight = task
        defer { refreshInFlight = nil }
        await task.value
    }

    private func featureEnabled(_ name: String) -> Bool {
        payload?.features?[name]?.enabled ?? true
    }

    private func uiFlag(module: String, key: String, defaultValue: Bool? = nil) -> Bool {
        // neuro_tts_premium: default false until capabilities loaded (Free must not hit /tts)
        let resolvedDefault: Bool
        if let defaultValue {
            resolvedDefault = defaultValue
        } else if module == "companion_neuro_tts" && key == "neuro_tts_premium" {
            resolvedDefault = false
        } else {
            resolvedDefault = true
        }
        return payload?.features?[module]?.ui?.flag(key) ?? resolvedDefault
    }
}
