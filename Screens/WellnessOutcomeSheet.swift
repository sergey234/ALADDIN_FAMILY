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

    private var ageBand: String {
        WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
    }

    var body: some View {
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
                } else {
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_outcome_title", ageBand: ageBand))
                        .font(.title3.bold())
                    Text(WellnessAgeL10n.text(localizationManager, key: "wellness_outcome_subtitle", ageBand: ageBand))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
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
                            .background(Color.purple.opacity(0.12))
                            .cornerRadius(12)
                        }
                        .buttonStyle(.plain)
                        .disabled(isSubmitting)
                    }
                    if isSubmitting {
                        ProgressView().frame(maxWidth: .infinity)
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
                }
            }
        }
        .wellnessSheetDetents()
    }

    private func submit(_ choice: Choice) async {
        isSubmitting = true
        errorText = nil
        defer { isSubmitting = false }
        do {
            _ = try await WellnessAPIService.shared.postOutcome(
                pillar: pillar,
                helpful: choice.helpfulScore
            )
            submitted = true
            try? await Task.sleep(nanoseconds: 900_000_000)
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
