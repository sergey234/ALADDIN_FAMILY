import SwiftUI

/// fws-13 / fws-15 — L3 fullscreen helplines + optional parent ping.
struct WellnessReferralSheet: View {
    let level: String
    let notifyParentsOnLoad: Bool
    let allowDismiss: Bool

    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var payload: WellnessReferralResponse?
    @State private var isLoading = true
    @State private var errorText: String?

    init(level: String = "L2", notifyParentsOnLoad: Bool = false, allowDismiss: Bool = false) {
        self.level = level
        self.notifyParentsOnLoad = notifyParentsOnLoad
        self.allowDismiss = allowDismiss
    }

    private var isL3: Bool { level.uppercased() == "L3" }

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .premium)
            navigationShell
        }
        .foregroundColor(.white)
        .wellnessSheetDetents(isL3: isL3)
        .interactiveDismissDisabled(isL3)
        .task { await load() }
    }

    @ViewBuilder
    private var navigationShell: some View {
        if !isL3 || allowDismiss {
            WellnessNavigationStack { navigationInner }
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button(closeButtonTitle) { dismiss() }
                            .tint(.white)
                    }
                }
        } else {
            WellnessNavigationStack { navigationInner }
        }
    }

    private var navigationInner: some View {
        sheetBody
            .navigationTitle(navigationTitle)
            .navigationBarTitleDisplayMode(.inline)
    }

    private var navigationTitle: String {
        let key = isL3 ? "wellness_crisis_sheet_title" : "wellness_referral_title"
        return localizationManager.localized(key)
    }

    private var closeButtonTitle: String {
        localizationManager.localized(isL3 ? "wellness_crisis_sheet_close" : "wellness_done")
    }

    @ViewBuilder
    private var sheetBody: some View {
        if isLoading {
            loadingView
        } else if let payload {
            payloadView(payload)
        } else if let errorText {
            errorView(errorText)
        }
    }

    private var loadingView: some View {
        ProgressView(localizationManager.localized("wellness_helpline_loading"))
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .tint(.white)
    }

    private func payloadView(_ payload: WellnessReferralResponse) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: isL3 ? 20 : 16) {
                if isL3 {
                    l3Header
                }
                Text(payload.disclaimer)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
                ForEach(payload.lines) { line in
                    helplineRow(line)
                }
                if allowDismiss {
                    dismissButton
                }
            }
            .padding()
        }
    }

    private var l3Header: some View {
        Group {
            Text(localizationManager.localized("wellness_crisis_message"))
                .font(.title3.weight(.semibold))
                .foregroundColor(.white)
                .fixedSize(horizontal: false, vertical: true)
            Text(localizationManager.localized("wellness_crisis_parent_ping_hint"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))
        }
    }

    private var dismissButton: some View {
        Button { dismiss() } label: {
            Text(localizationManager.localized("wellness_crisis_sheet_close"))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
        }
        .buttonStyle(.bordered)
        .tint(.white.opacity(0.85))
        .padding(.top, 8)
    }

    private func errorView(_ message: String) -> some View {
        Text(message)
            .foregroundStyle(.orange)
            .padding()
    }

    private func helplineRow(_ line: WellnessReferralLine) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(referralLineLabel(line))
                .font(isL3 ? .headline : .subheadline.bold())
            Button {
                dial(line.phone)
            } label: {
                HStack {
                    Image(systemName: "phone.fill")
                        .font(isL3 ? .title2 : .body)
                    Text(line.phone)
                        .font(isL3 ? .title2.bold() : .body.bold())
                    Spacer()
                    Text(localizationManager.localized("wellness_referral_call"))
                        .font(isL3 ? .subheadline : .caption)
                }
                .padding(isL3 ? 18 : 12)
                .frame(maxWidth: .infinity)
                .stormGlassCard(cornerRadius: isL3 ? 16 : 12, accentStripColor: .red)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("wellness_referral_call_\(line.id)")
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
            if notifyParentsOnLoad && isL3 {
                _ = try? await WellnessAPIService.shared.openCrisis(context: "one_tap_sheet")
            }
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

private extension View {
    @ViewBuilder
    func wellnessSheetDetents(isL3: Bool) -> some View {
        if isL3 {
            self
        } else if #available(iOS 16.0, *) {
            self.presentationDetents([.medium, .large])
        } else {
            self
        }
    }
}
