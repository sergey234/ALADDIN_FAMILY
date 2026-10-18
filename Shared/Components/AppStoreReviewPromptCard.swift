import SwiftUI

/// Lotus-карточка: 1× после онбординга → App Store write-review.
struct AppStoreReviewPromptCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    var onDismiss: () -> Void
    var onRate: () -> Void

    var body: some View {
        ZStack {
            Color.shyamNight.opacity(0.55)
                .ignoresSafeArea()
                .onTapGesture { onDismiss() }
                .accessibilityLabel(localizationManager.localized("store_review_not_now"))

            VStack(spacing: 0) {
                Spacer(minLength: 24)

                VStack(spacing: 18) {
                    Text(localizationManager.localized("store_review_title"))
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.shyamMoon)
                        .multilineTextAlignment(.center)

                    Text(localizationManager.localized("store_review_subtitle"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.shyamMoon)
                        .multilineTextAlignment(.center)

                    Text(localizationManager.localized("store_review_why"))
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.shyamMoon.opacity(0.88))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 4)

                    Text(localizationManager.localized("store_review_body"))
                        .font(.system(size: 15, weight: .regular))
                        .foregroundColor(.shyamMoon.opacity(0.92))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 4)

                    HStack(spacing: 10) {
                        ForEach(0..<5, id: \.self) { _ in
                            Image(systemName: "star.fill")
                                .font(.system(size: 28))
                                .foregroundColor(.shyamGold)
                        }
                    }
                    .padding(.top, 4)
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel(localizationManager.localized("store_review_stars_a11y"))

                    HStack(spacing: 12) {
                        Button(action: onDismiss) {
                            Text(localizationManager.localized("store_review_not_now"))
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.shyamMoon)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 14)
                                .background(
                                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                                        .stroke(Color.shyamMoon.opacity(0.55), lineWidth: 1.5)
                                )
                        }
                        .buttonStyle(.plain)

                        Button(action: onRate) {
                            Text(localizationManager.localized("store_review_cta"))
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 14)
                                .background(
                                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                                        .fill(Color.shyamPeacock)
                                )
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.top, 8)

                    VStack(spacing: 2) {
                        Text(localizationManager.localized("store_review_signoff_line1"))
                        Text(localizationManager.localized("store_review_signoff_line2"))
                    }
                    .font(.system(size: 13, weight: .regular))
                    .foregroundColor(.shyamMoon.opacity(0.78))
                    .multilineTextAlignment(.center)
                    .padding(.top, 10)
                }
                .padding(.horizontal, 22)
                .padding(.vertical, 26)
                .frame(maxWidth: 360)
                .background(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .fill(Color.shyamLotus)
                        .shadow(color: Color.shyamLotus.opacity(0.45), radius: 24, y: 10)
                )
                .padding(.horizontal, 28)

                Spacer(minLength: 24)
            }
        }
        .accessibilityAddTraits(.isModal)
    }
}

#if DEBUG
struct AppStoreReviewPromptCard_Previews: PreviewProvider {
    static var previews: some View {
        AppStoreReviewPromptCard(onDismiss: {}, onRate: {})
            .environmentObject(LocalizationManager.shared)
    }
}
#endif
