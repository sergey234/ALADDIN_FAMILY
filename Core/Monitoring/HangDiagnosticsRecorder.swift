import Foundation
import MetricKit

/// Persists MetricKit diagnostics (hangs, crashes, CPU exceptions) to `Documents/MetricKit/`.
/// A watchdog `.ips` holds one snapshot of the main thread at kill time; `MXHangDiagnostic`
/// keeps the call tree sampled over the whole hang. Files are visible in the Files app
/// (UIFileSharingEnabled) and are symbolicated offline with the build's dSYM.
final class HangDiagnosticsRecorder: NSObject, MXMetricManagerSubscriber {
    static let shared = HangDiagnosticsRecorder()

    static let directoryName = "MetricKit"
    static let maxStoredPayloads = 30

    private let ioQueue = DispatchQueue(label: "ai.aladdin.metrickit.io", qos: .utility)
    private var isStarted = false

    private override init() {
        super.init()
    }

    /// Call once on the main thread at launch.
    func start() {
        guard !isStarted else { return }
        isStarted = true
        MXMetricManager.shared.add(self)
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        guard !payloads.isEmpty else { return }
        let entries = payloads.map { payload in
            (
                json: payload.jsonRepresentation(),
                hangs: payload.hangDiagnostics?.count ?? 0,
                crashes: payload.crashDiagnostics?.count ?? 0,
                cpu: payload.cpuExceptionDiagnostics?.count ?? 0
            )
        }
        ioQueue.async {
            let stamp = Int(Date().timeIntervalSince1970)
            for (index, entry) in entries.enumerated() {
                Self.write(entry.json, fileName: "metrickit_\(stamp)_\(index).json")
                LaunchDiagnostics.appendLifecycleTrace(
                    "MetricKit diagnostic saved: hangs=\(entry.hangs) crashes=\(entry.crashes) cpu=\(entry.cpu)"
                )
            }
            Self.pruneOldFiles()
        }
    }

    private static func directoryURL() -> URL? {
        guard let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return nil
        }
        return docs.appendingPathComponent(directoryName, isDirectory: true)
    }

    private static func write(_ data: Data, fileName: String) {
        guard let dir = directoryURL() else { return }
        do {
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            try data.write(to: dir.appendingPathComponent(fileName), options: .atomic)
        } catch {
            print("⚠️ HangDiagnosticsRecorder write failed: \(error)")
        }
    }

    private static func pruneOldFiles() {
        guard let dir = directoryURL(),
              let files = try? FileManager.default.contentsOfDirectory(
                at: dir,
                includingPropertiesForKeys: [.contentModificationDateKey]
              ),
              files.count > maxStoredPayloads else { return }
        let sorted = files.sorted { lhs, rhs in
            let l = (try? lhs.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
            let r = (try? rhs.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
            return l < r
        }
        for url in sorted.prefix(files.count - maxStoredPayloads) {
            try? FileManager.default.removeItem(at: url)
        }
    }
}
