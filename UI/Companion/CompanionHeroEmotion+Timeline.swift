import Foundation

extension CompanionHeroEmotion {
    /// HERO-3-24 — без игривых акцентов (✨, широкий рот, playful tilt).
    var suppressesPlayfulVisuals: Bool {
        switch self {
        case .sad, .comfort:
            return true
        default:
            return false
        }
    }

    /// Фазы UI-диалога (§2.2 COMPANION_HEROES_3_FIGMA_RIVE_PLAN) — не смешивать с контент-эмоциями в одном кадре.
    var isDialoguePhase: Bool {
        switch self {
        case .listening, .thinking, .speaking:
            return true
        default:
            return false
        }
    }

    /// Эмоции контента после реплики (happy, sad, playful…).
    var isStreamContentEmotion: Bool {
        !isDialoguePhase
    }
}

/// HERO-3-18 — debounce смены emotion на SSE stream (≥ 400 ms).
@MainActor
final class CompanionStreamEmotionDebouncer {
    private var pending: CompanionHeroEmotion?
    private var debounceTask: Task<Void, Never>?

    private let intervalNs: UInt64

    init(intervalNs: UInt64 = 400_000_000) {
        self.intervalNs = intervalNs
    }

    func submit(_ emotion: CompanionHeroEmotion, apply: @escaping (CompanionHeroEmotion) -> Void) {
        pending = emotion
        debounceTask?.cancel()
        debounceTask = Task {
            try? await Task.sleep(nanoseconds: intervalNs)
            guard !Task.isCancelled, let value = pending else { return }
            apply(value)
            pending = nil
        }
    }

    func flush(apply: @escaping (CompanionHeroEmotion) -> Void) {
        debounceTask?.cancel()
        debounceTask = nil
        if let value = pending {
            apply(value)
        }
        pending = nil
    }

    func cancel() {
        debounceTask?.cancel()
        debounceTask = nil
        pending = nil
    }
}
