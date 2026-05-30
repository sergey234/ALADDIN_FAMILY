import Foundation

/// Proactive family roster reconcile at app start / login (server = source of truth for admin gate).
@MainActor
final class FamilyReconcileService: ObservableObject {
    static let shared = FamilyReconcileService()

    struct Snapshot: Sendable {
        let familyId: String
        let canManageRoster: Bool
        let rosterUsed: Int?
        let rosterMax: Int?
        let memberCount: Int
        let reconciledAt: Date
        let reason: String
    }

    @Published private(set) var snapshot: Snapshot?
    @Published private(set) var isReconciling = false
    @Published private(set) var lastError: String?

    private let api = APIService.shared
    private var lastReconcileAt: Date?
    private var inFlight: Task<Void, Never>?
    private let throttleSec: TimeInterval = 30
    private var loginObserver: NSObjectProtocol?

    private init() {
        loadPersistedSnapshot()
        loginObserver = NotificationCenter.default.addObserver(
            forName: NSNotification.Name("UserDidLogin"),
            object: nil,
            queue: .main
        ) { _ in
            Task { @MainActor in
                await FamilyReconcileService.shared.reconcileIfNeeded(reason: "UserDidLogin", force: true)
            }
        }
    }

    /// Server-confirmed admin rights for roster mutations (`X-Actor-Can-Manage-Roster`).
    var serverConfirmedCanManageRoster: Bool? {
        snapshot?.canManageRoster
    }

    func reconcileIfNeeded(reason: String, force: Bool = false) async {
        let now = Date()
        if !force,
           let last = lastReconcileAt,
           now.timeIntervalSince(last) < throttleSec,
           snapshot != nil {
            return
        }
        if let inFlight {
            await inFlight.value
            return
        }

        let task = Task<Void, Never> { @MainActor in
            self.isReconciling = true
            self.lastError = nil
            defer { self.isReconciling = false }

            FamilyLocalStore.reconcileFamilyContextWithCurrentJWT()

            guard KeychainManager.shared.loadString(forKey: .authToken)?.isEmpty == false else {
                self.snapshot = nil
                self.persistSnapshot(nil)
                return
            }

            do {
                let ctx = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<APIService.FamilyMembersSyncContext, Error>) in
                    self.api.getFamilyMembersWithSyncContext { result in
                        continuation.resume(with: result)
                    }
                }
                let members = ctx.members
                let fid = FamilyLocalStore.loadPersistedFamilyId()
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                let canManage = Self.readCanManageRosterFromDefaults()
                let used = UserDefaults.standard.object(forKey: "family_roster_used_last") as? Int
                let max = UserDefaults.standard.object(forKey: "family_limit") as? Int

                let snap = Snapshot(
                    familyId: fid,
                    canManageRoster: canManage ?? false,
                    rosterUsed: used,
                    rosterMax: max,
                    memberCount: members.count,
                    reconciledAt: Date(),
                    reason: reason
                )
                self.snapshot = snap
                self.lastReconcileAt = Date()
                self.persistSnapshot(snap)
                VisualLogger.shared.log(
                    "✅ FAMILY RECONCILE(\(reason)): fid=\(fid.isEmpty ? "none" : fid) members=\(members.count) canManage=\(canManage ?? false)",
                    level: .success,
                    category: "FAMILY"
                )
            } catch {
                self.lastError = error.localizedDescription
                if FamilyLocalStore.shouldClearFamilyCacheAfterMembersRequestFailure(error) {
                    FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                    self.snapshot = nil
                    self.persistSnapshot(nil)
                }
                VisualLogger.shared.log(
                    "⚠️ FAMILY RECONCILE(\(reason)) failed: \(error.localizedDescription)",
                    level: .warning,
                    category: "FAMILY"
                )
            }
        }
        inFlight = task
        defer { inFlight = nil }
        await task.value
    }

    private static func readCanManageRosterFromDefaults() -> Bool? {
        guard UserDefaults.standard.object(forKey: "family_actor_can_manage_roster_last") != nil else {
            return nil
        }
        return UserDefaults.standard.bool(forKey: "family_actor_can_manage_roster_last")
    }

    private func persistSnapshot(_ snap: Snapshot?) {
        let defaults = UserDefaults.standard
        if let snap {
            defaults.set(snap.familyId, forKey: "family_reconcile_family_id_last")
            defaults.set(snap.canManageRoster, forKey: "family_actor_can_manage_roster_last")
            defaults.set(snap.reconciledAt.timeIntervalSince1970, forKey: "family_reconcile_at_last")
        } else {
            defaults.removeObject(forKey: "family_reconcile_family_id_last")
            defaults.removeObject(forKey: "family_actor_can_manage_roster_last")
            defaults.removeObject(forKey: "family_reconcile_at_last")
        }
        defaults.synchronize()
    }

    private func loadPersistedSnapshot() {
        let defaults = UserDefaults.standard
        guard defaults.object(forKey: "family_reconcile_at_last") != nil else { return }
        let fid = (defaults.string(forKey: "family_reconcile_family_id_last") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let can = defaults.bool(forKey: "family_actor_can_manage_roster_last")
        let ts = defaults.double(forKey: "family_reconcile_at_last")
        snapshot = Snapshot(
            familyId: fid,
            canManageRoster: can,
            rosterUsed: defaults.object(forKey: "family_roster_used_last") as? Int,
            rosterMax: defaults.object(forKey: "family_limit") as? Int,
            memberCount: 0,
            reconciledAt: Date(timeIntervalSince1970: ts),
            reason: "persisted"
        )
    }
}
