import Foundation
import SwiftUI
import UIKit

// MARK: - W4-3 G12: unified feedback (haptic + sound + optional particles + VoiceOver)

/// Semantic feedback kind mapped to haptics, `AppSoundEffect`, optional `CelebrationBurstKind`, and AX copy.
enum FeedbackKind: Equatable {
    case success
    case error
    case warning
    case selection
}

/// Priority for debounce preemption: within the debounce window, a higher priority can run; `.critical` bypasses debounce.
enum FeedbackPriority: Int, Comparable {
    case background = 0
    case normal = 1
    case high = 2
    case critical = 3

    static func < (lhs: FeedbackPriority, rhs: FeedbackPriority) -> Bool {
        lhs.rawValue < rhs.rawValue
    }
}

struct FeedbackOptions: Equatable {
    var priority: FeedbackPriority = .normal
    /// `nil` — default particles per `FeedbackKind`; `true` / `false` — force.
    var includeParticles: Bool?
    /// Overrides localized announcement; empty string skips VoiceOver.
    var announcement: String?
}

struct FeedbackParticleSession: Equatable, Identifiable {
    let id: UUID
    let kind: CelebrationBurstKind
}

@MainActor
final class FeedbackSystem: ObservableObject {
    static let shared = FeedbackSystem()
    static let debounceInterval: TimeInterval = 0.1

    /// Drives the root `FeedbackParticleOverlay`.
    @Published private(set) var particleSession: FeedbackParticleSession?

    private var lastAcceptUptime: TimeInterval = -1_000_000
    private var lastAcceptedPriority: FeedbackPriority = .background

    /// Injected in unit tests to control debounce.
    var uptime: () -> TimeInterval = { ProcessInfo.processInfo.systemUptime }

    private init() {}

    func resetDebounceStateForUnitTests() {
        lastAcceptUptime = -1_000_000
        lastAcceptedPriority = .background
        particleSession = nil
    }

    @discardableResult
    func signal(_ kind: FeedbackKind, options: FeedbackOptions = .init()) -> Bool {
        let now = uptime()
        guard shouldAccept(now: now, options: options) else { return false }
        lastAcceptUptime = now
        lastAcceptedPriority = options.priority

        playHaptic(kind: kind)
        playSound(kind: kind, options: options)
        scheduleParticlesIfNeeded(kind: kind, options: options)
        postAnnouncementIfNeeded(kind: kind, options: options)
        return true
    }

    func clearParticleIfCurrent(_ id: UUID) {
        if particleSession?.id == id {
            particleSession = nil
        }
    }

    private func shouldAccept(now: TimeInterval, options: FeedbackOptions) -> Bool {
        if options.priority == .critical { return true }
        let gap = now - lastAcceptUptime
        if gap >= Self.debounceInterval { return true }
        if options.priority > lastAcceptedPriority { return true }
        return false
    }

    private func playHaptic(kind: FeedbackKind) {
        switch kind {
        case .success:
            HapticFeedback.notification(.success)
        case .error:
            HapticFeedback.notification(.error)
        case .warning:
            HapticFeedback.notification(.warning)
        case .selection:
            HapticFeedback.selection()
        }
    }

    private func soundPriority(for options: FeedbackOptions) -> SoundPriority {
        switch options.priority {
        case .background: return .low
        case .normal: return .medium
        case .high: return .high
        case .critical: return .critical
        }
    }

    private func playSound(kind: FeedbackKind, options: FeedbackOptions) {
        let sp = soundPriority(for: options)
        let effect: AppSoundEffect
        switch kind {
        case .success: effect = .success
        case .error: effect = .error
        case .warning: effect = .warning
        case .selection: effect = .tapSoft
        }
        SoundEffectPlayer.shared.play(effect, priority: sp)
    }

    private func defaultParticleKind(_ kind: FeedbackKind) -> CelebrationBurstKind? {
        switch kind {
        case .success: return .achievementMagic
        case .error: return .rewardPurchase
        case .warning: return nil
        case .selection: return nil
        }
    }

    private func scheduleParticlesIfNeeded(kind: FeedbackKind, options: FeedbackOptions) {
        let defaultKind = defaultParticleKind(kind)
        let wantParticles: Bool
        if let p = options.includeParticles {
            wantParticles = p
        } else {
            wantParticles = (defaultKind != nil)
        }
        guard wantParticles else { return }
        let particleKind: CelebrationBurstKind
        if let d = defaultKind {
            particleKind = d
        } else {
            particleKind = .correctAnswerStars
        }
        particleSession = FeedbackParticleSession(id: UUID(), kind: particleKind)
    }

    private func postAnnouncementIfNeeded(kind: FeedbackKind, options: FeedbackOptions) {
        guard UIAccessibility.isVoiceOverRunning else { return }
        let text: String
        if let a = options.announcement {
            if a.isEmpty { return }
            text = a
        } else {
            let key: String
            switch kind {
            case .success: key = "feedback_announcement_success"
            case .error: key = "feedback_announcement_error"
            case .warning: key = "feedback_announcement_warning"
            case .selection: key = "feedback_announcement_selection"
            }
            text = NSLocalizedString(key, comment: "Feedback VoiceOver")
        }
        UIAccessibility.post(notification: .announcement, argument: text)
    }
}

// MARK: - Root overlay (host in `ALADDINApp` above `NavigationView`)

struct FeedbackParticleOverlay: View {
    @EnvironmentObject private var feedback: FeedbackSystem

    var body: some View {
        ZStack {
            if let s = feedback.particleSession {
                CelebrationParticleBurstView(
                    kind: s.kind,
                    active: true,
                    onFinished: { feedback.clearParticleIfCurrent(s.id) }
                )
                .id(s.id)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .allowsHitTesting(false)
    }
}
