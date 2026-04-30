import Foundation
import AVFoundation

/// Сессия `AVAudioSession`, кэш данных из бундла, громкости. Плееры — `BackgroundMusicController` / `AudioOneShotPlayer` (W5-1).
final class AudioManager: ObservableObject {
    static let shared = AudioManager()

    @Published private(set) var isMuted: Bool
    @Published private(set) var masterVolume: Float
    @Published private(set) var effectsVolume: Float
    @Published private(set) var musicVolume: Float

    private let defaults = UserDefaults.standard
    private let masterVolumeKey = "audio.masterVolume"
    private let effectsVolumeKey = "audio.effectsVolume"
    private let musicVolumeKey = "audio.musicVolume"
    private let mutedKey = "audio.isMuted"

    private var cachedDataByName: [String: Data] = [:]
    // W8 performance contract: keep prepared one-shot players by sound key.
    private var cachedPlayerByName: [String: AVAudioPlayer] = [:]
    private var interruptionObserver: NSObjectProtocol?

    private init() {
        self.masterVolume = defaults.object(forKey: masterVolumeKey) as? Float ?? 1.0
        self.effectsVolume = defaults.object(forKey: effectsVolumeKey) as? Float ?? 0.8
        self.musicVolume = defaults.object(forKey: musicVolumeKey) as? Float ?? 0.6
        self.isMuted = defaults.bool(forKey: mutedKey)
        configureAudioSession()
        registerInterruptionHandler()
    }

    deinit {
        if let o = interruptionObserver {
            NotificationCenter.default.removeObserver(o)
        }
    }

    var effectiveMusicGain: Float {
        isMuted ? 0 : (musicVolume * masterVolume)
    }

    var effectiveEffectsGain: Float {
        isMuted ? 0 : (effectsVolume * masterVolume)
    }

    /// Данные из `Resources/Audio` в бундле, иначе из корня (совместимость).
    func bundledData(named resource: String, ext: String = "mp3", subdirectory: String? = "Audio") -> Data? {
        let key: String
        if let sub = subdirectory {
            key = "\(sub)/\(resource).\(ext)"
        } else {
            key = "\(resource).\(ext)"
        }
        if let cached = cachedDataByName[key] { return cached }
        if let sub = subdirectory, let u = Bundle.main.url(forResource: resource, withExtension: ext, subdirectory: sub) {
            guard let data = try? Data(contentsOf: u) else { return nil }
            cachedDataByName[key] = data
            return data
        }
        if let u = Bundle.main.url(forResource: resource, withExtension: ext) {
            let legacyKey = "\(resource).\(ext)"
            if let cached = cachedDataByName[legacyKey] { return cached }
            guard let data = try? Data(contentsOf: u) else { return nil }
            cachedDataByName[legacyKey] = data
            return data
        }
        return nil
    }

    func setMasterVolume(_ value: Float) {
        masterVolume = max(0, min(1, value))
        defaults.set(masterVolume, forKey: masterVolumeKey)
        applyVolumes()
    }

    func setEffectsVolume(_ value: Float) {
        effectsVolume = max(0, min(1, value))
        defaults.set(effectsVolume, forKey: effectsVolumeKey)
        applyVolumes()
    }

    func setMusicVolume(_ value: Float) {
        musicVolume = max(0, min(1, value))
        defaults.set(musicVolume, forKey: musicVolumeKey)
        applyVolumes()
    }

    func setMuted(_ muted: Bool) {
        isMuted = muted
        defaults.set(muted, forKey: mutedKey)
        applyVolumes()
    }

    private func configureAudioSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.ambient, mode: .default, options: [.mixWithOthers])
        try? session.setActive(true)
    }

    private func registerInterruptionHandler() {
        let session = AVAudioSession.sharedInstance()
        interruptionObserver = NotificationCenter.default.addObserver(
            forName: AVAudioSession.interruptionNotification,
            object: session,
            queue: .main
        ) { [weak self] notification in
            self?.processInterruption(notification)
        }
    }

    /// Общая логика для сессии и тестов (симуляция `AVAudioSession.interruptionNotification`).
    internal func processInterruption(_ notification: Notification) {
        guard let typeVal = notification.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: typeVal) else { return }
        let run: @MainActor () -> Void = {
            switch type {
            case .began:
                BackgroundMusicController.shared.pauseForInterruption()
            case .ended:
                let optionBits = notification.userInfo?[AVAudioSessionInterruptionOptionKey] as? UInt ?? 0
                let options = AVAudioSession.InterruptionOptions(rawValue: optionBits)
                if options.contains(.shouldResume) {
                    BackgroundMusicController.shared.resumeAfterInterruptionIfNeeded()
                }
            @unknown default:
                break
            }
        }
        if Thread.isMainThread {
            MainActor.assumeIsolated { run() }
        } else {
            Task { @MainActor in run() }
        }
    }

    private func applyVolumes() {
        if Thread.isMainThread {
            MainActor.assumeIsolated {
                BackgroundMusicController.shared.refreshVolume()
            }
        } else {
            Task { @MainActor in BackgroundMusicController.shared.refreshVolume() }
        }
    }
}
