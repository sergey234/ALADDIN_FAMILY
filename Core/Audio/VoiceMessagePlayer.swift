import Foundation
import AVFoundation
import Combine

/**
 * 🔊 Voice Message Player
 * Воспроизведение голосовых сообщений в семейном чате
 */

class VoiceMessagePlayer: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isPlaying: Bool = false
    @Published var currentMessageId: UUID? = nil
    @Published var playbackProgress: Double = 0.0
    @Published var playbackDuration: TimeInterval = 0.0
    @Published var playbackError: String? = nil
    
    // MARK: - Private Properties
    
    private var audioPlayer: AVAudioPlayer?
    private var playbackTimer: Timer?
    private var audioSession: AVAudioSession = AVAudioSession.sharedInstance()
    
    // MARK: - Singleton
    
    static let shared = VoiceMessagePlayer()
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        setupAudioSession()
    }
    
    // MARK: - Audio Session Setup
    
    private func setupAudioSession() {
        do {
            try audioSession.setCategory(.playback, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try audioSession.setActive(true)
        } catch {
            print("❌ VoiceMessagePlayer: Ошибка настройки аудио сессии: \(error.localizedDescription)")
            playbackError = error.localizedDescription
        }
    }
    
    // MARK: - Playback Methods
    
    /// Воспроизводит голосовое сообщение
    func play(url: URL, messageId: UUID) {
        // Останавливаем предыдущее воспроизведение, если есть
        if isPlaying {
            stop()
        }
        
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.delegate = self
            audioPlayer?.prepareToPlay()
            
            guard let player = audioPlayer, player.play() else {
                playbackError = "Не удалось начать воспроизведение"
                return
            }
            
            currentMessageId = messageId
            isPlaying = true
            playbackDuration = player.duration
            playbackProgress = 0.0
            playbackError = nil
            
            // Запускаем таймер для отслеживания прогресса
            startPlaybackTimer()
            
            print("✅ VoiceMessagePlayer: Воспроизведение начато для сообщения \(messageId)")
            
        } catch {
            print("❌ VoiceMessagePlayer: Ошибка воспроизведения: \(error.localizedDescription)")
            playbackError = error.localizedDescription
        }
    }
    
    /// Останавливает воспроизведение
    func stop() {
        audioPlayer?.stop()
        stopPlaybackTimer()
        
        isPlaying = false
        currentMessageId = nil
        playbackProgress = 0.0
        playbackDuration = 0.0
        
        print("✅ VoiceMessagePlayer: Воспроизведение остановлено")
    }
    
    /// Пауза/возобновление
    func togglePause() {
        guard let player = audioPlayer else { return }
        
        if player.isPlaying {
            player.pause()
            stopPlaybackTimer()
        } else {
            player.play()
            startPlaybackTimer()
        }
    }
    
    /// Перемотка к позиции
    func seek(to time: TimeInterval) {
        guard let player = audioPlayer else { return }
        player.currentTime = time
        playbackProgress = time / player.duration
    }
    
    // MARK: - Timer Methods
    
    private func startPlaybackTimer() {
        playbackTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self, let player = self.audioPlayer else { return }
            
            if player.duration > 0 {
                self.playbackProgress = player.currentTime / player.duration
            }
        }
    }
    
    private func stopPlaybackTimer() {
        playbackTimer?.invalidate()
        playbackTimer = nil
    }
    
    // MARK: - Format Duration
    
    func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}

// MARK: - AVAudioPlayerDelegate

extension VoiceMessagePlayer: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        stop()
        
        if !flag {
            playbackError = "Ошибка воспроизведения"
        }
    }
    
    func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        if let error = error {
            playbackError = error.localizedDescription
            stop()
        }
    }
}

