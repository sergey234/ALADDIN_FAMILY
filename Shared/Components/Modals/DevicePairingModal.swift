import SwiftUI
import CoreImage.CIFilterBuiltins

/**
 * 📱 Device Pairing Modal (Экран сопряжения устройства)
 * Открывается после успешного логического создания устройства на сервере.
 * Показывает 3 метода физической привязки:
 * 1. QR-код
 * 2. Deep Link (кнопка Поделиться)
 * 3. Короткий PIN-код (если камера сломана)
 */
struct DevicePairingModal: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Данные от сервера после создания устройства
    let deviceName: String
    let ownerName: String
    let qrToken: String
    let shortPin: String
    
    @State private var showShareSheet = false
    
    // Для генерации Deep Link
    private var inviteLink: String {
        "aladdin://bind?token=\(qrToken)"
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        
                        // Заголовок и пояснение
                        VStack(spacing: Spacing.s) {
                            Text("Устройство добавлено!")
                                .font(.h2)
                                .foregroundColor(.textPrimary)
                            
                            Text("Остался один шаг: привяжите физическое устройство \(deviceName) (\(ownerName)) к вашей семье.")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        .padding(.top, Spacing.m)
                        
                        // МЕТОД 1: QR КОД (Основной)
                        VStack(spacing: Spacing.m) {
                            Text("Способ 1: Сканировать QR-код (Рекомендуется)")
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            
                            VStack(spacing: Spacing.s) {
                                Text("Откройте ALADDIN на новом устройстве и отсканируйте этот код")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.center)
                                
                                if let qrImage = generateQRCode(from: inviteLink) {
                                    Image(uiImage: qrImage)
                                        .interpolation(.none)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 180, height: 180)
                                        .padding(Spacing.m)
                                        .background(Color.white)
                                        .cornerRadius(CornerRadius.large)
                                        .shadow(color: Color.black.opacity(0.1), radius: 10)
                                }
                            }
                            .padding(Spacing.cardPadding)
                            .frame(maxWidth: .infinity)
                            .background(Color.backgroundMedium.opacity(0.4))
                            .cornerRadius(CornerRadius.medium)
                        }
                        
                        // МЕТОД 2: ССЫЛКА (Удаленный)
                        VStack(spacing: Spacing.m) {
                            Text("Способ 2: Отправить ссылку")
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            
                            Button(action: {
                                let generator = UIImpactFeedbackGenerator(style: .medium)
                                generator.impactOccurred()
                                showShareSheet = true
                            }) {
                                HStack {
                                    Image(systemName: "square.and.arrow.up")
                                    Text("Поделиться ссылкой-приглашением")
                                }
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.m)
                                .background(Color.secondaryBlue.opacity(0.8))
                                .cornerRadius(CornerRadius.medium)
                            }
                        }
                        
                        // МЕТОД 3: PIN-КОД (Резервный)
                        VStack(spacing: Spacing.m) {
                            Text("Способ 3: Короткий код")
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            
                            VStack(spacing: Spacing.s) {
                                Text("Если камера не работает, введите этот код на новом устройстве")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.center)
                                
                                Text(shortPin)
                                    .font(.system(size: 32, weight: .black, design: .monospaced))
                                    .foregroundColor(Color(red: 1.0, green: 0.84, blue: 0.0)) // Золотой
                                    .tracking(4) // Исправлено letterSpacing на tracking
                                    .padding(.vertical, Spacing.s)
                            }
                            .padding(Spacing.cardPadding)
                            .frame(maxWidth: .infinity)
                            .background(Color.backgroundMedium.opacity(0.4))
                            .cornerRadius(CornerRadius.medium)
                        }
                        
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                    .font(.bodyBold)
                    .foregroundColor(.white)
                }
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheet(activityItems: ["Установи защиту ALADDIN на свое устройство, перейдя по ссылке: \(inviteLink)"])
            }
        }
    }
    
    // MARK: - QR Generator
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
