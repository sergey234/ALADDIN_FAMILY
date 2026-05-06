import Foundation

final class VoiceNotesStore {
    struct StoredVoiceNote: Codable {
        let id: UUID
        var title: String
        let createdAt: Date
        var durationSec: Int
        var transcriptPreview: String
        var summary: String
        var summaryConfidence: Double
        var summaryVersion: Int
        var tags: [String]
        var audioPath: String

        init(
            id: UUID,
            title: String,
            createdAt: Date,
            durationSec: Int,
            transcriptPreview: String,
            summary: String,
            summaryConfidence: Double,
            summaryVersion: Int,
            tags: [String],
            audioPath: String
        ) {
            self.id = id
            self.title = title
            self.createdAt = createdAt
            self.durationSec = durationSec
            self.transcriptPreview = transcriptPreview
            self.summary = summary
            self.summaryConfidence = summaryConfidence
            self.summaryVersion = summaryVersion
            self.tags = tags
            self.audioPath = audioPath
        }

        enum CodingKeys: String, CodingKey {
            case id, title, createdAt, durationSec, transcriptPreview, summary, summaryConfidence, summaryVersion, tags, audioPath
        }

        init(from decoder: Decoder) throws {
            let c = try decoder.container(keyedBy: CodingKeys.self)
            id = try c.decode(UUID.self, forKey: .id)
            title = try c.decode(String.self, forKey: .title)
            createdAt = try c.decode(Date.self, forKey: .createdAt)
            durationSec = try c.decode(Int.self, forKey: .durationSec)
            transcriptPreview = try c.decode(String.self, forKey: .transcriptPreview)
            summary = try c.decode(String.self, forKey: .summary)
            summaryConfidence = try c.decode(Double.self, forKey: .summaryConfidence)
            summaryVersion = try c.decodeIfPresent(Int.self, forKey: .summaryVersion) ?? (summary.isEmpty ? 0 : 1)
            tags = try c.decode([String].self, forKey: .tags)
            audioPath = try c.decode(String.self, forKey: .audioPath)
        }
    }

    private let notesFileURL: URL

    init() {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        let dir = appSupport.appendingPathComponent("VoiceNotes", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try? FileManager.default.setAttributes([.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication], ofItemAtPath: dir.path)
        notesFileURL = dir.appendingPathComponent("notes.json")
    }

    func load() -> [StoredVoiceNote] {
        guard let data = try? Data(contentsOf: notesFileURL) else { return [] }
        return (try? JSONDecoder().decode([StoredVoiceNote].self, from: data)) ?? []
    }

    func save(_ notes: [StoredVoiceNote]) {
        guard let data = try? JSONEncoder().encode(notes) else { return }
        try? data.write(to: notesFileURL, options: .atomic)
        try? FileManager.default.setAttributes([.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication], ofItemAtPath: notesFileURL.path)
    }

    func deleteAudioIfExists(path: String) {
        let url = URL(fileURLWithPath: path)
        if FileManager.default.fileExists(atPath: url.path) {
            try? FileManager.default.removeItem(at: url)
        }
    }
}
