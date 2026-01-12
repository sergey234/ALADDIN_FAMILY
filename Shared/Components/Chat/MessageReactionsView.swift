import SwiftUI

/**
 * 😊 Message Reactions View
 * UI для отображения и добавления реакций на сообщения
 */

struct MessageReactionsView: View {
    let message: FamilyChatMessage
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onAddReaction: (String) -> Void
    let onRemoveReaction: (String) -> Void
    @State private var showReactionPicker: Bool = false
    
    // Популярные эмодзи
    private let popularEmojis = ["👍", "❤️", "😂", "😮", "😢", "🙏", "🔥", "🎉"]
    
    var body: some View {
        HStack(spacing: Spacing.xs) {
            // Существующие реакции
            ForEach(groupedReactions, id: \.emoji) { reaction in
                ReactionButton(
                    emoji: reaction.emoji,
                    count: reaction.count,
                    isUserReacted: reaction.isUserReacted,
                    onTap: {
                        if reaction.isUserReacted {
                            onRemoveReaction(reaction.emoji)
                        } else {
                            onAddReaction(reaction.emoji)
                        }
                    }
                )
            }
            
            // Кнопка добавления реакции
            Button(action: {
                showReactionPicker = true
            }) {
                Image(systemName: "face.smiling")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .padding(Spacing.xs)
                    .background(Color.surfaceDark.opacity(0.5))
                    .cornerRadius(CornerRadius.small)
            }
        }
        .sheet(isPresented: $showReactionPicker) {
            ReactionPickerView(
                popularEmojis: popularEmojis,
                onSelect: { emoji in
                    onAddReaction(emoji)
                    showReactionPicker = false
                }
            )
        }
    }
    
    private var groupedReactions: [GroupedReaction] {
        let reactions = message.reactions
        guard !reactions.isEmpty else { return [] }
        
        let grouped = Dictionary(grouping: reactions) { $0.emoji }
        return grouped.map { emoji, reactionList in
            GroupedReaction(
                emoji: emoji,
                count: reactionList.count,
                isUserReacted: reactionList.contains { $0.userId == "current_user" } // TODO: Получить реальный userId
            )
        }.sorted { $0.count > $1.count }
    }
}

// MARK: - Grouped Reaction

struct GroupedReaction {
    let emoji: String
    let count: Int
    let isUserReacted: Bool
}

// MARK: - Reaction Button

struct ReactionButton: View {
    let emoji: String
    let count: Int
    let isUserReacted: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: Spacing.xxs) {
                Text(emoji)
                    .font(.caption)
                Text("\(count)")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            .padding(.horizontal, Spacing.xs)
            .padding(.vertical, Spacing.xxs)
            .background(isUserReacted ? Color.secondaryGold.opacity(0.3) : Color.surfaceDark.opacity(0.5))
            .cornerRadius(CornerRadius.small)
        }
    }
}

// MARK: - Reaction Picker View

struct ReactionPickerView: View {
    let popularEmojis: [String]
    let onSelect: (String) -> Void
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            Text("Выберите реакцию")
                .font(.headline)
                .padding()
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: Spacing.m) {
                ForEach(popularEmojis, id: \.self) { emoji in
                    Button(action: {
                        onSelect(emoji)
                    }) {
                        Text(emoji)
                            .font(.largeTitle)
                            .frame(width: 60, height: 60)
                            .background(Color.surfaceDark.opacity(0.3))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
            }
            .padding()
            
            Button(action: { dismiss() }) {
                Text("Отмена")
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .padding()
            }
        }
        .padding()
    }
}

