import SwiftUI

struct QuickRecorderBar: View {
    @ObservedObject var viewModel: VoiceNotesViewModel
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(spacing: 10) {
            HStack(spacing: 12) {
                Circle()
                    .fill(viewModel.recordingState == .recording ? Color.red : Color.gray)
                    .frame(width: 12, height: 12)
                Text(localizationManager.localized(viewModel.currentStatusText.isEmpty ? "voice_notes_status_idle" : viewModel.currentStatusText))
                    .font(.subheadline)
                Spacer()
                Text(timeString(viewModel.elapsedSec))
                    .font(.system(.body, design: .monospaced))
            }

            ProgressView(value: viewModel.noiseLevel)
                .tint(.orange)

            LazyVGrid(
                columns: [
                    GridItem(.flexible(minimum: 0), spacing: 10),
                    GridItem(.flexible(minimum: 0), spacing: 10)
                ],
                spacing: 10
            ) {
                Button {
                    viewModel.startRecording()
                } label: {
                    Text(localizationManager.localized("voice_notes_record"))
                        .lineLimit(2)
                        .multilineTextAlignment(.center)
                        .minimumScaleFactor(0.75)
                        .frame(maxWidth: .infinity, minHeight: 40)
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.recordingState == .recording)
                .accessibilityLabel(localizationManager.localized("voice_notes_record"))

                Button {
                    viewModel.pauseRecording()
                } label: {
                    Text(localizationManager.localized("voice_notes_pause"))
                        .lineLimit(2)
                        .multilineTextAlignment(.center)
                        .minimumScaleFactor(0.75)
                        .frame(maxWidth: .infinity, minHeight: 40)
                }
                .buttonStyle(.bordered)
                .disabled(viewModel.recordingState != .recording)
                .accessibilityLabel(localizationManager.localized("voice_notes_pause"))

                Button {
                    viewModel.resumeRecording()
                } label: {
                    Text(localizationManager.localized("voice_notes_resume"))
                        .lineLimit(2)
                        .multilineTextAlignment(.center)
                        .minimumScaleFactor(0.75)
                        .frame(maxWidth: .infinity, minHeight: 40)
                }
                .buttonStyle(.bordered)
                .disabled(viewModel.recordingState != .paused)
                .accessibilityLabel(localizationManager.localized("voice_notes_resume"))

                Button {
                    viewModel.stopAndSaveRecording()
                } label: {
                    Text(localizationManager.localized("voice_notes_stop"))
                        .lineLimit(2)
                        .multilineTextAlignment(.center)
                        .minimumScaleFactor(0.75)
                        .frame(maxWidth: .infinity, minHeight: 40)
                }
                .buttonStyle(.bordered)
                .disabled(!(viewModel.recordingState == .recording || viewModel.recordingState == .paused))
                .accessibilityLabel(localizationManager.localized("voice_notes_stop"))
            }
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    private func timeString(_ sec: Int) -> String {
        let m = sec / 60
        let s = sec % 60
        return String(format: "%02d:%02d", m, s)
    }
}
