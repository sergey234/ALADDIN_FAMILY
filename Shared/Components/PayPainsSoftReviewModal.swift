import SwiftUI

/// Soft review sheet — glass + gold (D1.4 / Snowball language, ALADDIN brand).
struct PayPainsSoftReviewModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var selectedStars: Int = 0
    @State private var appeared = false

    var onWriteReview: () -> Void
    var onLater: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.55)
                .ignoresSafeArea()
                .onTapGesture { onLater() }

            VStack(spacing: Spacing.m) {
                Image(systemName: "shield.checkered")
                    .font(.system(size: 36, weight: .semibold))
                    .foregroundColor(Color.secondaryGold)
                    .frame(width: 64, height: 64)
                    .background(Color.white.opacity(0.12))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 1)
                    )
                    .accessibilityHidden(true)

                Text(localizationManager.localized("pay_pains_review_title"))
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)

                Text(localizationManager.localized("pay_pains_review_subtitle"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.7))
                    .multilineTextAlignment(.center)

                HStack(spacing: 12) {
                    ForEach(1...5, id: \.self) { star in
                        Button {
                            selectedStars = star
                            HapticFeedback.impact(.light)
                        } label: {
                            Image(systemName: star <= selectedStars ? "star.fill" : "star")
                                .font(.system(size: 28))
                                .foregroundColor(Color.secondaryGold)
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel("\(star)")
                    }
                }
                .padding(.vertical, Spacing.xs)
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("pay_pains_review_stars_a11y"))

                Button(action: onWriteReview) {
                    Text(localizationManager.localized("pay_pains_review_write"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.secondaryGold.opacity(0.35))
                        .clipShape(Capsule())
                        .overlay(
                            Capsule()
                                .stroke(Color.secondaryGold.opacity(0.55), lineWidth: 1)
                        )
                }
                .buttonStyle(.plain)

                Button(action: onLater) {
                    Text(localizationManager.localized("pay_pains_review_later"))
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.white.opacity(0.65))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                }
                .buttonStyle(.plain)
            }
            .padding(Spacing.l)
            .frame(maxWidth: 340)
            .stormGlassCard(cornerRadius: 28)
            .overlay(
                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .stroke(Color.secondaryGold.opacity(0.45), lineWidth: 1.5)
            )
            .padding(.horizontal, Spacing.l)
            .scaleEffect(appeared || reduceMotion ? 1 : 0.94)
            .opacity(appeared || reduceMotion ? 1 : 0)
        }
        .accessibilityAddTraits(.isModal)
        .onAppear {
            if reduceMotion {
                appeared = true
            } else {
                withAnimation(.easeOut(duration: 0.28)) { appeared = true }
            }
        }
    }
}
