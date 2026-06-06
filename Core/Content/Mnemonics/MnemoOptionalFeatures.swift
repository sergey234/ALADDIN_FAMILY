import SwiftUI

// MARK: - B14-T08 Memory Hero avatars

enum MnemoMemoryHeroChrome {
    static var isEnabled: Bool { MnemoFeatureFlags.memoryHeroAvatars }

    static func heroEmoji(for level: MnemonicSkillLevel) -> String {
        switch level {
        case .novice: return "🐣"
        case .apprentice: return "⭐"
        case .champion: return "🏆"
        }
    }

    static func heroLabelKey(for level: MnemonicSkillLevel) -> String {
        switch level {
        case .novice: return "child_mnemo_hero_novice"
        case .apprentice: return "child_mnemo_hero_apprentice"
        case .champion: return "child_mnemo_hero_champion"
        }
    }
}

// MARK: - B14-T11 Family Memory Challenge

struct MnemoFamilyMemoryChallengeCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showShare = false
    @State private var sharePayload = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_mnemo_family_challenge_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_mnemo_family_challenge_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.85))
            Button(localizationManager.localized("child_mnemo_family_challenge_cta")) {
                prepareSharePayload()
                showShare = true
            }
            .font(.system(size: 13, weight: .semibold))
            .buttonStyle(.borderedProminent)
            .tint(.mint)
            .accessibilityIdentifier("child_mnemo_family_challenge_cta")
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.mint.opacity(0.22)))
        .accessibilityIdentifier("child_mnemo_family_challenge_card")
        .sheet(isPresented: $showShare) {
            ShareSheet(activityItems: [sharePayload])
        }
    }

    private func prepareSharePayload() {
        let words = MnemonicBaselineAssessment.wordLocalizationKeys
            .shuffled()
            .prefix(MnemonicBaselineAssessment.wordCount)
            .map { localizationManager.localized($0) }
        sharePayload = String(
            format: localizationManager.localized("child_mnemo_family_challenge_share_body"),
            words.joined(separator: " · ")
        )
        MasterLogger.shared.business("MNEMO-B14-T11 family challenge share prepared words=5")
    }
}

// MARK: - B14-T12 Companion voice SRS reminder

struct MnemoCompanionSRSReminderCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("mnemo.companionVoiceReminder.optIn") private var optIn = false

    let dueCount: Int

    @ViewBuilder
    var body: some View {
        if dueCount > 0 {
            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("child_mnemo_companion_srs_title"))
                    .font(.system(size: 15, weight: .bold))
                    .foregroundColor(.white)
                Toggle(
                    localizationManager.localized("child_mnemo_companion_srs_opt_in"),
                    isOn: $optIn
                )
                .font(.system(size: 13, weight: .semibold))
                .tint(.cyan)
                if optIn {
                    Button(localizationManager.localized("child_mnemo_companion_srs_speak_cta")) {
                        speakReminder()
                    }
                    .font(.system(size: 13, weight: .semibold))
                    .buttonStyle(.bordered)
                    .accessibilityIdentifier("child_mnemo_companion_srs_speak_cta")
                }
            }
            .padding(14)
            .background(RoundedRectangle(cornerRadius: 14).fill(Color.cyan.opacity(0.18)))
            .accessibilityIdentifier("child_mnemo_companion_srs_card")
            .onAppear {
                if optIn { speakReminder() }
            }
        }
    }

    private func speakReminder() {
        let line = String(
            format: localizationManager.localized("child_mnemo_companion_srs_line"),
            dueCount
        )
        SoundEffectPlayer.shared.playVoicePrompt(line, languageCode: "ru-RU", priority: .medium)
        MasterLogger.shared.business("MNEMO-B14-T12 companion SRS voice due=\(dueCount)")
    }
}

// MARK: - B14-T13 Stories optional recall hook

struct MnemoStoriesRecallHookBanner: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let storyTitle: String
    var onRecallTapped: () -> Void

    @State private var feedbackKey: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_mnemo_stories_recall_title"))
                .font(.system(size: 14, weight: .bold))
            Text(localizationManager.localized("child_mnemo_stories_recall_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
            Button(localizationManager.localized("child_mnemo_stories_recall_cta")) {
                _ = MnemonicRewardBridge.awardRecallAttempt(itemId: "stories.recall.hook", attemptKey: storyTitle)
                feedbackKey = "child_mnemo_stories_recall_feedback"
                onRecallTapped()
            }
            .buttonStyle(.borderedProminent)
            .tint(.indigo)
            .accessibilityIdentifier("child_mnemo_stories_recall_cta")
            if let feedbackKey {
                Text(localizationManager.localized(feedbackKey))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.green)
            }
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))
        .accessibilityIdentifier("child_mnemo_stories_recall_banner")
    }
}

// MARK: - B14-T14 Advanced number pegs 15+

struct MnemoAdvancedNumberPegsCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("mnemo.advancedNumberPegs.optIn") private var optIn = false
    @State private var showSheet = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("child_mnemo_number_pegs_title"))
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            Text(localizationManager.localized("child_mnemo_number_pegs_subtitle"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.85))
            Toggle(
                localizationManager.localized("child_mnemo_number_pegs_opt_in"),
                isOn: $optIn
            )
            .font(.system(size: 13, weight: .semibold))
            .tint(.orange)
            if optIn {
                Button(localizationManager.localized("child_mnemo_number_pegs_cta")) {
                    showSheet = true
                }
                .font(.system(size: 13, weight: .semibold))
                .buttonStyle(.borderedProminent)
                .tint(.orange)
                .accessibilityIdentifier("child_mnemo_number_pegs_cta")
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.orange.opacity(0.2)))
        .accessibilityIdentifier("child_mnemo_number_pegs_card")
        .sheet(isPresented: $showSheet) {
            MnemoAdvancedNumberPegsSheet()
                .environmentObject(localizationManager)
        }
    }
}

struct MnemoAdvancedNumberPegsSheet: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        NavigationView {
            List(0..<10, id: \.self) { index in
                HStack(spacing: 12) {
                    Text("\(index)")
                        .font(.system(size: 18, weight: .bold))
                        .frame(width: 28)
                    Text(localizationManager.localized("child_mnemo_number_pegs_\(index)"))
                        .font(.system(size: 15, weight: .medium))
                }
            }
            .navigationTitle(localizationManager.localized("child_mnemo_number_pegs_sheet_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("child_interface_back")) {
                        dismiss()
                    }
                }
            }
        }
        .accessibilityIdentifier("child_mnemo_number_pegs_sheet")
    }
}
