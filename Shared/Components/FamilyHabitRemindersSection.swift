import SwiftUI

// MARK: - fws-02 Family habit reminders (parent templates → member local push)

struct FamilyHabitRemindersSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var service = FamilyHabitRemindersService.shared

    let members: [FamilyMemberData]

    @State private var draft = FamilyHabitRemindersConfig.empty
    @State private var allMinorsSelected = true
    @State private var isSaving = false
    @State private var errorMessage: String?
    @State private var savedMessage: String?

    private var canConfigure: Bool {
        FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members)
    }

    private var receivesReminders: Bool {
        FamilyHabitRemindersPolicy.shouldReceiveReminders(config: service.config, members: members)
    }

    private var minorMembers: [FamilyMemberData] {
        members.filter { $0.role == .child || $0.role == .teenager || $0.role == .elderly }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("family_habit_section_title"),
                systemImage: "bell.badge"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(localizationManager.localized("family_habit_section_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))
                .fixedSize(horizontal: false, vertical: true)

            if canConfigure {
                parentEditor
            } else if receivesReminders {
                memberStatus
            } else {
                Text(localizationManager.localized("family_habit_ask_parent"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.65))
            }

            Text(localizationManager.localized("family_habit_not_bedtime_hint"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.5))
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .successGreen)
        .accessibilityIdentifier("family_habit_reminders_section")
        .task {
            draft = service.config
            allMinorsSelected = service.config.memberIds.isEmpty
            await service.refreshFromServer(members: members)
            draft = service.config
        }
    }

    @ViewBuilder
    private var parentEditor: some View {
        ForEach(FamilyHabitPresetId.allCases) { preset in
            presetRow(preset)
        }

        Toggle(
            localizationManager.localized("family_habit_all_minors_toggle"),
            isOn: $allMinorsSelected
        )
        .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
        .onChange(of: allMinorsSelected) { enabled in
            if enabled {
                draft.memberIds = []
            } else {
                draft.memberIds = minorMembers.map(\.canonicalId)
            }
        }

        if let errorMessage {
            Text(errorMessage)
                .font(.caption)
                .foregroundColor(.dangerRed)
        }
        if let savedMessage {
            Text(savedMessage)
                .font(.caption)
                .foregroundColor(.successGreen)
        }

        Button {
            Task { await save() }
        } label: {
            Label(
                localizationManager.localized("family_habit_save_button"),
                systemImage: "checkmark.circle.fill"
            )
            .font(.subheadline.weight(.semibold))
        }
        .buttonStyle(.plain)
        .foregroundColor(.secondaryGold)
        .disabled(isSaving)
        .accessibilityIdentifier("family_habit_save_button")
    }

    @ViewBuilder
    private var memberStatus: some View {
        ForEach(FamilyHabitPresetId.allCases) { preset in
            let schedule = service.config.schedule(for: preset)
            if schedule.enabled {
                HStack {
                    Text(preset.emoji)
                    Text(localizationManager.localized(preset.titleKey))
                        .font(.subheadline)
                        .foregroundColor(.white)
                    Spacer()
                    Text(timeLabel(hour: schedule.hour, minute: schedule.minute))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
            }
        }
        Text(localizationManager.localized("family_habit_member_status_hint"))
            .font(.caption2)
            .foregroundColor(.white.opacity(0.6))
    }

    @ViewBuilder
    private func presetRow(_ preset: FamilyHabitPresetId) -> some View {
        let binding = Binding<FamilyHabitPresetSchedule>(
            get: { draft.schedule(for: preset) },
            set: { draft.setSchedule($0, for: preset) }
        )
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Toggle(isOn: Binding(
                get: { binding.wrappedValue.enabled },
                set: { newValue in
                    var value = binding.wrappedValue
                    value.enabled = newValue
                    binding.wrappedValue = value
                }
            )) {
                HStack(spacing: Spacing.xs) {
                    Text(preset.emoji)
                    Text(localizationManager.localized(preset.titleKey))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                }
            }
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))

            if binding.wrappedValue.enabled {
                HStack {
                    Text(localizationManager.localized("family_habit_time_label"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                    Stepper(
                        timeLabel(hour: binding.wrappedValue.hour, minute: binding.wrappedValue.minute),
                        onIncrement: { adjustTime(binding: binding, deltaMinutes: 15) },
                        onDecrement: { adjustTime(binding: binding, deltaMinutes: -15) }
                    )
                    .labelsHidden()
                    Text(timeLabel(hour: binding.wrappedValue.hour, minute: binding.wrappedValue.minute))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
            }
        }
        .padding(.vertical, Spacing.xxs)
    }

    private func timeLabel(hour: Int, minute: Int) -> String {
        String(format: "%02d:%02d", hour, minute)
    }

    private func adjustTime(binding: Binding<FamilyHabitPresetSchedule>, deltaMinutes: Int) {
        var value = binding.wrappedValue
        let total = value.hour * 60 + value.minute + deltaMinutes
        let wrapped = (total % (24 * 60) + (24 * 60)) % (24 * 60)
        value.hour = wrapped / 60
        value.minute = wrapped % 60
        binding.wrappedValue = value
    }

    @MainActor
    private func save() async {
        isSaving = true
        errorMessage = nil
        savedMessage = nil
        defer { isSaving = false }

        if allMinorsSelected {
            draft.memberIds = []
        }

        do {
            _ = await FamilyHabitRemindersScheduler.shared.requestAuthorizationIfNeeded()
            try await service.save(config: draft, members: members)
            savedMessage = localizationManager.localized("family_habit_saved")
            HapticFeedback.notification(.success)
        } catch {
            errorMessage = localizationManager.localized("family_habit_save_failed")
            HapticFeedback.notification(.error)
        }
    }
}
