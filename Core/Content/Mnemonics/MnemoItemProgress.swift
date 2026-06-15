import Foundation

/// Mnemo catalog progress: «opened» (tap) vs «recalled» (SRS / lesson pass).
enum MnemoItemProgress {
    static func recallPercent(for itemId: String, store: MnemonicSRSStore = .shared) -> Int {
        store.recallMasteryPercent(itemId: itemId)
    }

    static func hasOpened(progress: ContentProgress?) -> Bool {
        guard let progress else { return false }
        return progress.attempts > 0 || progress.lastOpenedAt != nil
    }

    static func categoryId(for itemId: String) -> String? {
        MnemonicSRSStore.shared.categoryId(for: itemId)
    }
}
