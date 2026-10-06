import SwiftUI

/// fsl-13 — большая кнопка «Я в порядке» (не GPS).
struct FamilyImOkButton: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var displayName: String
    var style: Style = .standard

    @State private var isSending = false
    @State private var statusMessage: String?
    @State private var didSucceed = false

    enum Style {
        case standard
        case elderly
        case child
    }

    var body: some View {
        VStack(spacing: Spacing.s) {
            Button {
                Task { await send() }
            } label: {
                HStack(spacing: Spacing.m) {
                    if isSending {
                        ProgressView().tint(.white)
                    } else {
                        Image(systemName: "hand.thumbsup.fill")
                            .font(.title2.weight(.bold))
                    }
                    VStack(alignment: .leading, spacing: 2) {
                        Text(localizationManager.localized("im_ok_button_title"))
                            .font(titleFont)
                            .foregroundColor(.white)
                        Text(localizationManager.localized("im_ok_button_subtitle"))
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
                        .fill(didSucceed ? Color.successGreen : Color.secondaryGold)
                )
            }
            .buttonStyle(.plain)
            .disabled(isSending)
            .accessibilityIdentifier("family_im_ok_button")
            .accessibilityLabel(localizationManager.localized("im_ok_button_title"))
            .accessibilityHint(localizationManager.localized("im_ok_button_subtitle"))

            if let statusMessage {
                Text(statusMessage)
                    .font(.caption)
                    .foregroundColor(didSucceed ? .successGreen : .warningOrange)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
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
        let result = await FamilyImOkService.sendImOk(
            displayName: displayName,
            localization: localizationManager
        )
        switch result {
        case .success:
            didSucceed = true
            statusMessage = localizationManager.localized("im_ok_sent_ok")
            HapticFeedback.notification(.success)
        case .failure:
            // Local presence still saved; family chat may be offline.
            didSucceed = true
            statusMessage = localizationManager.localized("im_ok_sent_local")
            HapticFeedback.notification(.warning)
        }
    }
}
