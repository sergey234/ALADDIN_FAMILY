import Foundation
import Combine

/// p2-8a — Focus session state (25 / 60 min).
final class FocusSessionStore: ObservableObject {
    static let shared = FocusSessionStore()

    enum DurationMinutes: Int, CaseIterable, Identifiable {
        case twentyFive = 25
        case sixty = 60
        var id: Int { rawValue }
    }

    enum Phase: Equatable {
        case idle
        case running
        case completed
        case aborted
    }

    @Published var selectedDuration: DurationMinutes = .twentyFive
    @Published var phase: Phase = .idle
    @Published var secondsRemaining: Int = 25 * 60
    @Published var softAbortMessage: String?
    /// Last success grant (nil until complete); used for XP already vs applied copy.
    @Published private(set) var lastGrantApplied: Bool?

    private var timer: Timer?
    private var startedAt: Date?

    private init() {}

    func select(_ duration: DurationMinutes) {
        guard phase != .running else { return }
        selectedDuration = duration
        secondsRemaining = duration.rawValue * 60
        phase = .idle
        softAbortMessage = nil
    }

    func start() {
        guard FamilyFocusSessionFeature.isEnabled else { return }
        stopTimer()
        secondsRemaining = selectedDuration.rawValue * 60
        phase = .running
        softAbortMessage = nil
        lastGrantApplied = nil
        startedAt = Date()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.tick()
            }
        }
    }

    func abort(softMessage: String) {
        guard phase == .running else { return }
        stopTimer()
        phase = .aborted
        softAbortMessage = softMessage
        lastGrantApplied = nil
        // p2-8b: no XP penalty on abort
    }

    @discardableResult
    func completeSuccess() -> UnicornCareReward.GrantResult {
        stopTimer()
        phase = .completed
        softAbortMessage = nil
        let result = UnicornCareReward.grant(
            reason: .focusSuccess,
            sourceId: "focus_\(selectedDuration.rawValue)"
        )
        lastGrantApplied = result.applied
        _ = HabitStreakStore.shared.recordDone(sourceId: "focus")
        return result
    }

    func resetToIdle() {
        stopTimer()
        phase = .idle
        secondsRemaining = selectedDuration.rawValue * 60
        softAbortMessage = nil
        lastGrantApplied = nil
    }

    private func tick() {
        guard phase == .running else { return }
        if secondsRemaining <= 1 {
            secondsRemaining = 0
            _ = completeSuccess()
            HapticFeedback.notification(.success)
            return
        }
        secondsRemaining -= 1
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
    }

    deinit { stopTimer() }
}
