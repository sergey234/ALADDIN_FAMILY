import AVFoundation
import AVKit
import SwiftUI

/// fws-05 — on-device preview before upload (audio/video only).
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
                    EmptyView()
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
