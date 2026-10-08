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
                .ignoresSafeArea()
            Color.black.opacity(0.35)
                .ignoresSafeArea()
            if isL3 {
                l3Shell
            } else {
                navigationShell
            }
        }
        .foregroundColor(.white)
        .preferredColorScheme(.dark)
        .wellnessSheetDetents(isL3: isL3)
        .interactiveDismissDisabled(isL3 && !allowDismiss)
        .task { await load() }
    }

    /// L3: no system Navigation white sheet — custom chrome + always-visible close when allowed.
    private var l3Shell: some View {
        VStack(spacing: 0) {
            HStack {
                Text(localizationManager.localized("wellness_crisis_sheet_title"))
                    .font(.headline.weight(.bold))
                    .foregroundColor(.white)
                Spacer()
                if allowDismiss {
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title2)
                            .foregroundStyle(Color.white.opacity(0.9))
                    }
                    .accessibilityIdentifier("wellness_crisis_sheet_close_button")
                    .accessibilityLabel(localizationManager.localized("wellness_crisis_sheet_close"))
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)

            sheetBody
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    @ViewBuilder
    private var navigationShell: some View {
        WellnessNavigationStack { navigationInner }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(closeButtonTitle) { dismiss() }
                        .tint(.white)
                }
            }
    }

    private var navigationInner: some View {
        Group {
            if #available(iOS 16.0, *) {
                sheetBody
                    .navigationTitle(localizationManager.localized("wellness_referral_title"))
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbarColorScheme(.dark, for: .navigationBar)
            } else {
                sheetBody
                    .navigationTitle(localizationManager.localized("wellness_referral_title"))
                    .navigationBarTitleDisplayMode(.inline)
            }
        }
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
        ScrollView(.vertical, showsIndicators: true) {
            VStack(alignment: .leading, spacing: isL3 ? 20 : 16) {
                if isL3 {
                    l3Header
                }
                Text(payload.disclaimer)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
                    .fixedSize(horizontal: false, vertical: true)
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
        }
    }

    private var dismissButton: some View {
        Button { dismiss() } label: {
            Text(localizationManager.localized("wellness_crisis_sheet_close"))
                .font(.body.weight(.semibold))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(Color.white.opacity(0.18))
                .cornerRadius(14)
        }
        .buttonStyle(.plain)
        .padding(.top, 8)
        .accessibilityIdentifier("wellness_crisis_sheet_close_bottom")
    }

    private func errorView(_ message: String) -> some View {
        VStack(spacing: 16) {
            Text(message)
                .foregroundStyle(.orange)
                .multilineTextAlignment(.center)
                .padding()
            if allowDismiss {
                dismissButton
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func helplineRow(_ line: WellnessReferralLine) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(referralLineLabel(line))
                .font(isL3 ? .headline : .subheadline.bold())
                .foregroundColor(.white)
            Button {
                dial(line.phone)
            } label: {
                HStack {
                    Image(systemName: "phone.fill")
                        .font(isL3 ? .title2 : .body)
                        .foregroundColor(.white)
                    Text(line.phone)
                        .font(isL3 ? .title2.bold() : .body.bold())
                        .foregroundColor(.white)
                    Spacer()
                    Text(localizationManager.localized("wellness_referral_call"))
                        .font(isL3 ? .subheadline : .caption)
                        .foregroundColor(.white.opacity(0.9))
                }
                .padding(isL3 ? 18 : 12)
                .frame(maxWidth: .infinity)
                .stormGlassCard(cornerRadius: isL3 ? 16 : 12, accentStripColor: .dangerRed)
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
