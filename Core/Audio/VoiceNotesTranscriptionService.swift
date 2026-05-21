import Foundation
import Speech

enum VoiceNotesTranscriptionError: Error {
    case permissionDenied
    case recognizerUnavailable
    case timedOut
    case failed(String)
}

final class VoiceNotesTranscriptionService {
    private let timeoutSec: TimeInterval = 45

    func transcribeOnDevice(url: URL, completion: @escaping (Result<String, Error>) -> Void) {
        transcribe(url: url, preferOnDevice: true, completion: completion)
    }

    func transcribe(url: URL, preferOnDevice: Bool, completion: @escaping (Result<String, Error>) -> Void) {
        let lock = NSLock()
        var isCompleted = false
        func completeOnce(_ result: Result<String, Error>) {
            lock.lock()
            defer { lock.unlock() }
            guard !isCompleted else { return }
            isCompleted = true
            completion(result)
        }

        SFSpeechRecognizer.requestAuthorization { status in
            guard status == .authorized else {
                completeOnce(.failure(VoiceNotesTranscriptionError.permissionDenied))
                return
            }

            let locale = LocalizationManager.shared.speechRecognitionLocale
            let selection: SpeechRecognizerFactory.Selection?
            if preferOnDevice {
                selection = SpeechRecognizerFactory.bestForFileTranscription(preferred: locale)
            } else {
                selection = SpeechRecognizerFactory.cloudOnly(preferred: locale)
            }

            guard let selection else {
                if preferOnDevice {
                    self.transcribe(url: url, preferOnDevice: false, completion: completion)
                    return
                }
                completeOnce(.failure(VoiceNotesTranscriptionError.recognizerUnavailable))
                return
            }

            let request = SFSpeechURLRecognitionRequest(url: url)
            request.shouldReportPartialResults = false
            if selection.useOnDeviceRecognition {
                request.requiresOnDeviceRecognition = true
            }

            var recognitionTask: SFSpeechRecognitionTask?
            recognitionTask = selection.recognizer.recognitionTask(with: request) { result, error in
                if let error {
                    let ns = error as NSError
                    if preferOnDevice && selection.useOnDeviceRecognition,
                       ns.domain == "kAFAssistantErrorDomain", ns.code == 1101 {
                        recognitionTask?.cancel()
                        self.transcribe(url: url, preferOnDevice: false, completion: completion)
                        return
                    }
                    completeOnce(.failure(VoiceNotesTranscriptionError.failed(error.localizedDescription)))
                    return
                }
                if let result, result.isFinal {
                    completeOnce(.success(result.bestTranscription.formattedString))
                }
            }

            DispatchQueue.global().asyncAfter(deadline: .now() + self.timeoutSec) {
                lock.lock()
                let done = isCompleted
                lock.unlock()
                if !done {
                    recognitionTask?.cancel()
                    completeOnce(.failure(VoiceNotesTranscriptionError.timedOut))
                }
            }
        }
    }
}
