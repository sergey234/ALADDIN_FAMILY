import SwiftUI

/**
 * 💬 Reply Bubble View
 * Отображение цитаты сообщения при ответе
 */

struct ReplyBubbleView: View {
    let replyTo: FamilyChatMessage
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onCancel: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            // Цветная полоска
            Rectangle()
                .fill(Color.secondaryGold)
                .frame(width: 4)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                // Имя отправителя
                Text(replyTo.sender)
                    .font(.captionBold)
                    .foregroundColor(.secondaryGold)
                
                // Текст сообщения (обрезанный)
                Text(replyTo.text ?? "")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            // Кнопка отмены
            Button(action: onCancel) {
                Image(systemName: "xmark.circle.fill")
                    .font(.caption)
                    .foregroundColor(.textTertiary)
            }
        }
        .padding(Spacing.s)
        .background(Color.surfaceDark.opacity(0.5))
        .cornerRadius(CornerRadius.small)
    }
}

