import SwiftUI

// MARK: - UX-36 W10 / SH-1 — «Семейная вторая рука» для доверенного (parent)

/// Пакет «Защита родителей 60+»: CTA от сына/дочери, чеклист статусов, мастер шагов.
struct FamilySecondHandPackCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    let members: [FamilyMemberData]
    @State private var showSetupSheet = false

    private var actorRole: FamilyAccessPolicy.ActorRole {
        FamilyAccessPolicy.resolveActorRole(members: members)
    }

    /// Доверенный взрослый подключает пакет — не 60+ и не sole-teen.
    private var showsTrustedCTA: Bool {
        actorRole == .parent
    }

    private var hasElderlyMember: Bool {
        members.contains { $0.role == .elderly }
    }

    private var checklist: [(key: String, ok: Bool)] {
        let safeWord = FamilySafeWordService.shared.isConfiguredLocally
            || FamilySafeWordService.shared.isConfiguredOnServer
        // Soft hint: list synced to device (extension enable is on elderly phone).
        let callFilterHint = !AntifakeCallDirectoryStore.load().identifiedNumbers.isEmpty
        return [
            ("family_second_hand_check_scam", true),
            ("family_second_hand_check_safeword", safeWord),
            ("family_second_hand_check_callfilter", callFilterHint),
            ("family_second_hand_check_needhelp", true),
            ("family_second_hand_check_places", true)
        ]
    }

    var body: some View {
        Group {
            if showsTrustedCTA {
                trustedPackBody
            } else if actorRole == .teenager {
                FamilySecondHandTeenHelpCard()
                    .environmentObject(localizationManager)
            }
        }
    }

    private var trustedPackBody: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("family_second_hand_pack_title"),
                systemImage: "hand.raised.fill"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(localizationManager.localized("family_second_hand_pack_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)

            if hasElderlyMember {
                Text(localizationManager.localized("family_second_hand_pack_has_elderly"))
                    .font(.caption2)
                    .foregroundColor(.secondaryGold)
            } else {
                Text(localizationManager.localized("family_second_hand_pack_add_elderly_hint"))
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.7))
            }

            VStack(alignment: .leading, spacing: Spacing.xs) {
                ForEach(checklist, id: \.key) { row in
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: row.ok ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(row.ok ? .successGreen : .white.opacity(0.45))
                        Text(localizationManager.localized(row.key))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.92))
                        Spacer(minLength: 0)
                    }
                }
            }
            .padding(.top, Spacing.xs)
            .accessibilityIdentifier("family_second_hand_checklist")

            Button {
                HapticFeedback.impact(.light)
                showSetupSheet = true
            } label: {
                Label(
                    localizationManager.localized("family_second_hand_pack_cta"),
                    systemImage: "person.2.fill"
                )
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)
            .foregroundColor(.secondaryGold)
            .accessibilityIdentifier("family_second_hand_pack_cta")

        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("family_second_hand_pack_card")
        .sheet(isPresented: $showSetupSheet) {
            FamilySecondHandSetupSheet(isPresented: $showSetupSheet)
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
    }
}

// MARK: - SH-1b setup wizard (short steps for parent phone → elderly phone)

struct FamilySecondHandSetupSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    /// Binding — надёжнее `dismiss()` внутри NavigationView/sheet на iOS 15.
    @Binding var isPresented: Bool

    private var usesIOS18AppsPhonePath: Bool {
        if #available(iOS 18.0, *) { return true }
        return false
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("family_second_hand_setup_intro"))
                        .font(.body)
                        .foregroundColor(.primary)
                        .fixedSize(horizontal: false, vertical: true)

                    setupStepRow(number: 1, textKey: "family_second_hand_step_1")

                    // Step 2 — same tap path as Antifake Call Filter (Settings → Phone → …)
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack(alignment: .top, spacing: Spacing.s) {
                            Text("2.")
                                .font(.headline)
                                .foregroundColor(.secondaryGold)
                            Text(localizationManager.localized("family_second_hand_step_2"))
                                .font(.body)
                                .foregroundColor(.primary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        VStack(alignment: .leading, spacing: 6) {
                            callFilterSubstep("antifake_call_directory_setup_step1")
                            if usesIOS18AppsPhonePath {
                                callFilterSubstep("antifake_call_directory_setup_step2_ios18")
                                callFilterSubstep("antifake_call_directory_setup_step3_ios18")
                                callFilterSubstep("antifake_call_directory_setup_step4_ios18")
                            } else {
                                callFilterSubstep("antifake_call_directory_setup_step2")
                                callFilterSubstep("antifake_call_directory_setup_step3")
                                callFilterSubstep("antifake_call_directory_setup_step4")
                            }
                            Text(localizationManager.localized("antifake_call_directory_setup_step5_retry"))
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.leading, 28)
                        }
                        .padding(.leading, 4)
                    }

                    setupStepRow(number: 3, textKey: "family_second_hand_step_3")
                    setupStepRow(number: 4, textKey: "family_second_hand_step_4")

                    Button {
                        FamilyScamCallFunnel.log(.secondHandSetup, source: "setup_sheet")
                        openElderlyAfterClosingSheet()
                    } label: {
                        Text(localizationManager.localized("family_second_hand_open_elderly"))
                            .font(.headline)
                            .foregroundColor(.primary)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.secondaryGold.opacity(0.25))
                            .cornerRadius(CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("family_second_hand_open_elderly")

                    Button {
                        closeSheet()
                    } label: {
                        Text(localizationManager.localized("family_second_hand_setup_done"))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.primaryBlue)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.s)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("family_second_hand_setup_done_body")
                }
                .padding(Spacing.l)
            }
            .navigationBarTitle(
                localizationManager.localized("family_second_hand_setup_title"),
                displayMode: .inline
            )
            .navigationBarItems(
                leading: Button(localizationManager.localized("family_second_hand_setup_done")) {
                    closeSheet()
                }
                .foregroundColor(.primaryBlue)
                .accessibilityIdentifier("family_second_hand_setup_done")
            )
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    private func setupStepRow(number: Int, textKey: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Text("\(number).")
                .font(.headline)
                .foregroundColor(.secondaryGold)
            Text(localizationManager.localized(textKey))
                .font(.body)
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func callFilterSubstep(_ key: String) -> some View {
        Text(localizationManager.localized(key))
            .font(.subheadline)
            .foregroundColor(.primary.opacity(0.9))
            .fixedSize(horizontal: false, vertical: true)
            .padding(.leading, 28)
    }

    private func closeSheet() {
        HapticFeedback.impact(.light)
        isPresented = false
    }

    private func openElderlyAfterClosingSheet() {
        HapticFeedback.impact(.medium)
        isPresented = false
        // Сначала закрыть sheet, потом сменить корень — иначе navigateTo может
        // сработать «под» модалкой / no-op если уже elderly.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            if navigationManager.currentScreen != .elderlyInterface {
                navigationManager.navigateTo(.elderlyInterface)
            }
        }
    }
}

// MARK: - SH-3 teen 13+ witness card (not sole-admin)

struct FamilySecondHandTeenHelpCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("family_second_hand_teen_title"),
                systemImage: "person.fill.checkmark"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(localizationManager.localized("family_second_hand_teen_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                teenLine("family_second_hand_teen_tip_1")
                teenLine("family_second_hand_teen_tip_2")
                teenLine("family_second_hand_teen_tip_3")
            }

            Text(localizationManager.localized("family_second_hand_teen_not_admin"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("family_second_hand_teen_card")
    }

    private func teenLine(_ key: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.xs) {
            Text("•")
            Text(localizationManager.localized(key))
                .font(.caption)
                .foregroundColor(.white.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}
