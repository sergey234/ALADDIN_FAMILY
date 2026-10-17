import SwiftUI

// MARK: - fws-01 Family safe-word card (all members see status; parent/elderly can configure)

struct FamilySafeWordCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
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
                        systemImage: "key.fill"
                    )
                    .font(.headline)
                    .foregroundColor(.white)

                    Text(localizationManager.localized("family_safe_word_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.92))
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
                .foregroundColor(.white.opacity(0.85))
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
                .environmentObject(navigationManager)
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
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var service = FamilySafeWordService.shared

    let members: [FamilyMemberData]

    @State private var phrase = ""
    @State private var confirmPhrase = ""
    @State private var errorMessage: String?
    @State private var isSaving = false
    @State private var isPhraseVisible = false
    /// Показать инструкцию: нет familyId на устройстве или ошибка `.noFamily` после Save.
    @State private var showNoFamilyHelp = false

    private var hasServerFamilyId: Bool {
        !FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .isEmpty
    }

    var body: some View {
        WellnessNavigationStack {
            Form {
                Section {
                    Text(localizationManager.localized("family_safe_word_setup_what"))
                        .font(.subheadline)
                        .foregroundColor(.primary)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(localizationManager.localized("family_safe_word_setup_intro"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if showNoFamilyHelp || !hasServerFamilyId {
                    Section {
                        noFamilyHelpBlock
                    }
                    .accessibilityIdentifier("family_safe_word_no_family_help")
                }

                Section(localizationManager.localized("family_safe_word_phrase_section")) {
                    if isPhraseVisible {
                        TextField(
                            localizationManager.localized("family_safe_word_phrase_placeholder"),
                            text: $phrase
                        )
                        .textContentType(.password)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        TextField(
                            localizationManager.localized("family_safe_word_confirm_placeholder"),
                            text: $confirmPhrase
                        )
                        .textContentType(.password)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    } else {
                        SecureField(
                            localizationManager.localized("family_safe_word_phrase_placeholder"),
                            text: $phrase
                        )
                        SecureField(
                            localizationManager.localized("family_safe_word_confirm_placeholder"),
                            text: $confirmPhrase
                        )
                    }
                    Button {
                        isPhraseVisible.toggle()
                    } label: {
                        Label(
                            localizationManager.localized(
                                isPhraseVisible
                                    ? "family_safe_word_hide_phrase"
                                    : "family_safe_word_show_phrase"
                            ),
                            systemImage: isPhraseVisible ? "eye.slash.fill" : "eye.fill"
                        )
                    }
                    .accessibilityIdentifier("family_safe_word_visibility_toggle")
                }

                Section {
                    Text(localizationManager.localized("family_safe_word_rules"))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let errorMessage, !showNoFamilyHelp {
                    Section {
                        Text(errorMessage)
                            .foregroundColor(.dangerRed)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("family_safe_word_setup_title"))
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button(localizationManager.localized("common_cancel")) {
                    print("🔐 FamilySafeWord: Cancel tapped")
                    dismiss()
                },
                trailing: Button(localizationManager.localized("common_save")) {
                    Task { await savePhrase() }
                }
                .disabled(isSaving || phrase.isEmpty || confirmPhrase.isEmpty || !hasServerFamilyId)
            )
            .onAppear {
                if !hasServerFamilyId {
                    showNoFamilyHelp = true
                }
            }
        }
        .modifier(AntifakeMediumSheetDetentModifier())
    }

    @ViewBuilder
    private var noFamilyHelpBlock: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("family_safe_word_no_family"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.dangerRed)
                .fixedSize(horizontal: false, vertical: true)

            Text(localizationManager.localized("family_safe_word_no_family_how_title"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.primary)
                .padding(.top, 2)

            VStack(alignment: .leading, spacing: 6) {
                howToStep(number: 1, key: "family_safe_word_no_family_step_1")
                howToStep(number: 2, key: "family_safe_word_no_family_step_2")
                howToStep(number: 3, key: "family_safe_word_no_family_step_3")
                howToStep(number: 4, key: "family_safe_word_no_family_step_4")
            }

            Button {
                print("🔐 FamilySafeWord: Open family connect CTA")
                dismiss()
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                    navigationManager.navigateTo(.addMemberOptions)
                }
            } label: {
                Text(localizationManager.localized("family_safe_word_no_family_cta"))
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)
            .foregroundColor(.primaryBlue)
            .padding(.top, 4)
            .accessibilityIdentifier("family_safe_word_no_family_cta")
        }
        .padding(.vertical, 2)
    }

    private func howToStep(number: Int, key: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Text("\(number).")
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondary)
                .frame(width: 18, alignment: .leading)
            Text(localizationManager.localized(key))
                .font(.caption)
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    @MainActor
    private func savePhrase() async {
        guard hasServerFamilyId else {
            showNoFamilyHelp = true
            errorMessage = localizationManager.localized("family_safe_word_no_family")
            return
        }

        guard FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members) else {
            showNoFamilyHelp = false
            errorMessage = localizationManager.localized("family_safe_word_parent_only")
            return
        }

        let biometricsOK = await SecurityManager.shared.authenticateWithBiometrics()
        guard biometricsOK || !SecurityManager.shared.biometricAuthAvailable else {
            showNoFamilyHelp = false
            errorMessage = localizationManager.localized("family_safe_word_biometric_required")
            return
        }

        guard phrase == confirmPhrase else {
            showNoFamilyHelp = false
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
            if case .noFamily = error {
                showNoFamilyHelp = true
            } else {
                showNoFamilyHelp = false
            }
            errorMessage = localizedValidation(error)
        } catch {
            showNoFamilyHelp = false
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
    @State private var isPhraseVisible = false

    var body: some View {
        WellnessNavigationStack {
            Form {
                Section {
                    Text(localizationManager.localized("family_safe_word_verify_intro"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Section(localizationManager.localized("family_safe_word_phrase_section")) {
                    if isPhraseVisible {
                        TextField(
                            localizationManager.localized("family_safe_word_phrase_placeholder"),
                            text: $phrase
                        )
                        .textContentType(.password)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                    } else {
                        SecureField(
                            localizationManager.localized("family_safe_word_phrase_placeholder"),
                            text: $phrase
                        )
                    }
                    Button {
                        isPhraseVisible.toggle()
                    } label: {
                        Label(
                            localizationManager.localized(
                                isPhraseVisible
                                    ? "family_safe_word_hide_phrase"
                                    : "family_safe_word_show_phrase"
                            ),
                            systemImage: isPhraseVisible ? "eye.slash.fill" : "eye.fill"
                        )
                    }
                    .accessibilityIdentifier("family_safe_word_verify_visibility_toggle")
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
                leading: Button(localizationManager.localized("common_cancel")) {
                    print("🔐 FamilySafeWord: Verify Cancel tapped")
                    dismiss()
                },
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
