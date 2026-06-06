import SwiftUI

/// Parent dashboard — 10 techniques × 4 mastery stages (B14-T03).
struct MnemoParentTechniqueMasteryView: View {
    let localizationManager: LocalizationManager
    let rows: [MnemoParentTechniqueMasteryRow]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("parent_dashboard_mnemo_technique_title"))
                .font(.system(size: 18, weight: .semibold))

            Text(localizationManager.localized("parent_dashboard_mnemo_technique_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.72))

            if rows.allSatisfy({ $0.successCount == 0 }) {
                Text(localizationManager.localized("parent_dashboard_mnemo_technique_empty"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
            } else {
                ForEach(rows) { row in
                    techniqueRow(row)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_mnemo_technique_breakdown")
    }

    private func techniqueRow(_ row: MnemoParentTechniqueMasteryRow) -> some View {
        HStack(alignment: .center, spacing: 10) {
            VStack(alignment: .leading, spacing: 6) {
                Text(localizationManager.localized(row.technique.localizationKey))
                    .font(.system(size: 13, weight: .semibold))
                    .lineLimit(2)
                    .minimumScaleFactor(0.85)

                HStack(spacing: 5) {
                    ForEach(0..<MnemonicTechniqueMastery.Stage.allCases.count, id: \.self) { index in
                        Circle()
                            .fill(
                                index <= row.stage.rawValue
                                    ? Color.purple.opacity(0.95)
                                    : Color.white.opacity(0.18)
                            )
                            .frame(width: 8, height: 8)
                    }
                }
                .accessibilityIdentifier("parent_dashboard_mnemo_technique_dots_\(row.technique.rawValue)")
            }

            Spacer(minLength: 8)

            VStack(alignment: .trailing, spacing: 4) {
                Text(localizationManager.localized(row.stage.localizationKey))
                    .font(.system(size: 11, weight: .semibold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.white.opacity(0.16))
                    .clipShape(Capsule())

                if row.successCount > 0 {
                    Text(
                        String(
                            format: localizationManager.localized("parent_dashboard_mnemo_technique_successes"),
                            row.successCount
                        )
                    )
                    .font(.system(size: 10, weight: .medium))
                    .foregroundColor(.white.opacity(0.65))
                }
            }
        }
        .padding(.vertical, 4)
        .accessibilityIdentifier("parent_dashboard_mnemo_technique_row_\(row.technique.rawValue)")
    }
}

struct MnemoParentTechniqueMasteryRow: Identifiable {
    let technique: MnemonicTechnique
    let stage: MnemonicTechniqueMastery.Stage
    let successCount: Int

    var id: String { technique.rawValue }
}

enum MnemoParentTechniqueMasterySnapshot {
    static func rows(childId: String? = nil) -> [MnemoParentTechniqueMasteryRow] {
        MnemonicTechniqueMastery.shared.masterySummary(childId: childId).map { item in
            MnemoParentTechniqueMasteryRow(
                technique: item.technique,
                stage: item.stage,
                successCount: item.count
            )
        }
    }
}
