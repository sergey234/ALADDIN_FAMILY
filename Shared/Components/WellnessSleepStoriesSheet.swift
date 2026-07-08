import AVFoundation
import SwiftUI

/// fws-18 — sleep stories catalog from existing API (no new sleep endpoint).
struct WellnessSleepStoriesSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var stories: [WellnessSleepStoryDTO] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var player: AVPlayer?

    var body: some View {
        WellnessNavigationStack {
            ZStack {
                StormMeshBackground(variant: .warm)
                if isLoading {
                    ProgressView().tint(.white)
                } else if let errorText {
                    Text(errorText).foregroundStyle(.orange).padding()
                } else {
                    List(stories) { story in
                        Button {
                            play(story)
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(story.title)
                                        .font(.subheadline.bold())
                                    if let min = story.durationMin {
                                        Text(String(format: localizationManager.localized("wellness_sleep_story_duration"), min))
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                Spacer()
                                Image(systemName: "play.circle.fill")
                            }
                        }
                        .listRowBackground(Color.clear)
                    }
                    .wellnessScrollContentBackgroundHidden()
                }
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("wellness_sleep_stories_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_sleep_stories_close")) {
                        stopPlayback()
                        dismiss()
                    }
                }
            }
        }
        .task { await load() }
        .onDisappear { stopPlayback() }
        .accessibilityIdentifier("wellness_sleep_stories_sheet")
    }

    @MainActor
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let response = try await WellnessAPIService.shared.fetchSleepStories()
            stories = response.stories
        } catch {
            errorText = localizationManager.localized("wellness_sleep_stories_load_failed")
        }
    }

    private func play(_ story: WellnessSleepStoryDTO) {
        guard let urlString = story.audioUrl, let url = URL(string: urlString) else { return }
        stopPlayback()
        let item = AVPlayerItem(url: url)
        player = AVPlayer(playerItem: item)
        player?.play()
    }

    private func stopPlayback() {
        player?.pause()
        player = nil
    }
}
