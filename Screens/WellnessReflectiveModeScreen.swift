import SwiftUI

/// p2-22 — Reflective sub-modes (gated by `FEATURE_WELLNESS_REFLECTIVE` on backend).
struct WellnessReflectiveModeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var modes: [WellnessReflectiveModeItem] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var isSelecting = false
    @State private var pendingMode: WellnessReflectiveModeItem?
    @State private var promptMode: WellnessReflectiveModeItem?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    header
                    infoBlock
                    if isLoading {
                        ProgressView().frame(maxWidth: .infinity).tint(.white)
                    } else if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    } else {
                        ForEach(modes) { mode in
                            modeRow(mode)
                        }
                    }
                }
                .padding()
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .accessibilityIdentifier("wellness_reflective_screen")
        .task { await loadModes() }
        .sheet(item: $promptMode) { mode in
            reflectivePromptSheet(mode)
        }
        .confirmationDialog(
            localizationManager.localized("wellness_reflective_confirm_title"),
            isPresented: Binding(
                get: { pendingMode != nil },
                set: { if !$0 { pendingMode = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button(localizationManager.localized("wellness_reflective_confirm_continue")) {
                if let mode = pendingMode {
                    pendingMode = nil
                    Task { await proceedToCompanion(mode) }
                }
            }
            Button(localizationManager.localized("wellness_reflective_confirm_cancel"), role: .cancel) {
                pendingMode = nil
            }
        } message: {
            if let mode = pendingMode {
                Text(
                    String(
                        format: localizationManager.localized("wellness_reflective_confirm_message"),
                        modeLabel(mode)
                    )
                )
            }
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            .accessibilityIdentifier("wellness_subpage_back")
            Text(localizationManager.localized("wellness_deep_explore_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private var infoBlock: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(
                localizationManager.localized("wellness_reflective_info_title"),
                systemImage: "bubble.left.and.bubble.right.fill"
            )
            .font(.subheadline.bold())
            Text(localizationManager.localized("wellness_deep_explore_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.9))
            Text(localizationManager.localized("wellness_reflective_info_body"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .stormGlassCard(cornerRadius: 12, accentStripColor: Color(hex: "8B5CF6"))
    }

    private func modeRow(_ mode: WellnessReflectiveModeItem) -> some View {
        Button {
            promptMode = mode
        } label: {
            VStack(alignment: .leading, spacing: 6) {
                Text(modeLabel(mode))
                    .font(.subheadline.bold())
                Text(modeHint(mode))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
            .stormGlassCard(cornerRadius: 12)
        }
        .buttonStyle(.plain)
        .disabled(isSelecting)
    }

    private func loadModes() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let resp = try await WellnessAPIService.shared.fetchReflectiveModes()
            modes = resp.modes
        } catch {
            errorText = localizationManager.localized("wellness_reflective_unavailable")
        }
    }

    private func modeLabel(_ mode: WellnessReflectiveModeItem) -> String {
        if let key = mode.labelKey, !key.isEmpty {
            let text = localizationManager.localized(key)
            if text != key { return text }
        }
        return mode.label
    }

    private func modeHint(_ mode: WellnessReflectiveModeItem) -> String {
        if let key = mode.hintKey, !key.isEmpty {
            let text = localizationManager.localized(key)
            if text != key { return text }
        }
        return mode.hint
    }

    private func pillar(for modeId: String) -> String {
        switch modeId {
        case "presence", "single_question":
            return "humanistic"
        case "structured_view":
            return "cognitive"
        default:
            return "jung"
        }
    }

    private func proceedToCompanion(_ mode: WellnessReflectiveModeItem) async {
        isSelecting = true
        errorText = nil
        defer { isSelecting = false }
        let p = pillar(for: mode.id)
        WellnessSessionStore.setActivePillar(p)
        WellnessSessionStore.setExercisePillar(p)
        do {
            _ = try await WellnessAPIService.shared.setSessionPillar(p, forceSwitch: true)
        } catch {
            // Офлайн / сервер недоступен — pillar уже сохранён локально, продолжаем.
        }
        let label = modeLabel(mode)
        let banner = String(
            format: localizationManager.localized("wellness_companion_mode_banner"),
            label
        )
        WellnessSessionStore.setCompanionEntryBanner(banner)
        WellnessSessionStore.requestMicHighlight()
        navigationManager.navigateToCompanionHome(returnTo: .wellnessReflective)
    }

    private func reflectivePromptSheet(_ mode: WellnessReflectiveModeItem) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 16) {
                Text(modeLabel(mode))
                    .font(.title3.bold())
                Text(modeHint(mode))
                    .font(.body)
                    .foregroundColor(.secondary)
                Spacer()
                Button {
                    promptMode = nil
                    pendingMode = mode
                } label: {
                    Text(localizationManager.localized("wellness_reflective_prompt_continue"))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(Color(hex: "8B5CF6"))
            }
            .padding()
            .navigationTitle(localizationManager.localized("wellness_reflective_prompt_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_reflective_confirm_cancel")) {
                        promptMode = nil
                    }
                }
            }
        }
        .accessibilityIdentifier("wellness_reflective_prompt_sheet")
    }
}
