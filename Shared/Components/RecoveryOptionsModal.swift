import SwiftUI

/// 🔐 Recovery Options Modal
/// Модальное окно для восстановления доступа
struct RecoveryOptionsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var selectedOption: RecoveryOption = .backup
    
    enum RecoveryOption: String, CaseIterable {
        case backup = "backup"
        
        var displayName: String {
            return LocalizationManager.shared.localized("recovery_option_backup")
        }
        
        var icon: String {
            return "externaldrive"
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("🔐")
                    .font(.system(size: 64))
                
                Text(localizationManager.localized("recovery_access_title"))
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text(localizationManager.localized("recovery_access_subtitle"))
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                
                VStack(spacing: 12) {
                    // Показать только Backup опцию (без выбора)
                    HStack {
                        Image(systemName: RecoveryOption.backup.icon)
                            .font(.title2)
                            .foregroundColor(.blue)
                            .frame(width: 30)
                        
                        Text(RecoveryOption.backup.displayName)
                            .font(.body)
                            .foregroundColor(.primary)
                        
                        Spacer()
                        
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.blue)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.blue.opacity(0.1))
                    )
                }
                
                Spacer()
                
                Button("Продолжить") {
                    if selectedOption == .backup {
                        // Открыть BackupRecoveryModal
                        // (будет реализовано в Этапе 2)
                        isPresented = false
                    }
                }
                .buttonStyle(.bordered)
                .disabled(false)
            }
            .padding()
            .navigationTitle(localizationManager.localized("recovery_navigation_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

#if DEBUG
struct RecoveryOptionsModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryOptionsModal(isPresented: .constant(true))
    }
}
#endif
