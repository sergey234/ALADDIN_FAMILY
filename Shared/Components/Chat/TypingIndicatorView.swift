import SwiftUI

/**
 * ⌨️ Typing Indicator View
 * Индикатор "печатает..."
 */

struct TypingIndicatorView: View {
    let typingUsers: [String]
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var animationOffset: CGFloat = 0
    
    var body: some View {
        if !typingUsers.isEmpty {
            HStack {
                // Анимированные точки
                HStack(spacing: 4) {
                    ForEach(0..<3, id: \.self) { index in
                        Circle()
                            .fill(Color.textSecondary)
                            .frame(width: 8, height: 8)
                            .offset(y: animationOffset)
                            .animation(
                                Animation.easeInOut(duration: 0.6)
                                    .repeatForever()
                                    .delay(Double(index) * 0.2),
                                value: animationOffset
                            )
                    }
                }
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .background(Color.surfaceDark)
                .cornerRadius(CornerRadius.medium)
                
                // Текст
                Text(typingText)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .italic()
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            .onAppear {
                animationOffset = -5
            }
        }
    }
    
    private var typingText: String {
        if typingUsers.count == 1 {
            return String(format: localizationManager.localized("family_chat_typing"), typingUsers[0])
        } else {
            return String(format: localizationManager.localized("family_chat_typing_multiple"), typingUsers.count)
        }
    }
}

