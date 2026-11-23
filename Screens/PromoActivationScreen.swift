import SwiftUI
import UIKit

struct PromoActivationScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var code: String = ""
    @State private var isRedeeming = false
    @State private var statusMessage: String?
    @State private var isSuccess = false
    @State private var showAppStoreRedeemHelp = false
    @AppStorage("subscription_expires_at_iso") private var subscriptionExpiresAtIso: String = ""
    @AppStorage("promo_bonus_active_until") private var promoBonusActiveUntil: String = ""

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)
            .ignoresSafeArea()

            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("promo_activation_title"),
                    subtitle: localizationManager.localized("promo_activation_subtitle_short"),
                    showBackButton: true,
                    onBack: {
                        if navigationManager.previousScreen == .profile {
                            navigationManager.goBack(reason: "PromoActivationScreen back")
                        } else {
                            navigationManager.navigateToRoot(.profile)
                        }
                    }
                )

                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        header
                        accessStatusCard
                        inputCard
                        appStoreFriendCodeCard
                        explanationCard
                    }
                    .padding(20)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showAppStoreRedeemHelp) {
            AppStoreRedeemCodeHelpSheet()
                .environmentObject(localizationManager)
        }
        .onAppear {
            if code.isEmpty, let pending = navigationManager.pendingPromoCode {
                let normalized = normalizeCode(pending)
                if routeFamilyInviteIfNeeded(normalized) {
                    return
                }
                code = normalized
            }
        }
        .onChange(of: code) { newValue in
            let normalized = normalizeCode(newValue)
            guard !normalized.isEmpty else { return }
            // Smart door: FAM never stays on promo — route to family join.
            if routeFamilyInviteIfNeeded(normalized) {
                statusMessage = localizationManager.localized("promo_routing_to_family_join")
                isSuccess = false
            }
        }
    }

    private var appStoreFriendCodeCard: some View {
        card {
            VStack(alignment: .leading, spacing: 10) {
                Text(localizationManager.localized("appstore_redeem_help_card_title"))
                    .font(.headline)
                    .foregroundColor(.white)
                Text(localizationManager.localized("appstore_redeem_help_card_body"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.72))
                    .fixedSize(horizontal: false, vertical: true)
                Button {
                    showAppStoreRedeemHelp = true
                } label: {
                    Text(localizationManager.localized("appstore_redeem_help_card_cta"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("promo_appstore_redeem_help_cta")
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(localizationManager.localized("promo_activation_title"))
                .font(.system(size: 30, weight: .bold))
                .foregroundColor(.white)

            Text(localizationManager.localized("promo_activation_subtitle"))
                .font(.body)
                .foregroundColor(.white.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.top, 8)
    }

    private var accessStatusCard: some View {
        Group {
            if !promoBonusActiveUntil.isEmpty {
                card {
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundColor(.green)
                            .font(.title2)
                        VStack(alignment: .leading, spacing: 6) {
                            Text(localizationManager.localized("promo_active_card_title"))
                                .font(.headline)
                                .foregroundColor(.white)
                            Text(String(format: localizationManager.localized("promo_active_card_body"), displayDate(promoBonusActiveUntil)))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.75))
                        }
                    }
                }
            } else if !subscriptionExpiresAtIso.isEmpty {
                card {
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: "clock.fill")
                            .foregroundColor(.blue)
                            .font(.title2)
                        VStack(alignment: .leading, spacing: 6) {
                            Text(localizationManager.localized("promo_current_access_card_title"))
                                .font(.headline)
                                .foregroundColor(.white)
                            Text(String(format: localizationManager.localized("promo_current_access_card_body"), displayDate(subscriptionExpiresAtIso)))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.75))
                        }
                    }
                }
            }
        }
    }

    private var inputCard: some View {
        card {
            VStack(alignment: .leading, spacing: 14) {
                Text(localizationManager.localized("promo_activation_code_label"))
                    .font(.headline)
                    .foregroundColor(.white)

                TextField(localizationManager.localized("promo_activation_code_placeholder"), text: $code)
                    .textInputAutocapitalization(.characters)
                    .autocorrectionDisabled()
                    .foregroundColor(.white)
                    .padding(14)
                    .background(Color.white.opacity(0.10))
                    .cornerRadius(14)
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.white.opacity(0.18), lineWidth: 1)
                    )

                HStack(spacing: 10) {
                    Button {
                        if let pasted = UIPasteboard.general.string?.trimmingCharacters(in: .whitespacesAndNewlines), !pasted.isEmpty {
                            code = normalizeCode(pasted)
                            statusMessage = nil
                            isSuccess = false
                        }
                    } label: {
                        Text(localizationManager.localized("promo_activation_paste"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 14)
                            .padding(.vertical, 12)
                            .background(Color.white.opacity(0.12))
                            .cornerRadius(12)
                    }

                    Button(action: redeem) {
                        HStack {
                            if isRedeeming {
                                ProgressView()
                                    .tint(Color.backgroundDark)
                            }
                            Text(localizationManager.localized("promo_activation_activate"))
                                .font(.subheadline.weight(.bold))
                                .lineLimit(1)
                                .minimumScaleFactor(0.55)
                                .allowsTightening(true)
                        }
                        .foregroundColor(code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.textSecondary : Color.backgroundDark)
                        .padding(.horizontal, 18)
                        .padding(.vertical, 12)
                        .frame(maxWidth: .infinity)
                        .background(code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.backgroundMedium : Color.secondaryGold)
                        .cornerRadius(12)
                    }
                    .disabled(isRedeeming || code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }

                if let statusMessage {
                    Text(statusMessage)
                        .font(.subheadline)
                        .foregroundColor(isSuccess ? .green : .orange)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    private var explanationCard: some View {
        card {
            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("promo_activation_note_title"))
                    .font(.headline)
                    .foregroundColor(.white)
                Text(localizationManager.localized("promo_activation_note_body"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.72))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private func card<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        content()
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.08))
            .cornerRadius(22)
            .overlay(
                RoundedRectangle(cornerRadius: 22)
                    .stroke(Color.white.opacity(0.12), lineWidth: 1)
            )
    }

    private func redeem() {
        let cleanCode = normalizeCode(code)
        guard !cleanCode.isEmpty else { return }
        if routeFamilyInviteIfNeeded(cleanCode) {
            return
        }
        if let localError = localPromoInputError(for: cleanCode) {
            code = cleanCode
            isSuccess = false
            statusMessage = localError
            return
        }
        code = cleanCode
        isRedeeming = true
        statusMessage = nil
        isSuccess = false

        APIService.shared.redeemPromoCode(code: cleanCode) { result in
            DispatchQueue.main.async {
                isRedeeming = false
                switch result {
                case .success(let response):
                    let activeUntil = response.subscription_active_until ?? response.expires_at ?? ""
                    promoBonusActiveUntil = activeUntil
                    if !activeUntil.isEmpty {
                        subscriptionExpiresAtIso = activeUntil
                    }
                    navigationManager.pendingPromoCode = nil
                    isSuccess = true
                    statusMessage = String(
                        format: localizationManager.localized("promo_activation_success"),
                        displayDate(activeUntil)
                    )
                case .failure(let error):
                    isSuccess = false
                    statusMessage = localizedPromoError(error)
                }
            }
        }
    }

    private func normalizeCode(_ raw: String) -> String {
        raw.trimmingCharacters(in: .whitespacesAndNewlines)
            .uppercased()
            .filter { $0.isLetter || $0.isNumber || $0 == "-" || $0 == "_" }
    }

    /// FAM / family QR → join flow (not team promo). Require parse or FAM-… long enough (avoid routing on "FAM" alone while typing).
    @discardableResult
    private func routeFamilyInviteIfNeeded(_ cleanCode: String) -> Bool {
        let looksLikeFamilyInvite =
            FamilyInviteCodeParser.parse(cleanCode) != nil
            || (cleanCode.hasPrefix("FAM-") && cleanCode.count >= 12)
        guard looksLikeFamilyInvite else { return false }
        guard navigationManager.currentScreen != .invitationCode else { return true }
        navigationManager.pendingFamilyInviteCode = cleanCode
        navigationManager.pendingPromoCode = nil
        navigationManager.navigateTo(.invitationCode)
        return true
    }

    private func localPromoInputError(for cleanCode: String) -> String? {
        if cleanCode.hasPrefix("MEM_") {
            return localizationManager.localized("promo_error_member_id")
        }
        // Family invite handled by routeFamilyInviteIfNeeded before redeem.
        if cleanCode.filter({ $0.isNumber }).count == 6,
           cleanCode.range(of: #"^[0-9-]+$"#, options: .regularExpression) != nil {
            return localizationManager.localized("promo_error_device_code")
        }
        return nil
    }

    private func displayDate(_ iso: String) -> String {
        guard !iso.isEmpty else { return localizationManager.localized("promo_activation_unknown_date") }
        return DateFormatterService.shared.formatExpirationDate(
            from: iso,
            language: localizationManager.currentLanguage
        ) ?? iso
    }

    private func localizedPromoError(_ error: Error) -> String {
        let text = error.localizedDescription.lowercased()
        if text.contains("promo_expired") {
            return localizationManager.localized("promo_error_expired")
        }
        if text.contains("promo_used_up") {
            return localizationManager.localized("promo_error_used_up")
        }
        if text.contains("promo_already_redeemed") {
            return localizationManager.localized("promo_error_already_redeemed")
        }
        if text.contains("promo_code_required") {
            return localizationManager.localized("promo_error_required")
        }
        if text.contains("promo_not_found") || text.contains("404") {
            return localizationManager.localized("promo_error_not_found")
        }
        if text.contains("401") {
            return localizationManager.localized("promo_error_login_required")
        }
        if text.contains("mock") || text.contains("unknown function") || text.contains("create_promo_redeem") {
            return localizationManager.localized("promo_error_backend_not_ready")
        }
        return localizationManager.localized("promo_error_generic")
    }
}

/// Пошаговая инструкция: коды App Store Connect («для друзей») → App Store → «Активировать код».
struct AppStoreRedeemCodeHelpSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    private let stepKeys = [
        "appstore_redeem_help_step1",
        "appstore_redeem_help_step2",
        "appstore_redeem_help_step3",
        "appstore_redeem_help_step4",
        "appstore_redeem_help_step5",
        "appstore_redeem_help_step6",
        "appstore_redeem_help_step7",
        "appstore_redeem_help_step8"
    ]

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                HStack {
                    Spacer()
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title2)
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel(localizationManager.localized("appstore_redeem_help_close"))
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)

                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text(localizationManager.localized("appstore_redeem_help_title"))
                            .font(AladdinFamilyType.title2())
                            .foregroundColor(.secondaryGold)
                            .accessibilityAddTraits(.isHeader)

                        Text(localizationManager.localized("appstore_redeem_help_intro"))
                            .font(.body)
                            .foregroundColor(.white.opacity(0.85))
                            .fixedSize(horizontal: false, vertical: true)

                        VStack(alignment: .leading, spacing: 10) {
                            ForEach(stepKeys, id: \.self) { key in
                                Text(localizationManager.localized(key))
                                    .font(.body)
                                    .foregroundColor(.white.opacity(0.92))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(16)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(16)
                        .overlay(
                            RoundedRectangle(cornerRadius: 16)
                                .stroke(Color.secondaryGold.opacity(0.35), lineWidth: 1)
                        )
                    }
                    .padding(20)
                }

                VStack(spacing: 12) {
                    Button {
                        openAppStore()
                    } label: {
                        Text(localizationManager.localized("appstore_redeem_help_open_store"))
                            .font(.bodyBold)
                            .foregroundColor(Color.backgroundDark)
                            .lineLimit(1)
                            .minimumScaleFactor(0.55)
                            .allowsTightening(true)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.secondaryGold)
                            .cornerRadius(14)
                    }
                    .accessibilityIdentifier("appstore_redeem_help_open_store")

                    Button {
                        dismiss()
                    } label: {
                        Text(localizationManager.localized("appstore_redeem_help_close"))
                            .font(.body.weight(.semibold))
                            .foregroundColor(.white.opacity(0.75))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                    }
                    .buttonStyle(.plain)
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
        }
    }

    private func openAppStore() {
        // Opens App Store; user then follows steps (Account → Activate / Redeem code).
        let candidates = [
            URL(string: "itms-apps://apps.apple.com"),
            URL(string: "https://apps.apple.com")
        ].compactMap { $0 }
        guard let url = candidates.first(where: { UIApplication.shared.canOpenURL($0) }) ?? candidates.first else { return }
        UIApplication.shared.open(url)
    }
}
