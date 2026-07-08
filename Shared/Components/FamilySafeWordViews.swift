import SwiftUI

// MARK: - fws-01 Family safe-word card (all members see status; parent/elderly can configure)

struct FamilySafeWordCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var service = FamilySafeWordService.shared

    let members: [FamilyMemberData]
    @State private var showSetupSheet = false
    @State private var showVerifySheet = false

    private var canConfigure: Bool {
        FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members)
    }

    private var isConfigured: Bool {
        service.isConfiguredLocally || service.isConfiguredOnServer
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.s) {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Label(
                        localizationManager.localized("family_safe_word_title"),
                        systemImage: "key.horizontal.fill"
                    )
                    .font(.headline)
                    .foregroundColor(.white)

                    Text(localizationManager.localized("family_safe_word_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))
                        .fixedSize(horizontal: false, vertical: true)

                    statusBadge
                }
                Spacer(minLength: Spacing.s)
            }

            if canConfigure {
                Button {
                    HapticFeedback.impact(.light)
                    showSetupSheet = true
                } label: {
                    Label(
                        localizationManager.localized(
                            isConfigured ? "family_safe_word_change_button" : "family_safe_word_setup_button"
                        ),
                        systemImage: isConfigured ? "arrow.triangle.2.circlepath" : "plus.circle.fill"
                    )
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .foregroundColor(.secondaryGold)
                .accessibilityIdentifier("family_safe_word_setup_button")
            } else if isConfigured {
                Button {
                    HapticFeedback.impact(.light)
                    showVerifySheet = true
                } label: {
                    Label(
                        localizationManager.localized("family_safe_word_practice_button"),
                        systemImage: "checkmark.shield"
                    )
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                .foregroundColor(.primaryBlue)
                .accessibilityIdentifier("family_safe_word_practice_button")
            } else {
                Text(localizationManager.localized("family_safe_word_ask_parent"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.65))
            }

            Text(localizationManager.localized("family_safe_word_not_recovery_hint"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.5))
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("family_safe_word_card")
        .task {
            service.refreshLocalStatus()
            await service.refreshServerStatus()
        }
        .sheet(isPresented: $showSetupSheet) {
            FamilySafeWordSetupSheet(members: members)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showVerifySheet) {
            FamilySafeWordVerifySheet(context: "family_practice")
                .environmentObject(localizationManager)
        }
    }

    @ViewBuilder
    private var statusBadge: some View {
        Text(
            localizationManager.localized(
                isConfigured ? "family_safe_word_status_on" : "family_safe_word_status_off"
            )
        )
        .font(.caption.weight(.semibold))
        .padding(.horizontal, Spacing.s)
        .padding(.vertical, 4)
        .background((isConfigured ? Color.successGreen : Color.warningOrange).opacity(0.25))
        .foregroundColor(isConfigured ? .successGreen : .warningOrange)
        .clipShape(Capsule())
        .accessibilityIdentifier("family_safe_word_status_badge")
    }
}

// MARK: - Setup (parent/elderly + biometric gate)

struct FamilySafeWordSetupSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var service = FamilySafeWordService.shared

    let members: [FamilyMemberData]

    @State private var phrase = ""
    @State private var confirmPhrase = ""
    @State private var errorMessage: String?
    @State private var isSaving = false

    var body: some View {
        WellnessNavigationStack {
            Form {
                Section {
                    Text(localizationManager.localized("family_safe_word_setup_intro"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Section(localizationManager.localized("family_safe_word_phrase_section")) {
                    SecureField(
                        localizationManager.localized("family_safe_word_phrase_placeholder"),
                        text: $phrase
                    )
                    SecureField(
                        localizationManager.localized("family_safe_word_confirm_placeholder"),
                        text: $confirmPhrase
                    )
                }

                Section {
                    Text(localizationManager.localized("family_safe_word_rules"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let errorMessage {
                    Section {
                        Text(errorMessage)
                            .foregroundColor(.dangerRed)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("family_safe_word_setup_title"))
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button(localizationManager.localized("common_cancel")) { dismiss() },
                trailing: Button(localizationManager.localized("common_save")) {
                    Task { await savePhrase() }
                }
                .disabled(isSaving || phrase.isEmpty || confirmPhrase.isEmpty)
            )
        }
        .modifier(AntifakeMediumSheetDetentModifier())
    }

    @MainActor
    private func savePhrase() async {
        guard FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members) else {
            errorMessage = localizationManager.localized("family_safe_word_parent_only")
            return
        }

        let biometricsOK = await SecurityManager.shared.authenticateWithBiometrics()
        guard biometricsOK || !SecurityManager.shared.biometricAuthAvailable else {
            errorMessage = localizationManager.localized("family_safe_word_biometric_required")
            return
        }

        guard phrase == confirmPhrase else {
            errorMessage = localizationManager.localized("family_safe_word_mismatch_confirm")
            return
        }

        isSaving = true
        errorMessage = nil
        defer { isSaving = false }

        do {
            try service.savePhraseLocally(phrase)
            try await service.setPhraseOnServer(phrase)
            HapticFeedback.notification(.success)
            dismiss()
        } catch let error as FamilySafeWordError {
            errorMessage = localizedValidation(error)
        } catch {
            errorMessage = localizationManager.localized("family_safe_word_save_failed")
        }
    }

    private func localizedValidation(_ error: FamilySafeWordError) -> String {
        switch error {
        case .validation(let code):
            return localizationManager.localized("family_safe_word_error_\(code)")
        case .parentGateFailed:
            return localizationManager.localized("family_safe_word_biometric_required")
        case .noFamily:
            return localizationManager.localized("family_safe_word_no_family")
        case .persistenceFailed:
            return localizationManager.localized("family_safe_word_save_failed")
        }
    }
}

// MARK: - Verify (antifake + practice)

struct FamilySafeWordVerifySheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var service = FamilySafeWordService.shared

    let context: String
    var onResult: ((Bool) -> Void)?

    @State private var phrase = ""
    @State private var feedback: String?
    @State private var isVerifying = false

    var body: some View {
        WellnessNavigationStack {
            Form {
                Section {
                    Text(localizationManager.localized("family_safe_word_verify_intro"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Section(localizationManager.localized("family_safe_word_phrase_section")) {
                    SecureField(
                        localizationManager.localized("family_safe_word_phrase_placeholder"),
                        text: $phrase
                    )
                }

                if let feedback {
                    Section {
                        Text(feedback)
                            .foregroundColor(feedback.contains("✓") ? .successGreen : .dangerRed)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("family_safe_word_verify_title"))
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button(localizationManager.localized("common_cancel")) { dismiss() },
                trailing: Button(localizationManager.localized("family_safe_word_verify_action")) {
                    Task { await verify() }
                }
                .disabled(isVerifying || phrase.isEmpty)
            )
        }
        .modifier(AntifakeMediumSheetDetentModifier())
    }

    @MainActor
    private func verify() async {
        isVerifying = true
        defer { isVerifying = false }

        let localMatch = service.verifyLocally(phrase)
        let serverResult = await service.verifyOnServer(phrase, context: context)

        let match = serverResult.configured ? serverResult.match : localMatch
        if match {
            feedback = localizationManager.localized("family_safe_word_verify_match")
            HapticFeedback.notification(.success)
            onResult?(true)
            dismiss()
        } else {
            if serverResult.parentsNotified > 0 {
                feedback = localizationManager.localized("family_safe_word_verify_mismatch_notified")
            } else {
                feedback = localizationManager.localized("family_safe_word_verify_mismatch")
            }
            HapticFeedback.notification(.error)
            onResult?(false)
        }
    }
}

private struct AntifakeMediumSheetDetentModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.presentationDetents([.medium])
        } else {
            content
        }
    }
}
