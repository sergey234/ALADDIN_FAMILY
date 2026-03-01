import SwiftUI
import StoreKit


/**
 * 💳 Payment Recovery View
 * Модальное окно для восстановления после неудачной оплаты
 * Показывает варианты: retry, alternative payment, support
 */
struct PaymentRecoveryView: View {

    // MARK: - Properties

    @Binding var isPresented: Bool
    let errorMessage: String
    let errorType: StoreError?
    let onRetry: () -> Void
    let onAlternativePayment: (() -> Void)?
    let onContactSupport: () -> Void
    let onRestorePurchases: (() -> Void)?

    @State private var showDetailedHelp = false

    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - Body

    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.orange)
                        .padding(.top, Spacing.xl)

                    Text(errorTitle)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, Spacing.l)

                    Text(errorMessage)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, Spacing.l)
                }

                // Recovery Options
                VStack(spacing: Spacing.m) {
                    // Retry Button (primary action)
                    if true { // Always show retry for demo
                        Button(action: {
                            isPresented = false
                            onRetry()
                        }) {
                            HStack {
                                Image(systemName: "arrow.clockwise")
                                Text(localizationManager.localized("payment_recovery_retry"))
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                            .font(.headline)
                        }
                    }

                    // Alternative Payment (if available)
                    if onAlternativePayment != nil {
                        Button(action: {
                            isPresented = false
                            onAlternativePayment?()
                        }) {
                            HStack {
                                Image(systemName: "creditcard")
                                Text(localizationManager.localized("payment_recovery_alternative"))
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                            .background(Color.green.opacity(0.1))
                            .foregroundColor(.green)
                            .cornerRadius(12)
                            .font(.headline)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.green.opacity(0.3), lineWidth: 1)
                            )
                        }
                    }

                    // Restore Purchases
                    if onRestorePurchases != nil {
                        Button(action: {
                            isPresented = false
                            onRestorePurchases?()
                        }) {
                            HStack {
                                Image(systemName: "arrow.triangle.2.circlepath")
                                Text(localizationManager.localized("payment_recovery_restore"))
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                            .background(Color.purple.opacity(0.1))
                            .foregroundColor(.purple)
                            .cornerRadius(12)
                            .font(.headline)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.purple.opacity(0.3), lineWidth: 1)
                            )
                        }
                    }
                }
                .padding(.horizontal, Spacing.xl)

                // Recovery Suggestion
                if let suggestion = errorType?.recoverySuggestion {
                    VStack(spacing: Spacing.s) {
                        Text(localizationManager.localized("payment_recovery_suggestion"))
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)

                        Text(suggestion)
                            .font(.callout)
                            .foregroundColor(.blue)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, Spacing.l)
                    }
                    .padding(.vertical, Spacing.m)
                    .background(Color.blue.opacity(0.05))
                    .cornerRadius(8)
                    .padding(.horizontal, Spacing.xl)
                }

                // Action Buttons Row
                HStack(spacing: Spacing.l) {
                    // Help Button
                    Button(action: {
                        showDetailedHelp = true
                    }) {
                        HStack {
                            Image(systemName: "questionmark.circle.fill")
                            Text(localizationManager.localized("payment_help_button"))
                        }
                        .foregroundColor(.blue)
                        .font(.subheadline)
                    }

                    Spacer()

                    // Support Button
                    Button(action: {
                        onContactSupport()
                        // Don't dismiss here - user might want to contact support while keeping recovery options visible
                    }) {
                        HStack {
                            Image(systemName: "message.fill")
                            Text(localizationManager.localized("payment_recovery_support"))
                        }
                        .foregroundColor(.blue)
                        .font(.subheadline)
                    }
                }
                .padding(.horizontal, Spacing.xl)
                .padding(.bottom, Spacing.xl)

                Spacer()
            }
            .navigationBarItems(trailing:
                Button(action: {
                    isPresented = false
                }) {
                    Image(systemName: "xmark")
                        .foregroundColor(.textSecondary)
                }
            )
            .navigationBarTitle(localizationManager.localized("payment_recovery_title"), displayMode: .inline)
            .sheet(isPresented: $showDetailedHelp) {
                PaymentHelpView(isPresented: $showDetailedHelp, errorType: errorType)
            }
        }
    }

    // MARK: - Helper Properties

    private var errorTitle: String {
        return localizationManager.localized("payment_recovery_title")
    }
}

// MARK: - Preview

#if DEBUG
struct PaymentRecoveryView_Previews: PreviewProvider {
    static var previews: some View {
        PaymentRecoveryView(
            isPresented: .constant(true),
            errorMessage: "Payment was cancelled by user",
            errorType: .paymentCancelled,
            onRetry: {},
            onAlternativePayment: {},
            onContactSupport: {},
            onRestorePurchases: {}
        )
        .environmentObject(LocalizationManager())
    }
}
#endif