import SwiftUI
import CoreImage.CIFilterBuiltins

/**
 * 🔐 Recovery Code Modal
 * Модальное окно для показа кода восстановления и QR-кода
 * 
 * Функции:
 * - Отображение кода в формате FAM-XXXX-XXXX-XXXX
 * - Генерация QR-кода из кода
 * - Кнопка "Копировать"
 * - Кнопка "Поделиться"
 * - Закрытие окна
 */

struct RecoveryCodeModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    let recoveryCode: String
    let familyID: String
    var onComplete: (() -> Void)? = nil
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showShareSheet = false
    @State private var showSuccessAlert = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 30) {
                    // Иконка успеха
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.green)
                    
                    // Заголовок
                    VStack(spacing: 8) {
                        Text(localizationManager.localized("recovery_family_created"))
                            .font(.system(size: 28, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("recovery_save_code"))
                            .font(.system(size: 16))
                            .foregroundColor(.secondary)
                    }
                    
                    // Код восстановления
                    VStack(spacing: 16) {
                        Text(localizationManager.localized("recovery_code_title"))
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        
                        // Код в монопространственном шрифте
                        Text(recoveryCode)
                            .font(.system(size: 20, weight: .bold, design: .monospaced))
                            .foregroundColor(.primary)
                            .padding(20)
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.gray.opacity(0.1))
                            )
                        
                        // Кнопки действий
                        HStack(spacing: 12) {
                            Button(action: {
                                UIPasteboard.general.string = recoveryCode
                                // Haptic feedback
                                let generator = UINotificationFeedbackGenerator()
                                generator.notificationOccurred(.success)
                            }) {
                                HStack {
                                    Image(systemName: "doc.on.doc")
                                    Text(localizationManager.localized("recovery_copy"))
                                }
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.blue)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(Color.blue.opacity(0.1))
                                )
                            }
                            
                            Button(action: {
                                showShareSheet = true
                            }) {
                                HStack {
                                    Image(systemName: "square.and.arrow.up")
                                    Text(localizationManager.localized("recovery_share"))
                                }
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.blue)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(Color.blue.opacity(0.1))
                                )
                            }
                        }
                    }
                    
                    // QR-код
                    VStack(spacing: 12) {
                        Text(localizationManager.localized("recovery_qr_title"))
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.secondary)
                        
                        // Генерация QR-кода
                        if let qrCodeImage = generateQRCode(from: recoveryCode) {
                            Image(uiImage: qrCodeImage)
                                .interpolation(.none)
                                .resizable()
                                .scaledToFit()
                                .frame(width: 200, height: 200)
                                .background(Color.white)
                                .cornerRadius(12)
                                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
                        }
                        
                        Text(localizationManager.localized("recovery_qr_scan"))
                            .font(.system(size: 13))
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(20)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color.gray.opacity(0.05))
                    )
                    
                    // Предупреждение
                    VStack(alignment: .leading, spacing: 12) {
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .font(.system(size: 20))
                                .foregroundColor(.orange)
                            
                            Text(localizationManager.localized("recovery_important_save"))
                                .font(.system(size: 13))
                                .foregroundColor(.secondary)
                        }
                        
                        // Инструкция по использованию QR-кода
                        VStack(alignment: .leading, spacing: 8) {
                            Text(localizationManager.localized("recovery_qr_how_works"))
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.primary)
                            
                            VStack(alignment: .leading, spacing: 6) {
                                infoItem(
                                    icon: "1.circle.fill",
                                    text: localizationManager.localized("recovery_qr_info_1")
                                )
                                infoItem(
                                    icon: "2.circle.fill",
                                    text: localizationManager.localized("recovery_qr_info_2")
                                )
                                infoItem(
                                    icon: "3.circle.fill",
                                    text: localizationManager.localized("recovery_qr_info_3")
                                )
                            }
                            .font(.system(size: 12))
                        }
                    }
                    .padding(16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.orange.opacity(0.1))
                    )
                    
                    // Кнопка "Готово"
                    Button(action: {
                        // Сохраняем что семья создана
                        UserDefaults.standard.set(familyID, forKey: AppConfig.UserDefaultsKeys.familyId)
                        UserDefaults.standard.synchronize()
                        
                        // ✅ ИСПРАВЛЕНИЕ: Закрываем модал - onComplete вызовется через setter
                        isPresented = false
                    }) {
                        Text(localizationManager.localized("recovery_done"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.blue)
                            )
                    }
                }
                .padding(20)
            }
            .navigationTitle(localizationManager.localized("recovery_nav_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_close")) {
                        // ✅ ИСПРАВЛЕНИЕ: Закрываем модал - onComplete вызовется автоматически через setter
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheet(activityItems: getShareItems())
            }
        }
    }
    
    // MARK: - Helper Functions
    
    private func getShareItems() -> [Any] {
        let shareText = String(format: localizationManager.localized("recovery_share_text"), recoveryCode)
        var shareItems: [Any] = [shareText]
        
        // Добавляем QR-код как изображение
        if let qrCodeImage = generateQRCode(from: recoveryCode) {
            shareItems.append(qrCodeImage)
        }
        
        return shareItems
    }
    
    private func infoItem(icon: String, text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundColor(.blue)
            
            Text(text)
                .foregroundColor(.secondary)
        }
    }
    
    // MARK: - QR Code Generation
    
    private func generateQRCode(from string: String) -> UIImage? {
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        
        filter.message = Data(string.utf8)
        
        if let outputImage = filter.outputImage {
            let transform = CGAffineTransform(scaleX: 10, y: 10)
            let scaledImage = outputImage.transformed(by: transform)
            
            if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
                return UIImage(cgImage: cgImage)
            }
        }
        
        return nil
    }
}

// MARK: - Preview

struct RecoveryCodeModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryCodeModal(
            isPresented: .constant(true),
            recoveryCode: "FAM-A1B2-C3D4-E5F6",
            familyID: "FAM_123456"
        )
    }
}
