import Foundation
import Speech

enum VoiceNotesTranscriptionError: Error {
    case permissionDenied
    case recognizerUnavailable
    case timedOut
    case failed(String)
}

final class VoiceNotesTranscriptionService {
    private let recognizer = SFSpeechRecognizer(locale: LocalizationManager.shared.speechRecognitionLocale)

    func transcribeOnDevice(url: URL, completion: @escaping (Result<String, Error>) -> Void) {
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

            guard let recognizer = self.recognizer, recognizer.isAvailable else {
                completeOnce(.failure(VoiceNotesTranscriptionError.recognizerUnavailable))
                return
            }

            let request = SFSpeechURLRecognitionRequest(url: url)
            request.requiresOnDeviceRecognition = true
            request.shouldReportPartialResults = false

            let task = recognizer.recognitionTask(with: request) { result, error in
                if let error {
                    completeOnce(.failure(VoiceNotesTranscriptionError.failed(error.localizedDescription)))
                    return
                }
                if let result, result.isFinal {
                    completeOnce(.success(result.bestTranscription.formattedString))
                }
            }

            DispatchQueue.global().asyncAfter(deadline: .now() + 15) {
                lock.lock()
                let done = isCompleted
                lock.unlock()
                if !done {
                    task.cancel()
                    completeOnce(.failure(VoiceNotesTranscriptionError.timedOut))
                }
            }
        }
    }
}
