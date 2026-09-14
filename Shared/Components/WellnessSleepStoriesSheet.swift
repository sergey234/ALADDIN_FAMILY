import AVFoundation
import SwiftUI

/// fws-18 — sleep stories: bundled catalog always; API adds/updates when online.
struct WellnessSleepStoriesSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    @State private var stories: [WellnessSleepStoryDTO] = []
    @State private var isLoading = false
    @State private var usingBundleOnly = true
    @State private var player: AVPlayer?
    @State private var speech: AVSpeechSynthesizer?

    var body: some View {
        WellnessNavigationStack {
            ZStack {
                StormMeshBackground(variant: .warm)
                VStack(alignment: .leading, spacing: 8) {
                    if usingBundleOnly {
                        Text(localizationManager.localized("wellness_sleep_stories_offline_hint"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                            .padding(.horizontal)
                    }
                    if stories.isEmpty && isLoading {
                        ProgressView().tint(.white)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else if stories.isEmpty {
                        Text(localizationManager.localized("wellness_sleep_stories_load_failed"))
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.85))
                            .padding()
                            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
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
        .onAppear {
            if stories.isEmpty {
                stories = BundledSleepStories.catalog(localization: localizationManager)
                usingBundleOnly = true
            }
        }
        .task { await load() }
        .onDisappear { stopPlayback() }
        .accessibilityIdentifier("wellness_sleep_stories_sheet")
    }

    @MainActor
    private func load() async {
        // Show bundled catalog immediately — never wait on API spinner when offline.
        let bundled = BundledSleepStories.catalog(localization: localizationManager)
        stories = bundled
        usingBundleOnly = true
        isLoading = false
        do {
            let response = try await WellnessAPIService.shared.fetchSleepStories()
            stories = BundledSleepStories.merged(apiStories: response.stories, localization: localizationManager)
            usingBundleOnly = false
        } catch {
            stories = bundled
            usingBundleOnly = true
        }
    }

    private func play(_ story: WellnessSleepStoryDTO) {
        stopPlayback()
        if let urlString = story.audioUrl, let url = URL(string: urlString), url.scheme?.hasPrefix("http") == true {
            let item = AVPlayerItem(url: url)
            player = AVPlayer(playerItem: item)
            player?.play()
            return
        }
        guard let script = BundledSleepStories.script(id: story.id, localization: localizationManager) else { return }
        let utterance = AVSpeechUtterance(string: script)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate * 0.85
        utterance.pitchMultiplier = 0.95
        let voiceLocale = localizationManager.speechRecognitionLocale
        utterance.voice = AVSpeechSynthesisVoice(language: voiceLocale.identifier)
            ?? AVSpeechSynthesisVoice(language: localizationManager.aiResponseLanguageCode)
        let synthesizer = AVSpeechSynthesizer()
        speech = synthesizer
        synthesizer.speak(utterance)
    }

    private func stopPlayback() {
        player?.pause()
        player = nil
        speech?.stopSpeaking(at: .immediate)
        speech = nil
    }
}
