import SwiftUI
import Combine

/// 💾 Backup Recovery Modal
/// Модальное окно для восстановления доступа из локального сохранения
struct BackupRecoveryModal: View {
    @Binding var isPresented: Bool
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showSuccess = false
    
    // Callback для успешного восстановления
    var onRecoverySuccess: (() -> Void)?
    
    // Publishers для уведомлений
    private let successPublisher = NotificationCenter.default.publisher(for: NSNotification.Name("FamilyRecoverySuccess"))
    private let errorPublisher = NotificationCenter.default.publisher(for: NSNotification.Name("FamilyRecoveryError"))
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Иконка
                Image(systemName: "externaldrive.badge.icloud")
                    .font(.system(size: 64))
                    .foregroundColor(.blue)
                
                // Заголовок
                VStack(spacing: 8) {
                    Text("Восстановление из сохранения")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Восстановить доступ используя сохраненный код")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                
                // Проверка наличия кода
                if isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                } else if let error = errorMessage {
                    // Ошибка
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.orange)
                        
                        Text(error)
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.orange.opacity(0.1))
                    )
                } else if showSuccess {
                    // Успех
                    VStack(spacing: 12) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 40))
                            .foregroundColor(.green)
                        
                        Text("Доступ восстановлен!")
                            .font(.body)
                            .fontWeight(.semibold)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.green.opacity(0.1))
                    )
                } else {
                    // Информация
                    VStack(spacing: 12) {
                        Text("Нажмите кнопку ниже для восстановления доступа из локального сохранения")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                }
                
                Spacer()
                
                // Кнопка восстановления
                if !showSuccess {
                    Button(action: {
                        performRecovery()
                    }) {
                        Text("Восстановить")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(isLoading ? Color.gray : Color.blue)
                            )
                    }
                    .disabled(isLoading)
                } else {
                    Button(action: {
                        onRecoverySuccess?()
                        isPresented = false
                    }) {
                        Text("Готово")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.green)
                            )
                    }
                }
            }
            .padding(20)
            .navigationTitle("Восстановление")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
            .onReceive(successPublisher) { _ in
                isLoading = false
                showSuccess = true
            }
            .onReceive(errorPublisher) { notification in
                isLoading = false
                if let error = notification.userInfo?["error"] as? String {
                    errorMessage = error
                } else {
                    errorMessage = "Ошибка восстановления доступа"
                }
            }
        }
    }
    
    // MARK: - Recovery Logic
    
    private func performRecovery() {
        isLoading = true
        errorMessage = nil
        
        // Проверяем наличие кода
        guard RecoveryCodeStorageManager.shared.hasRecoveryCode() else {
            isLoading = false
            errorMessage = "Сохранение не найдено. Убедитесь, что вы ранее создали семью на этом устройстве."
            return
        }
        
        // Получаем код
        guard let recoveryCode = RecoveryCodeStorageManager.shared.getRecoveryCode() else {
            isLoading = false
            errorMessage = "Ошибка чтения сохранения"
            return
        }
        
        // Создаем ViewModel для восстановления
        let viewModel = FamilyRegistrationViewModel()
        
        // Вызываем метод восстановления
        viewModel.recoverAccess(withCode: recoveryCode)
    }
}

// MARK: - Preview

#if DEBUG
struct BackupRecoveryModal_Previews: PreviewProvider {
    static var previews: some View {
        BackupRecoveryModal(isPresented: .constant(true))
    }
}
#endif

