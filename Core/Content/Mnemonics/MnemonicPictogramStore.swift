import Foundation
import UIKit

/// Co-created mnemo pictograms — PNG per `itemId` under Application Support (no Documents, no PII in filenames).
final class MnemonicPictogramStore {
    static let shared = MnemonicPictogramStore()

    static let directoryName = "MnemoPictograms"

    /// Aligns with `ChildDrawingGalleryStore` active child key.
    static func activeChildId() -> String {
        let raw = UserDefaults.standard
            .string(forKey: "active_child_profile_server_id")?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return raw.isEmpty ? "local-default-child" : raw
    }

    static func supportsCoCreation(itemId: String) -> Bool {
        itemId.hasPrefix("study.") || itemId.hasPrefix("songs.")
    }

    struct IndexEntry: Codable, Equatable {
        let itemId: String
        let childScope: String
        var updatedAt: Date
    }

    private let fileManager: FileManager
    private let rootURL: URL

    init(fileManager: FileManager = .default, rootURL: URL? = nil) {
        self.fileManager = fileManager
        if let rootURL {
            self.rootURL = rootURL
        } else {
            let appSupport = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            self.rootURL = appSupport.appendingPathComponent(Self.directoryName, isDirectory: true)
        }
        ensureRootDirectory()
    }

    // MARK: - Public API

    @discardableResult
    func savePNG(_ data: Data, itemId: String, childId: String? = nil) throws -> URL {
        guard !data.isEmpty else {
            throw StoreError.emptyPayload
        }
        let scope = resolvedChildScope(childId)
        let url = pngFileURL(itemId: itemId, childScope: scope)
        try fileManager.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        try data.write(to: url, options: .atomic)
        try applyFileProtection(at: url)
        upsertIndex(itemId: itemId, childScope: scope, updatedAt: Date())
        return url
    }

    @discardableResult
    func saveImage(_ image: UIImage, itemId: String, childId: String? = nil) throws -> URL {
        guard let data = image.pngData() else {
            throw StoreError.pngEncodingFailed
        }
        return try savePNG(data, itemId: itemId, childId: childId)
    }

    func loadImage(itemId: String, childId: String? = nil) -> UIImage? {
        let url = pngFileURL(itemId: itemId, childScope: resolvedChildScope(childId))
        guard fileManager.fileExists(atPath: url.path),
              let data = try? Data(contentsOf: url),
              let image = UIImage(data: data) else {
            return nil
        }
        return image
    }

    func hasPictogram(itemId: String, childId: String? = nil) -> Bool {
        let url = pngFileURL(itemId: itemId, childScope: resolvedChildScope(childId))
        return fileManager.fileExists(atPath: url.path)
    }

    func pictogramCount(childId: String? = nil) -> Int {
        let scope = resolvedChildScope(childId)
        if let childId, !childId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return loadIndex().filter { $0.childScope == scope }.count
        }
        return loadIndex().count
    }

    func savedItemIds(childId: String? = nil) -> [String] {
        let scope = resolvedChildScope(childId)
        return loadIndex()
            .filter { $0.childScope == scope }
            .sorted { $0.updatedAt > $1.updatedAt }
            .map(\.itemId)
    }

    func fileURL(itemId: String, childId: String? = nil) -> URL {
        pngFileURL(itemId: itemId, childScope: resolvedChildScope(childId))
    }

    func delete(itemId: String, childId: String? = nil) {
        let scope = resolvedChildScope(childId)
        let url = pngFileURL(itemId: itemId, childScope: scope)
        try? fileManager.removeItem(at: url)
        var index = loadIndex()
        index.removeAll { $0.itemId == itemId && $0.childScope == scope }
        persistIndex(index)
    }

    // MARK: - Paths

    func pngFileURL(itemId: String, childScope: String) -> URL {
        rootURL
            .appendingPathComponent(childScope, isDirectory: true)
            .appendingPathComponent(sanitizedFileName(for: itemId) + ".png", isDirectory: false)
    }

    func resolvedChildScope(_ childId: String?) -> String {
        let trimmed = (childId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty { return "default" }
        return sanitizedFileName(for: trimmed)
    }

    func sanitizedFileName(for raw: String) -> String {
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "._-"))
        let scalars = raw.unicodeScalars.map { allowed.contains($0) ? Character($0) : "_" }
        let collapsed = String(scalars)
        return collapsed.isEmpty ? "item" : String(collapsed.prefix(120))
    }

    // MARK: - Index

    private func indexFileURL() -> URL {
        rootURL.appendingPathComponent("index.json", isDirectory: false)
    }

    private func loadIndex() -> [IndexEntry] {
        let url = indexFileURL()
        guard let data = try? Data(contentsOf: url),
              let entries = try? JSONDecoder().decode([IndexEntry].self, from: data) else {
            return []
        }
        return entries
    }

    private func persistIndex(_ entries: [IndexEntry]) {
        let url = indexFileURL()
        guard let data = try? JSONEncoder().encode(entries) else { return }
        try? data.write(to: url, options: .atomic)
        try? applyFileProtection(at: url)
    }

    private func upsertIndex(itemId: String, childScope: String, updatedAt: Date) {
        var index = loadIndex()
        if let idx = index.firstIndex(where: { $0.itemId == itemId && $0.childScope == childScope }) {
            index[idx].updatedAt = updatedAt
        } else {
            index.append(IndexEntry(itemId: itemId, childScope: childScope, updatedAt: updatedAt))
        }
        persistIndex(index)
    }

    private func ensureRootDirectory() {
        try? fileManager.createDirectory(at: rootURL, withIntermediateDirectories: true)
        try? applyFileProtection(at: rootURL)
    }

    private func applyFileProtection(at url: URL) throws {
        try fileManager.setAttributes(
            [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication],
            ofItemAtPath: url.path
        )
    }

    enum StoreError: Error {
        case emptyPayload
        case pngEncodingFailed
    }
}
