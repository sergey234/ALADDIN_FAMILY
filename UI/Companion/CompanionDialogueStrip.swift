import SwiftUI

/// Grok-style: 1–2 последних реплики + крупный субтитр ответа (не лента пузырей).
struct CompanionDialogueStrip: View {
    let messages: [CompanionChatBubble]
    let showResumeStream: Bool
    let isSending: Bool
    let feedbackBusyId: UUID?
    let onResume: () -> Void
    let onShowHistory: () -> Void
    let onFeedback: (Int, String) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if showResumeStream {
                Button(action: onResume) {
                    Label("Продолжить загрузку", systemImage: "arrow.clockwise.circle.fill")
                        .font(.subheadline.bold())
                        .foregroundStyle(.purple)
                }
                .disabled(isSending)
                .frame(maxWidth: .infinity, alignment: .center)
            }

            if let user = penultimateUserLine {
                Text(user)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }

            if let (idx, assistant) = lastAssistantPair {
                Text(assistant.text.isEmpty ? "…" : assistant.text)
                    .font(.title3.weight(.medium))
                    .foregroundStyle(.primary)
                    .lineLimit(5)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .accessibilityIdentifier("companion_hero_subtitle")

                feedbackRow(message: assistant, index: idx)
            } else if messages.isEmpty {
                Text("Скажи или напиши — я рядом.")
                    .font(.title3.weight(.medium))
                    .foregroundStyle(.secondary)
            }

            if messages.count > 2 {
                Button(action: onShowHistory) {
                    Label("Вся история (\(messages.count))", systemImage: "text.bubble")
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.plain)
                .foregroundStyle(.purple)
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
                disabled: feedbackBusyId == message.id || message.feedbackVote != nil
            ) { onFeedback(index, "up") }
            feedbackButton(
                systemName: message.feedbackVote == "down" ? "hand.thumbsdown.fill" : "hand.thumbsdown",
                tint: .orange,
                disabled: feedbackBusyId == message.id || message.feedbackVote != nil
            ) { onFeedback(index, "down") }
        }
        .font(.caption)
    }

    private func feedbackButton(
        systemName: String,
        tint: Color,
        disabled: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .foregroundStyle(tint)
        }
        .disabled(disabled)
        .buttonStyle(.plain)
    }
}
