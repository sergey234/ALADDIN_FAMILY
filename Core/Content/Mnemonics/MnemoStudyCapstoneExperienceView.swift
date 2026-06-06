import SwiftUI

/// study.26 — pick topic → teach-back 3 min → Champion unlock (B12-T05).
struct MnemoStudyCapstoneExperienceView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let item: ContentItem
    let onComplete: () async -> Void

    private enum Phase {
        case pickTopic
        case prepare
        case teachBack
        case reward
    }

    @State private var phase: Phase = .pickTopic
    @State private var selectedTopicIndex: Int?
    @State private var secondsRemaining = MnemonicCapstoneStore.teachBackDurationSeconds
    @State private var teachBackElapsed = 0

    private let ticker = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("child_mnemo_capstone_title"))
                .font(.system(size: 17, weight: .bold))

            switch phase {
            case .pickTopic:
                topicPickerSection
            case .prepare:
                prepareSection
            case .teachBack:
                teachBackSection
            case .reward:
                rewardSection
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white))
        .onReceive(ticker) { _ in
            guard phase == .teachBack else { return }
            if secondsRemaining > 0 {
                secondsRemaining -= 1
                teachBackElapsed += 1
            } else {
                finishCapstone()
            }
        }
        .accessibilityIdentifier("child_mnemo_capstone_experience")
    }

    private var topicPickerSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_capstone_subtitle"))
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)

            Text(localizationManager.localized("child_mnemo_capstone_topic_picker"))
                .font(.system(size: 13, weight: .semibold))

            ForEach(Array(MnemonicCapstoneStore.topicLocalizationKeys.enumerated()), id: \.offset) { index, key in
                Button {
                    selectedTopicIndex = index
                } label: {
                    HStack {
                        Text(localizationManager.localized(key))
                            .font(.system(size: 14, weight: .semibold))
                            .multilineTextAlignment(.leading)
                        Spacer()
                        if selectedTopicIndex == index {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.purple)
                        }
                    }
                    .padding(10)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(selectedTopicIndex == index ? Color.purple.opacity(0.12) : Color.gray.opacity(0.08))
                    )
                }
                .buttonStyle(.plain)
            }

            Button(localizationManager.localized("child_interface_done")) {
                guard selectedTopicIndex != nil else { return }
                phase = .prepare
            }
            .buttonStyle(.borderedProminent)
            .disabled(selectedTopicIndex == nil)
            .accessibilityIdentifier("child_mnemo_capstone_topic_confirm")
        }
    }

    private var prepareSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let selectedTopicIndex {
                Text(localizationManager.localized(MnemonicCapstoneStore.topicLocalizationKeys[selectedTopicIndex]))
                    .font(.system(size: 16, weight: .bold))
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color.indigo.opacity(0.08)))
            }

            Text(localizationManager.localized("child_mnemo_capstone_prepare_hint"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_study_anchor_template"),
                    localizationManager.localized(MnemonicStudyTechniqueMap.technique(for: item.id).localizationKey),
                    MnemonicStudyTechniqueMap.journeyStop(for: item.id),
                    localizationManager.localized("child_mnemo_capstone_prepare_anchor")
                )
            )
            .font(.system(size: 14))
            .padding(12)
            .background(RoundedRectangle(cornerRadius: 10).fill(Color.blue.opacity(0.08)))

            HStack {
                Button(localizationManager.localized("child_interface_back")) {
                    phase = .pickTopic
                }
                .buttonStyle(.bordered)

                Spacer()

                Button(localizationManager.localized("child_mnemo_capstone_start_teachback")) {
                    secondsRemaining = MnemonicCapstoneStore.teachBackDurationSeconds
                    teachBackElapsed = 0
                    phase = .teachBack
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }

    private var teachBackSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_capstone_teach_title"))
                .font(.system(size: 15, weight: .semibold))

            Text(
                String(
                    format: localizationManager.localized("child_mnemo_capstone_timer"),
                    secondsRemaining / 60,
                    secondsRemaining % 60
                )
            )
            .font(.system(size: 18, weight: .bold))
            .foregroundColor(.purple)
            .accessibilityIdentifier("child_mnemo_capstone_timer")

            Text(localizationManager.localized("child_mnemo_capstone_teach_hint"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Button(localizationManager.localized("child_mnemo_capstone_finish_early")) {
                finishCapstone()
            }
            .buttonStyle(.borderedProminent)
            .disabled(teachBackElapsed < MnemonicCapstoneStore.minimumTeachBackSeconds)
            .accessibilityIdentifier("child_mnemo_capstone_finish_early")
        }
    }

    private var rewardSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("child_mnemo_capstone_complete_title"))
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.green)

            Text(localizationManager.localized("child_mnemo_capstone_champion_unlock"))
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.purple)

            Text(localizationManager.localized(MnemonicRewardEvent.capstoneComplete.localizationKey))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.secondary)

            Button(localizationManager.localized("child_interface_done")) {
                Task { await onComplete() }
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private func finishCapstone() {
        guard phase == .teachBack, let topicIndex = selectedTopicIndex else { return }
        let childId = MnemonicBaselineAssessment.activeChildId()
        MnemonicCapstoneStore.shared.recordCompletion(
            topicIndex: topicIndex,
            teachBackSeconds: teachBackElapsed,
            childId: childId
        )
        MnemonicSkillTracker.shared.recordCapstoneCompleted(childId: childId)
        MnemonicSRSStore.shared.recordSuccess(itemId: item.id)
        MnemonicRewardBridge.award(.capstoneComplete, itemId: item.id)
        MnemonicSkillTracker.shared.recordAnchorPlaced(count: 3, childId: childId)
        phase = .reward
        SoundEffectPlayer.shared.play(.success, priority: .high)
    }
}
