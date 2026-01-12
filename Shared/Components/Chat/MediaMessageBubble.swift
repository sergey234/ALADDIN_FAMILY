import SwiftUI
import PhotosUI

/**
 * 📷 Media Message Bubble
 * UI для отображения медиа сообщений (фото, видео)
 */

struct MediaMessageBubble: View {
    let message: FamilyChatMessage
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showFullscreen: Bool = false
    @State private var image: UIImage? = nil
    
    var body: some View {
        HStack {
            if message.isCurrentUser {
                Spacer()
            }
            
            VStack(alignment: message.isCurrentUser ? .trailing : .leading, spacing: Spacing.xxs) {
                if !message.isCurrentUser {
                    Text(message.sender)
                        .font(.captionBold)
                        .foregroundColor(.secondaryGold)
                }
                
                // Медиа контент
                Group {
                    if let mediaUrl = message.mediaUrl, let url = URL(string: mediaUrl) {
                        if message.mediaType == "image" || message.mediaType == "photo" {
                            AsyncImage(url: url) { phase in
                                switch phase {
                                case .empty:
                                    ProgressView()
                                        .frame(width: 200, height: 200)
                                case .success(let image):
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                        .frame(maxWidth: 200, maxHeight: 200)
                                        .clipped()
                                        .cornerRadius(CornerRadius.medium)
                                        .onTapGesture {
                                            showFullscreen = true
                                        }
                                case .failure:
                                    Image(systemName: "photo")
                                        .font(.largeTitle)
                                        .foregroundColor(.textTertiary)
                                        .frame(width: 200, height: 200)
                                @unknown default:
                                    EmptyView()
                                }
                            }
                        } else if message.mediaType == "video" {
                            VideoThumbnailView(url: url)
                                .frame(maxWidth: 200, maxHeight: 200)
                                .cornerRadius(CornerRadius.medium)
                                .onTapGesture {
                                    showFullscreen = true
                                }
                        }
                    } else {
                        // Локальное изображение
                        if let image = image {
                            Image(uiImage: image)
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(maxWidth: 200, maxHeight: 200)
                                .clipped()
                                .cornerRadius(CornerRadius.medium)
                                .onTapGesture {
                                    showFullscreen = true
                                }
                        }
                    }
                }
                .padding(Spacing.xxs)
                .background(
                    message.isCurrentUser
                        ? Color.primaryBlue
                        : Color.surfaceDark
                )
                .cornerRadius(CornerRadius.medium)
                
                // Время
                Text(message.time)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: message.isCurrentUser ? .trailing : .leading)
            
            if !message.isCurrentUser {
                Spacer()
            }
        }
        .sheet(isPresented: $showFullscreen) {
            if let mediaUrl = message.mediaUrl, let url = URL(string: mediaUrl) {
                FullscreenMediaView(url: url, mediaType: message.mediaType ?? "image")
            }
        }
    }
}

// MARK: - Video Thumbnail View

struct VideoThumbnailView: View {
    let url: URL
    @State private var thumbnail: UIImage? = nil
    
    var body: some View {
        Group {
            if let thumbnail = thumbnail {
                Image(uiImage: thumbnail)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else {
                ZStack {
                    Color.surfaceDark
                    VStack {
                        Image(systemName: "play.circle.fill")
                            .font(.largeTitle)
                            .foregroundColor(.secondaryGold)
                        Text("Video")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
        .onAppear {
            generateThumbnail()
        }
    }
    
    private func generateThumbnail() {
        // Генерация thumbnail для видео
        // TODO: Реализовать генерацию thumbnail
    }
}

// MARK: - Fullscreen Media View

struct FullscreenMediaView: View {
    let url: URL
    let mediaType: String
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            if mediaType == "image" || mediaType == "photo" {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        ProgressView()
                            .tint(.white)
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    case .failure:
                        Text("Ошибка загрузки")
                            .foregroundColor(.white)
                    @unknown default:
                        EmptyView()
                    }
                }
            }
            
            VStack {
                HStack {
                    Spacer()
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title)
                            .foregroundColor(.white)
                    }
                    .padding()
                }
                Spacer()
            }
        }
    }
}

