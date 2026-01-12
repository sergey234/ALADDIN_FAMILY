import Foundation
import AVFoundation
import Combine

/**
 * 🎤 Voice Message Recorder
 * Запись голосовых сообщений для семейного чата
 */

class VoiceMessageRecorder: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isRecording: Bool = false
    @Published var recordingDuration: TimeInterval = 0
    @Published var recordingError: String? = nil
    @Published var audioLevel: Float = 0.0
    
    // MARK: - Private Properties
    
    private var audioRecorder: AVAudioRecorder?
    private var audioSession: AVAudioSession = AVAudioSession.sharedInstance()
    private var recordingTimer: Timer?
    private var levelTimer: Timer?
    private var recordingURL: URL?
    
    // MARK: - Constants
    
    private let maxRecordingDuration: TimeInterval = 60.0 // Максимум 60 секунд
    private let minRecordingDuration: TimeInterval = 0.5 // Минимум 0.5 секунды
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        setupAudioSession()
    }
    
    // MARK: - Audio Session Setup
    
    private func setupAudioSession() {
        do {
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try audioSession.setActive(true)
        } catch {
            print("❌ VoiceMessageRecorder: Ошибка настройки аудио сессии: \(error.localizedDescription)")
            recordingError = error.localizedDescription
        }
    }
    
    // MARK: - Recording Methods
    
    /// Начинает запись голосового сообщения
    func startRecording() -> URL? {
        guard !isRecording else {
            print("⚠️ VoiceMessageRecorder: Запись уже идет")
            return nil
        }
        
        // Создаем URL для записи
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let audioFilename = documentsPath.appendingPathComponent("voice_message_\(UUID().uuidString).m4a")
        recordingURL = audioFilename
        
        // Настройки записи
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100.0,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        
        do {
            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.delegate = self
            audioRecorder?.isMeteringEnabled = true
            
            guard let recorder = audioRecorder, recorder.record() else {
                recordingError = "Не удалось начать запись"
                return nil
            }
            
            isRecording = true
            recordingDuration = 0
            recordingError = nil
            
            // Запускаем таймер для отслеживания длительности
            startRecordingTimer()
            
            // Запускаем таймер для отслеживания уровня звука
            startLevelTimer()
            
            print("✅ VoiceMessageRecorder: Запись начата")
            return audioFilename
            
        } catch {
            print("❌ VoiceMessageRecorder: Ошибка создания записи: \(error.localizedDescription)")
            recordingError = error.localizedDescription
            return nil
        }
    }
    
    /// Останавливает запись
    func stopRecording() -> URL? {
        guard isRecording, let recorder = audioRecorder else {
            print("⚠️ VoiceMessageRecorder: Запись не активна")
            return nil
        }
        
        recorder.stop()
        stopRecordingTimer()
        stopLevelTimer()
        
        isRecording = false
        
        // Проверяем минимальную длительность
        if recordingDuration < minRecordingDuration {
            print("⚠️ VoiceMessageRecorder: Запись слишком короткая (\(recordingDuration)s)")
            recordingError = "Запись слишком короткая"
            cleanup()
            return nil
        }
        
        print("✅ VoiceMessageRecorder: Запись остановлена, длительность: \(recordingDuration)s")
        return recordingURL
    }
    
    /// Отменяет запись
    func cancelRecording() {
        guard isRecording else { return }
        
        audioRecorder?.stop()
        stopRecordingTimer()
        stopLevelTimer()
        isRecording = false
        
        cleanup()
        print("✅ VoiceMessageRecorder: Запись отменена")
    }
    
    /// Очищает ресурсы
    private func cleanup() {
        if let url = recordingURL {
            try? FileManager.default.removeItem(at: url)
        }
        recordingURL = nil
        audioRecorder = nil
        recordingDuration = 0
        audioLevel = 0.0
    }
    
    // MARK: - Timer Methods
    
    private func startRecordingTimer() {
        recordingTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            
            self.recordingDuration += 0.1
            
            // Автоматическая остановка при достижении максимума
            if self.recordingDuration >= self.maxRecordingDuration {
                _ = self.stopRecording()
            }
        }
    }
    
    private func stopRecordingTimer() {
        recordingTimer?.invalidate()
        recordingTimer = nil
    }
    
    private func startLevelTimer() {
        levelTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self, let recorder = self.audioRecorder else { return }
            
            recorder.updateMeters()
            let level = recorder.averagePower(forChannel: 0)
            
            // Нормализуем уровень от -160 до 0 dB в диапазон 0.0-1.0
            let normalizedLevel = pow(10, (level + 60) / 60)
            self.audioLevel = min(max(normalizedLevel, 0.0), 1.0)
        }
    }
    
    private func stopLevelTimer() {
        levelTimer?.invalidate()
        levelTimer = nil
        audioLevel = 0.0
    }
    
    // MARK: - Format Duration
    
    func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}

// MARK: - AVAudioRecorderDelegate

extension VoiceMessageRecorder: AVAudioRecorderDelegate {
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        if !flag {
            recordingError = "Ошибка записи"
            cleanup()
        }
    }
    
    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        if let error = error {
            recordingError = error.localizedDescription
            cleanup()
        }
    }
}

