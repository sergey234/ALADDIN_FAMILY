import SwiftUI

/**
 * 🔊 Voice Message Bubble
 * UI для отображения и воспроизведения голосовых сообщений
 */

struct VoiceMessageBubble: View {
    let message: FamilyChatMessage
    @ObservedObject var player = VoiceMessagePlayer.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var isDownloading: Bool = false
    @State private var resolvedPlayURL: URL?
    
    private var isPlaying: Bool {
        player.isPlaying && player.currentMessageId == message.id
    }
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            if !message.isCurrentUser {
                Spacer()
            }
            
            VStack(alignment: message.isCurrentUser ? .trailing : .leading, spacing: Spacing.xxs) {
                if !message.isCurrentUser {
                    Text(message.sender)
                        .font(.captionBold)
                        .foregroundColor(.secondaryGold)
                }
                
                // Голосовое сообщение
                HStack(spacing: Spacing.m) {
                    // Кнопка воспроизведения
                    Button(action: {
                        if isPlaying {
                            player.togglePause()
                        } else {
                            if let url = resolvedPlayURL ?? message.voiceUrl.flatMap({ URL(string: $0) }) {
                                player.play(url: url, messageId: message.id)
                            }
                        }
                    }) {
                        Image(systemName: isPlaying ? "pause.circle.fill" : "play.circle.fill")
                            .font(.title2)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    // Прогресс-бар
                    if isPlaying {
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                Rectangle()
                                    .fill(Color.surfaceDark.opacity(0.3))
                                    .frame(height: 4)
                                
                                Rectangle()
                                    .fill(Color.secondaryGold)
                                    .frame(width: geometry.size.width * CGFloat(player.playbackProgress), height: 4)
                            }
                        }
                        .frame(height: 4)
                    } else {
                        // Длительность
                        Text(message.voiceDuration != nil ? player.formatDuration(message.voiceDuration!) : "0:00")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .frame(width: 50)
                    }
                }
                .padding(Spacing.m)
                .background(
                    message.isCurrentUser
                        ? Color.primaryBlue
                        : Color.surfaceDark
                )
                .cornerRadius(CornerRadius.medium)
                
                // Время и статус
                HStack(spacing: Spacing.xs) {
                    Text(message.time)
                        .font(.captionSmall)
                        .foregroundColor(.textTertiary)
                    
                    if message.editedAt != nil {
                        Text(localizationManager.localized("family_chat_message_edited"))
                            .font(.captionSmall)
                            .foregroundColor(.textTertiary)
                    }
                    
                    if message.isCurrentUser {
                        // Статус прочтения
                        Image(systemName: statusIcon)
                            .font(.captionSmall)
                            .foregroundColor(statusColor)
                    }
                }
            }
            .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: message.isCurrentUser ? .trailing : .leading)
            
            if message.isCurrentUser {
                Spacer()
            }
        }
        .task(id: message.id) {
            await loadDecryptedVoiceIfNeeded()
        }
    }

    private func loadDecryptedVoiceIfNeeded() async {
        if let voiceUrl = message.voiceUrl, URL(string: voiceUrl) != nil {
            resolvedPlayURL = URL(string: voiceUrl)
            return
        }
        guard let enc = message.encryptedMedia else { return }
        isDownloading = true
        defer { isDownloading = false }
        do {
            resolvedPlayURL = try await FamilyE2EEMediaLoader.shared.resolvePlayableURL(
                messageId: message.id,
                media: enc
            )
        } catch {
            print("⚠️ VoiceMessageBubble E2EE decrypt: \(error)")
        }
    }
    
    private var statusIcon: String {
        switch message.readStatus {
        case "read":
            return "checkmark.circle.fill"
        case "delivered":
            return "checkmark.circle"
        default:
            return "circle"
        }
    }
    
    private var statusColor: Color {
        switch message.readStatus {
        case "read":
            return .secondaryGold
        case "delivered":
            return .textTertiary
        default:
            return .textTertiary.opacity(0.5)
        }
    }
}

