import SwiftUI

/// Модальное окно для просмотра деталей карантина антивируса
struct AntivirusQuarantineModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var quarantineManager = QuarantineManager.shared
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                if quarantineManager.quarantinedFiles.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "shield.checkered")
                            .font(.system(size: 64))
                            .foregroundColor(.textSecondary.opacity(0.5))
                        
                        Text(localizationManager.localized("antivirus_no_quarantine"))
                            .font(.headline)
                            .foregroundColor(.textSecondary)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: Spacing.m) {
                            // Статистика карантина
                            QuarantineStatsCard()
                            
                            // Список файлов в карантине
                            ForEach(quarantineManager.quarantinedFiles.filter { $0.status == "quarantined" }, id: \.id) { file in
                                QuarantineFileRow(file: file)
                            }
                        }
                        .padding(Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("antivirus_quarantine_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    private struct QuarantineStatsCard: View {
        @ObservedObject private var quarantineManager = QuarantineManager.shared
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            let stats = quarantineManager.getQuarantineStats()
            
            VStack(spacing: Spacing.m) {
                HStack {
                    Text(localizationManager.localized("antivirus_quarantine_title"))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Spacer()
                }
                
                HStack(spacing: Spacing.l) {
                    StatItem(
                        value: "\(stats.activeFiles)",
                        label: localizationManager.localized("antivirus_active_files")
                    )
                    
                    StatItem(
                        value: "\(stats.restoredFiles)",
                        label: localizationManager.localized("antivirus_restored_files")
                    )
                    
                    StatItem(
                        value: "\(stats.removedFiles)",
                        label: localizationManager.localized("antivirus_removed_files")
                    )
                }
                
                HStack {
                    Text(localizationManager.localized("antivirus_quarantine_size"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(formatBytes(stats.quarantineSize))
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private struct StatItem: View {
            let value: String
            let label: String
            
            var body: some View {
                VStack(spacing: 4) {
                    Text(value)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.textPrimary)
                    Text(label)
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
            }
        }
        
        private func formatBytes(_ bytes: Int64) -> String {
            let formatter = ByteCountFormatter()
            formatter.allowedUnits = [.useKB, .useMB, .useGB]
            formatter.countStyle = .file
            return formatter.string(fromByteCount: bytes)
        }
    }
    
    private struct QuarantineFileRow: View {
        let file: QuarantineManager.QuarantinedFile
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Image(systemName: threatIcon(file.severity))
                        .foregroundColor(threatColor(file.severity))
                        .font(.title3)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(file.originalName)
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                        
                        Text(file.threatName)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                    
                    Menu {
                        Button(action: {
                            Task {
                                do {
                                    let restoreURL = URL(fileURLWithPath: file.originalPath)
                                    try await QuarantineManager.shared.restoreFile(from: file, to: restoreURL)
                                } catch {
                                    print("Ошибка восстановления: \(error)")
                                }
                            }
                        }) {
                            Label("Восстановить", systemImage: "arrow.uturn.backward")
                        }
                        
                        Button(role: .destructive, action: {
                            Task {
                                do {
                                    try await QuarantineManager.shared.permanentlyRemoveFile(file)
                                } catch {
                                    print("Ошибка удаления: \(error)")
                                }
                            }
                        }) {
                            Label("Удалить навсегда", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .foregroundColor(.textSecondary)
                    }
                }
                
                HStack {
                    Label(file.threatType, systemImage: "tag")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Spacer()
                    
                    Text(formatDate(file.quarantinedAt))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private func threatIcon(_ severity: String) -> String {
            switch severity.lowercased() {
            case "high", "critical":
                return "exclamationmark.triangle.fill"
            case "medium":
                return "exclamationmark.circle.fill"
            default:
                return "info.circle.fill"
            }
        }
        
        private func threatColor(_ severity: String) -> Color {
            switch severity.lowercased() {
            case "high", "critical":
                return .red
            case "medium":
                return .warningOrange
            default:
                return .textSecondary
            }
        }
        
        private func formatDate(_ date: Date) -> String {
            let formatter = DateFormatter()
            formatter.dateStyle = .short
            formatter.timeStyle = .short
            formatter.locale = Locale(identifier: localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US")
            return formatter.string(from: date)
        }
    }
}
