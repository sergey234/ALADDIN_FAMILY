import Foundation

/// Russian-school mnemotable: 3×3 grid, show → hide → ordered recall (B13-T01).
final class MnemonicTableEngine {
    static let shared = MnemonicTableEngine()

    static let rowCount = 3
    static let columnCount = 3
    static let slotCount = rowCount * columnCount
    static let showDurationSeconds: TimeInterval = 3
    static let study09ItemId = "study.09"
    static let study09ActiveCellCount = 6

    static let study09PhraseKeys: [String] = (1...study09ActiveCellCount).map {
        "child_mnemo_table_cell_\($0)"
    }

    static let study09Emojis: [String] = ["📖", "🦸", "🗺️", "⚡", "🏰", "💡"]

    /// Per-cell co-creation key in `MnemonicPictogramStore` (B13-T03), e.g. `study.09.table.3`.
    static func cellPictogramItemId(parentItemId: String, slotIndex: Int) -> String {
        "\(parentItemId).table.\(slotIndex + 1)"
    }

    func pictogramItemId(for cell: Cell, parentItemId: String) -> String {
        Self.cellPictogramItemId(parentItemId: parentItemId, slotIndex: cell.slotIndex)
    }

    struct Cell: Equatable, Identifiable {
        let slotIndex: Int
        let emoji: String
        let phraseKey: String

        var id: Int { slotIndex }

        var gridRow: Int { slotIndex / columnCount }
        var gridColumn: Int { slotIndex % columnCount }
    }

    enum Phase: Equatable {
        case study
        case recall
        case completed(correctCount: Int, total: Int)
    }

    struct RoundState: Equatable {
        let cells: [Cell]
        let targetOrder: [Int]
        var phase: Phase
        var recallPicks: [Int]
    }

    func presetCells(for itemId: String) -> [Cell]? {
        guard itemId == Self.study09ItemId else { return nil }
        return zip(Self.study09Emojis, Self.study09PhraseKeys).enumerated().map { index, pair in
            Cell(slotIndex: index, emoji: pair.0, phraseKey: pair.1)
        }
    }

    func beginRound(cells: [Cell]) -> RoundState {
        let ordered = cells.sorted { $0.slotIndex < $1.slotIndex }
        return RoundState(
            cells: ordered,
            targetOrder: ordered.map(\.slotIndex),
            phase: .study,
            recallPicks: []
        )
    }

    func transitionToRecall(_ state: RoundState) -> RoundState {
        guard state.phase == .study else { return state }
        var next = state
        next.phase = .recall
        next.recallPicks = []
        return next
    }

    @discardableResult
    func pickCell(_ state: RoundState, slotIndex: Int) -> RoundState {
        guard state.phase == .recall else { return state }
        guard state.cells.contains(where: { $0.slotIndex == slotIndex }) else { return state }
        guard state.recallPicks.count < state.targetOrder.count else { return state }

        var next = state
        next.recallPicks.append(slotIndex)
        guard next.recallPicks.count == next.targetOrder.count else { return next }

        let correctCount = zip(next.recallPicks, next.targetOrder).filter { $0.0 == $0.1 }.count
        next.phase = .completed(correctCount: correctCount, total: next.targetOrder.count)
        MasterLogger.shared.business(
            "MNEMO-B13 table recall itemSlots=\(next.targetOrder.count) correct=\(correctCount)"
        )
        return next
    }

    func activeCells(in state: RoundState) -> [Cell] {
        state.cells.sorted { $0.slotIndex < $1.slotIndex }
    }

    func isPerfectRecall(_ state: RoundState) -> Bool {
        guard case .completed(let correct, let total) = state.phase else { return false }
        return correct == total && total > 0
    }

    func shuffledPickerCells(from state: RoundState, seed: UInt64? = nil) -> [Cell] {
        var cells = state.cells
        var generator: SeededRandomNumberGenerator
        if let seed {
            generator = SeededRandomNumberGenerator(seed: seed)
        } else {
            generator = SeededRandomNumberGenerator(seed: UInt64(Date().timeIntervalSince1970 * 1000))
        }
        cells.shuffle(using: &generator)
        return cells
    }

    /// Perfect table recall → Leitner advance + rewards (B13-T04).
    func recordRecallSuccess(
        itemId: String,
        correctCount: Int,
        total: Int,
        srsStore: MnemonicSRSStore? = nil,
        now: Date = Date()
    ) {
        guard correctCount == total, total > 0 else { return }
        let srs = srsStore ?? MnemonicSRSStore.shared
        srs.recordSuccess(itemId: itemId, now: now)
        MnemonicRewardBridge.award(.studyPass, itemId: itemId)
        MnemonicSkillTracker.shared.recordSuccessfulRecall(count: correctCount)
        MasterLogger.shared.business(
            "MNEMO-B13 table SRS success itemId=\(itemId) correct=\(correctCount)/\(total)"
        )
    }
}
