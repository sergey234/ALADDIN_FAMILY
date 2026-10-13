import Foundation

/// Local-only persistence for Calls hub cards.
final class CallSessionsStore {
    private let fileURL: URL

    init() {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        let dir = appSupport.appendingPathComponent("CallSessions", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try? FileManager.default.setAttributes(
            [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication],
            ofItemAtPath: dir.path
        )
        fileURL = dir.appendingPathComponent("sessions.json")
    }

    func load() -> [CallSession] {
        guard let data = try? Data(contentsOf: fileURL) else { return [] }
        return (try? JSONDecoder().decode([CallSession].self, from: data)) ?? []
    }

    func save(_ sessions: [CallSession]) {
        guard let data = try? JSONEncoder().encode(sessions) else { return }
        try? data.write(to: fileURL, options: .atomic)
        try? FileManager.default.setAttributes(
            [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication],
            ofItemAtPath: fileURL.path
        )
    }

    func upsert(_ session: CallSession) {
        var all = load()
        if let idx = all.firstIndex(where: { $0.id == session.id }) {
            all[idx] = session
        } else {
            all.insert(session, at: 0)
        }
        all.sort { $0.createdAt > $1.createdAt }
        save(all)
    }

    func delete(id: UUID) {
        var all = load()
        if let session = all.first(where: { $0.id == id }) {
            deleteAudioIfExists(path: session.audioPath)
        }
        all.removeAll { $0.id == id }
        save(all)
    }

    func deleteAudioIfExists(path: String) {
        guard !path.isEmpty else { return }
        let url = URL(fileURLWithPath: path)
        if FileManager.default.fileExists(atPath: url.path) {
            try? FileManager.default.removeItem(at: url)
        }
    }
}
