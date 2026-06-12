import SwiftUI

/// p2-22 — Reflective sub-modes (gated by `FEATURE_WELLNESS_REFLECTIVE` on backend).
struct WellnessReflectiveModeScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var modes: [WellnessReflectiveModeItem] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var isSelecting = false

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Button { navigationManager.wellnessGoBack() } label: {
                            Image(systemName: "chevron.left")
                                .font(.body.weight(.semibold))
                        }
                        Text(localizationManager.localized("wellness_deep_explore_title"))
                            .font(.headline.bold())
                        Spacer()
                    }
                    Text(localizationManager.localized("wellness_deep_explore_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
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
        .task { await loadModes() }
    }

    private func modeRow(_ mode: WellnessReflectiveModeItem) -> some View {
        Button {
            Task { await selectMode(mode) }
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

    private func selectMode(_ mode: WellnessReflectiveModeItem) async {
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
}
