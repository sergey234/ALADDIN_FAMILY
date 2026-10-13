import SwiftUI
import UIKit

/// Unified «Звонки» hub — call memory cards (not carrier line recording).
struct CallsHubScreen: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @ObservedObject private var lifecycle = CallsLifecycleService.shared
    @Environment(\.dismiss) private var dismiss

    @State private var sessions: [CallSession] = []
    @State private var showPrep = false
    @State private var showAfter = false
    @State private var showPaywallHint = false
    @State private var draftGoal = ""
    @State private var wantMicRecord = true
    @State private var consentChecked = false
    @AppStorage(AppConfig.UserDefaultsKeys.postCallSafetyPromptEnabled)
    private var postCallSafetyPromptEnabled = true

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .shield)
                VStack(spacing: Spacing.m) {
                    safetyToggleCard
                    content
                }
            }
            .navigationBarTitle(localizationManager.localized("calls_hub_title"), displayMode: .inline)
            .navigationBarItems(
                leading: Button(action: { dismiss() }) {
                    Text(localizationManager.localized("common_close"))
                },
                trailing: Button(action: {
                    if CallsAccessPolicy.isAvailable() {
                        showPrep = true
                    } else {
                        showPaywallHint = true
                    }
                }) {
                    Image(systemName: "plus.circle.fill")
                        .foregroundColor(.secondaryGold)
                }
                .accessibilityIdentifier("calls_hub_prep_button")
            )
            .onAppear(perform: reload)
            .onChange(of: lifecycle.showAfterSheet) { open in
                if open { showAfter = true }
            }
            .sheet(isPresented: $showPrep) { prepSheet }
            .sheet(isPresented: $showAfter, onDismiss: {
                lifecycle.showAfterSheet = false
            }) {
                CallsAfterMemorySheet()
                    .environmentObject(localizationManager)
                    .environmentObject(navigationManager)
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
        }
        .navigationViewStyle(StackNavigationViewStyle())
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
        .padding(.top, Spacing.s)
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
            Button(localizationManager.localized("calls_prep_cta")) {
                showPrep = true
            }
            .buttonStyle(.borderedProminent)
            .tint(.secondaryGold)
            .accessibilityIdentifier("calls_hub_empty_prep")

            #if DEBUG
            spikeDebugCard
            #endif
        }
        .padding(Spacing.l)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    private var list: some View {
        List {
            Section {
                Text(localizationManager.localized("calls_disclaimer_short"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .listRowBackground(Color.clear)
            }
            ForEach(sessions) { session in
                VStack(alignment: .leading, spacing: 6) {
                    Text(session.goal.isEmpty
                         ? localizationManager.localized("calls_card_untitled")
                         : session.goal)
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
    }

    private var prepSheet: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("calls_prep_goal_section")) {
                    TextField(localizationManager.localized("calls_prep_goal_placeholder"), text: $draftGoal)
                }
                Section {
                    Toggle(localizationManager.localized("calls_prep_mic_toggle"), isOn: $wantMicRecord)
                    Text(localizationManager.localized("calls_prep_mic_hint"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Section {
                    Toggle(localizationManager.localized("calls_consent_checkbox"), isOn: $consentChecked)
                    Text(localizationManager.localized("calls_disclaimer_full"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Section {
                    Button(action: {
                        guard consentChecked else { return }
                        CallConsentPolicy.acceptCurrent()
                        lifecycle.armPrep(goal: draftGoal, wantMicRecord: wantMicRecord)
                        // Phase 0/3: mic record during PSTN depends on spike — save prep card now; open Phone.
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
                        if let url = URL(string: "tel://") {
                            UIApplication.shared.open(url)
                        }
                    }) {
                        Text(localizationManager.localized("calls_prep_start"))
                    }
                    .disabled(!consentChecked)
                    .accessibilityIdentifier("calls_prep_start_button")
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
