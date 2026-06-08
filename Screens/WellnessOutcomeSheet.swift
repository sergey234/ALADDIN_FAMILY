import SwiftUI

/// p2-42 — 1-tap outcome after exercise: легче / так же / хуже → POST /outcomes.
struct WellnessOutcomeSheet: View {
    enum Choice: String, CaseIterable {
        case better
        case same
        case worse

        var helpfulScore: Int {
            switch self {
            case .better: return 5
            case .same: return 3
            case .worse: return 1
            }
        }

        var titleKey: String {
            switch self {
            case .better: return "wellness_outcome_better"
            case .same: return "wellness_outcome_same"
            case .worse: return "wellness_outcome_worse"
            }
        }

        var icon: String {
            switch self {
            case .better: return "arrow.up.circle.fill"
            case .same: return "equal.circle.fill"
            case .worse: return "arrow.down.circle.fill"
            }
        }
    }

    let pillar: String
    var onFinished: (() -> Void)?

    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var submitted = false
    @State private var isSubmitting = false
    @State private var errorText: String?
    @State private var followUpHint: String?

    private var ageBand: String {
        WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
    }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)

            WellnessNavigationStack {
                VStack(alignment: .leading, spacing: 20) {
                    if submitted {
                        Label(
                            localizationManager.localized("wellness_outcome_thanks"),
                            systemImage: "checkmark.circle.fill"
                        )
                        .font(.headline)
                        .foregroundStyle(.green)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.top, 24)
                        if let followUpHint, !followUpHint.isEmpty {
                            Text(followUpHint)
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.85))
                                .multilineTextAlignment(.center)
                                .frame(maxWidth: .infinity)
                                .padding(.top, 8)
                        }
                    } else {
                        Text(WellnessAgeL10n.text(localizationManager, key: "wellness_outcome_title", ageBand: ageBand))
                            .font(.title3.bold())
                        Text(WellnessAgeL10n.text(localizationManager, key: "wellness_outcome_subtitle", ageBand: ageBand))
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.85))
                        if let errorText {
                            Text(errorText).font(.caption).foregroundStyle(.orange)
                        }
                        ForEach(Choice.allCases, id: \.self) { choice in
                            Button {
                                Task { await submit(choice) }
                            } label: {
                                HStack(spacing: 12) {
                                    Image(systemName: choice.icon)
                                        .font(.title2)
                                    Text(localizationManager.localized(choice.titleKey))
                                        .font(.body.bold())
                                    Spacer()
                                }
                                .padding()
                                .frame(maxWidth: .infinity)
                                .stormGlassCard(cornerRadius: 12)
                            }
                            .buttonStyle(.plain)
                            .disabled(isSubmitting)
                            .accessibilityIdentifier("wellness_outcome_\(choice.rawValue)")
                        }
                        if isSubmitting {
                            ProgressView().frame(maxWidth: .infinity).tint(.white)
                        }
                    }
                    Spacer()
                }
                .padding()
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button(localizationManager.localized("wellness_outcome_skip")) {
                            close()
                        }
                        .tint(.white)
                        .accessibilityIdentifier("wellness_outcome_skip")
                    }
                }
            }
        }
        .foregroundColor(.white)
        .wellnessSheetDetents()
    }

    private func submit(_ choice: Choice) async {
        isSubmitting = true
        errorText = nil
        defer { isSubmitting = false }
        do {
            let resp = try await WellnessAPIService.shared.postOutcome(
                pillar: pillar,
                helpful: choice.helpfulScore
            )
            if let next = resp.adjustedPillar, !next.isEmpty, next != pillar {
                WellnessSessionStore.setActivePillar(next)
                if let wp = WellnessPillar(rawValue: next) {
                    followUpHint = String(
                        format: localizationManager.localized("wellness_outcome_pillar_switch"),
                        localizationManager.localized(wp.titleKey)
                    )
                }
            } else if resp.pillarFatigue?.fatigued == true,
                      let suggested = resp.pillarFatigue?.suggestedPillar,
                      let wp = WellnessPillar(rawValue: suggested) {
                WellnessSessionStore.setActivePillar(suggested)
                let fatigueMsg = resp.pillarFatigue?.message
                    ?? localizationManager.localized("wellness_fatigue_switch")
                followUpHint = "\(fatigueMsg) \(localizationManager.localized(wp.titleKey))"
            } else if choice == .worse {
                followUpHint = localizationManager.localized("wellness_outcome_worse_hint")
            }
            submitted = true
            try? await Task.sleep(nanoseconds: followUpHint == nil ? 900_000_000 : 1_800_000_000)
            close()
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }

    private func close() {
        onFinished?()
        dismiss()
    }
}
