import AVFoundation
import Accelerate

/// Нормализация уровня микрофона (0…1) для UI waveform.
enum AudioLevelMeter {
    static func normalizedLevel(fromAveragePower decibels: Float) -> Double {
        let clamped = min(max(decibels, -60), 0)
        let linear = pow(10, clamped / 20)
        return min(max(Double(linear), 0), 1)
    }

    static func normalizedLevel(from buffer: AVAudioPCMBuffer) -> Double {
        let count = Int(buffer.frameLength)
        guard count > 0 else { return 0 }

        if let channel = buffer.floatChannelData?.pointee {
            var rms: Float = 0
            vDSP_rmsqv(channel, 1, &rms, vDSP_Length(count))
            let db = 20 * log10(max(rms, 1e-7))
            return normalizedLevel(fromAveragePower: db)
        }

        if let channel = buffer.int16ChannelData?.pointee {
            var sum: Float = 0
            for i in 0..<count {
                let sample = Float(channel[i])
                sum += sample * sample
            }
            let rms = sqrt(sum / Float(count))
            let db = 20 * log10(max(rms, 1e-7))
            return normalizedLevel(fromAveragePower: db)
        }

        return 0
    }
}
