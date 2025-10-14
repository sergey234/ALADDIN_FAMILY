import Foundation
import Speech
import AVFoundation

class VoiceController {
    static let shared = VoiceController()
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "ru-RU"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    
    private var isListening = false
    
    private init() {
        requestAuthorization()
    }
    
    // MARK: - Authorization
    
    func requestAuthorization() {
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                switch status {
                case .authorized:
                    print("✅ Speech recognition authorized")
                case .denied:
                    print("❌ Speech recognition denied")
                case .restricted:
                    print("❌ Speech recognition restricted")
                case .notDetermined:
                    print("⚠️ Speech recognition not determined")
                @unknown default:
                    print("⚠️ Speech recognition unknown status")
                }
            }
        }
    }
    
    // MARK: - Voice Recognition
    
    func startListening(completion: @escaping (String?) -> Void) {
        guard !isListening else {
            print("⚠️ Already listening")
            return
        }
        
        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            print("❌ Speech recognizer not available")
            completion(nil)
            return
        }
        
        do {
            // Cancel previous task
            recognitionTask?.cancel()
            recognitionTask = nil
            
            // Audio session
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
            
            // Recognition request
            recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
            
            guard let recognitionRequest = recognitionRequest else {
                print("❌ Unable to create recognition request")
                completion(nil)
                return
            }
            
            recognitionRequest.shouldReportPartialResults = true
            
            // Input node
            let inputNode = audioEngine.inputNode
            
            // Recognition task
            recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { result, error in
                var isFinal = false
                
                if let result = result {
                    let transcription = result.bestTranscription.formattedString
                    print("🎤 Recognized: \(transcription)")
                    completion(transcription)
                    isFinal = result.isFinal
                }
                
                if error != nil || isFinal {
                    self.audioEngine.stop()
                    inputNode.removeTap(onBus: 0)
                    
                    self.recognitionRequest = nil
                    self.recognitionTask = nil
                    self.isListening = false
                }
            }
            
            // Audio format
            let recordingFormat = inputNode.outputFormat(forBus: 0)
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
                recognitionRequest.append(buffer)
            }
            
            audioEngine.prepare()
            try audioEngine.start()
            
            isListening = true
            print("✅ Listening started...")
            
        } catch {
            print("❌ Audio engine error: \(error.localizedDescription)")
            completion(nil)
        }
    }
    
    func stopListening() {
        guard isListening else { return }
        
        audioEngine.stop()
        recognitionRequest?.endAudio()
        
        isListening = false
        print("🛑 Listening stopped")
    }
    
    // MARK: - Voice Commands
    
    func processCommand(_ command: String, completion: @escaping (VoiceCommandResult) -> Void) {
        let lowercasedCommand = command.lowercased()
        
        if lowercasedCommand.contains("включи защиту") || lowercasedCommand.contains("включить защиту") {
            completion(VoiceCommandResult(action: .enableProtection, message: "Защита включена"))
        }
        else if lowercasedCommand.contains("выключи защиту") || lowercasedCommand.contains("выключить защиту") {
            completion(VoiceCommandResult(action: .disableProtection, message: "Защита выключена"))
        }
        else if lowercasedCommand.contains("включи впн") || lowercasedCommand.contains("включить vpn") {
            completion(VoiceCommandResult(action: .enableVPN, message: "VPN включен"))
        }
        else if lowercasedCommand.contains("выключи впн") || lowercasedCommand.contains("выключить vpn") {
            completion(VoiceCommandResult(action: .disableVPN, message: "VPN выключен"))
        }
        else if lowercasedCommand.contains("покажи аналитику") || lowercasedCommand.contains("показать аналитику") {
            completion(VoiceCommandResult(action: .showAnalytics, message: "Открываю аналитику"))
        }
        else if lowercasedCommand.contains("покажи семью") || lowercasedCommand.contains("показать семью") {
            completion(VoiceCommandResult(action: .showFamily, message: "Открываю семью"))
        }
        else if lowercasedCommand.contains("помощь") || lowercasedCommand.contains("помоги") {
            completion(VoiceCommandResult(action: .showHelp, message: "Чем могу помочь?"))
        }
        else {
            completion(VoiceCommandResult(action: .unknown, message: "Команда не распознана"))
        }
    }
    
    // MARK: - Text to Speech
    
    func speak(_ text: String) {
        let synthesizer = AVSpeechSynthesizer()
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "ru-RU")
        utterance.rate = 0.5
        
        synthesizer.speak(utterance)
        print("🔊 Speaking: \(text)")
    }
}

// MARK: - Data Models

struct VoiceCommandResult {
    let action: VoiceAction
    let message: String
}

enum VoiceAction {
    case enableProtection
    case disableProtection
    case enableVPN
    case disableVPN
    case showAnalytics
    case showFamily
    case showHelp
    case unknown
}

