import SwiftUI

/// fws-24 — catalog of self-help methods (not live therapy).
struct DigitalPsychologyLibraryScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var methods: [WellnessPsychLibraryMethod] = []
    @State private var disclaimerKey = "psych_library_disclaimer"
    @State private var isLoading = true
    @State private var errorText: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    header
                    Text(localizationManager.localized(disclaimerKey))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))

                    if isLoading {
                        ProgressView().tint(.white)
                    } else if let errorText {
                        Text(errorText).foregroundStyle(.orange)
                    } else {
                        ForEach(methods) { method in
                            methodCard(method)
                        }
                    }
                }
                .padding()
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .accessibilityIdentifier("digital_psychology_library_screen")
        .task { await load() }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.wellnessGoBack() } label: {
                Image(systemName: "chevron.left").font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("psych_library_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private func methodCard(_ method: WellnessPsychLibraryMethod) -> some View {
        Button {
            open(method)
        } label: {
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(localizationManager.localized(method.titleKey))
                        .font(.subheadline.bold())
                    Spacer()
                    Text(method.heroId)
                        .font(.caption2)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.white.opacity(0.12))
                        .clipShape(Capsule())
                }
                Text(localizationManager.localized(method.subtitleKey))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
                    .multilineTextAlignment(.leading)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(12)
            .stormGlassCard(cornerRadius: 12)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("psych_library_\(method.id)")
    }

    private func open(_ method: WellnessPsychLibraryMethod) {
        WellnessSessionStore.setExercisePillar(method.pillar)
        if let exerciseId = method.exerciseId {
            WellnessSessionStore.setPendingExerciseId(exerciseId)
        }
        let screen: NavigationManager.ALADDINScreen
        switch method.route {
        case "wellness_reflective": screen = .wellnessReflective
        case "wellness_dream_journal": screen = .wellnessDreamJournal
        case "wellness_if_then": screen = .wellnessHub
        default: screen = .wellnessExercise
        }
        navigationManager.navigateToWellnessScreen(screen, returnTo: .wellnessHub)
    }

    @MainActor
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let payload = try await WellnessAPIService.shared.fetchPsychLibraryManifest()
            methods = payload.methods
            if let key = payload.disclaimerKey { disclaimerKey = key }
        } catch {
            errorText = localizationManager.localized("psych_library_load_failed")
        }
    }
}
