import SwiftUI

/**
 * ⚙️ Message Actions Menu
 * Меню действий для сообщений (удалить, редактировать, ответить и т.д.)
 */

struct MessageActionsMenu: View {
    let message: FamilyChatMessage
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onDelete: () -> Void
    let onEdit: () -> Void
    let onReply: () -> Void
    let onCopy: () -> Void
    let onForward: () -> Void
    let onAddReaction: () -> Void
    let onReport: () -> Void
    let onRestrictSender: () -> Void
    let canRestrictSender: Bool
    @State private var showDeleteConfirm: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Ответить
            if !message.isCurrentUser {
                ActionButton(
                    icon: "arrowshape.turn.up.left",
                    title: localizationManager.localized("family_chat_message_reply"),
                    action: onReply
                )
            }
            
            // Копировать
            if message.text != nil {
                ActionButton(
                    icon: "doc.on.doc",
                    title: localizationManager.localized("family_chat_message_copy"),
                    action: onCopy
                )
            }
            
            // Добавить реакцию
            ActionButton(
                icon: "face.smiling",
                title: localizationManager.localized("family_chat_reaction_add"),
                action: onAddReaction
            )
            
            // Редактировать (только свои сообщения)
            if message.isCurrentUser && message.messageType == .text {
                ActionButton(
                    icon: "pencil",
                    title: localizationManager.localized("family_chat_message_edit"),
                    action: onEdit
                )
            }
            
            // Переслать
            ActionButton(
                icon: "arrowshape.turn.up.right",
                title: localizationManager.localized("family_chat_message_forward"),
                action: onForward
            )

            if !message.isCurrentUser {
                Divider()

                ActionButton(
                    icon: "exclamationmark.bubble",
                    title: localizationManager.localized("family_chat_report"),
                    action: onReport,
                    isDestructive: true
                )
                .accessibilityIdentifier("family_chat_report_action")

                if canRestrictSender {
                    ActionButton(
                        icon: "person.crop.circle.badge.xmark",
                        title: localizationManager.localized("family_chat_restrict_sender"),
                        action: onRestrictSender,
                        isDestructive: true
                    )
                    .accessibilityIdentifier("family_chat_restrict_action")
                }
            }
            
            // Удалить (только свои сообщения)
            if message.isCurrentUser {
                Divider()
                
                ActionButton(
                    icon: "trash",
                    title: localizationManager.localized("family_chat_message_delete"),
                    action: {
                        showDeleteConfirm = true
                    },
                    isDestructive: true
                )
                .accessibilityIdentifier("family_chat_delete_action")
            }
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.medium)
        .alert(
            localizationManager.localized("family_chat_message_delete_confirm_title"),
            isPresented: $showDeleteConfirm
        ) {
            Button(localizationManager.localized("family_chat_voice_cancel"), role: .cancel) {}
            Button(localizationManager.localized("family_chat_message_delete"), role: .destructive) {
                onDelete()
            }
        } message: {
            Text(localizationManager.localized("family_chat_message_delete_confirm"))
        }
    }
}

// MARK: - Action Button

struct ActionButton: View {
    let icon: String
    let title: String
    let action: () -> Void
    var isDestructive: Bool = false
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Image(systemName: icon)
                    .font(.body)
                    .foregroundColor(isDestructive ? .red : .textPrimary)
                    .frame(width: 24)
                
                Text(title)
                    .font(.body)
                    .foregroundColor(isDestructive ? .red : .textPrimary)
                
                Spacer()
            }
            .padding(Spacing.s)
            .background(Color.surfaceDark.opacity(0.3))
            .cornerRadius(CornerRadius.small)
        }
    }
}

