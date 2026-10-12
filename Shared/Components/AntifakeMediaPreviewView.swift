import AVFoundation
import AVKit
import SwiftUI
import UIKit

/// fws-05 — on-device preview before upload (audio/video/document image).
struct AntifakeMediaPreviewView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let previewURL: URL
    let mediaKind: AntifakeMediaKind

    @State private var isPlayingAudio = false
    @State private var audioPlayer: AVAudioPlayer?

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized("antifake_media_preview_title"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.white.opacity(0.75))

            Group {
                switch mediaKind {
                case .video:
                    VideoPlayer(player: AVPlayer(url: previewURL))
                        .frame(height: 180)
                        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                case .audio, .call:
                    audioPreviewControls
                case .document:
                    if let uiImage = UIImage(contentsOfFile: previewURL.path) {
                        Image(uiImage: uiImage)
                            .resizable()
                            .scaledToFit()
                            .frame(maxHeight: 220)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                            .accessibilityLabel(localizationManager.localized("antifake_document_title"))
                    } else {
                        Label(
                            previewURL.lastPathComponent,
                            systemImage: "doc.richtext"
                        )
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))
                        .padding(Spacing.m)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .stormGlassCard(cornerRadius: CornerRadius.medium)
                    }
                }
            }
        }
        .onDisappear {
            stopAudio()
        }
        .accessibilityIdentifier("antifake_media_preview")
    }

    private var audioPreviewControls: some View {
        HStack(spacing: Spacing.m) {
            Button {
                toggleAudio()
            } label: {
                Image(systemName: isPlayingAudio ? "pause.circle.fill" : "play.circle.fill")
                    .font(.system(size: 44))
                    .foregroundColor(.secondaryGold)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("antifake_media_preview_play")

            Text(localizationManager.localized(isPlayingAudio ? "antifake_media_preview_playing" : "antifake_media_preview_tap_play"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))
            Spacer(minLength: 0)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private func toggleAudio() {
        if isPlayingAudio {
            stopAudio()
            return
        }
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .default)
            try session.setActive(true)
            let player = try AVAudioPlayer(contentsOf: previewURL)
            player.play()
            audioPlayer = player
            isPlayingAudio = true
        } catch {
            stopAudio()
        }
    }

    private func stopAudio() {
        audioPlayer?.stop()
        audioPlayer = nil
        isPlayingAudio = false
    }
}
