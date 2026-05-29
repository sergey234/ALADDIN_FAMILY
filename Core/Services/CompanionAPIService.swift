import Foundation

/// HTTP-клиент companion API (JWT).
@MainActor
final class CompanionAPIService {
    static let shared = CompanionAPIService()
    private let network: NetworkManager
    private var legalCache: [String: (response: CompanionLegalResponse, fetchedAt: Date)] = [:]
    private var legalInFlight: [String: Task<CompanionLegalResponse, Error>] = [:]
    private let legalCacheTTL: TimeInterval = 30
    private var profileCache: (response: CompanionProfileSettings, fetchedAt: Date)?
    private var profileInFlight: Task<CompanionProfileSettings, Error>?
    private let profileCacheTTL: TimeInterval = 20
    private var stateCache: [String: (response: CompanionStateResponse, fetchedAt: Date)] = [:]
    private var stateInFlight: [String: Task<CompanionStateResponse, Error>] = [:]
    private let stateCacheTTL: TimeInterval = 12

    private init() {
        network = APIService.shared.networkManager
    }

    private func familyScopeHeaders() -> [String: String] {
        let fid = FamilyLocalStore.loadPersistedFamilyId().trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty else { return [:] }
        return ["X-Aladdin-Family-Id": fid]
    }

    func fetchCapabilities() async throws -> CompanionCapabilitiesPayload {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionCapabilities,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionCapabilitiesPayload, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchCharacters() async throws -> [CompanionCharacterDTO] {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionCharacters,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionCharactersResponse, Error>) in
                continuation.resume(with: result.map(\.characters))
            }
        }
    }

    func fetchLifeDomains(
        locale: String = "ru",
        securityExpertMode: Bool = false
    ) async throws -> [CompanionLifeDomainDTO] {
        var path = "\(AppConfig.Endpoint.aiCompanionDomains)?locale=\(locale)"
        if securityExpertMode {
            path += "&security_expert_mode=true"
        }
        return try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: path,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionLifeDomainsResponse, Error>) in
                continuation.resume(with: result.map(\.domains))
            }
        }
    }

    func fetchLegal(locale: String = "ru") async throws -> CompanionLegalResponse {
        let now = Date()
        if let cached = legalCache[locale], now.timeIntervalSince(cached.fetchedAt) < legalCacheTTL {
            return cached.response
        }
        if let inflight = legalInFlight[locale] {
            return try await inflight.value
        }

        let task = Task<CompanionLegalResponse, Error> {
        let path = "\(AppConfig.Endpoint.aiCompanionLegal)?locale=\(locale)"
            return try await withCheckedThrowingContinuation { continuation in
                network.get(
                    endpoint: path,
                    requiresAuth: true,
                    additionalHeaders: familyScopeHeaders()
                ) { (result: Result<CompanionLegalResponse, Error>) in
                    continuation.resume(with: result)
                }
            }
        }
        legalInFlight[locale] = task
        defer { legalInFlight[locale] = nil }

        let response = try await task.value
        legalCache[locale] = (response, now)
        return response
    }

    func fetchCosmetics(characterId: String) async throws -> CompanionCosmeticsResponse {
        let path = "\(AppConfig.Endpoint.aiCompanionCosmetics)?character_id=\(characterId)"
        return try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: path,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionCosmeticsResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func updateEquippedCosmetic(characterId: String, cosmeticId: String) async throws -> CompanionProfileSettings {
        let body = CompanionEquippedCosmeticBody(
            equippedCosmeticId: cosmeticId,
            equippedCosmeticCharacterId: characterId
        )
        let updated = try await withCheckedThrowingContinuation { continuation in
            network.put(
                endpoint: AppConfig.Endpoint.aiCompanionProfile,
                body: body,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionProfileSettings, Error>) in
                continuation.resume(with: result)
            }
        }
        profileCache = (updated, Date())
        stateCache.removeValue(forKey: characterId)
        return updated
    }

    func fetchState(characterId: String, forceRefresh: Bool = false) async throws -> CompanionStateResponse {
        let now = Date()
        if !forceRefresh, let cached = stateCache[characterId], now.timeIntervalSince(cached.fetchedAt) < stateCacheTTL {
            return cached.response
        }
        if !forceRefresh, let inflight = stateInFlight[characterId] {
            return try await inflight.value
        }

        let task = Task<CompanionStateResponse, Error> {
        let path = "\(AppConfig.Endpoint.aiCompanionState)?character_id=\(characterId)"
            return try await withCheckedThrowingContinuation { continuation in
                network.get(
                    endpoint: path,
                    requiresAuth: true,
                    additionalHeaders: familyScopeHeaders()
                ) { (result: Result<CompanionStateResponse, Error>) in
                    continuation.resume(with: result)
                }
            }
        }
        stateInFlight[characterId] = task
        defer { stateInFlight[characterId] = nil }

        let response = try await task.value
        stateCache[characterId] = (response, now)
        return response
    }

    func sendChat(
        message: String,
        characterId: String,
        sessionId: String?,
        inputMode: String = "text",
        securityExpertMode: Bool? = nil,
        chatMode: String = "fast",
        workspaceId: String? = nil,
        attachments: [CompanionAttachmentPayload] = []
    ) async throws -> CompanionChatResponse {
        let cloudText: String
        do {
            cloudText = try AIOutboundTextGate.prepareUserMessage(message).cloudText
        } catch {
            throw error
        }

        let body = CompanionChatRequest(
            message: cloudText,
            characterId: characterId,
            context: "companion",
            responseLanguage: LocalizationManager.shared.aiResponseLanguageCode,
            sessionId: sessionId,
            inputMode: inputMode,
            securityExpertMode: securityExpertMode,
            chatMode: chatMode,
            workspaceId: workspaceId,
            attachments: attachments
        )

        return try await withCheckedThrowingContinuation { continuation in
            network.post(
                endpoint: AppConfig.Endpoint.aiCompanionChat,
                body: body,
                requiresAuth: true,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionChatResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchThreads(limit: Int = 50) async throws -> [CompanionThreadSummary] {
        let path = "\(AppConfig.Endpoint.aiCompanionThreads)?limit=\(limit)"
        return try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: path,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionThreadsResponse, Error>) in
                continuation.resume(with: result.map(\.threads))
            }
        }
    }

    func fetchThreadMessages(threadId: String) async throws -> [CompanionThreadMessage] {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionThreadMessages(threadId: threadId),
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionThreadMessagesResponse, Error>) in
                continuation.resume(with: result.map(\.messages))
            }
        }
    }

    func fetchConsent() async throws -> CompanionConsentSettings {
        let fid = FamilyLocalStore.loadPersistedFamilyId()
        var path = AppConfig.Endpoint.aiCompanionConsent
        if !fid.isEmpty {
            path += "?family_id=\(fid.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? fid)"
        }
        return try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: path,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionConsentSettings, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func updateConsent(_ settings: CompanionConsentSettings) async throws -> CompanionConsentSettings {
        let fid = FamilyLocalStore.loadPersistedFamilyId()
        let body = CompanionConsentRequestBody(
            memoryEnabled: settings.memoryEnabled,
            childCanUseCompanion: settings.childCanUseCompanion,
            allowedCharacters: settings.allowedCharacters,
            familyId: fid.isEmpty ? nil : fid
        )
        return try await withCheckedThrowingContinuation { continuation in
            network.post(
                endpoint: AppConfig.Endpoint.aiCompanionConsent,
                body: body,
                requiresAuth: true,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionConsentSettings, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchMemory() async throws -> CompanionMemoryListResponse {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionMemory,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionMemoryListResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func exportMemory() async throws -> CompanionMemoryExportResponse {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionMemoryExport,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionMemoryExportResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchProfile(forceRefresh: Bool = false) async throws -> CompanionProfileSettings {
        let now = Date()
        if !forceRefresh, let cached = profileCache, now.timeIntervalSince(cached.fetchedAt) < profileCacheTTL {
            return cached.response
        }
        if !forceRefresh, let inflight = profileInFlight {
            return try await inflight.value
        }

        let task = Task<CompanionProfileSettings, Error> {
            try await withCheckedThrowingContinuation { continuation in
                network.get(
                    endpoint: AppConfig.Endpoint.aiCompanionProfile,
                    requiresAuth: true,
                    additionalHeaders: familyScopeHeaders()
                ) { (result: Result<CompanionProfileSettings, Error>) in
                    continuation.resume(with: result)
                }
            }
        }
        profileInFlight = task
        defer { profileInFlight = nil }

        let response = try await task.value
        profileCache = (response, now)
        return response
    }

    func updateProfile(
        customInstructions: String,
        personalityPreset: String,
        securityExpertMode: Bool? = nil
    ) async throws -> CompanionProfileSettings {
        let body = CompanionProfileUpdateBody(
            customInstructions: customInstructions,
            personalityPreset: personalityPreset,
            securityExpertMode: securityExpertMode,
            equippedCosmeticId: nil,
            equippedCosmeticCharacterId: nil
        )
        let updated = try await withCheckedThrowingContinuation { continuation in
            network.put(
                endpoint: AppConfig.Endpoint.aiCompanionProfile,
                body: body,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionProfileSettings, Error>) in
                continuation.resume(with: result)
            }
        }
        profileCache = (updated, Date())
        return updated
    }

    func deleteAllMemory() async throws -> CompanionMemoryDeleteResponse {
        try await withCheckedThrowingContinuation { continuation in
            network.delete(
                endpoint: AppConfig.Endpoint.aiCompanionMemory,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionMemoryDeleteResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func submitFeedback(
        vote: String,
        characterId: String,
        threadId: String?,
        messageId: String,
        assistantText: String,
        userQueryText: String?
    ) async throws -> CompanionFeedbackResponse {
        let body = CompanionFeedbackRequestBody(
            vote: vote,
            characterId: characterId,
            threadId: threadId,
            messageId: messageId,
            assistantText: assistantText,
            userQueryText: userQueryText
        )
        return try await withCheckedThrowingContinuation { continuation in
            network.post(
                endpoint: AppConfig.Endpoint.aiCompanionFeedback,
                body: body,
                requiresAuth: true,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionFeedbackResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchEphemeralVoiceToken() async throws -> CompanionEphemeralTokenResponse {
        try await withCheckedThrowingContinuation { continuation in
            network.post(
                endpoint: AppConfig.Endpoint.aiVoiceEphemeralToken,
                body: EmptyBody(),
                requiresAuth: true,
                extraHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionEphemeralTokenResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    func fetchWorkspaces(limit: Int = 30) async throws -> [CompanionWorkspaceDTO] {
        let path = "\(AppConfig.Endpoint.aiCompanionWorkspaces)?limit=\(limit)"
        return try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: path,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionWorkspacesResponse, Error>) in
                continuation.resume(with: result.map(\.workspaces))
            }
        }
    }

    func fetchCogs() async throws -> CompanionCogsResponse {
        try await withCheckedThrowingContinuation { continuation in
            network.get(
                endpoint: AppConfig.Endpoint.aiCompanionCogs,
                requiresAuth: true,
                additionalHeaders: familyScopeHeaders()
            ) { (result: Result<CompanionCogsResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    /// P1-10 — fire-and-forget; errors ignored.
    func recordAnalyticsEvent(
        event: String,
        characterId: String?,
        sessionId: String?,
        extra: [String: String]
    ) async {
        let body = CompanionAnalyticsEventBody(
            event: event,
            characterId: characterId,
            sessionId: sessionId,
            extra: extra.isEmpty ? nil : extra
        )
        do {
            _ = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<CompanionAnalyticsEventResponse, Error>) in
                network.post(
                    endpoint: AppConfig.Endpoint.aiCompanionAnalytics,
                    body: body,
                    requiresAuth: true,
                    extraHeaders: familyScopeHeaders()
                ) { (result: Result<CompanionAnalyticsEventResponse, Error>) in
                    continuation.resume(with: result)
                }
            }
        } catch {
            #if DEBUG
            print("Companion analytics BE skip: \(error.localizedDescription)")
            #endif
        }
    }
}

private struct EmptyBody: Encodable {}
