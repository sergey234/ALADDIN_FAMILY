import UIKit
import UniformTypeIdentifiers

/// B2-08 / af-7-01 — Share sheet «Проверить в ALADDIN» for plain text, URLs, images, and PDF.
/// fsl-02: image / PDF → App Group inbox → Hub tab «Документ».
final class ShareViewController: UIViewController {

    private var didProcess = false

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !didProcess else { return }
        didProcess = true
        processSharedItems()
    }

    private func processSharedItems() {
        guard let items = extensionContext?.inputItems as? [NSExtensionItem], !items.isEmpty else {
            finish()
            return
        }

        Task {
            guard let payload = await extractPayload(from: items) else {
                await MainActor.run { finish() }
                return
            }

            AntifakeSharePayloadStore.save(payload)
            let appURL = AntifakeShareConstants.checkDeepLinkURL
            let webURL = AntifakeShareConstants.webCheckURL(for: payload)

            await MainActor.run {
                self.extensionContext?.open(appURL, completionHandler: { opened in
                    if !opened {
                        self.extensionContext?.open(webURL, completionHandler: { _ in
                            self.finish()
                        })
                    } else {
                        self.finish()
                    }
                })
            }
        }
    }

    private func extractPayload(from items: [NSExtensionItem]) async -> AntifakeSharePayload? {
        for item in items {
            if let payload = await extractFromAttachments(item.attachments) {
                return payload
            }

            if let attributed = item.attributedContentText?.string {
                if let payload = makeTextOrURLPayload(from: attributed) {
                    return payload
                }
            }
        }
        return nil
    }

    private func extractFromAttachments(_ attachments: [NSItemProvider]?) async -> AntifakeSharePayload? {
        guard let attachments else { return nil }

        for provider in attachments {
            if provider.hasItemConformingToTypeIdentifier(UTType.pdf.identifier),
               let payload = await loadDocumentPayload(from: provider, type: .pdf, defaultName: "shared.pdf") {
                return payload
            }

            if provider.hasItemConformingToTypeIdentifier(UTType.image.identifier),
               let payload = await loadDocumentPayload(from: provider, type: .image, defaultName: "shared.jpg") {
                return payload
            }

            if provider.hasItemConformingToTypeIdentifier(UTType.url.identifier),
               let url = try? await loadURL(from: provider) {
                // file:// PDF/image from Files
                if url.isFileURL, let payload = loadLocalFileAsDocument(url) {
                    return payload
                }
                let value = url.absoluteString.trimmingCharacters(in: .whitespacesAndNewlines)
                if !value.isEmpty {
                    return AntifakeSharePayload(mode: .url, value: value, createdAt: Date())
                }
            }

            if provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier),
               let text = try? await loadText(from: provider),
               let payload = makeTextOrURLPayload(from: text) {
                return payload
            }
        }

        return nil
    }

    private func loadDocumentPayload(
        from provider: NSItemProvider,
        type: UTType,
        defaultName: String
    ) async -> AntifakeSharePayload? {
        do {
            let (data, filename) = try await loadFileData(from: provider, typeIdentifier: type.identifier, defaultName: defaultName)
            guard !data.isEmpty else { return nil }
            try AntifakeSharePayloadStore.saveDocument(data: data, filename: filename)
            return AntifakeSharePayloadStore.load()
        } catch {
            return nil
        }
    }

    private func loadLocalFileAsDocument(_ url: URL) -> AntifakeSharePayload? {
        let ext = url.pathExtension.lowercased()
        let allowed = ["pdf", "jpg", "jpeg", "png", "heic", "webp"]
        guard allowed.contains(ext) else { return nil }
        guard let data = try? Data(contentsOf: url), !data.isEmpty else { return nil }
        do {
            try AntifakeSharePayloadStore.saveDocument(data: data, filename: url.lastPathComponent)
            return AntifakeSharePayloadStore.load()
        } catch {
            return nil
        }
    }

    private func makeTextOrURLPayload(from raw: String) -> AntifakeSharePayload? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        if let url = URL(string: trimmed),
           let scheme = url.scheme?.lowercased(),
           scheme == "http" || scheme == "https" {
            return AntifakeSharePayload(mode: .url, value: trimmed, createdAt: Date())
        }

        return AntifakeSharePayload(mode: .text, value: trimmed, createdAt: Date())
    }

    private func loadFileData(
        from provider: NSItemProvider,
        typeIdentifier: String,
        defaultName: String
    ) async throws -> (Data, String) {
        try await withCheckedThrowingContinuation { continuation in
            provider.loadItem(forTypeIdentifier: typeIdentifier, options: nil) { item, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                if let url = item as? URL {
                    let accessing = url.startAccessingSecurityScopedResource()
                    defer {
                        if accessing { url.stopAccessingSecurityScopedResource() }
                    }
                    do {
                        let data = try Data(contentsOf: url)
                        let name = url.lastPathComponent.isEmpty ? defaultName : url.lastPathComponent
                        continuation.resume(returning: (data, name))
                    } catch {
                        continuation.resume(throwing: error)
                    }
                    return
                }

                if let data = item as? Data {
                    continuation.resume(returning: (data, defaultName))
                    return
                }

                if let image = item as? UIImage {
                    let data = image.jpegData(compressionQuality: 0.85) ?? Data()
                    continuation.resume(returning: (data, defaultName))
                    return
                }

                continuation.resume(throwing: AntifakeShareInboxError.noAppGroup)
            }
        }
    }

    private func loadText(from provider: NSItemProvider) async throws -> String? {
        try await withCheckedThrowingContinuation { continuation in
            provider.loadItem(forTypeIdentifier: UTType.plainText.identifier, options: nil) { item, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                if let text = item as? String {
                    continuation.resume(returning: text)
                    return
                }

                if let data = item as? Data {
                    continuation.resume(returning: String(data: data, encoding: .utf8))
                    return
                }

                if let url = item as? URL,
                   let text = try? String(contentsOf: url, encoding: .utf8) {
                    continuation.resume(returning: text)
                    return
                }

                continuation.resume(returning: nil)
            }
        }
    }

    private func loadURL(from provider: NSItemProvider) async throws -> URL? {
        try await withCheckedThrowingContinuation { continuation in
            provider.loadItem(forTypeIdentifier: UTType.url.identifier, options: nil) { item, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }

                if let url = item as? URL {
                    continuation.resume(returning: url)
                    return
                }

                if let text = item as? String, let url = URL(string: text) {
                    continuation.resume(returning: url)
                    return
                }

                continuation.resume(returning: nil)
            }
        }
    }

    private func finish() {
        extensionContext?.completeRequest(returningItems: nil, completionHandler: nil)
    }
}
