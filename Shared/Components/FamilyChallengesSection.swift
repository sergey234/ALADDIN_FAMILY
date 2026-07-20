import SwiftUI

/// p2-9i — accordion «Свои челленджи» on Family screen.
struct FamilyChallengesSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var service = FamilyChallengesService.shared

    let members: [FamilyMemberData]

    @State private var isExpanded = false
    @State private var draftTitle = ""
    @State private var draftEmoji = "🏁"
    @State private var statusNote: String?
    @State private var medalToggles: [String: Bool] = [:]

    private var canConfigure: Bool {
        FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members)
    }

    var body: some View {
        Group {
            if FamilyChallengesFeature.isEnabled {
                content
            }
        }
    }

    private var content: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            if isExpanded {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_challenge_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                    Text(
                        String(
                            format: localizationManager.localized("family_challenge_limit_fmt"),
                            service.challenges.count,
                            FamilyChallengesFeature.maxActive
                        )
                    )
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.55))

                    ForEach(service.challenges) { challenge in
                        challengeRow(challenge)
                    }

                    if canConfigure {
                        addRow
                    } else if service.challenges.isEmpty {
                        Text(localizationManager.localized("family_challenge_ask_parent"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.65))
                    }

                    if let statusNote {
                        Text(statusNote)
                            .font(.caption)
                            .foregroundColor(.successGreen)
                    }
                }
                .padding(.top, Spacing.s)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: Color(hex: "8B5CF6"))
        .accessibilityIdentifier("family_challenges_section")
        .task {
            await service.refreshFromServer()
            if let draft = FamilyChallengesStore.consumeWellnessDraft() {
                draftTitle = draft
                isExpanded = true
            }
            reloadMedalToggles()
        }
    }

    private var header: some View {
        Button {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                isExpanded.toggle()
            }
            HapticFeedback.impact(.light)
        } label: {
            HStack(alignment: .top, spacing: Spacing.m) {
                Image(systemName: "flag.fill")
                    .font(.title3)
                    .foregroundColor(.secondaryGold)
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_challenge_section_title"))
                        .font(.headline)
                        .foregroundColor(.white)
                    Text(localizationManager.localized("family_challenge_section_hint"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))
                        .multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.7))
            }
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("family_challenges_section_header")
    }

    @ViewBuilder
    private func challengeRow(_ challenge: FamilyChallenge) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(challenge.emoji)
                Text(challenge.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                Spacer()
                if canConfigure {
                    Toggle("", isOn: Binding(
                        get: { challenge.enabled },
                        set: { on in
                            var c = challenge
                            c.enabled = on
                            Task { await service.update(c) }
                        }
                    ))
                    .labelsHidden()
                    .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
                }
            }

            let done = FamilyChallengesStore.isDoneToday(challengeId: challenge.id)
            Button {
                markDone(challenge)
            } label: {
                Text(
                    done
                        ? localizationManager.localized("family_challenge_done_today")
                        : localizationManager.localized("family_challenge_done")
                )
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
            }
            .buttonStyle(.borderedProminent)
            .tint(done ? .gray : Color(hex: "8B5CF6"))
            .disabled(done || !challenge.enabled)
            .accessibilityIdentifier("family_challenge_done_\(challenge.id)")

            if HabitMedalSourcesSettings.masterEnabled {
                let sourceId = challenge.medalSourceId
                Toggle(
                    localizationManager.localized("family_challenge_medal_toggle"),
                    isOn: Binding(
                        get: { medalToggles[sourceId] ?? HabitMedalSourcesSettings.isSourceEnabled(sourceId) },
                        set: { on in
                            medalToggles[sourceId] = on
                            HabitMedalSourcesSettings.setSourceEnabled(sourceId, on)
                        }
                    )
                )
                .font(.caption)
                .toggleStyle(SwitchToggleStyle(tint: .secondaryGold))
            }

            if canConfigure {
                Button(role: .destructive) {
                    Task { await service.delete(id: challenge.id) }
                } label: {
                    Text(localizationManager.localized("family_challenge_delete"))
                        .font(.caption)
                }
                .buttonStyle(.plain)
                .foregroundColor(.dangerRed.opacity(0.9))
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.06))
        .cornerRadius(12)
    }

    private var addRow: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                TextField(localizationManager.localized("family_challenge_placeholder"), text: $draftTitle)
                    .textFieldStyle(.roundedBorder)
                TextField("🏁", text: $draftEmoji)
                    .frame(width: 44)
                    .textFieldStyle(.roundedBorder)
                    .multilineTextAlignment(.center)
            }
            Button {
                Task { await addChallenge() }
            } label: {
                Label(
                    localizationManager.localized("family_challenge_add"),
                    systemImage: "plus.circle.fill"
                )
                .font(.subheadline.weight(.semibold))
            }
            .buttonStyle(.plain)
            .foregroundColor(.secondaryGold)
            .disabled(draftTitle.trimmingCharacters(in: .whitespacesAndNewlines).count < 2)
            .accessibilityIdentifier("family_challenge_add")
        }
    }

    private func addChallenge() async {
        let ok = await service.add(title: draftTitle, emoji: draftEmoji.isEmpty ? "🏁" : draftEmoji)
        if ok {
            draftTitle = ""
            draftEmoji = "🏁"
            statusNote = localizationManager.localized("family_challenge_added")
            reloadMedalToggles()
            HapticFeedback.notification(.success)
        } else {
            statusNote = localizationManager.localized("family_challenge_limit_reached")
            HapticFeedback.notification(.warning)
        }
    }

    private func markDone(_ challenge: FamilyChallenge) {
        if let result = FamilyChallengesStore.markDoneToday(challenge: challenge) {
            statusNote = result.applied
                ? localizationManager.localized("family_challenge_rewarded")
                : localizationManager.localized("family_challenge_done_today")
            HapticFeedback.notification(.success)
        } else {
            statusNote = localizationManager.localized("family_challenge_done_today")
        }
    }

    private func reloadMedalToggles() {
        var map: [String: Bool] = [:]
        for c in service.challenges {
            map[c.medalSourceId] = HabitMedalSourcesSettings.isSourceEnabled(c.medalSourceId)
        }
        medalToggles = map
    }
}
