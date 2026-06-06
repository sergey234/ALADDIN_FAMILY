import XCTest
@testable import ALADDIN

final class MnemonicTableEngineTests: XCTestCase {

    private let engine = MnemonicTableEngine.shared

    func testGridConstants_isThreeByThree() {
        XCTAssertEqual(MnemonicTableEngine.rowCount, 3)
        XCTAssertEqual(MnemonicTableEngine.columnCount, 3)
        XCTAssertEqual(MnemonicTableEngine.slotCount, 9)
        XCTAssertEqual(MnemonicTableEngine.showDurationSeconds, 3)
    }

    func testStudy09Preset_hasSixLiteratureCells() {
        let cells = engine.presetCells(for: MnemonicTableEngine.study09ItemId)
        XCTAssertEqual(cells?.count, 6)
        XCTAssertEqual(cells?.map(\.slotIndex), [0, 1, 2, 3, 4, 5])
        XCTAssertEqual(cells?.map(\.phraseKey), MnemonicTableEngine.study09PhraseKeys)
        XCTAssertEqual(engine.presetCells(for: "study.04"), nil)
    }

    func testBeginRound_ordersCellsBySlotIndex() {
        let shuffled = [
            MnemonicTableEngine.Cell(slotIndex: 3, emoji: "⚡", phraseKey: "child_mnemo_table_cell_4"),
            MnemonicTableEngine.Cell(slotIndex: 0, emoji: "📖", phraseKey: "child_mnemo_table_cell_1")
        ]
        let round = engine.beginRound(cells: shuffled)
        XCTAssertEqual(round.targetOrder, [0, 3])
        XCTAssertEqual(round.phase, .study)
        XCTAssertTrue(round.recallPicks.isEmpty)
    }

    func testRecall_perfectSequenceCompletes() {
        guard let cells = engine.presetCells(for: MnemonicTableEngine.study09ItemId) else {
            return XCTFail("missing preset")
        }
        var round = engine.beginRound(cells: cells)
        round = engine.transitionToRecall(round)
        for slot in round.targetOrder {
            round = engine.pickCell(round, slotIndex: slot)
        }
        XCTAssertTrue(engine.isPerfectRecall(round))
        if case .completed(let correct, let total) = round.phase {
            XCTAssertEqual(correct, 6)
            XCTAssertEqual(total, 6)
        } else {
            XCTFail("expected completed phase")
        }
    }

    func testRecall_wrongOrderScoresPartial() {
        guard let cells = engine.presetCells(for: MnemonicTableEngine.study09ItemId) else {
            return XCTFail("missing preset")
        }
        var round = engine.beginRound(cells: cells)
        round = engine.transitionToRecall(round)
        let reversed = round.targetOrder.reversed()
        for slot in reversed {
            round = engine.pickCell(round, slotIndex: slot)
        }
        XCTAssertFalse(engine.isPerfectRecall(round))
        if case .completed(let correct, let total) = round.phase {
            XCTAssertEqual(total, 6)
            XCTAssertLessThan(correct, total)
        } else {
            XCTFail("expected completed phase")
        }
    }

    func testCellPictogramItemId_mapsSlotToB11StoreKey() {
        XCTAssertEqual(
            MnemonicTableEngine.cellPictogramItemId(parentItemId: "study.09", slotIndex: 0),
            "study.09.table.1"
        )
        XCTAssertEqual(
            MnemonicTableEngine.cellPictogramItemId(parentItemId: "study.09", slotIndex: 5),
            "study.09.table.6"
        )
        XCTAssertTrue(MnemonicPictogramStore.supportsCoCreation(itemId: "study.09.table.3"))
    }

    func testPictogramItemId_forCell_matchesSlotIndex() {
        let cell = MnemonicTableEngine.Cell(slotIndex: 2, emoji: "🗺️", phraseKey: "child_mnemo_table_cell_3")
        XCTAssertEqual(
            engine.pictogramItemId(for: cell, parentItemId: MnemonicTableEngine.study09ItemId),
            "study.09.table.3"
        )
    }

    func testRecordRecallSuccess_advancesSRSOnPerfectRecallOnly() {
        let srsSuite = UserDefaults(suiteName: "test.mnemo.table.srs.\(UUID().uuidString)")!
        let srs = MnemonicSRSStore(defaults: srsSuite)
        let now = Date(timeIntervalSince1970: 1_750_000_000)
        let itemId = MnemonicTableEngine.study09ItemId

        srs.scheduleInitial(itemId: itemId, now: now)
        XCTAssertTrue(srs.dueItems(now: now).contains(itemId))

        engine.recordRecallSuccess(
            itemId: itemId,
            correctCount: 4,
            total: 6,
            srsStore: srs,
            now: now
        )
        XCTAssertTrue(srs.dueItems(now: now).contains(itemId))

        engine.recordRecallSuccess(
            itemId: itemId,
            correctCount: 6,
            total: 6,
            srsStore: srs,
            now: now
        )
        XCTAssertFalse(srs.dueItems(now: now).contains(itemId))
    }

    func testShuffledPicker_isDeterministicWithSeed() {
        guard let cells = engine.presetCells(for: MnemonicTableEngine.study09ItemId) else {
            return XCTFail("missing preset")
        }
        let round = engine.beginRound(cells: cells)
        let a = engine.shuffledPickerCells(from: round, seed: 99)
        let b = engine.shuffledPickerCells(from: round, seed: 99)
        XCTAssertEqual(a.map(\.slotIndex), b.map(\.slotIndex))
    }
}
