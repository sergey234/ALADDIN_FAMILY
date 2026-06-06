import SwiftUI

/// Academy brand + semester progress + 4-phase dots + SRS due badge (extracted from ChildContentScreen).
struct MnemoAcademyBannerView: View {
    let ageGroup: ChildInterfaceScreen.AgeGroup
    @ObservedObject var localizationManager: LocalizationManager
    let activeSemester: MnemonicCurriculumSpine.Semester?
    let activeSemesterWeek: Int
    let dueTodayCount: Int
    let onOpenFirstDue: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(MnemoBrandChrome.brandTagline(ageGroup: ageGroup, localization: localizationManager))
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white)

            Text(localizationManager.localized(MnemoBrandChrome.promiseKey))
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.88))
                .accessibilityIdentifier("child_mnemo_brand_promise")

            Text(MnemoBrandChrome.brandAccent(ageGroup: ageGroup, localization: localizationManager))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.78))
                .accessibilityIdentifier("child_mnemo_brand_accent")

            if ageGroup == .teen, let examLine = MnemoBrandChrome.examHacksBannerLine(localization: localizationManager) {
                Text(examLine)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.orange.opacity(0.95))
                    .accessibilityIdentifier("child_mnemo_exam_hacks_banner")
            }

            Text(localizationManager.localized(MnemoBrandChrome.superpowerTitleKey))
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.yellow.opacity(0.95))

            Text(localizationManager.localized("child_mnemo_framework_aim"))
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.9))

            if let semester = activeSemester {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized(semester.titleKey))
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.white)
                    Text(localizationManager.localized(semester.subtitleKey))
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.82))
                    Text(
                        String(
                            format: localizationManager.localized("child_mnemo_semester_week_progress"),
                            activeSemesterWeek,
                            MnemonicCurriculumSpine.weeksPerSemester
                        )
                    )
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.yellow.opacity(0.95))
                }
                .accessibilityIdentifier("child_mnemo_semester_progress")
            }

            HStack(spacing: 8) {
                ForEach(MnemoAcademyPhase.catalogPhases) { phase in
                    VStack(spacing: 4) {
                        Circle()
                            .fill(Color.white.opacity(0.25))
                            .frame(width: 10, height: 10)
                            .accessibilityIdentifier("child_mnemo_phase_dot_\(phase.rawValue)")
                        Text(localizationManager.localized(phase.localizationKey))
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.white)
                            .lineLimit(1)
                            .minimumScaleFactor(0.7)
                            .accessibilityIdentifier("child_mnemo_phase_label_\(phase.rawValue)")
                    }
                    .frame(maxWidth: .infinity)
                }
            }

            if dueTodayCount > 0 {
                Button(action: onOpenFirstDue) {
                    Text(String(format: localizationManager.localized("child_mnemo_srs_due_today"), dueTodayCount))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.yellow)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("child_mnemo_srs_due_badge")
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.16))
        )
        .accessibilityIdentifier("child_mnemo_academy_banner")
    }
}
