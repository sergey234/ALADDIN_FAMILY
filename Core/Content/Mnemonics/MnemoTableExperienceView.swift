import SwiftUI

/// Mnemotable UI — 3×3 show 3s → hide → ordered cell recall (`study.09` literature, B13-T02).
struct MnemoTableExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    @State private var round = MnemonicTableEngine.shared.beginRound(
        cells: MnemonicTableEngine.shared.presetCells(for: MnemonicTableEngine.study09ItemId) ?? []
    )
    @State private var pickerCells: [MnemonicTableEngine.Cell] = []
    @State private var showTable = true
    @State private var feedbackKey: String?
    @State private var pictogramCellSlot: Int?
    @State private var pictogramUIRevision = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_table_title"))
                .font(.system(size: 17, weight: .bold))

            Text(localizationManager.localized("child_mnemo_table_subtitle"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            switch round.phase {
            case .study:
                studyGrid
            case .recall:
                recallSection
            case .completed(let correct, let total):
                resultSection(correct: correct, total: total)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onAppear {
            reloadRound()
        }
        .sheet(isPresented: Binding(
            get: { pictogramCellSlot != nil },
            set: { if !$0 { pictogramCellSlot = nil } }
        )) {
            if let slot = pictogramCellSlot {
                MnemoPictogramDrawingSheet(
                    itemId: MnemonicTableEngine.cellPictogramItemId(
                        parentItemId: item.id,
                        slotIndex: slot
                    ),
                    onSaved: {
                        pictogramUIRevision += 1
                    }
                )
                .environmentObject(localizationManager)
            }
        }
        .accessibilityIdentifier("child_mnemo_table_experience")
    }

    private var studyGrid: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_table_show_hint"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)

            tableGrid(cells: MnemonicTableEngine.shared.activeCells(in: round), reveal: showTable)
                .id(pictogramUIRevision)

            if showTable {
                Text(localizationManager.localized("child_mnemo_pictogram_encode_hint"))
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.secondary)
                Button(localizationManager.localized("child_mnemo_table_start_recall")) {
                    beginRecall()
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("child_mnemo_table_start_recall")
            }
        }
        .onAppear {
            showTable = true
            DispatchQueue.main.asyncAfter(deadline: .now() + MnemonicTableEngine.showDurationSeconds) {
                if case .study = round.phase {
                    showTable = false
                }
            }
        }
    }

    private var recallSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_table_recall_prompt"))
                .font(.system(size: 14, weight: .semibold))

            if !round.recallPicks.isEmpty {
                Text(
                    round.recallPicks.compactMap { slot in
                        round.cells.first(where: { $0.slotIndex == slot })?.emoji
                    }.joined(separator: " ")
                )
                .font(.system(size: 20, weight: .bold))
                .frame(maxWidth: .infinity, alignment: .center)
            }

            LazyVGrid(
                columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: MnemonicTableEngine.columnCount),
                spacing: 8
            ) {
                ForEach(pickerCells) { cell in
                    Button {
                        pickCell(cell.slotIndex)
                    } label: {
                        VStack(spacing: 4) {
                            MnemoTableCellVisual(
                                cell: cell,
                                parentItemId: item.id,
                                emojiFontSize: 26,
                                imageMaxHeight: 40,
                                showEmojiBadgeWhenPictogram: true
                            )
                            .id("\(pictogramUIRevision)-\(cell.slotIndex)")
                            Text(localizationManager.localized(cell.phraseKey))
                                .font(.system(size: 10, weight: .semibold))
                                .lineLimit(2)
                                .minimumScaleFactor(0.7)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity, minHeight: 64)
                    }
                    .buttonStyle(.bordered)
                    .disabled(round.recallPicks.count >= round.targetOrder.count)
                }
            }

            if let feedbackKey {
                Text(localizationManager.localized(feedbackKey))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(feedbackKey.contains("ok") ? .green : .orange)
            }
        }
    }

    private func resultSection(correct: Int, total: Int) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(
                String(
                    format: localizationManager.localized("child_mnemo_table_score"),
                    correct,
                    total
                )
            )
            .font(.system(size: 16, weight: .bold))
            .foregroundColor(.green)
            .accessibilityIdentifier("child_mnemo_table_score")

            Button(localizationManager.localized("child_interface_done")) {
                Task { await onComplete() }
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private func tableGrid(cells: [MnemonicTableEngine.Cell], reveal: Bool) -> some View {
        let slots = (0..<MnemonicTableEngine.slotCount).map { index -> MnemonicTableEngine.Cell? in
            cells.first(where: { $0.slotIndex == index })
        }
        return LazyVGrid(
            columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: MnemonicTableEngine.columnCount),
            spacing: 8
        ) {
            ForEach(Array(slots.enumerated()), id: \.offset) { _, cell in
                if let cell, reveal {
                    Button {
                        pictogramCellSlot = cell.slotIndex
                    } label: {
                        VStack(spacing: 4) {
                            MnemoTableCellVisual(
                                cell: cell,
                                parentItemId: item.id,
                                emojiFontSize: 28,
                                imageMaxHeight: 48
                            )
                            Text(localizationManager.localized(cell.phraseKey))
                                .font(.system(size: 11, weight: .semibold))
                                .lineLimit(2)
                                .minimumScaleFactor(0.7)
                                .multilineTextAlignment(.center)
                                .foregroundColor(.primary)
                        }
                        .frame(maxWidth: .infinity, minHeight: 72)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("child_mnemo_table_cell_tap_\(cell.slotIndex)")
                } else {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.gray.opacity(0.06))
                        .frame(minHeight: 72)
                }
            }
        }
    }

    private func reloadRound() {
        let cells = MnemonicTableEngine.shared.presetCells(for: item.id)
            ?? MnemonicTableEngine.shared.presetCells(for: MnemonicTableEngine.study09ItemId)
            ?? []
        round = MnemonicTableEngine.shared.beginRound(cells: cells)
        pickerCells = MnemonicTableEngine.shared.shuffledPickerCells(from: round, seed: 7)
        showTable = true
        feedbackKey = nil
    }

    private func beginRecall() {
        round = MnemonicTableEngine.shared.transitionToRecall(round)
        showTable = false
        pickerCells = MnemonicTableEngine.shared.shuffledPickerCells(from: round)
        feedbackKey = nil
    }

    private func pickCell(_ slotIndex: Int) {
        round = MnemonicTableEngine.shared.pickCell(round, slotIndex: slotIndex)
        if case .completed(let correct, let total) = round.phase {
            let isPerfect = correct == total && total > 0
            feedbackKey = isPerfect
                ? "child_mnemo_table_feedback_ok"
                : "child_mnemo_table_feedback_retry"
            if isPerfect {
                MnemonicTableEngine.shared.recordRecallSuccess(
                    itemId: item.id,
                    correctCount: correct,
                    total: total
                )
            }
        }
    }
}
