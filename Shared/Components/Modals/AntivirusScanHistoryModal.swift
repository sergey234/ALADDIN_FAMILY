import SwiftUI

/// Модальное окно для просмотра полной истории сканирований антивируса
struct AntivirusScanHistoryModal: View {
    @Binding var isPresented: Bool
    let scanHistory: [AntivirusScanHistoryItem]
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Структура для истории сканирований (копия из NetworkProtectionScreen)
    struct AntivirusScanHistoryItem: Identifiable {
        let id: String
        let startTime: Date
        let endTime: Date?
        let filesScanned: Int
        let threatsFound: Int
        let status: String
        let duration: TimeInterval?
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                if scanHistory.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "clock.badge.questionmark")
                            .font(.system(size: 64))
                            .foregroundColor(.textSecondary.opacity(0.5))
                        
                        Text(localizationManager.localized("antivirus_no_scans"))
                            .font(.headline)
                            .foregroundColor(.textSecondary)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: Spacing.m) {
                            ForEach(scanHistory, id: \.id) { session in
                                ScanHistoryRow(session: session)
                            }
                        }
                        .padding(Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("antivirus_scan_history_title"))
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
    
    private struct ScanHistoryRow: View {
        let session: AntivirusScanHistoryItem
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Image(systemName: session.threatsFound > 0 ? "exclamationmark.triangle.fill" : "checkmark.circle.fill")
                        .foregroundColor(session.threatsFound > 0 ? .red : .successGreen)
                        .font(.title3)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(formatDate(session.startTime))
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                        
                        if let endTime = session.endTime, let duration = session.duration {
                            Text("\(localizationManager.localized("antivirus_scan_duration")): \(formatDuration(duration))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("\(session.threatsFound)")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(session.threatsFound > 0 ? .red : .successGreen)
                        
                        Text(localizationManager.localized("antivirus_threats_found_in_scan"))
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                HStack {
                    Label("\(session.filesScanned)", systemImage: "doc.text")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Spacer()
                    
                    Text(session.status.capitalized)
                        .font(.caption)
                        .foregroundColor(statusColor(session.status))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            Capsule()
                                .fill(statusColor(session.status).opacity(0.2))
                        )
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private func formatDate(_ date: Date) -> String {
            let formatter = DateFormatter()
            formatter.dateStyle = .medium
            formatter.timeStyle = .short
            formatter.locale = Locale(identifier: localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US")
            return formatter.string(from: date)
        }
        
        private func formatDuration(_ duration: TimeInterval) -> String {
            let minutes = Int(duration) / 60
            let seconds = Int(duration) % 60
            return String(format: "%d:%02d", minutes, seconds)
        }
        
        private func statusColor(_ status: String) -> Color {
            switch status {
            case "completed":
                return .successGreen
            case "failed":
                return .red
            case "cancelled":
                return .textSecondary
            default:
                return .textSecondary
            }
        }
    }
}
