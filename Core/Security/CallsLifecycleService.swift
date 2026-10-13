import Combine
import Foundation

/// Arms call-memory prep / after-flow. Mic-during-PSTN quality is decided by device spike (Phase 0).
@MainActor
final class CallsLifecycleService: ObservableObject {
    static let shared = CallsLifecycleService()

    @Published var showAfterSheet = false
    @Published var armedGoal: String = ""
    @Published var armedWantMicRecord = false
    @Published var lastSpikeResultRaw: String {
        didSet { UserDefaults.standard.set(lastSpikeResultRaw, forKey: AppConfig.UserDefaultsKeys.callsSpikeResult) }
    }

    private let store = CallSessionsStore()

    private init() {
        lastSpikeResultRaw = UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.callsSpikeResult) ?? "pending"
    }

    enum SpikeResult: String {
        case pending
        case green
        case yellow
        case red
    }

    var spikeResult: SpikeResult {
        SpikeResult(rawValue: lastSpikeResultRaw) ?? .pending
    }

    func setSpikeResult(_ result: SpikeResult) {
        lastSpikeResultRaw = result.rawValue
    }

    func armPrep(goal: String, wantMicRecord: Bool) {
        armedGoal = goal.trimmingCharacters(in: .whitespacesAndNewlines)
        armedWantMicRecord = wantMicRecord
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.callsPrepArmed)
        UserDefaults.standard.set(armedGoal, forKey: AppConfig.UserDefaultsKeys.callsPrepGoal)
        UserDefaults.standard.set(wantMicRecord, forKey: AppConfig.UserDefaultsKeys.callsPrepWantMic)
    }

    func clearArm() {
        armedGoal = ""
        armedWantMicRecord = false
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.callsPrepArmed)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.callsPrepGoal)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.callsPrepWantMic)
    }

    /// CallKit ended → open after sheet when Calls access is on.
    func handleCallEnded() {
        guard CallsAccessPolicy.isAvailable() else { return }
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingCallsAfterSheet)
        showAfterSheet = true
    }

    func consumePendingAfterIfNeeded() {
        guard UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.pendingCallsAfterSheet) else { return }
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.pendingCallsAfterSheet)
        showAfterSheet = true
    }

    @discardableResult
    func saveAfterNote(goal: String, note: String, source: CallSessionSource = .postCallPush) -> CallSession {
        let g = goal.trimmingCharacters(in: .whitespacesAndNewlines)
        let n = note.trimmingCharacters(in: .whitespacesAndNewlines)
        let summary = CallSummaryService.summarize(goal: g, transcriptOrNote: n)
        let session = CallSession(
            endedAt: Date(),
            goal: g,
            mode: .postOnly,
            source: source,
            transcript: n,
            summary: summary
        )
        store.upsert(session)
        clearArm()
        showAfterSheet = false
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.pendingCallsAfterSheet)
        return session
    }

    func allSessions() -> [CallSession] {
        store.load()
    }

    func deleteSession(id: UUID) {
        store.delete(id: id)
        objectWillChange.send()
    }
}
