import SwiftUI
import UIKit
import Contacts
import ContactsUI

/// Unified «Звонки» hub — call memory cards (not carrier line recording).
/// Apple-safe: mic/speaker ambient + after-call notes only. No PSTN tap.
struct CallsHubScreen: View {
    enum CallSaveMode: String, CaseIterable, Identifiable {
        case outgoingOnly = "a"
        case afterOnly = "b"
        case hybrid = "c"
        var id: String { rawValue }
    }

    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @ObservedObject private var lifecycle = CallsLifecycleService.shared
    @Environment(\.dismiss) private var dismiss

    @State private var sessions: [CallSession] = []
    @State private var showPrep = false
    @State private var showAfter = false
    @State private var showPaywallHint = false
    @State private var showContactPicker = false
    @State private var draftGoal = ""
    @State private var draftPhone = ""
    @State private var wantMicRecord = true
    @State private var consentChecked = false
    @State private var prepNeedPhoneHint = false
    @State private var saveMode: CallSaveMode = .hybrid
    @State private var phoneOpenMessage: String?
    @AppStorage(AppConfig.UserDefaultsKeys.postCallSafetyPromptEnabled)
    private var postCallSafetyPromptEnabled = true
    @AppStorage("calls_hub_preferred_save_mode")
    private var preferredSaveModeRaw: String = CallSaveMode.hybrid.rawValue

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .shield)
                VStack(spacing: Spacing.m) {
                    safetyToggleCard
                    content
                }

                // Large visible CTA — center-bottom (not only tiny + in nav)
                if CallsAccessPolicy.isAvailable() {
                    VStack {
                        Spacer()
                        Button(action: openPrimaryAction) {
                            HStack(spacing: 10) {
                                Image(systemName: "plus.circle.fill")
                                    .font(.title2)
                                Text(localizationManager.localized("calls_hub_fab_label"))
                                    .font(.headline.weight(.semibold))
                            }
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.l)
                            .padding(.vertical, Spacing.m)
                            .background(Color.secondaryGold)
                            .clipShape(Capsule())
                            .shadow(color: .black.opacity(0.35), radius: 10, y: 4)
                        }
                        .accessibilityIdentifier("calls_hub_fab")
                        .padding(.bottom, Spacing.l)
                    }
                }
            }
            .navigationBarTitle(localizationManager.localized("calls_hub_title"), displayMode: .inline)
            .navigationBarItems(
                leading: Button(action: { dismiss() }) {
                    Text(localizationManager.localized("common_close"))
                },
                trailing: Button(action: openPrimaryAction) {
                    Image(systemName: "plus.circle.fill")
                        .foregroundColor(.secondaryGold)
                        .font(.title3)
                }
                .accessibilityIdentifier("calls_hub_prep_button")
            )
            .onAppear {
                if let m = CallSaveMode(rawValue: preferredSaveModeRaw) {
                    saveMode = m
                }
                reload()
            }
            .onChange(of: lifecycle.showAfterSheet) { open in
                if open { showAfter = true }
            }
            .onChange(of: saveMode) { mode in
                preferredSaveModeRaw = mode.rawValue
                print("📞 CallsHub: saveMode=\(mode.rawValue)")
            }
            .sheet(isPresented: $showPrep) { prepSheet }
            .sheet(isPresented: $showAfter, onDismiss: {
                lifecycle.showAfterSheet = false
            }) {
                CallsAfterMemorySheet()
                    .environmentObject(localizationManager)
                    .environmentObject(navigationManager)
            }
            // Contact picker at hub level — nested sheet inside prep was a white blank page.
            .sheet(isPresented: $showContactPicker) {
                CallsContactPickerView(
                    onSelect: { contact in
                        applyContact(contact)
                        showContactPicker = false
                    },
                    onCancel: { showContactPicker = false }
                )
            }
            .alert(
                localizationManager.localized("calls_paywall_title"),
                isPresented: $showPaywallHint
            ) {
                Button(localizationManager.localized("calls_paywall_open_tariffs")) {
                    dismiss()
                    navigationManager.navigateTo(.tariffs)
                }
                Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            } message: {
                Text(localizationManager.localized("calls_paywall_body"))
            }
            .alert(
                localizationManager.localized("calls_hub_title"),
                isPresented: Binding(
                    get: { phoneOpenMessage != nil },
                    set: { if !$0 { phoneOpenMessage = nil } }
                )
            ) {
                Button(localizationManager.localized("common_ok"), role: .cancel) {
                    phoneOpenMessage = nil
                }
            } message: {
                Text(phoneOpenMessage ?? "")
            }
            .withToast()
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    private func openPrimaryAction() {
        guard CallsAccessPolicy.isAvailable() else {
            showPaywallHint = true
            return
        }
        switch saveMode {
        case .afterOnly:
            showAfter = true
        case .outgoingOnly, .hybrid:
            showPrep = true
        }
    }

    private var safetyToggleCard: some View {
        Toggle(isOn: $postCallSafetyPromptEnabled) {
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("calls_safety_prompt_toggle"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)
                    .allowsTightening(true)
                Text(localizationManager.localized("calls_safety_prompt_toggle_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(1)
                    .minimumScaleFactor(0.75)
                    .allowsTightening(true)
            }
        }
        .tint(.secondaryGold)
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .padding(.horizontal, Spacing.m)
        .accessibilityIdentifier("calls_hub_safety_prompt_toggle")
        .accessibilityHint(localizationManager.localized("calls_safety_prompt_toggle_a11y_hint"))
    }

    private var content: some View {
        Group {
            if !CallsAccessPolicy.isAvailable() {
                lockedState
            } else if sessions.isEmpty {
                emptyState
            } else {
                list
            }
        }
    }

    private var lockedState: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("calls_paywall_title"))
                .font(.title3.bold())
                .foregroundColor(.white)
            Text(localizationManager.localized("calls_paywall_body"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))
                .multilineTextAlignment(.center)
            Button(localizationManager.localized("calls_paywall_open_tariffs")) {
                dismiss()
                navigationManager.navigateTo(.tariffs)
            }
            .buttonStyle(.borderedProminent)
            .tint(.secondaryGold)
        }
        .padding(Spacing.l)
    }

    private var emptyState: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("calls_hub_empty_title"))
                    .font(.title3.bold())
                    .foregroundColor(.white)
                Text(localizationManager.localized("calls_hub_empty_subtitle"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.85))
                Text(localizationManager.localized("calls_disclaimer_short"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.65))

                modePickerCard

                Button(localizationManager.localized("calls_prep_cta")) {
                    openPrimaryAction()
                }
                .buttonStyle(.borderedProminent)
                .tint(.secondaryGold)
                .frame(maxWidth: .infinity)
                .accessibilityIdentifier("calls_hub_empty_prep")

                #if DEBUG
                spikeDebugCard
                #endif
            }
            .padding(Spacing.l)
            .padding(.bottom, 88)
        }
    }

    private var modePickerCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("calls_direction_section"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white)

            ForEach(CallSaveMode.allCases) { mode in
                Button {
                    saveMode = mode
                } label: {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: saveMode == mode ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(saveMode == mode ? .secondaryGold : .white.opacity(0.5))
                        VStack(alignment: .leading, spacing: 4) {
                            Text(title(for: mode))
                                .font(.subheadline.weight(.semibold))
                                .foregroundColor(.white)
                                .multilineTextAlignment(.leading)
                            Text(body(for: mode))
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.78))
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Spacer(minLength: 0)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(saveMode == mode ? Color.secondaryGold.opacity(0.18) : Color.white.opacity(0.08))
                    )
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("calls_mode_\(mode.rawValue)")
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private func title(for mode: CallSaveMode) -> String {
        switch mode {
        case .outgoingOnly: return localizationManager.localized("calls_option_a_title")
        case .afterOnly: return localizationManager.localized("calls_option_b_title")
        case .hybrid: return localizationManager.localized("calls_option_c_title")
        }
    }

    private func body(for mode: CallSaveMode) -> String {
        switch mode {
        case .outgoingOnly: return localizationManager.localized("calls_option_a_body")
        case .afterOnly: return localizationManager.localized("calls_option_b_body")
        case .hybrid: return localizationManager.localized("calls_option_c_body")
        }
    }

    private var list: some View {
        List {
            Section {
                modePickerCard
                    .listRowBackground(Color.clear)
                    .listRowInsets(EdgeInsets(top: 8, leading: 0, bottom: 8, trailing: 0))
            }
            Section {
                Text(localizationManager.localized("calls_disclaimer_short"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .listRowBackground(Color.clear)
            }
            ForEach(sessions) { session in
                VStack(alignment: .leading, spacing: 6) {
                    Text(displayTitle(for: session))
                        .font(.headline)
                    if !session.summary.previewLine.isEmpty {
                        Text(session.summary.previewLine)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .lineLimit(3)
                    }
                    Text(session.createdAt.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .accessibilityIdentifier("calls_session_row")
            }
            .onDelete { indexSet in
                for i in indexSet {
                    lifecycle.deleteSession(id: sessions[i].id)
                }
                reload()
            }
        }
        .listStyle(.insetGrouped)
        .padding(.bottom, 72)
    }

    private var prepSheet: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("calls_direction_section")) {
                    Picker("", selection: $saveMode) {
                        Text(localizationManager.localized("calls_option_a_title")).tag(CallSaveMode.outgoingOnly)
                        Text(localizationManager.localized("calls_option_b_title")).tag(CallSaveMode.afterOnly)
                        Text(localizationManager.localized("calls_option_c_title")).tag(CallSaveMode.hybrid)
                    }
                    .pickerStyle(.segmented)
                    .labelsHidden()
                }

                if saveMode == .hybrid {
                    Section {
                        Button(action: startIncomingSpeakerFlow) {
                            Text(localizationManager.localized("calls_incoming_cta"))
                        }
                        .accessibilityIdentifier("calls_incoming_cta")
                        Text(localizationManager.localized("calls_incoming_hint"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                if saveMode != .afterOnly {
                    Section(localizationManager.localized("calls_prep_goal_section")) {
                        TextField(localizationManager.localized("calls_prep_goal_placeholder"), text: $draftGoal)
                    }
                    Section(localizationManager.localized("calls_prep_phone_section")) {
                        TextField(localizationManager.localized("calls_prep_phone_placeholder"), text: $draftPhone)
                            .keyboardType(.phonePad)
                            .textContentType(.telephoneNumber)
                        Button {
                            // Present picker from hub (not nested) — fix white blank sheet.
                            showPrep = false
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                                showContactPicker = true
                            }
                        } label: {
                            Label(
                                localizationManager.localized("calls_prep_pick_contact"),
                                systemImage: "person.crop.circle"
                            )
                        }
                        .accessibilityIdentifier("calls_prep_pick_contact")
                        if prepNeedPhoneHint {
                            Text(localizationManager.localized("calls_prep_need_phone"))
                                .font(.caption)
                                .foregroundColor(.orange)
                        }
                    }
                    Section {
                        Toggle(localizationManager.localized("calls_prep_mic_toggle"), isOn: $wantMicRecord)
                        Text(localizationManager.localized("calls_prep_mic_hint"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Section {
                    Toggle(localizationManager.localized("calls_consent_checkbox"), isOn: $consentChecked)
                    Text(localizationManager.localized("calls_disclaimer_full"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Section {
                    if saveMode == .afterOnly {
                        Button(action: {
                            guard consentChecked else { return }
                            CallConsentPolicy.acceptCurrent()
                            showPrep = false
                            showAfter = true
                        }) {
                            Text(localizationManager.localized("calls_option_b_title"))
                        }
                        .disabled(!consentChecked)
                    } else {
                        Button(action: startPrepAndDial) {
                            Text(localizationManager.localized("calls_prep_start"))
                        }
                        .disabled(!consentChecked)
                        .accessibilityIdentifier("calls_prep_start_button")

                        Button(action: openPhoneAppFallback) {
                            Text(localizationManager.localized("calls_prep_open_phone"))
                        }
                        .accessibilityIdentifier("calls_prep_open_phone_button")
                    }
                }
            }
            .navigationBarTitle(localizationManager.localized("calls_prep_title"), displayMode: .inline)
            .navigationBarItems(leading:
                Button(action: { showPrep = false }) {
                    Text(localizationManager.localized("common_close"))
                }
            )
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    private func applyContact(_ contact: CNContact) {
        print("📞 CallsHub: contact picked phones=\(contact.phoneNumbers.count)")
        if let phone = contact.phoneNumbers.first?.value.stringValue, !phone.isEmpty {
            draftPhone = phone
            prepNeedPhoneHint = false
            ToastManager.shared.showSuccess(localizationManager.localized("calls_contact_picked"))
            // Re-open prep so user sees the number.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                showPrep = true
            }
        } else {
            ToastManager.shared.showWarning(localizationManager.localized("calls_contact_no_phone"))
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                showPrep = true
            }
        }
    }

    private func displayTitle(for session: CallSession) -> String {
        let goal = session.goal.trimmingCharacters(in: .whitespacesAndNewlines)
        if goal.isEmpty {
            return localizationManager.localized("calls_card_untitled")
        }
        let lower = goal.lowercased()
        if lower == "пробный" || lower == "trial" || lower == "practice" || lower == "тренировка" {
            return localizationManager.localized("calls_card_trial")
        }
        return goal
    }

    private func startIncomingSpeakerFlow() {
        guard consentChecked else { return }
        CallConsentPolicy.acceptCurrent()
        lifecycle.armPrep(goal: draftGoal.isEmpty ? localizationManager.localized("calls_incoming_cta") : draftGoal,
                          wantMicRecord: true)
        let summary = CallSummaryService.summarize(
            goal: draftGoal,
            transcriptOrNote: localizationManager.localized("calls_incoming_hint")
        )
        let session = CallSession(
            goal: draftGoal.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ? localizationManager.localized("calls_incoming_cta")
                : draftGoal,
            mode: .micRecord,
            source: .userPrep,
            summary: summary
        )
        CallSessionsStore().upsert(session)
        reload()
        showPrep = false
        print("📞 CallsHub: incoming speaker flow armed (Apple-safe mic, no PSTN tap)")
        ToastManager.shared.showInfo(localizationManager.localized("calls_incoming_hint"))
    }

    private func startPrepAndDial() {
        guard consentChecked else { return }
        let digits = draftPhone.filter { $0.isNumber || $0 == "+" }
        if digits.count < 3 {
            prepNeedPhoneHint = true
            return
        }
        prepNeedPhoneHint = false
        CallConsentPolicy.acceptCurrent()
        lifecycle.armPrep(goal: draftGoal, wantMicRecord: wantMicRecord)
        let summary = CallSummaryService.summarize(goal: draftGoal, transcriptOrNote: "")
        let session = CallSession(
            goal: draftGoal.trimmingCharacters(in: .whitespacesAndNewlines),
            mode: wantMicRecord ? .micRecord : .prepOnly,
            source: .userPrep,
            summary: summary
        )
        CallSessionsStore().upsert(session)
        reload()
        showPrep = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
            openTelURL(digits: digits)
        }
    }

    private func openPhoneAppFallback() {
        print("📞 CallsHub: Open Phone tapped")
        showPrep = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
            #if targetEnvironment(simulator)
            phoneOpenMessage = localizationManager.localized("calls_phone_unavailable_sim")
            print("⚠️ CallsHub: Simulator — Phone URL unsupported")
            return
            #else
            let digits = draftPhone.filter { $0.isNumber || $0 == "+" }
            if digits.count >= 3 {
                openTelURL(digits: digits)
                return
            }
            // Empty tel:// is a no-op / fails — prefer opening dial pad via telprompt with placeholder path.
            if let url = URL(string: "telprompt://"), UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url) { ok in
                    print(ok ? "✅ telprompt opened" : "⚠️ telprompt open failed")
                    if !ok {
                        phoneOpenMessage = localizationManager.localized("calls_phone_open_failed")
                    }
                }
            } else {
                phoneOpenMessage = localizationManager.localized("calls_phone_open_failed")
                print("⚠️ CallsHub: cannot open Phone (scheme / device)")
            }
            #endif
        }
    }

    private func openTelURL(digits: String) {
        let encoded = digits.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? digits
        print("📞 CallsHub: openTelURL digits_len=\(digits.count)")
        #if targetEnvironment(simulator)
        phoneOpenMessage = localizationManager.localized("calls_phone_unavailable_sim")
        return
        #else
        if let prompt = URL(string: "telprompt://\(encoded)"), UIApplication.shared.canOpenURL(prompt) {
            UIApplication.shared.open(prompt) { ok in
                print(ok ? "✅ telprompt:// opened" : "⚠️ telprompt:// failed")
                if !ok { phoneOpenMessage = localizationManager.localized("calls_phone_open_failed") }
            }
            return
        }
        if let tel = URL(string: "tel://\(encoded)") {
            UIApplication.shared.open(tel) { ok in
                print(ok ? "✅ tel:// opened" : "⚠️ tel:// failed")
                if !ok { phoneOpenMessage = localizationManager.localized("calls_phone_open_failed") }
            }
            return
        }
        phoneOpenMessage = localizationManager.localized("calls_phone_open_failed")
        #endif
    }

    #if DEBUG
    private var spikeDebugCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("DEBUG spike: \(lifecycle.spikeResult.rawValue)")
                .font(.caption.monospaced())
                .foregroundColor(.white.opacity(0.7))
            HStack {
                ForEach([CallsLifecycleService.SpikeResult.green, .yellow, .red], id: \.rawValue) { r in
                    Button(r.rawValue) { lifecycle.setSpikeResult(r) }
                        .font(.caption2)
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
    #endif

    private func reload() {
        sessions = lifecycle.allSessions()
        lifecycle.consumePendingAfterIfNeeded()
        if lifecycle.showAfterSheet { showAfter = true }
    }
}

// MARK: - Contacts picker (ProdQA S08)

private struct CallsContactPickerView: UIViewControllerRepresentable {
    let onSelect: (CNContact) -> Void
    let onCancel: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onSelect: onSelect, onCancel: onCancel)
    }

    func makeUIViewController(context: Context) -> CNContactPickerViewController {
        let picker = CNContactPickerViewController()
        picker.delegate = context.coordinator
        picker.predicateForEnablingContact = NSPredicate(format: "phoneNumbers.@count > 0")
        picker.displayedPropertyKeys = [
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactPhoneNumbersKey
        ]
        return picker
    }

    func updateUIViewController(_ uiViewController: CNContactPickerViewController, context: Context) {}

    final class Coordinator: NSObject, CNContactPickerDelegate {
        let onSelect: (CNContact) -> Void
        let onCancel: () -> Void

        init(onSelect: @escaping (CNContact) -> Void, onCancel: @escaping () -> Void) {
            self.onSelect = onSelect
            self.onCancel = onCancel
        }

        func contactPicker(_ picker: CNContactPickerViewController, didSelect contact: CNContact) {
            onSelect(contact)
        }

        func contactPicker(
            _ picker: CNContactPickerViewController,
            didSelect contactProperty: CNContactProperty
        ) {
            onSelect(contactProperty.contact)
        }

        func contactPickerDidCancel(_ picker: CNContactPickerViewController) {
            onCancel()
        }
    }
}
