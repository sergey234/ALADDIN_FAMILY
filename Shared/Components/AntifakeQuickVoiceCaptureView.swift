import AVFoundation
import SwiftUI

/// 30-second voice snippet for in-call manual check (Round2 S72 — owner: 30s, not 5/10).
struct AntifakeQuickVoiceCaptureView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var showPremiumPaywall: Bool

    @StateObject private var viewModel = AntifakeMediaCheckViewModel(mediaKind: .audio)
    @State private var recorder: AVAudioRecorder?
    @State private var recordingURL: URL?
    @State private var secondsLeft = 30
    @State private var isRecording = false
    @State private var timer: Timer?

    /// Owner GO: 30s — enough phrase for antifake without companion STT-class load.
    private let maxDuration: TimeInterval = 30

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(localizationManager.localized("antifake_quick_voice_title"), systemImage: "mic.circle.fill")
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.white)

            Text(localizationManager.localized("antifake_quick_voice_body"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.85))

            HStack(spacing: Spacing.m) {
                Button {
                    isRecording ? stopRecording(submit: false) : startRecording()
                } label: {
                    HStack {
                        Image(systemName: isRecording ? "stop.circle.fill" : "record.circle")
                        Text(
                            isRecording
                                ? String(format: localizationManager.localized("antifake_quick_voice_recording"), secondsLeft)
                                : localizationManager.localized("antifake_quick_voice_start")
                        )
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundColor(isRecording ? .red : .white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background((isRecording ? Color.red : Color.secondaryGold).opacity(0.35))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("antifake_quick_voice_button")
            }

            if viewModel.isChecking {
                HStack(spacing: 8) {
                    ProgressView().tint(.white)
                    Text(viewModel.statusMessage ?? localizationManager.localized("antifake_job_analyzing"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
                }
            }

            if let error = viewModel.errorMessage, !viewModel.isChecking {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red.opacity(0.95))
                        .fixedSize(horizontal: false, vertical: true)
                    if viewModel.canSubmit {
                        Button {
                            SelectionHaptic.selection()
                            Task {
                                _ = await viewModel.submitCheck()
                                if viewModel.requiresPremiumUpgrade {
                                    showPremiumPaywall = true
                                }
                            }
                        } label: {
                            Label(
                                localizationManager.localized("antifake_retry"),
                                systemImage: "arrow.clockwise"
                            )
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("antifake_quick_voice_retry")
                    }
                }
            }

            if let verdict = viewModel.verdict {
                AntifakeVerdictCard(
                    verdict: verdict,
                    checkTypeKey: "pay_pains_check_type_voice"
                )
                    .environmentObject(localizationManager)
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .purple)
        .accessibilityIdentifier("antifake_quick_voice_panel")
        .onDisappear { stopRecording(submit: false) }
    }

    private func startRecording() {
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            Task { @MainActor in
                guard granted else { return }
                do {
                    let session = AVAudioSession.sharedInstance()
                    try session.setCategory(.playAndRecord, mode: .spokenAudio, options: [.duckOthers])
                    try session.setActive(true)
                    let url = FileManager.default.temporaryDirectory
                        .appendingPathComponent("antifake_quick_\(UUID().uuidString).m4a")
                    let settings: [String: Any] = [
                        AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                        AVSampleRateKey: 44_100,
                        AVNumberOfChannelsKey: 1,
                        AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
                    ]
                    recorder = try AVAudioRecorder(url: url, settings: settings)
                    recordingURL = url
                    recorder?.record(forDuration: maxDuration)
                    isRecording = true
                    secondsLeft = Int(maxDuration)
                    timer?.invalidate()
                    timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { t in
                        Task { @MainActor in
                            secondsLeft -= 1
                            if secondsLeft <= 0 {
                                t.invalidate()
                                stopRecording(submit: true)
                            }
                        }
                    }
                } catch {
                    isRecording = false
                }
            }
        }
    }

    private func stopRecording(submit: Bool) {
        timer?.invalidate()
        timer = nil
        recorder?.stop()
        isRecording = false
        guard submit, let url = recordingURL, let data = try? Data(contentsOf: url) else {
            recorder = nil
            return
        }
        Task {
            viewModel.setSelectedFile(data: data, filename: "quick_voice.m4a")
            _ = await viewModel.submitCheck()
            if viewModel.requiresPremiumUpgrade {
                showPremiumPaywall = true
            }
            if let verdict = viewModel.verdict {
                AntifakeHistoryRecorder.record(
                    verdict: verdict,
                    kind: "audio",
                    summary: localizationManager.localized("antifake_quick_voice_title")
                )
            }
        }
        recorder = nil
    }
}
