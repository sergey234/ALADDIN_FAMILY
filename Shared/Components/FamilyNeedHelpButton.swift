import SwiftUI

/// sos — красная кнопка «Нужна помощь» (зеркало «Я в порядке»). Confirm перед отправкой.
struct FamilyNeedHelpButton: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var displayName: String
    var style: FamilyImOkButton.Style = .child

    @State private var showConfirm = false
    @State private var isSending = false
    @State private var statusMessage: String?
    @State private var didSucceed = false

    var body: some View {
        VStack(spacing: Spacing.s) {
            Button {
                showConfirm = true
            } label: {
                HStack(spacing: Spacing.m) {
                    if isSending {
                        ProgressView().tint(.white)
                    } else {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.title2.weight(.bold))
                            .foregroundColor(.white)
                    }
                    VStack(alignment: .leading, spacing: 2) {
                        Text(localizationManager.localized("need_help_button_title"))
                            .font(titleFont)
                            .foregroundColor(.white)
                        Text(localizationManager.localized("need_help_button_subtitle"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Spacer(minLength: 0)
                }
                .padding(padding)
                .frame(maxWidth: .infinity, minHeight: minHeight)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(Color.dangerRed)
                )
            }
            .buttonStyle(.plain)
            .disabled(isSending)
            .accessibilityIdentifier("family_need_help_button")
            .accessibilityLabel(localizationManager.localized("need_help_button_title"))
            .accessibilityHint(localizationManager.localized("need_help_button_subtitle"))

            if let statusMessage {
                Text(statusMessage)
                    .font(.caption)
                    .foregroundColor(didSucceed ? .dangerRed : .warningOrange)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .accessibilityIdentifier("family_need_help_status")
            }
        }
        .confirmationDialog(
            localizationManager.localized("need_help_confirm_title"),
            isPresented: $showConfirm,
            titleVisibility: .visible
        ) {
            Button(localizationManager.localized("need_help_confirm_send"), role: .destructive) {
                Task { await send() }
            }
            .accessibilityIdentifier("family_need_help_confirm_send")
            Button(localizationManager.localized("need_help_confirm_cancel"), role: .cancel) {}
                .accessibilityIdentifier("family_need_help_confirm_cancel")
        } message: {
            Text(localizationManager.localized("need_help_confirm_body"))
        }
    }

    private var titleFont: Font {
        switch style {
        case .elderly: return .system(size: 22, weight: .bold)
        case .child: return .system(size: 18, weight: .bold)
        case .standard: return .headline.weight(.bold)
        }
    }

    private var padding: CGFloat {
        style == .elderly ? Spacing.l : Spacing.m
    }

    private var minHeight: CGFloat {
        style == .elderly ? 72 : 56
    }

    @MainActor
    private func send() async {
        isSending = true
        statusMessage = nil
        defer { isSending = false }
        let result = await FamilyImOkService.sendNeedHelp(
            displayName: displayName,
            localization: localizationManager
        )
        switch result {
        case .success:
            didSucceed = true
            statusMessage = localizationManager.localized("need_help_sent_ok")
            HapticFeedback.notification(.warning)
        case .failure:
            didSucceed = true
            statusMessage = localizationManager.localized("need_help_sent_local")
            HapticFeedback.notification(.error)
        }
    }
}
