import Foundation

/// Child POST / parent GET usage aggregates (no opaque tokens).
enum ScreenTimeUsageSync {
    static let path = "/api/parental-control/screen-time/usage"

    struct RemoteApp: Codable {
        let tokenHash: String
        let displayName: String?
        let seconds: Int
        let limitSeconds: Int?
    }

    struct RemoteBody: Codable {
        let familyId: String
        let memberId: String
        let deviceId: String
        let dayStart: String
        let timezone: String
        let totalSeconds: Int
        let apps: [RemoteApp]
        let source: String
        let updatedAt: String
    }

    struct PostOK: Codable {
        let success: Bool?
        let ok: Bool?
    }

    private static let iso = ISO8601DateFormatter()

    static func body(from snap: ScreenTimeUsageStore.Snapshot) -> RemoteBody {
        RemoteBody(
            familyId: snap.familyId,
            memberId: snap.memberId,
            deviceId: snap.deviceId,
            dayStart: snap.dayStart,
            timezone: snap.timezone,
            totalSeconds: snap.totalSeconds,
            apps: snap.apps.map {
                RemoteApp(
                    tokenHash: $0.tokenHash,
                    displayName: $0.displayName,
                    seconds: $0.seconds,
                    limitSeconds: $0.limitSeconds
                )
            },
            source: snap.source,
            updatedAt: iso.string(from: snap.updatedAt)
        )
    }

    /// Child: push local store snapshot to `:8002`.
    static func postIfChild() async -> Bool {
        guard FamilyScreenTimeEligibility.isSupervisedDevice() else { return false }
        guard let snap = ScreenTimeUsageStore.load(), !snap.familyId.isEmpty, !snap.memberId.isEmpty else {
            return false
        }
        let payload = body(from: snap)
        return await withCheckedContinuation { (cont: CheckedContinuation<Bool, Never>) in
            Task { @MainActor in
                NetworkManager.shared.post(endpoint: path, body: payload, requiresAuth: true) { (result: Result<PostOK, Error>) in
                    switch result {
                    case .success:
                        cont.resume(returning: true)
                    case .failure(let error):
                        print("⚠️ ScreenTimeUsageSync POST failed: \(error.localizedDescription)")
                        cont.resume(returning: false)
                    }
                }
            }
        }
    }

    /// Parent: pull aggregate for member/day into `parental_time_stats` (source=server).
    static func pullForParent(familyId: String, memberId: String, dayStart: String? = nil) async -> Bool {
        let day = dayStart ?? ScreenTimeUsageStore.dayKey()
        let query = [
            "familyId": familyId,
            "memberId": memberId,
            "dayStart": day
        ]
        return await withCheckedContinuation { (cont: CheckedContinuation<Bool, Never>) in
            Task { @MainActor in
                NetworkManager.shared.get(
                    endpoint: path,
                    queryParams: query,
                    requiresAuth: true
                ) { (result: Result<RemoteBody, Error>) in
                    switch result {
                    case .success(let remote):
                        guard let updated = iso.date(from: remote.updatedAt) else {
                            cont.resume(returning: false)
                            return
                        }
                        if Date().timeIntervalSince(updated) > ScreenTimeUsageStore.staleAfterSeconds {
                            cont.resume(returning: false)
                            return
                        }
                        let remoteApps: [ScreenTimeUsageStore.AppMinute] = remote.apps.map {
                            ScreenTimeUsageStore.AppMinute(
                                tokenHash: $0.tokenHash,
                                displayName: $0.displayName,
                                seconds: $0.seconds,
                                limitSeconds: $0.limitSeconds
                            )
                        }
                        let payload = ScreenTimeUsageStore.buildParentalTimeStatsPayload(
                            source: "server",
                            totalSeconds: remote.totalSeconds,
                            apps: remoteApps,
                            memberId: remote.memberId,
                            deviceId: remote.deviceId,
                            dayStart: remote.dayStart,
                            updatedAt: remote.updatedAt
                        )
                        ScreenTimeUsageStore.applyServerPayload(payload)
                        cont.resume(returning: true)
                    case .failure(let error):
                        print("⚠️ ScreenTimeUsageSync GET failed: \(error.localizedDescription)")
                        cont.resume(returning: false)
                    }
                }
            }
        }
    }
}
