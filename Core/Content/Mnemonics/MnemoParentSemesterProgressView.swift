import SwiftUI

/// Parent widget — «до следующего семестра: N%» from `SemesterGate` (B14-T16).
struct MnemoParentSemesterProgressView: View {
    let localizationManager: LocalizationManager
    let progress: MnemonicCurriculumSpine.NextSemesterUnlockProgress

    private var progressFraction: Double {
        let threshold = max(1, progress.gate.unlockThresholdPercent)
        return min(1.0, Double(progress.gate.priorMasteryPercent) / Double(threshold))
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("parent_dashboard_mnemo_semester_progress_title"))
                .font(.system(size: 18, weight: .semibold))

            if progress.allSemestersUnlocked {
                Text(localizationManager.localized("parent_dashboard_mnemo_semester_progress_complete"))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.82))
            } else if let nextSemester = MnemonicCurriculumSpine.shared.semester(at: progress.nextSemesterIndex) {
                Text(
                    String(
                        format: localizationManager.localized("parent_dashboard_mnemo_semester_progress_headline"),
                        progress.gate.priorMasteryPercent
                    )
                )
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundColor(.yellow.opacity(0.95))

                Text(
                    String(
                        format: localizationManager.localized("parent_dashboard_mnemo_semester_progress_next_label"),
                        localizationManager.localized(nextSemester.titleKey)
                    )
                )
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white.opacity(0.78))

                ProgressView(value: progressFraction)
                    .tint(.yellow)

                Text(
                    String(
                        format: localizationManager.localized("parent_dashboard_mnemo_semester_progress_threshold"),
                        progress.gate.priorMasteryPercent,
                        progress.gate.unlockThresholdPercent
                    )
                )
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.white.opacity(0.72))

                if progress.gate.remainingPercent > 0 {
                    Text(
                        String(
                            format: localizationManager.localized("parent_dashboard_mnemo_semester_progress_remaining"),
                            progress.gate.remainingPercent
                        )
                    )
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.orange.opacity(0.9))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(10)
        .background(Color.white.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .accessibilityIdentifier("parent_dashboard_mnemo_semester_progress")
    }
}
