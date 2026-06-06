import Foundation

final class MnemonicSkillTracker {
    static let shared = MnemonicSkillTracker()

    private let defaults: UserDefaults
    private let recallsKey = "child.mnemo.skill.recalls"
    private let anchorsKey = "child.mnemo.skill.anchors"
    private let capstoneKey = "child.mnemo.skill.capstone"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func recordSuccessfulRecall(count: Int = 1, childId: String? = nil) {
        let key = resolvedKey(recallsKey, childId: childId)
        defaults.set(successfulRecallCount(childId: childId) + max(1, count), forKey: key)
    }

    func recordAnchorPlaced(count: Int = 1, childId: String? = nil) {
        let key = resolvedKey(anchorsKey, childId: childId)
        defaults.set(anchorCount(childId: childId) + max(1, count), forKey: key)
    }

    func successfulRecallCount(childId: String? = nil) -> Int {
        defaults.integer(forKey: resolvedKey(recallsKey, childId: childId))
    }

    func anchorCount(childId: String? = nil) -> Int {
        defaults.integer(forKey: resolvedKey(anchorsKey, childId: childId))
    }

    func recordCapstoneCompleted(childId: String? = nil) {
        defaults.set(true, forKey: resolvedKey(capstoneKey, childId: childId))
    }

    func hasCompletedCapstone(childId: String? = nil) -> Bool {
        defaults.bool(forKey: resolvedKey(capstoneKey, childId: childId))
    }

    func currentLevel(childId: String? = nil) -> MnemonicSkillLevel {
        MnemonicSkillLevel.from(
            successfulRecalls: successfulRecallCount(childId: childId),
            anchors: anchorCount(childId: childId),
            capstoneCompleted: hasCompletedCapstone(childId: childId)
        )
    }

    func masteryPercent(childId: String? = nil) -> Int {
        let recalls = successfulRecallCount(childId: childId)
        let anchors = anchorCount(childId: childId)
        let raw = min(100, recalls * 3 + anchors * 2)
        return max(0, raw)
    }

    private func resolvedKey(_ base: String, childId: String?) -> String {
        let sid = (childId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !sid.isEmpty else { return "\(base).global" }
        return "\(base).\(sid)"
    }
}
