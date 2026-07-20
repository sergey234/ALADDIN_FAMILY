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
    @State private var isSectionExpanded = false
    @State private var waterDetailsExpanded = true
    @State private var showMomentsSheet = false
    @State private var medalsMaster = HabitMedalSourcesSettings.masterEnabled
    @State private var medalWater = HabitMedalSourcesSettings.isSourceEnabled("water")
    @State private var medalMedicine = HabitMedalSourcesSettings.isSourceEnabled("medicine")

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
        VStack(alignment: .leading, spacing: 0) {
            sectionHeader

            if isSectionExpanded {
                VStack(alignment: .leading, spacing: Spacing.s) {
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
                .padding(.top, Spacing.s)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .successGreen)
        .accessibilityIdentifier("family_habit_reminders_section")
        .sheet(isPresented: $showMomentsSheet) {
            FamilyMomentsListSheet()
                .environmentObject(localizationManager)
        }
        .task {
            draft = service.config
            allMinorsSelected = service.config.memberIds.isEmpty
            waterDetailsExpanded = draft.schedule(for: .water).enabled
            await service.refreshFromServer(members: members)
            draft = service.config
            allMinorsSelected = service.config.memberIds.isEmpty
        }
    }

    private var sectionHeader: some View {
        Button {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                isSectionExpanded.toggle()
            }
            HapticFeedback.impact(.light)
        } label: {
            HStack(alignment: .top, spacing: Spacing.m) {
                Image(systemName: "bell.badge")
                    .font(.title3)
                    .foregroundColor(.secondaryGold)
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_habit_section_title"))
                        .font(.headline)
                        .foregroundColor(.white)
                    Text(localizationManager.localized("family_habit_section_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
                Image(systemName: isSectionExpanded ? "chevron.up" : "chevron.down")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.7))
            }
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("family_habit_section_header")
    }

    @ViewBuilder
    private var parentEditor: some View {
        ForEach(FamilyHabitPresetId.allCases) { preset in
            presetRow(preset)
        }

        Button {
            showMomentsSheet = true
        } label: {
            Label(
                localizationManager.localized("family_moments_title"),
                systemImage: "photo.on.rectangle.angled"
            )
            .font(.subheadline.weight(.semibold))
        }
        .buttonStyle(.plain)
        .foregroundColor(.secondaryGold)
        .accessibilityIdentifier("family_moments_open")

        VStack(alignment: .leading, spacing: 8) {
            Toggle(
                localizationManager.localized("family_habit_medals_master"),
                isOn: $medalsMaster
            )
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
            .onChange(of: medalsMaster) { HabitMedalSourcesSettings.masterEnabled = $0 }
            if medalsMaster {
                Toggle(
                    localizationManager.localized("family_habit_medals_water"),
                    isOn: $medalWater
                )
                .onChange(of: medalWater) { HabitMedalSourcesSettings.setSourceEnabled("water", $0) }
                Toggle(
                    localizationManager.localized("family_habit_medals_medicine"),
                    isOn: $medalMedicine
                )
                .onChange(of: medalMedicine) { HabitMedalSourcesSettings.setSourceEnabled("medicine", $0) }
            }
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
                HStack(alignment: .top) {
                    Text(preset.emoji)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(localizationManager.localized(preset.titleKey))
                            .font(.subheadline)
                            .foregroundColor(.white)
                        if preset == .water {
                            Text(schedule.waterSummaryLine(localization: localizationManager))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.7))
                        }
                    }
                    Spacer()
                    Button {
                        Task { await markDone(preset: preset) }
                    } label: {
                        Text(localizationManager.localized("family_habit_done"))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("family_habit_done_\(preset.rawValue)")
                    if preset != .water {
                        Text(timeLabel(hour: schedule.hour, minute: schedule.minute))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                    }
                }
            }
        }
        Text(localizationManager.localized("family_habit_member_status_hint"))
            .font(.caption2)
            .foregroundColor(.white.opacity(0.6))
    }

    @MainActor
    private func markDone(preset: FamilyHabitPresetId) async {
        let result = await FamilyHabitRemindersScheduler.shared.handleDone(presetRaw: preset.rawValue)
        if result.applied {
            savedMessage = localizationManager.localized("family_habit_done_rewarded")
            HapticFeedback.notification(.success)
        } else {
            savedMessage = localizationManager.localized("family_habit_done")
        }
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
                    if preset == .water {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            waterDetailsExpanded = newValue
                        }
                    }
                }
            )) {
                HStack(spacing: Spacing.xs) {
                    Text(preset.emoji)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(localizationManager.localized(preset.titleKey))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        if preset == .water, binding.wrappedValue.enabled, !waterDetailsExpanded {
                            Text(binding.wrappedValue.waterSummaryLine(localization: localizationManager))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.65))
                        }
                    }
                }
            }
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))

            if binding.wrappedValue.enabled {
                if preset == .water {
                    waterExpandedEditor(binding: binding)
                } else {
                    simpleTimeRow(binding: binding)
                }
                if preset == .medicine {
                    Text(localizationManager.localized("family_habit_medicine_disclaimer"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.65))
                        .accessibilityIdentifier("family_habit_medicine_disclaimer")
                }
                duePingEditor(binding: binding)
            }
        }
        .padding(.vertical, Spacing.xxs)
    }

    @ViewBuilder
    private func waterExpandedEditor(binding: Binding<FamilyHabitPresetSchedule>) -> some View {
        Button {
            withAnimation(.easeInOut(duration: 0.2)) {
                waterDetailsExpanded.toggle()
            }
        } label: {
            HStack {
                Text(localizationManager.localized("family_habit_water_details_toggle"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.85))
                Spacer()
                Image(systemName: waterDetailsExpanded ? "chevron.up" : "chevron.down")
                    .font(.caption2.weight(.semibold))
                    .foregroundColor(.white.opacity(0.6))
            }
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("family_habit_water_details_toggle")

        if waterDetailsExpanded {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("family_habit_water_liters_label"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                litersPicker(binding: binding)

                Text(localizationManager.localized("family_habit_water_interval_label"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                intervalPicker(binding: binding)

                timeWindowRow(
                    labelKey: "family_habit_water_from_label",
                    hour: Binding(
                        get: { binding.wrappedValue.hour },
                        set: { h in
                            var v = binding.wrappedValue
                            v.hour = h
                            binding.wrappedValue = v
                        }
                    ),
                    minute: Binding(
                        get: { binding.wrappedValue.minute },
                        set: { m in
                            var v = binding.wrappedValue
                            v.minute = m
                            binding.wrappedValue = v
                        }
                    ),
                    binding: binding
                )

                timeWindowRow(
                    labelKey: "family_habit_water_until_label",
                    hour: Binding(
                        get: { binding.wrappedValue.endHour },
                        set: { h in
                            var v = binding.wrappedValue
                            v.endHour = h
                            binding.wrappedValue = v
                        }
                    ),
                    minute: Binding(
                        get: { binding.wrappedValue.endMinute },
                        set: { m in
                            var v = binding.wrappedValue
                            v.endMinute = m
                            binding.wrappedValue = v
                        }
                    ),
                    binding: binding,
                    endWindow: true
                )

                // p2-pol — Planwoo-lite slot chips (visual only)
                let slots = binding.wrappedValue.waterNotificationSlots()
                if !slots.isEmpty {
                    Text(localizationManager.localized("family_habit_water_slots_label"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 6) {
                            ForEach(Array(slots.enumerated()), id: \.offset) { _, slot in
                                Text(timeLabel(hour: slot.hour, minute: slot.minute))
                                    .font(.caption2.monospacedDigit().weight(.semibold))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 6)
                                    .background(Color.secondaryGold.opacity(0.22))
                                    .overlay(
                                        Capsule()
                                            .stroke(Color.secondaryGold.opacity(0.45), lineWidth: 1)
                                    )
                                    .clipShape(Capsule())
                                    .foregroundColor(.white)
                            }
                        }
                    }
                    .accessibilityIdentifier("family_habit_water_slot_chips")
                }
            }
            .padding(Spacing.s)
            .background(Color.white.opacity(0.06))
            .cornerRadius(CornerRadius.medium)
        }
    }

    private func litersPicker(binding: Binding<FamilyHabitPresetSchedule>) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.xs) {
                ForEach(FamilyHabitWaterDailyLiters.allCases) { option in
                    let selected = FamilyHabitWaterDailyLiters.nearest(binding.wrappedValue.dailyLiters) == option
                    Button {
                        var v = binding.wrappedValue
                        v.dailyLiters = option.rawValue
                        binding.wrappedValue = v
                    } label: {
                        Text(localizationManager.localized(option.labelKey))
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(selected ? Color.secondaryGold.opacity(0.35) : Color.white.opacity(0.08))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .accessibilityIdentifier("family_habit_water_liters_picker")
    }

    private func intervalPicker(binding: Binding<FamilyHabitPresetSchedule>) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: Spacing.xs) {
                ForEach(FamilyHabitWaterInterval.allCases) { option in
                    let selected = FamilyHabitWaterInterval.nearest(binding.wrappedValue.intervalMinutes) == option
                    Button {
                        var v = binding.wrappedValue
                        v.intervalMinutes = option.rawValue
                        binding.wrappedValue = v
                    } label: {
                        Text(localizationManager.localized(option.labelKey))
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(selected ? Color.secondaryGold.opacity(0.35) : Color.white.opacity(0.08))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .accessibilityIdentifier("family_habit_water_interval_picker")
    }

    private func timeWindowRow(
        labelKey: String,
        hour: Binding<Int>,
        minute: Binding<Int>,
        binding: Binding<FamilyHabitPresetSchedule>,
        endWindow: Bool = false
    ) -> some View {
        HStack {
            Text(localizationManager.localized(labelKey))
                .font(.caption)
                .foregroundColor(.white.opacity(0.7))
            Spacer()
            Stepper(
                timeLabel(hour: hour.wrappedValue, minute: minute.wrappedValue),
                onIncrement: {
                    if endWindow {
                        adjustEndTime(binding: binding, deltaMinutes: 15)
                    } else {
                        adjustTime(binding: binding, deltaMinutes: 15)
                    }
                },
                onDecrement: {
                    if endWindow {
                        adjustEndTime(binding: binding, deltaMinutes: -15)
                    } else {
                        adjustTime(binding: binding, deltaMinutes: -15)
                    }
                }
            )
            .labelsHidden()
            Text(timeLabel(hour: hour.wrappedValue, minute: minute.wrappedValue))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)
        }
    }

    private func simpleTimeRow(binding: Binding<FamilyHabitPresetSchedule>) -> some View {
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

    /// p1-7c — Due-ping toggle (requires feature flag; water stays default OFF in model).
    @ViewBuilder
    private func duePingEditor(binding: Binding<FamilyHabitPresetSchedule>) -> some View {
        if FamilyHabitDuePingFeature.isEnabled {
            Toggle(isOn: Binding(
                get: { binding.wrappedValue.pingUntilDone },
                set: { newValue in
                    var value = binding.wrappedValue
                    value.pingUntilDone = newValue
                    binding.wrappedValue = value
                }
            )) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(localizationManager.localized("family_habit_ping_toggle"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.white.opacity(0.9))
                    Text(localizationManager.localized("family_habit_ping_warning"))
                        .font(.caption2)
                        .foregroundColor(.orange.opacity(0.9))
                }
            }
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
            .accessibilityIdentifier("family_habit_ping_until_done")
        }
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

    private func adjustEndTime(binding: Binding<FamilyHabitPresetSchedule>, deltaMinutes: Int) {
        var value = binding.wrappedValue
        let total = value.endHour * 60 + value.endMinute + deltaMinutes
        let wrapped = (total % (24 * 60) + (24 * 60)) % (24 * 60)
        value.endHour = wrapped / 60
        value.endMinute = wrapped % 60
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
