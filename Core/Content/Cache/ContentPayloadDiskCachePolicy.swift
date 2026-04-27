import Foundation

/// Лимит диска и LRU для `Application Support/ContentPayloads` (G2 / W1-2).
/// Eviction: удаляются целые каталоги `<contentId>/`, начиная с самого старого по `mtime` файла `payload.bin`.
enum ContentPayloadDiskCachePolicy {

    static func payloadsRoot() throws -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        let root = base.appendingPathComponent("ContentPayloads", isDirectory: true)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        return root
    }

    static func enforceBudgetIfNeeded(maxTotalBytes: Int) throws {
        guard maxTotalBytes > 0 else { return }
        let root = try payloadsRoot()
        try enforceBudget(root: root, maxTotalBytes: maxTotalBytes)
    }

    /// Удаляет самые старые payload-каталоги, пока суммарный размер `payload.bin` не станет ≤ лимита.
    static func enforceBudget(root: URL, maxTotalBytes: Int) throws {
        guard maxTotalBytes > 0 else { return }
        guard FileManager.default.fileExists(atPath: root.path) else { return }

        while try totalPayloadBytes(under: root) > maxTotalBytes {
            guard let victim = try oldestPayloadContentDirectory(under: root) else { break }
            try FileManager.default.removeItem(at: victim)
        }
    }

    static func totalPayloadBytes(under root: URL) throws -> Int {
        let fm = FileManager.default
        let children = try fm.contentsOfDirectory(at: root, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])
        var sum = 0
        for child in children {
            var isDir: ObjCBool = false
            guard fm.fileExists(atPath: child.path, isDirectory: &isDir), isDir.boolValue else { continue }
            let bin = child.appendingPathComponent("payload.bin", isDirectory: false)
            guard fm.fileExists(atPath: bin.path),
                  let attrs = try? fm.attributesOfItem(atPath: bin.path),
                  let size = attrs[.size] as? NSNumber
            else { continue }
            sum += size.intValue
        }
        return sum
    }

    private static func oldestPayloadContentDirectory(under root: URL) throws -> URL? {
        let fm = FileManager.default
        let children = try fm.contentsOfDirectory(at: root, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])
        var best: (url: URL, date: Date)?
        for child in children {
            var isDir: ObjCBool = false
            guard fm.fileExists(atPath: child.path, isDirectory: &isDir), isDir.boolValue else { continue }
            let bin = child.appendingPathComponent("payload.bin", isDirectory: false)
            guard fm.fileExists(atPath: bin.path) else { continue }
            let vals = try bin.resourceValues(forKeys: [.contentModificationDateKey])
            let date = vals.contentModificationDate ?? .distantPast
            if let cur = best {
                if date < cur.date { best = (child, date) }
            } else {
                best = (child, date)
            }
        }
        return best?.url
    }
}
