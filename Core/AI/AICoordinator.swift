import Foundation

/// P3.4 — thin client facade for AI-related API calls.
/// **Not** a multi-agent orchestrator: no local tool-calling, no refund/VPN, no parental bypass.
/// Server remains the brain (Companion router / Antifake / Wellness).
@MainActor
enum AICoordinator {
    enum Domain: String {
        case companion
        case antifake
        case wellness
    }

    /// Routes companion chat to existing `CompanionAPIService` (same contract as before).
    static func sendCompanionChat(
        message: String,
        characterId: String,
        sessionId: String?,
        inputMode: String = "text",
        securityExpertMode: Bool? = nil,
        chatMode: String = "fast",
        workspaceId: String? = nil,
        attachments: [CompanionAttachmentPayload] = [],
        wellnessPillar: String? = WellnessSessionStore.activePillar,
        guideMode: String? = WellnessGuideSessionStore.activeGuideModeIdForAPI
    ) async throws -> CompanionChatResponse {
        try await CompanionAPIService.shared.sendChat(
            message: message,
            characterId: characterId,
            sessionId: sessionId,
            inputMode: inputMode,
            securityExpertMode: securityExpertMode,
            chatMode: chatMode,
            workspaceId: workspaceId,
            attachments: attachments,
            wellnessPillar: wellnessPillar,
            guideMode: guideMode
        )
    }

    /// Canonical API paths for domains (documentation + single lookup). Does not perform network I/O.
    static func endpointHint(for domain: Domain) -> String {
        switch domain {
        case .companion:
            return AppConfig.Endpoint.aiCompanionChat
        case .antifake:
            return AppConfig.Endpoint.antifakeCheckText
        case .wellness:
            return "/api/wellness/"
        }
    }
}
