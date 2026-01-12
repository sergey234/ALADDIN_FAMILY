import SwiftUI
import AVFoundation

/**
 * 🎤 Voice Recording View
 * UI для записи голосовых сообщений
 */

struct VoiceRecordingView: View {
    @ObservedObject var recorder: VoiceMessageRecorder
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSend: (URL) -> Void
    let onCancel: () -> Void
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Индикатор записи
            HStack(spacing: Spacing.s) {
                // Визуализация уровня звука
                HStack(spacing: 2) {
                    ForEach(0..<20, id: \.self) { index in
                        RoundedRectangle(cornerRadius: 2)
                            .fill(index < Int(recorder.audioLevel * 20) ? Color.secondaryGold : Color.surfaceDark.opacity(0.3))
                            .frame(width: 3, height: CGFloat(10 + Int(recorder.audioLevel * 20) * 2))
                    }
                }
                .frame(height: 40)
                
                // Длительность записи
                Text(recorder.formatDuration(recorder.recordingDuration))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                    .monospacedDigit()
            }
            .padding(Spacing.m)
            
            // Текст состояния
            Text(localizationManager.localized("family_chat_voice_recording"))
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            // Кнопки действий
            HStack(spacing: Spacing.l) {
                // Отмена
                Button(action: {
                    recorder.cancelRecording()
                    onCancel()
                }) {
                    Text(localizationManager.localized("family_chat_voice_cancel"))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(.horizontal, Spacing.l)
                        .padding(.vertical, Spacing.m)
                        .background(Color.surfaceDark)
                        .cornerRadius(CornerRadius.medium)
                }
                
                // Отправить
                Button(action: {
                    if let url = recorder.stopRecording() {
                        onSend(url)
                    }
                }) {
                    HStack {
                        Image(systemName: "paperplane.fill")
                        Text(localizationManager.localized("family_chat_voice_send"))
                    }
                    .font(.body)
                    .foregroundColor(.backgroundDark)
                    .padding(.horizontal, Spacing.l)
                    .padding(.vertical, Spacing.m)
                    .background(Color.secondaryGold)
                    .cornerRadius(CornerRadius.medium)
                }
                .disabled(recorder.recordingDuration < 0.5)
            }
        }
        .padding(Spacing.l)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
    }
}

