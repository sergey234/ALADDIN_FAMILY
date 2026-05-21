import AVFoundation
import CoreMedia

/// Извлекает амплитуды из m4a для отображения реальной формы волны на карточке заметки.
enum VoiceNoteWaveformSampler {
    private static var cache: [String: [CGFloat]] = [:]
    private static let cacheLock = NSLock()

    static func samples(forFilePath path: String, barCount: Int = 24) -> [CGFloat] {
        let count = max(barCount, 1)
        cacheLock.lock()
        if let cached = cache[path], cached.count == count {
            cacheLock.unlock()
            return cached
        }
        cacheLock.unlock()

        let url = URL(fileURLWithPath: path)
        guard FileManager.default.fileExists(atPath: path) else {
            return decorativeFallback(barCount: count)
        }

        let asset = AVURLAsset(url: url)
        guard let track = asset.tracks(withMediaType: .audio).first else {
            return decorativeFallback(barCount: count)
        }

        let settings: [String: Any] = [
            AVFormatIDKey: kAudioFormatLinearPCM,
            AVLinearPCMIsBigEndianKey: false,
            AVLinearPCMIsFloatKey: false,
            AVLinearPCMBitDepthKey: 16,
            AVLinearPCMIsNonInterleaved: false
        ]

        guard let reader = try? AVAssetReader(asset: asset) else {
            return decorativeFallback(barCount: count)
        }
        let output = AVAssetReaderTrackOutput(track: track, outputSettings: settings)
        reader.add(output)
        guard reader.startReading() else {
            return decorativeFallback(barCount: count)
        }

        var bucketMax: [Float] = Array(repeating: 0, count: count)
        var bucketSamples: [Int] = Array(repeating: 0, count: count)
        var totalSamples = 0

        while reader.status == .reading, let sampleBuffer = output.copyNextSampleBuffer() {
            guard let block = CMSampleBufferGetDataBuffer(sampleBuffer) else { continue }
            var length = 0
            var dataPointer: UnsafeMutablePointer<Int8>?
            let status = CMBlockBufferGetDataPointer(
                block,
                atOffset: 0,
                lengthAtOffsetOut: nil,
                totalLengthOut: &length,
                dataPointerOut: &dataPointer
            )
            guard status == kCMBlockBufferNoErr, let dataPointer else { continue }

            let sampleCount = length / MemoryLayout<Int16>.size
            dataPointer.withMemoryRebound(to: Int16.self, capacity: sampleCount) { samples in
                for i in 0..<sampleCount {
                    let amplitude = abs(Float(samples[i])) / Float(Int16.max)
                    let bucket = totalSamples % count
                    bucketMax[bucket] = max(bucketMax[bucket], amplitude)
                    bucketSamples[bucket] += 1
                    totalSamples += 1
                }
            }
        }

        let heights: [CGFloat] = bucketMax.map { peak in
            let normalized = min(max(peak, 0), 1)
            return CGFloat(4 + normalized * 18)
        }

        cacheLock.lock()
        cache[path] = heights
        cacheLock.unlock()
        return heights
    }

    private static func decorativeFallback(barCount: Int) -> [CGFloat] {
        (0..<barCount).map { i in
            let n = ((i * 7 + 3) % 17 + 17) % 17
            return CGFloat(4 + n)
        }
    }
}
