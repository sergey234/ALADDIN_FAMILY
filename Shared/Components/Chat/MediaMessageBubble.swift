import SwiftUI

/// 🖼️ MediaMessageBubble
/// Красивый универсальный компонент для отображения всех типов медиа в семейном чате
/// Поддерживает: изображения, видео, голосовые сообщения, прогресс загрузки
struct MediaMessageBubble: View {
    
    let message: FamilyChatMessage
    let isCurrentUser: Bool
    let uploadProgress: Double? // 0.0...1.0 для отображения прогресса
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showFullImage = false
    @State private var resolvedMediaURL: URL?
    @ObservedObject private var voicePlayer = VoiceMessagePlayer.shared
    
    var body: some View {
        VStack(alignment: isCurrentUser ? .trailing : .leading, spacing: 6) {
            // Тип медиа
            switch message.mediaType {
            case .image:
                imageView
            case .video:
                videoThumbnailView
            case .voice, .audio:
                voiceMessageView
            default:
                placeholderView
            }
            
            // Прогресс загрузки
            if let progress = uploadProgress, progress < 1.0 {
                ProgressView(value: progress)
                    .progressViewStyle(.linear)
                    .tint(isCurrentUser ? .blue : .white)
                    .frame(width: 180)
            }

            if message.mediaType == .voice || message.mediaType == .audio {
                Text(voiceDeliveryStatusText)
                    .font(.caption2)
                    .foregroundColor(isCurrentUser ? .white.opacity(0.8) : .secondary)
            }
            
            // Подпись (если есть текст вместе с медиа)
            if let text = message.text, !text.isEmpty {
                Text(text)
                    .font(.caption)
                    .foregroundColor(isCurrentUser ? .white.opacity(0.9) : .primary)
                    .padding(.horizontal, 12)
                    .padding(.bottom, 4)
            }
        }
        .padding(8)
        .background(
            isCurrentUser 
            ? Color.blue.opacity(0.9) 
            : Color(.systemGray5)
        )
        .cornerRadius(18)
        .shadow(color: Color.black.opacity(0.1), radius: 3, x: 0, y: 2)
        .task(id: message.id) {
            await loadDecryptedMediaIfNeeded()
        }
    }

    private func loadDecryptedMediaIfNeeded() async {
        if message.mediaUrl != nil || message.voiceUrl != nil { return }
        guard let enc = message.encryptedMedia else { return }
        do {
            resolvedMediaURL = try await FamilyE2EEMediaLoader.shared.resolvePlayableURL(
                messageId: message.id,
                media: enc
            )
        } catch {
            print("⚠️ MediaMessageBubble E2EE decrypt: \(error)")
        }
    }
    
    /// Превью от сервера или полный URL медиа
    private var displayImageURLString: String? {
        resolvedMediaURL?.absoluteString ?? message.mediaThumbnailUrl ?? message.mediaUrl
    }
    
    private var imageView: some View {
        Group {
            if let urlString = displayImageURLString, let url = URL(string: urlString) {
                AsyncImage(url: url) { image in
                    image
                        .resizable()
                        .scaledToFit()
                        .frame(maxWidth: 220, maxHeight: 280)
                        .cornerRadius(12)
                } placeholder: {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 180, height: 180)
                        .overlay(ProgressView())
                }
                .onTapGesture {
                    showFullImage = true
                }
            } else {
                placeholderImage
            }
        }
        .fullScreenCover(isPresented: $showFullImage) {
            if let urlString = message.mediaUrl, let url = URL(string: urlString) {
                FullScreenImageView(url: url, isPresented: $showFullImage)
                    .environmentObject(localizationManager)
            }
        }
    }
    
    private var videoThumbnailView: some View {
        ZStack {
            Group {
                if let urlString = displayImageURLString, let url = URL(string: urlString) {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .success(let image):
                            image
                                .resizable()
                                .scaledToFill()
                        default:
                            placeholderImage
                        }
                    }
                } else {
                    placeholderImage
                }
            }
            .frame(width: 200, height: 160)
            .clipped()
            .cornerRadius(12)
            .overlay(
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 44))
                    .foregroundColor(.white)
            )
            Text(localizationManager.localized("family_chat_media_video"))
                .font(.caption2)
                .foregroundColor(.white)
                .padding(6)
                .background(Color.black.opacity(0.6))
                .cornerRadius(8)
        }
        .frame(width: 200, height: 160)
    }
    
    private var voiceMessageView: some View {
        HStack(spacing: 12) {
            let isPlayingCurrentVoice = voicePlayer.isPlaying && voicePlayer.currentMessageId == message.id
            Button(action: {
                if isPlayingCurrentVoice {
                    voicePlayer.togglePause()
                } else if let url = resolvedMediaURL ?? message.voiceUrl.flatMap({ URL(string: $0) }) {
                    voicePlayer.play(url: url, messageId: message.id)
                }
            }) {
                Image(systemName: isPlayingCurrentVoice ? "pause.circle.fill" : "play.circle.fill")
                    .font(.system(size: 32))
                    .foregroundColor(isCurrentUser ? .white : .blue)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(Self.formatVoiceDuration(message.voiceDuration))
                    .font(.caption)
                    .foregroundColor(isCurrentUser ? .white.opacity(0.8) : .secondary)
                
                if let urlString = message.voiceUrl {
                    Text(URL(string: urlString)?.lastPathComponent ?? urlString)
                        .font(.caption2)
                        .foregroundColor(isCurrentUser ? .white.opacity(0.6) : .secondary)
                        .lineLimit(1)
                }
            }
        }
        .padding(.horizontal, 8)
        .frame(minWidth: 160)
    }
    
    private var placeholderImage: some View {
        Rectangle()
            .fill(Color.gray.opacity(0.2))
            .frame(width: 180, height: 180)
            .overlay(
                Image(systemName: "photo.on.rectangle")
                    .font(.largeTitle)
                    .foregroundColor(.gray)
            )
    }
    
    private var placeholderView: some View {
        Text(localizationManager.localized("family_chat_media_generic"))
            .padding()
            .foregroundColor(.gray)
    }
    
    private static func formatVoiceDuration(_ seconds: Double?) -> String {
        guard let s = seconds, s >= 0 else { return "0:00" }
        let m = Int(s) / 60
        let r = Int(s) % 60
        return String(format: "%d:%02d", m, r)
    }

    private var voiceDeliveryStatusText: String {
        if voicePlayer.currentMessageId == message.id,
           let playbackError = voicePlayer.playbackError,
           !playbackError.isEmpty {
            return playbackError
        }
        if let progress = uploadProgress, progress < 1.0 {
            return "\(localizationManager.localized("family_chat_voice_status_uploading")) \(Int(progress * 100))%"
        }
        if let voiceUrl = message.voiceUrl, voiceUrl.hasPrefix("file://"), isCurrentUser {
            return localizationManager.localized("family_chat_voice_status_upload_error")
        }
        if isCurrentUser, (message.readStatus ?? "").isEmpty {
            return localizationManager.localized("family_chat_voice_status_transcribing")
        }
        return localizationManager.localized("family_chat_voice_status_ready")
    }
}

// MARK: - Full Screen Image Viewer
struct FullScreenImageView: View {
    let url: URL
    @Binding var isPresented: Bool
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            AsyncImage(url: url) { image in
                image
                    .resizable()
                    .scaledToFit()
                    .background(Color.black)
            } placeholder: {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
            }
            .navigationTitle(localizationManager.localized("family_chat_media_image_viewer_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("close")) {
                        isPresented = false
                    }
                    .foregroundColor(.white)
                }
            }
        }
    }
}
