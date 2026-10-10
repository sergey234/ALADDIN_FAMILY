import SwiftUI

// MARK: - fhc-05 Custom reminders under Medicine (Hybrid Variant 2)

struct FamilyHabitCustomRemindersBlock: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var custom: [FamilyHabitCustomReminder]
    var onChanged: (() -> Void)?

    @State private var editorDraft: FamilyHabitCustomReminder?
    @State private var isNewEditor = false
    @State private var limitMessage: String?

    private var sortedCustom: [FamilyHabitCustomReminder] {
        FamilyHabitCustomReminder.normalizedList(custom)
    }

    private var atLimit: Bool {
        sortedCustom.count >= FamilyHabitCustomReminder.maxPerFamily
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("family_habit_custom_section_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white)
                .accessibilityIdentifier("family_habit_custom_section_title")

            Text(localizationManager.localized("family_habit_custom_audience_hint"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.65))
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityIdentifier("family_habit_custom_audience_hint")

            if sortedCustom.isEmpty {
                Text(localizationManager.localized("family_habit_custom_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                    .accessibilityIdentifier("family_habit_custom_empty")
            } else {
                ForEach(Array(sortedCustom.enumerated()), id: \.element.id) { index, item in
                    customRow(item, index: index, total: sortedCustom.count)
                }
            }

            // fhc-06 — quick templates (prefill only; not the 4 system presets).
            if !atLimit {
                quickTemplateChips(openEditor: true)
            }

            if let limitMessage {
                Text(limitMessage)
                    .font(.caption2)
                    .foregroundColor(.orange.opacity(0.95))
                    .accessibilityIdentifier("family_habit_custom_limit_message")
            }

            Button {
                openNewEditor(template: nil)
            } label: {
                Label(
                    localizationManager.localized("family_habit_custom_add"),
                    systemImage: "plus.circle.fill"
                )
                .font(.subheadline.weight(.semibold))
            }
            .buttonStyle(.plain)
            .foregroundColor(atLimit ? .white.opacity(0.35) : .secondaryGold)
            .disabled(atLimit)
            .accessibilityIdentifier("family_habit_custom_add")
        }
        .padding(Spacing.s)
        .background(Color.white.opacity(0.06))
        .cornerRadius(CornerRadius.medium)
        .accessibilityIdentifier("family_habit_custom_block")
        .sheet(item: $editorDraft) { draft in
            FamilyHabitCustomEditorSheet(
                draft: draft,
                isNew: isNewEditor,
                onSave: { saved in
                    upsert(saved)
                    editorDraft = nil
                },
                onDelete: isNewEditor ? nil : {
                    delete(id: draft.id)
                    editorDraft = nil
                },
                onCancel: { editorDraft = nil }
            )
            .environmentObject(localizationManager)
        }
    }

    @ViewBuilder
    private func customRow(_ item: FamilyHabitCustomReminder, index: Int, total: Int) -> some View {
        HStack(alignment: .center, spacing: Spacing.s) {
            // fhc-16 — ▲▼ reorder (persist sort_order on save)
            if total > 1 {
                VStack(spacing: 2) {
                    Button {
                        moveCustom(id: item.id, direction: -1)
                    } label: {
                        Image(systemName: "chevron.up")
                            .font(.caption.weight(.bold))
                            .foregroundColor(index == 0 ? .white.opacity(0.25) : .secondaryGold)
                    }
                    .disabled(index == 0)
                    .accessibilityIdentifier("family_habit_custom_move_up_\(item.id)")

                    Button {
                        moveCustom(id: item.id, direction: 1)
                    } label: {
                        Image(systemName: "chevron.down")
                            .font(.caption.weight(.bold))
                            .foregroundColor(index >= total - 1 ? .white.opacity(0.25) : .secondaryGold)
                    }
                    .disabled(index >= total - 1)
                    .accessibilityIdentifier("family_habit_custom_move_down_\(item.id)")
                }
                .buttonStyle(.plain)
            }

            Button {
                isNewEditor = false
                editorDraft = item
            } label: {
                HStack(spacing: Spacing.xs) {
                    Text(item.emoji)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(item.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                            .lineLimit(1)
                        Text(item.scheduleSummaryLine(localization: localizationManager))
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.65))
                            .lineLimit(1)
                    }
                }
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("family_habit_custom_row_\(item.id)")

            Spacer(minLength: 0)

            Toggle(
                "",
                isOn: Binding(
                    get: { item.enabled },
                    set: { enabled in
                        var copy = custom
                        if let idx = copy.firstIndex(where: { $0.id == item.id }) {
                            copy[idx].enabled = enabled
                            custom = FamilyHabitCustomReminder.normalizedList(copy)
                            onChanged?()
                        }
                    }
                )
            )
            .labelsHidden()
            .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
            .accessibilityIdentifier("family_habit_custom_toggle_\(item.id)")
        }
        .padding(.vertical, 4)
    }

    private func moveCustom(id: String, direction: Int) {
        var list = FamilyHabitCustomReminder.normalizedList(custom)
        guard let idx = list.firstIndex(where: { $0.id == id }) else { return }
        let target = idx + direction
        guard list.indices.contains(target) else { return }
        list.swapAt(idx, target)
        for i in list.indices {
            list[i].sortOrder = i
        }
        custom = FamilyHabitCustomReminder.normalizedList(list)
        onChanged?()
        HapticFeedback.impact(.light)
    }

    @ViewBuilder
    private func quickTemplateChips(openEditor: Bool) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("family_habit_custom_templates_label"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.65))
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(FamilyHabitCustomQuickTemplate.allCases) { template in
                        Button {
                            if openEditor {
                                openNewEditor(template: template)
                            }
                        } label: {
                            HStack(spacing: 4) {
                                Text(template.emoji)
                                Text(localizationManager.localized(template.titleKey))
                                    .font(.caption.weight(.semibold))
                                    .lineLimit(1)
                            }
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color.secondaryGold.opacity(0.22))
                            .overlay(
                                Capsule()
                                    .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 1)
                            )
                            .clipShape(Capsule())
                            .foregroundColor(.white)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("family_habit_custom_tpl_\(template.rawValue)")
                    }
                }
            }
            .accessibilityIdentifier("family_habit_custom_templates")
        }
    }

    private func openNewEditor(template: FamilyHabitCustomQuickTemplate?) {
        if atLimit {
            limitMessage = localizationManager.localized("family_habit_custom_limit_reached")
            HapticFeedback.notification(.warning)
            return
        }
        limitMessage = nil
        isNewEditor = true
        var draft = FamilyHabitCustomReminder.prefill(mode: .onceDaily)
        template?.apply(to: &draft, localization: localizationManager)
        editorDraft = draft
        HapticFeedback.impact(.light)
    }

    private func upsert(_ item: FamilyHabitCustomReminder) {
        var copy = custom
        let normalized = item.clamped()
        guard !normalized.title.isEmpty else { return }
        if let idx = copy.firstIndex(where: { $0.id == normalized.id }) {
            copy[idx] = normalized
            FamilyHabitCustomAnalytics.log(.edit, id: normalized.id, mode: normalized.mode.rawValue)
        } else {
            guard copy.count < FamilyHabitCustomReminder.maxPerFamily else {
                limitMessage = localizationManager.localized("family_habit_custom_limit_reached")
                return
            }
            copy.append(normalized)
            FamilyHabitCustomAnalytics.log(.create, id: normalized.id, mode: normalized.mode.rawValue)
        }
        custom = FamilyHabitCustomReminder.normalizedList(copy)
        onChanged?()
        HapticFeedback.notification(.success)
    }

    private func delete(id: String) {
        custom = custom.filter { $0.id != id }
        FamilyHabitCustomAnalytics.log(.delete, id: id, mode: nil)
        onChanged?()
        HapticFeedback.impact(.medium)
    }
}

// MARK: - Editor sheet

struct FamilyHabitCustomEditorSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var draft: FamilyHabitCustomReminder
    let isNew: Bool
    let onSave: (FamilyHabitCustomReminder) -> Void
    let onDelete: (() -> Void)?
    let onCancel: () -> Void

    @State private var testPushMessage: String?
    @State private var titleError: String?

    init(
        draft: FamilyHabitCustomReminder,
        isNew: Bool,
        onSave: @escaping (FamilyHabitCustomReminder) -> Void,
        onDelete: (() -> Void)?,
        onCancel: @escaping () -> Void
    ) {
        _draft = State(initialValue: draft)
        self.isNew = isNew
        self.onSave = onSave
        self.onDelete = onDelete
        self.onCancel = onCancel
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    if isNew {
                        editorQuickTemplates
                    }
                    titleField
                    emojiChips
                    modePicker
                    scheduleEditor
                    if FamilyHabitDuePingFeature.isEnabled {
                        pingToggle
                    }
                    if draft.needsHealthDisclaimer {
                        Text(localizationManager.localized("family_habit_custom_health_disclaimer"))
                            .font(.caption2)
                            .foregroundColor(.orange.opacity(0.95))
                            .accessibilityIdentifier("family_habit_custom_health_disclaimer")
                    }
                    Text(localizationManager.localized("family_habit_custom_audience_hint"))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    testPushButton
                    if let testPushMessage {
                        Text(testPushMessage)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    if let onDelete {
                        Button(role: .destructive) {
                            onDelete()
                        } label: {
                            Text(localizationManager.localized("family_habit_custom_delete"))
                                .frame(maxWidth: .infinity)
                        }
                        .accessibilityIdentifier("family_habit_custom_delete")
                    }
                }
                .padding(Spacing.m)
            }
            .navigationTitle(
                localizationManager.localized(
                    isNew ? "family_habit_custom_editor_new" : "family_habit_custom_editor_edit"
                )
            )
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("family_habit_custom_cancel")) {
                        onCancel()
                    }
                    .accessibilityIdentifier("family_habit_custom_cancel")
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("family_habit_custom_save")) {
                        saveTapped()
                    }
                    .accessibilityIdentifier("family_habit_custom_save")
                }
            }
        }
    }

    private var editorQuickTemplates: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("family_habit_custom_templates_label"))
                .font(.caption)
                .foregroundColor(.secondary)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(FamilyHabitCustomQuickTemplate.allCases) { template in
                        Button {
                            template.apply(to: &draft, localization: localizationManager)
                            titleError = nil
                            HapticFeedback.impact(.light)
                        } label: {
                            HStack(spacing: 4) {
                                Text(template.emoji)
                                Text(localizationManager.localized(template.titleKey))
                                    .font(.caption.weight(.semibold))
                                    .lineLimit(1)
                            }
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color.accentColor.opacity(0.18))
                            .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("family_habit_custom_editor_tpl_\(template.rawValue)")
                    }
                }
            }
            .accessibilityIdentifier("family_habit_custom_editor_templates")
        }
    }

    private var titleField: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("family_habit_custom_title_label"))
                .font(.caption)
                .foregroundColor(.secondary)
            TextField(
                localizationManager.localized("family_habit_custom_title_placeholder"),
                text: $draft.title
            )
            .textFieldStyle(.roundedBorder)
            .accessibilityIdentifier("family_habit_custom_title_field")
            if let titleError {
                Text(titleError)
                    .font(.caption2)
                    .foregroundColor(.red)
            }
        }
    }

    private var emojiChips: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("family_habit_custom_emoji_label"))
                .font(.caption)
                .foregroundColor(.secondary)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(FamilyHabitCustomReminder.editorEmojiChoices, id: \.self) { emoji in
                        let selected = draft.emoji == emoji
                        Button {
                            draft.emoji = emoji
                        } label: {
                            Text(emoji)
                                .font(.title3)
                                .padding(8)
                                .background(selected ? Color.accentColor.opacity(0.25) : Color.secondary.opacity(0.12))
                                .cornerRadius(8)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .accessibilityIdentifier("family_habit_custom_emoji_chips")
        }
    }

    private var modePicker: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("family_habit_custom_mode_label"))
                .font(.caption)
                .foregroundColor(.secondary)
            HStack(spacing: 8) {
                modeChip(
                    title: localizationManager.localized("family_habit_custom_mode_once_daily"),
                    selected: draft.mode == .onceDaily
                ) {
                    draft = FamilyHabitCustomReminder.prefill(
                        mode: .onceDaily,
                        title: draft.title,
                        emoji: draft.emoji
                    ).withIdentity(from: draft)
                }
                modeChip(
                    title: localizationManager.localized("family_habit_custom_mode_window"),
                    selected: draft.mode == .window
                ) {
                    draft = FamilyHabitCustomReminder.prefill(
                        mode: .window,
                        title: draft.title,
                        emoji: draft.emoji
                    ).withIdentity(from: draft)
                }
                modeChip(
                    title: localizationManager.localized("family_habit_custom_mode_once_at"),
                    selected: draft.mode == .onceAt
                ) {
                    draft = FamilyHabitCustomReminder.prefill(
                        mode: .onceAt,
                        title: draft.title,
                        emoji: draft.emoji
                    ).withIdentity(from: draft)
                }
            }
        }
    }

    private func modeChip(title: String, selected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(selected ? Color.accentColor.opacity(0.3) : Color.secondary.opacity(0.12))
                .foregroundColor(.primary)
                .cornerRadius(8)
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private var scheduleEditor: some View {
        switch draft.mode {
        case .onceDaily:
            HStack {
                Text(localizationManager.localized("family_habit_time_label"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Stepper(
                    timeLabel(hour: draft.hour, minute: draft.minute),
                    onIncrement: { adjustDaily(delta: 15) },
                    onDecrement: { adjustDaily(delta: -15) }
                )
                .labelsHidden()
                Text(timeLabel(hour: draft.hour, minute: draft.minute))
                    .font(.caption.monospacedDigit().weight(.semibold))
            }
            .accessibilityIdentifier("family_habit_custom_once_daily_time")
        case .onceAt:
            VStack(alignment: .leading, spacing: 8) {
                DatePicker(
                    localizationManager.localized("family_habit_custom_once_at_picker"),
                    selection: Binding(
                        get: {
                            draft.fireAtDate
                                ?? Calendar.current.date(byAdding: .hour, value: 1, to: Date())
                                ?? Date()
                        },
                        set: { draft.setFireAtDate($0) }
                    ),
                    in: Date()...,
                    displayedComponents: [.date, .hourAndMinute]
                )
                .accessibilityIdentifier("family_habit_custom_once_at_picker")
                if draft.onceAtIsPast {
                    Text(localizationManager.localized("family_habit_custom_once_at_past"))
                        .font(.caption2)
                        .foregroundColor(.orange)
                        .accessibilityIdentifier("family_habit_custom_once_at_past")
                }
            }
        case .window:
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("family_habit_water_interval_label"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                customIntervalChips
                windowTimeRow(
                    label: localizationManager.localized("family_habit_water_from_label"),
                    hour: draft.hour,
                    minute: draft.minute,
                    end: false
                )
                windowTimeRow(
                    label: localizationManager.localized("family_habit_water_until_label"),
                    hour: draft.endHour,
                    minute: draft.endMinute,
                    end: true
                )
            }
            .accessibilityIdentifier("family_habit_custom_window_editor")
        }
    }

    private var customIntervalChips: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(FamilyHabitCustomInterval.allCases) { option in
                    let selection = FamilyHabitCustomInterval.selection(for: draft.intervalMinutes)
                    let selected = !selection.isCustom && selection.chip == option
                    Button {
                        draft.setIntervalMinutes(option.rawValue)
                    } label: {
                        Text(localizationManager.localized(option.labelKey))
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(selected ? Color.accentColor.opacity(0.3) : Color.secondary.opacity(0.12))
                            .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .accessibilityIdentifier("family_habit_custom_interval_chips")
    }

    private var pingToggle: some View {
        Toggle(isOn: $draft.pingUntilDone) {
            VStack(alignment: .leading, spacing: 2) {
                Text(localizationManager.localized("family_habit_ping_toggle"))
                    .font(.caption.weight(.semibold))
                Text(localizationManager.localized("family_habit_ping_warning"))
                    .font(.caption2)
                    .foregroundColor(.orange.opacity(0.9))
            }
        }
        .accessibilityIdentifier("family_habit_custom_ping_toggle")
    }

    private var testPushButton: some View {
        Button {
            Task { await fireTestPush() }
        } label: {
            Label(
                localizationManager.localized("family_habit_custom_test_push"),
                systemImage: "bell.badge"
            )
            .font(.subheadline.weight(.semibold))
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
        .accessibilityIdentifier("family_habit_custom_test_push")
    }

    private func windowTimeRow(label: String, hour: Int, minute: Int, end: Bool) -> some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Stepper(
                timeLabel(hour: hour, minute: minute),
                onIncrement: { adjustWindow(delta: 15, end: end) },
                onDecrement: { adjustWindow(delta: -15, end: end) }
            )
            .labelsHidden()
            Text(timeLabel(hour: hour, minute: minute))
                .font(.caption.monospacedDigit().weight(.semibold))
        }
    }

    private func adjustDaily(delta: Int) {
        let total = draft.hour * 60 + draft.minute + delta
        let wrapped = (total % (24 * 60) + (24 * 60)) % (24 * 60)
        draft.hour = wrapped / 60
        draft.minute = wrapped % 60
    }

    private func adjustWindow(delta: Int, end: Bool) {
        if end {
            let total = draft.endHour * 60 + draft.endMinute + delta
            let wrapped = (total % (24 * 60) + (24 * 60)) % (24 * 60)
            draft.endHour = wrapped / 60
            draft.endMinute = wrapped % 60
        } else {
            adjustDaily(delta: delta)
        }
    }

    private func timeLabel(hour: Int, minute: Int) -> String {
        String(format: "%02d:%02d", hour, minute)
    }

    private func saveTapped() {
        var normalized = draft.clamped()
        if normalized.title.isEmpty {
            titleError = localizationManager.localized("family_habit_custom_title_required")
            return
        }
        if normalized.mode == .onceAt, normalized.fireAtDate == nil {
            titleError = localizationManager.localized("family_habit_custom_once_at_needs_date")
            return
        }
        titleError = nil
        onSave(normalized)
    }

    @MainActor
    private func fireTestPush() async {
        var sample = draft.clamped()
        if sample.title.isEmpty {
            sample.title = localizationManager.localized("family_habit_custom_title_placeholder")
        }
        await FamilyHabitRemindersScheduler.shared.fireCustomTestNotification(for: sample)
        testPushMessage = localizationManager.localized("family_habit_custom_test_push_sent")
        HapticFeedback.notification(.success)
    }
}

private extension FamilyHabitCustomReminder {
    /// Keep id / enabled / ping / sort when switching mode prefills.
    func withIdentity(from other: FamilyHabitCustomReminder) -> FamilyHabitCustomReminder {
        var copy = self
        copy.id = other.id
        copy.enabled = other.enabled
        copy.pingUntilDone = other.pingUntilDone
        copy.pingIntervalMinutes = other.pingIntervalMinutes
        copy.pingMaxPerDay = other.pingMaxPerDay
        copy.sortOrder = other.sortOrder
        if mode == .onceAt, fireAt == nil, let keep = other.fireAt {
            copy.fireAt = keep
        }
        copy.modeRecognized = true
        copy.unrecognizedModeRaw = nil
        return copy.clamped()
    }
}
