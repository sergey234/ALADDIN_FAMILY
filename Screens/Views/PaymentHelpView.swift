import SwiftUI

/**
 * 💡 Payment Help View
 * Подробные инструкции по решению проблем с оплатой
 * Показывает пошаговые решения для распространенных ошибок
 */
struct PaymentHelpView: View {

    // MARK: - Properties

    @Binding var isPresented: Bool
    let errorType: StoreError?

    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - Body

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.xl) {
                    // Header
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Image(systemName: "lightbulb.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.blue)

                        Text(localizationManager.localized("payment_help_title"))
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)

                        Text(localizationManager.localized("payment_help_subtitle"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(.horizontal, Spacing.l)
                    .padding(.top, Spacing.xl)

                    // Solutions based on error type
                    if let errorType = errorType {
                        specificHelpSection(for: errorType)
                    } else {
                        generalHelpSection()
                    }

                    // Common issues section
                    commonIssuesSection()

                    Spacer(minLength: Spacing.xxl)
                }
            }
            .navigationBarItems(trailing:
                Button(action: {
                    isPresented = false
                }) {
                    Image(systemName: "xmark")
                        .foregroundColor(.textSecondary)
                }
            )
            .navigationBarTitle("", displayMode: .inline)
        }
    }

    // MARK: - Specific Help Sections

    @ViewBuilder
    private func specificHelpSection(for errorType: StoreError) -> some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            Text(localizationManager.localized("payment_help_specific_solution"))
                .font(.headline)
                .foregroundColor(.primary)
                .padding(.horizontal, Spacing.l)

            VStack(alignment: .leading, spacing: Spacing.m) {
                // Show general help for all error types
                generalPaymentHelp()
            }
            .padding(.horizontal, Spacing.l)
        }
    }

    private func cancelledPaymentHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("❌ \(localizationManager.localized("payment_help_cancelled_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.orange)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_cancelled_1"))")
                Text("• \(localizationManager.localized("payment_help_cancelled_2"))")
                Text("• \(localizationManager.localized("payment_help_cancelled_3"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    private func paymentNotAllowedHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("🚫 \(localizationManager.localized("payment_help_not_allowed_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.red)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_not_allowed_1"))")
                Text("• \(localizationManager.localized("payment_help_not_allowed_2"))")
                Text("• \(localizationManager.localized("payment_help_not_allowed_3"))")
                Text("• \(localizationManager.localized("payment_help_not_allowed_4"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    private func networkErrorHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("📡 \(localizationManager.localized("payment_help_network_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.blue)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_network_1"))")
                Text("• \(localizationManager.localized("payment_help_network_2"))")
                Text("• \(localizationManager.localized("payment_help_network_3"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    private func productUnavailableHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("🌍 \(localizationManager.localized("payment_help_unavailable_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.purple)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_unavailable_1"))")
                Text("• \(localizationManager.localized("payment_help_unavailable_2"))")
                Text("• \(localizationManager.localized("payment_help_unavailable_3"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    private func cloudPermissionHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("☁️ \(localizationManager.localized("payment_help_cloud_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.gray)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_cloud_1"))")
                Text("• \(localizationManager.localized("payment_help_cloud_2"))")
                Text("• \(localizationManager.localized("payment_help_cloud_3"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    private func generalPaymentHelp() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("💡 \(localizationManager.localized("payment_help_general_title"))")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.green)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("• \(localizationManager.localized("payment_help_general_1"))")
                Text("• \(localizationManager.localized("payment_help_general_2"))")
                Text("• \(localizationManager.localized("payment_help_general_3"))")
            }
            .font(.body)
            .foregroundColor(.textSecondary)
        }
    }

    // MARK: - General Help Section

    private func generalHelpSection() -> some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            Text(localizationManager.localized("payment_help_general_solutions"))
                .font(.headline)
                .foregroundColor(.primary)
                .padding(.horizontal, Spacing.l)

            VStack(alignment: .leading, spacing: Spacing.m) {
                generalPaymentHelp()
            }
            .padding(.horizontal, Spacing.l)
        }
    }

    // MARK: - Common Issues Section

    private func commonIssuesSection() -> some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            Text(localizationManager.localized("payment_help_common_issues"))
                .font(.headline)
                .foregroundColor(.primary)
                .padding(.horizontal, Spacing.l)

            VStack(alignment: .leading, spacing: Spacing.m) {
                // Issue 1: Payment method issues
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("💳 \(localizationManager.localized("payment_help_issue_payment_method"))")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)

                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text("• \(localizationManager.localized("payment_help_issue_payment_1"))")
                        Text("• \(localizationManager.localized("payment_help_issue_payment_2"))")
                        Text("• \(localizationManager.localized("payment_help_issue_payment_3"))")
                    }
                    .font(.body)
                    .foregroundColor(.textSecondary)
                }

                // Issue 2: Account restrictions
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("🔒 \(localizationManager.localized("payment_help_issue_account"))")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)

                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text("• \(localizationManager.localized("payment_help_issue_account_1"))")
                        Text("• \(localizationManager.localized("payment_help_issue_account_2"))")
                    }
                    .font(.body)
                    .foregroundColor(.textSecondary)
                }

                // Issue 3: App Store issues
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("📱 \(localizationManager.localized("payment_help_issue_app_store"))")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)

                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text("• \(localizationManager.localized("payment_help_issue_app_store_1"))")
                        Text("• \(localizationManager.localized("payment_help_issue_app_store_2"))")
                        Text("• \(localizationManager.localized("payment_help_issue_app_store_3"))")
                    }
                    .font(.body)
                    .foregroundColor(.textSecondary)
                }
            }
            .padding(.horizontal, Spacing.l)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct PaymentHelpView_Previews: PreviewProvider {
    static var previews: some View {
        PaymentHelpView(isPresented: .constant(true), errorType: .paymentCancelled)
            .environmentObject(LocalizationManager())
    }
}
#endif