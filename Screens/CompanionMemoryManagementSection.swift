import SwiftUI

/// P1-03: просмотр, экспорт и удаление памяти компаньона (семейный scope).
struct CompanionMemoryManagementSection: View {
    @State private var memoryEnabled = false
    @State private var items: [CompanionMemoryItemDTO] = []
    @State private var isLoading = true
    @State private var isDeleting = false
    @State private var isExporting = false
    @State private var statusMessage: String?
    @State private var errorText: String?
    @State private var shareURL: URL?
    @State private var showShareSheet = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: 8) {
                Text("🧠")
                    .font(.title2)
                Text("Память компаньона")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }

            Text("Краткие заметки без PII после разговоров. Родитель может выгрузить или удалить всё (152-ФЗ).")
                .font(.caption)
                .foregroundColor(.textSecondary)

            if isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else if !memoryEnabled {
                Text("Память выключена. Включите переключатель «Память компаньона» выше и сохраните настройки.")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                if items.isEmpty {
                    Text("Пока нет сохранённых заметок. Они появятся после диалогов ребёнка с героем.")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                } else {
                    Text("Записей: \(items.count)")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.textSecondary)

                    ForEach(items.prefix(8)) { item in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.summary)
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                                .lineLimit(3)
                            Text(item.updatedAt)
                                .font(.caption2)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.backgroundMedium.opacity(0.25))
                        .cornerRadius(8)
                    }
                    if items.count > 8 {
                        Text("… и ещё \(items.count - 8)")
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                    }
                }

                HStack(spacing: 12) {
                    Button {
                        Task { await exportMemory() }
                    } label: {
                        Label(isExporting ? "Экспорт…" : "Экспорт JSON", systemImage: "square.and.arrow.up")
                            .font(.caption.weight(.semibold))
                    }
                    .disabled(isExporting || isDeleting)

                    Button(role: .destructive) {
                        Task { await deleteAll() }
                    } label: {
                        Label(isDeleting ? "Удаление…" : "Удалить всё", systemImage: "trash")
                            .font(.caption.weight(.semibold))
                    }
                    .disabled(isDeleting || isExporting)
                }
                .padding(.top, 4)
            }

            if let statusMessage {
                Text(statusMessage)
                    .font(.caption)
                    .foregroundColor(.green)
            }
            if let errorText {
                Text(errorText)
                    .font(.caption)
                    .foregroundColor(.orange)
            }
        }
        .padding(Spacing.m)
        .background(Color.blue.opacity(0.08))
        .cornerRadius(CornerRadius.medium)
        .task { await reload() }
        .onReceive(NotificationCenter.default.publisher(for: .companionConsentDidSave)) { _ in
            Task { await reload() }
        }
        .sheet(isPresented: $showShareSheet, onDismiss: { shareURL = nil }) {
            if let shareURL {
                ShareSheet(activityItems: [shareURL])
            }
        }
    }

    private func reload() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let response = try await CompanionAPIService.shared.fetchMemory()
            memoryEnabled = response.memoryEnabled
            items = response.items
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func deleteAll() async {
        isDeleting = true
        errorText = nil
        statusMessage = nil
        defer { isDeleting = false }
        do {
            let resp = try await CompanionAPIService.shared.deleteAllMemory()
            items = []
            memoryEnabled = resp.memoryEnabled
            statusMessage = "Удалено записей: \(resp.itemsRemoved). Память выключена."
            HapticFeedback.impact(.medium)
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func exportMemory() async {
        isExporting = true
        errorText = nil
        defer { isExporting = false }
        do {
            let payload = try await CompanionAPIService.shared.exportMemory()
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let data = try encoder.encode(payload)
            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("aladdin_companion_memory_\(Int(Date().timeIntervalSince1970)).json")
            try data.write(to: url, options: .atomic)
            shareURL = url
            showShareSheet = true
            statusMessage = "Готово к отправке (\(payload.itemCount) записей)."
        } catch {
            errorText = error.localizedDescription
        }
    }
}

extension Notification.Name {
    static let companionConsentDidSave = Notification.Name("companionConsentDidSave")
}
