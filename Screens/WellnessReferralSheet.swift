import SwiftUI

/// p2-43 — Local helplines from GET /api/wellness/referral (non-clinical referral).
struct WellnessReferralSheet: View {
    let level: String

    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var payload: WellnessReferralResponse?
    @State private var isLoading = true
    @State private var errorText: String?

    init(level: String = "L2") {
        self.level = level
    }

    var body: some View {
        WellnessNavigationStack {
            Group {
                if isLoading {
                    ProgressView(localizationManager.localized("wellness_helpline_loading"))
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let payload {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 16) {
                            Text(payload.disclaimer)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            ForEach(payload.lines) { line in
                                helplineRow(line)
                            }
                        }
                        .padding()
                    }
                } else if let errorText {
                    Text(errorText)
                        .foregroundStyle(.orange)
                        .padding()
                }
            }
            .navigationTitle(localizationManager.localized("wellness_referral_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_done")) {
                        dismiss()
                    }
                }
            }
        }
        .wellnessSheetDetents()
        .task { await load() }
    }

    private func helplineRow(_ line: WellnessReferralLine) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(referralLineLabel(line))
                .font(.subheadline.bold())
            Button {
                dial(line.phone)
            } label: {
                HStack {
                    Image(systemName: "phone.fill")
                    Text(line.phone)
                        .font(.body.bold())
                    Spacer()
                    Text(localizationManager.localized("wellness_referral_call"))
                        .font(.caption)
                }
                .padding(12)
                .frame(maxWidth: .infinity)
                .background(Color.red.opacity(0.12))
                .cornerRadius(12)
            }
            .buttonStyle(.plain)
        }
    }

    private func referralLineLabel(_ line: WellnessReferralLine) -> String {
        if let key = line.labelKey, !key.isEmpty {
            let text = localizationManager.localized(key)
            if text != key { return text }
        }
        return line.label
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            payload = try await WellnessAPIService.shared.fetchReferral(level: level)
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }

    private func dial(_ raw: String) {
        let digits = raw.filter { $0.isNumber || $0 == "+" }
        guard let url = URL(string: "tel://\(digits)"), !digits.isEmpty else { return }
        UIApplication.shared.open(url)
    }
}
