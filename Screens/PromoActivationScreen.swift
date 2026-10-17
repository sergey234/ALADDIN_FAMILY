import SwiftUI
import UIKit

struct PromoActivationScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var code: String = ""
    @State private var isRedeeming = false
    @State private var statusMessage: String?
    @State private var isSuccess = false
    @AppStorage("subscription_expires_at_iso") private var subscriptionExpiresAtIso: String = ""
    @AppStorage("promo_bonus_active_until") private var promoBonusActiveUntil: String = ""

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(red: 0.04, green: 0.06, blue: 0.12), Color(red: 0.08, green: 0.12, blue: 0.22)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
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
                        explanationCard
                    }
                    .padding(20)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            if code.isEmpty, let pending = navigationManager.pendingPromoCode {
                code = normalizeCode(pending)
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
                                    .tint(.white)
                            }
                            Text(localizationManager.localized("promo_activation_activate"))
                                .font(.subheadline.weight(.bold))
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 18)
                        .padding(.vertical, 12)
                        .frame(maxWidth: .infinity)
                        .background(code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.gray : Color.blue)
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

    private func localPromoInputError(for cleanCode: String) -> String? {
        if cleanCode.hasPrefix("MEM_") {
            return localizationManager.localized("promo_error_member_id")
        }
        if FamilyInviteCodeParser.parse(cleanCode) != nil || cleanCode.hasPrefix("FAM") {
            return localizationManager.localized("promo_error_family_invite_code")
        }
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
