import SwiftUI

/// Grok-style: 1–2 последних реплики + крупный субтитр ответа (не лента пузырей).
struct CompanionDialogueStrip: View {
    @EnvironmentObject private var localizationManager: LocalizationManager

    let messages: [CompanionChatBubble]
    let showResumeStream: Bool
    let showVoiceReconnect: Bool
    let isSending: Bool
    let feedbackBusyId: UUID?
    let onResume: () -> Void
    let onVoiceReconnect: () -> Void
    let onShowHistory: () -> Void
    let onFeedback: (Int, String) -> Void
    var onActionTap: ((CompanionSuggestedActionDTO) -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if showResumeStream {
                Button {
                    HapticFeedback.impact(.light)
                    onResume()
                } label: {
                    Label(localizationManager.localized("companion_conversation_resume_stream"), systemImage: "arrow.clockwise.circle.fill")
                        .font(.subheadline.bold())
                        .foregroundStyle(.purple)
                }
                .disabled(isSending)
                .frame(maxWidth: .infinity, alignment: .center)
                .accessibilityIdentifier("companion_resume_stream_button")
            }
            if showVoiceReconnect {
                Button {
                    HapticFeedback.impact(.light)
                    onVoiceReconnect()
                } label: {
                    Label(localizationManager.localized("companion_conversation_resume_voice"), systemImage: "mic.circle.fill")
                        .font(.subheadline.bold())
                        .foregroundStyle(.orange)
                }
                .disabled(isSending)
                .frame(maxWidth: .infinity, alignment: .center)
                .accessibilityIdentifier("companion_resume_voice_button")
            }

            if let user = penultimateUserLine {
                // W3: dark StormMesh — `.secondary`/`.primary` read as near-black; force light ink.
                Text(user)
                    .font(.caption)
                    .foregroundStyle(Color.white.opacity(0.72))
                    .lineLimit(1)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }

            if isSending {
                HStack(spacing: 8) {
                    ProgressView()
                        .controlSize(.small)
                        .tint(.white.opacity(0.85))
                    Text(localizationManager.localized("companion_sending_reply"))
                        .font(.subheadline)
                        .foregroundStyle(Color.white.opacity(0.75))
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityIdentifier("companion_sending_indicator")
            }

            if let (idx, assistant) = lastAssistantPair {
                Text(assistant.text.isEmpty ? "…" : assistant.text)
                    .font(.title3.weight(.medium))
                    .foregroundStyle(Color.white.opacity(0.95))
                    .lineLimit(5)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .accessibilityIdentifier("companion_hero_subtitle")

                feedbackRow(message: assistant, index: idx)

                if let actions = assistant.suggestedActions, !actions.isEmpty {
                    wellnessActionRow(actions)
                }
            }
            // Empty chat: no center placeholder («Скажи или напиши…») — composer is enough.

            if messages.count > 2 {
                Button {
                    HapticFeedback.selection()
                    onShowHistory()
                } label: {
                    Label(
                        String(format: localizationManager.localized("companion_conversation_full_history"), messages.count),
                        systemImage: "text.bubble"
                    )
                    .font(.caption.weight(.semibold))
                }
                .buttonStyle(.plain)
                .foregroundStyle(.purple)
                .accessibilityIdentifier("companion_full_history_button")
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var penultimateUserLine: String? {
        guard let lastIdx = messages.lastIndex(where: { !$0.isUser }) else { return nil }
        for i in stride(from: lastIdx - 1, through: 0, by: -1) where messages[i].isUser {
            return messages[i].text
        }
        return nil
    }

    private var lastAssistantPair: (Int, CompanionChatBubble)? {
        guard let idx = messages.lastIndex(where: { !$0.isUser }) else { return nil }
        return (idx, messages[idx])
    }

    @ViewBuilder
    private func feedbackRow(message: CompanionChatBubble, index: Int) -> some View {
        HStack(spacing: 20) {
            feedbackButton(
                systemName: message.feedbackVote == "up" ? "hand.thumbsup.fill" : "hand.thumbsup",
                tint: .green,
                label: localizationManager.localized("companion_feedback_up"),
                disabled: feedbackBusyId == message.id || message.feedbackVote != nil
            ) { onFeedback(index, "up") }
            feedbackButton(
                systemName: message.feedbackVote == "down" ? "hand.thumbsdown.fill" : "hand.thumbsdown",
                tint: .orange,
                label: localizationManager.localized("companion_feedback_down"),
                disabled: feedbackBusyId == message.id || message.feedbackVote != nil
            ) { onFeedback(index, "down") }
        }
        .font(.caption)
    }

    private func feedbackButton(
        systemName: String,
        tint: Color,
        label: String,
        disabled: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button {
            HapticFeedback.selection()
            action()
        } label: {
            Image(systemName: systemName)
                .foregroundStyle(tint)
        }
        .disabled(disabled)
        .buttonStyle(.plain)
        .accessibilityLabel(label)
    }

    @ViewBuilder
    private func wellnessActionRow(_ actions: [CompanionSuggestedActionDTO]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(actions) { action in
                Button {
                    HapticFeedback.impact(.light)
                    onActionTap?(action)
                } label: {
                    Text(action.title)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color(hex: "8B5CF6").opacity(0.9))
                        .clipShape(Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("companion_action_\(action.id)")
            }
        }
    }
}
