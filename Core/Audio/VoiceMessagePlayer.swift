import Foundation
import AVFoundation
import Combine
import CryptoKit

/**
 * 🔊 Voice Message Player
 * Воспроизведение голосовых сообщений в семейном чате
 */

class VoiceMessagePlayer: NSObject, ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isPlaying: Bool = false
    @Published var currentMessageId: String? = nil
    @Published var playbackProgress: Double = 0.0
    @Published var playbackDuration: TimeInterval = 0.0
    @Published var playbackError: String? = nil
    
    // MARK: - Private Properties
    
    private var audioPlayer: AVAudioPlayer?
    private var playbackTimer: Timer?
    private var audioSession: AVAudioSession = AVAudioSession.sharedInstance()
    private var activeLoadMessageId: String?
    private var cacheDirectoryURL: URL {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("VoiceMessageCache", isDirectory: true)
    }
    
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
    func play(url: URL, messageId: String) {
        // Останавливаем предыдущее воспроизведение, если есть
        if isPlaying {
            stop()
        }

        currentMessageId = messageId
        playbackError = nil
        activeLoadMessageId = messageId

        if url.isFileURL {
            prepareAndStartPlayback(localURL: url, messageId: messageId)
            return
        }

        resolveLocalURL(for: url, messageId: messageId) { [weak self] result in
            DispatchQueue.main.async {
                guard let self else { return }
                guard self.activeLoadMessageId == messageId else { return }
                switch result {
                case .success(let localURL):
                    self.prepareAndStartPlayback(localURL: localURL, messageId: messageId)
                case .failure(let error):
                    self.playbackError = error.localizedDescription
                    self.isPlaying = false
                    print("❌ VoiceMessagePlayer: Ошибка подготовки файла: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// Останавливает воспроизведение
    func stop() {
        audioPlayer?.stop()
        stopPlaybackTimer()
        activeLoadMessageId = nil
        
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
            isPlaying = false
        } else {
            player.play()
            startPlaybackTimer()
            isPlaying = true
        }
    }

    // MARK: - Local file preparation

    private func prepareAndStartPlayback(localURL: URL, messageId: String) {
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: localURL)
            audioPlayer?.delegate = self
            audioPlayer?.prepareToPlay()

            guard let player = audioPlayer, player.play() else {
                playbackError = "Не удалось начать воспроизведение"
                isPlaying = false
                return
            }

            currentMessageId = messageId
            isPlaying = true
            playbackDuration = player.duration
            playbackProgress = 0.0
            playbackError = nil
            startPlaybackTimer()
            print("✅ VoiceMessagePlayer: Воспроизведение начато для сообщения \(messageId)")
        } catch {
            print("❌ VoiceMessagePlayer: Ошибка воспроизведения: \(error.localizedDescription)")
            playbackError = error.localizedDescription
            isPlaying = false
        }
    }

    private func resolveLocalURL(for remoteURL: URL, messageId: String, completion: @escaping (Result<URL, Error>) -> Void) {
        do {
            try FileManager.default.createDirectory(at: cacheDirectoryURL, withIntermediateDirectories: true, attributes: nil)
        } catch {
            completion(.failure(error))
            return
        }

        let cacheFileName = makeCacheFileName(for: remoteURL)
        let cachedURL = cacheDirectoryURL.appendingPathComponent(cacheFileName)
        if FileManager.default.fileExists(atPath: cachedURL.path) {
            completion(.success(cachedURL))
            return
        }

        URLSession.shared.downloadTask(with: remoteURL) { tempURL, _, error in
            if let error {
                completion(.failure(error))
                return
            }
            guard let tempURL else {
                completion(.failure(NSError(domain: "VoiceMessagePlayer", code: -1, userInfo: [NSLocalizedDescriptionKey: "Файл не загружен"])))
                return
            }

            do {
                if FileManager.default.fileExists(atPath: cachedURL.path) {
                    try FileManager.default.removeItem(at: cachedURL)
                }
                try FileManager.default.moveItem(at: tempURL, to: cachedURL)
                completion(.success(cachedURL))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    private func makeCacheFileName(for remoteURL: URL) -> String {
        let digest = SHA256.hash(data: Data(remoteURL.absoluteString.utf8))
        let hash = digest.compactMap { String(format: "%02x", $0) }.joined()
        let ext = remoteURL.pathExtension.isEmpty ? "m4a" : remoteURL.pathExtension
        return "\(hash).\(ext)"
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

