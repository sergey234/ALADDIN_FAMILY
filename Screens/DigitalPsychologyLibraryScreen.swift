import SwiftUI

/// fws-24 — catalog of self-help methods (not live therapy).
struct DigitalPsychologyLibraryScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var methods: [WellnessPsychLibraryMethod] = []
    @State private var disclaimerKey = "psych_library_disclaimer"
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showingCachedHint = false

    private static let cacheKey = "wellness_psych_library_manifest_cache_v1"

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .warm)
            ScrollView(.vertical, showsIndicators: true) {
                VStack(alignment: .leading, spacing: 14) {
                    header
                    Text(localizationManager.localized(disclaimerKey))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))

                    if isLoading {
                        ProgressView().tint(.white)
                    } else if let errorText, methods.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(errorText).foregroundStyle(.orange)
                            Button(localizationManager.localized("psych_library_retry")) {
                                Task { await load() }
                            }
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                            .accessibilityIdentifier("psych_library_retry")
                        }
                    } else {
                        if showingCachedHint {
                            Text(localizationManager.localized("psych_library_cached_hint"))
                                .font(.caption)
                                .foregroundColor(.orange.opacity(0.95))
                            Button(localizationManager.localized("psych_library_retry")) {
                                Task { await load() }
                            }
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                        }
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
        errorText = nil
        showingCachedHint = false
        defer { isLoading = false }
        do {
            let payload = try await WellnessAPIService.shared.fetchPsychLibraryManifest()
            methods = payload.methods
            if let key = payload.disclaimerKey { disclaimerKey = key }
            Self.cacheManifest(payload)
        } catch {
            if let cached = Self.loadCachedManifest() {
                methods = cached.methods
                if let key = cached.disclaimerKey { disclaimerKey = key }
                showingCachedHint = true
            } else {
                methods = []
                errorText = localizationManager.localized("psych_library_load_failed")
            }
        }
    }

    private static func cacheManifest(_ payload: WellnessPsychLibraryResponse) {
        guard let data = try? JSONEncoder().encode(payload) else { return }
        UserDefaults.standard.set(data, forKey: cacheKey)
    }

    private static func loadCachedManifest() -> WellnessPsychLibraryResponse? {
        guard let data = UserDefaults.standard.data(forKey: cacheKey),
              let payload = try? JSONDecoder().decode(WellnessPsychLibraryResponse.self, from: data),
              !payload.methods.isEmpty else {
            return nil
        }
        return payload
    }
}
