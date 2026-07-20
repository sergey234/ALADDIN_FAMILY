import Foundation
import Combine

/// p2-9h — sync FamilyChallenge list (local-first, last-write wins on server).
@MainActor
final class FamilyChallengesService: ObservableObject {
    static let shared = FamilyChallengesService()

    @Published private(set) var challenges: [FamilyChallenge] = []
    @Published private(set) var isConfiguredOnServer = false

    private init() {
        challenges = FamilyChallengesStore.loadLocal()
    }

    func refreshFromServer() async {
        let result: Result<FamilyChallengesAPIResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilyChallenges { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            challenges = Array((payload.challenges ?? []).prefix(FamilyChallengesFeature.maxActive))
            isConfiguredOnServer = payload.configured ?? false
            FamilyChallengesStore.saveLocal(challenges)
        case .failure:
            challenges = FamilyChallengesStore.loadLocal()
        }
    }

    func save(_ list: [FamilyChallenge]) async throws {
        let capped = Array(list.prefix(FamilyChallengesFeature.maxActive))
        FamilyChallengesStore.saveLocal(capped)
        challenges = capped
        let result: Result<FamilyChallengesAPIResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.setFamilyChallenges(challenges: capped) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            challenges = Array((payload.challenges ?? capped).prefix(FamilyChallengesFeature.maxActive))
            isConfiguredOnServer = true
            FamilyChallengesStore.saveLocal(challenges)
        case .failure(let error):
            // Keep local — offline OK
            throw error
        }
    }

    @discardableResult
    func add(title: String, emoji: String = "🏁") async -> Bool {
        var list = challenges
        guard list.count < FamilyChallengesFeature.maxActive else { return false }
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.count >= 2 else { return false }
        list.append(FamilyChallenge(title: trimmed, emoji: emoji))
        do {
            try await save(list)
        } catch {
            FamilyChallengesStore.saveLocal(list)
            challenges = list
        }
        return true
    }

    func update(_ challenge: FamilyChallenge) async {
        var list = challenges
        guard let idx = list.firstIndex(where: { $0.id == challenge.id }) else { return }
        list[idx] = challenge
        do {
            try await save(list)
        } catch {
            FamilyChallengesStore.saveLocal(list)
            challenges = list
        }
    }

    func delete(id: String) async {
        let list = challenges.filter { $0.id != id }
        do {
            try await save(list)
        } catch {
            FamilyChallengesStore.saveLocal(list)
            challenges = list
        }
    }
}
