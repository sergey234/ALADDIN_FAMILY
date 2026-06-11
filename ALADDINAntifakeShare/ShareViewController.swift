import UIKit
import UniformTypeIdentifiers

/// B2-08 / af-7-01 — Share sheet «Проверить в ALADDIN» for plain text and URLs.
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
            let url = AntifakeShareConstants.checkDeepLinkURL

            await MainActor.run {
                extensionContext?.open(url, completionHandler: { _ in
                    self.finish()
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
                if let payload = makePayload(from: attributed) {
                    return payload
                }
            }
        }
        return nil
    }

    private func extractFromAttachments(_ attachments: [NSItemProvider]?) async -> AntifakeSharePayload? {
        guard let attachments else { return nil }

        for provider in attachments {
            if provider.hasItemConformingToTypeIdentifier(UTType.url.identifier),
               let url = try? await loadURL(from: provider) {
                let value = url.absoluteString.trimmingCharacters(in: .whitespacesAndNewlines)
                if !value.isEmpty {
                    return AntifakeSharePayload(mode: .url, value: value, createdAt: Date())
                }
            }

            if provider.hasItemConformingToTypeIdentifier(UTType.plainText.identifier),
               let text = try? await loadText(from: provider),
               let payload = makePayload(from: text) {
                return payload
            }
        }

        return nil
    }

    private func makePayload(from raw: String) -> AntifakeSharePayload? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        if let url = URL(string: trimmed),
           let scheme = url.scheme?.lowercased(),
           scheme == "http" || scheme == "https" {
            return AntifakeSharePayload(mode: .url, value: trimmed, createdAt: Date())
        }

        return AntifakeSharePayload(mode: .text, value: trimmed, createdAt: Date())
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
