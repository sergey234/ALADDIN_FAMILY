import SwiftUI
import CoreImage.CIFilterBuiltins

/**
 * ✅ Family Created Modal
 * Модальное окно "Семья создана!" с QR-кодом и кодом восстановления
 * Окно #4 в процессе регистрации
 * 
 * ВАЖНО: Это окно НЕЛЬЗЯ закрыть без выбора способа сохранения!
 */

struct FamilyCreatedModal: View {
    
    @Binding var isPresented: Bool
    let familyID: String
    let recoveryCode: String
    
    @State private var selectedSaveMethods: Set<SaveMethod> = []
    @State private var showEmailInput: Bool = false
    @State private var email: String = ""
    
    var onContinue: () -> Void
    
    // MARK: - Save Methods
    
    enum SaveMethod: String, CaseIterable {
        case clipboard = "📋 Скопировать в буфер"
        case screenshot = "📸 Сделать скриншот"
        case cloud = "💾 Сохранить в облако"
        case email = "📧 Отправить на email"
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur (НЕ КЛИКАБЕЛЬНЫЙ!)
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
                .allowsHitTesting(false)
            
            // Modal content
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Header
                    VStack(spacing: Spacing.m) {
                        Text("✅")
                            .font(.system(size: 60))
                        
                        Text("СЕМЬЯ СОЗДАНА!")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.successGreen)
                    }
                    
                    // Recovery code section
                    VStack(spacing: Spacing.m) {
                        Text("🔑 Ваш код восстановления:")
                            .font(.system(size: 14))
                            .foregroundColor(.textSecondary)
                        
                        // QR Code
                        if let qrImage = generateQRCode(from: recoveryCode) {
                            Image(uiImage: qrImage)
                                .interpolation(.none)
                                .resizable()
                                .frame(width: 180, height: 180)
                                .background(Color.white)
                                .cornerRadius(12)
                        }
                        
                        // Recovery code text
                        Text(recoveryCode)
                            .font(.system(size: 18, weight: .bold, design: .monospaced))
                            .foregroundColor(Color(hex: "#FCD34D"))  // Яркое золото из иконки!
                            .tracking(2)
                            .padding(Spacing.m)
                            .background(Color.black.opacity(0.3))
                            .cornerRadius(8)
                    }
                    
                    // Warning box
                    HStack(spacing: Spacing.m) {
                        Text("⚠️")
                            .font(.system(size: 24))
                        
                        Text("ВАЖНО: Сохраните этот код!")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.warningOrange)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(Spacing.m)
                    .background(Color.warningOrange.opacity(0.15))
                    .cornerRadius(12)
                    .overlay(
                        Rectangle()
                            .fill(Color.warningOrange)
                            .frame(width: 3),
                        alignment: .leading
                    )
                    
                    // Save methods
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("СПОСОБЫ СОХРАНЕНИЯ:")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.textPrimary)
                        
                        ForEach(SaveMethod.allCases, id: \.self) { method in
                            SaveMethodCheckbox(
                                method: method,
                                isSelected: selectedSaveMethods.contains(method)
                            ) {
                                toggleSaveMethod(method)
                            }
                        }
                    }
                    
                    // Email input (if selected)
                    if showEmailInput {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Введите email:")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            ALADDINTextField(
                                placeholder: "example@mail.com",
                                text: $email,
                                icon: "✉️"
                            )
                        }
                        .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    // Continue button
                    PrimaryButton(
                        title: "СОХРАНИЛ, ПРОДОЛЖИТЬ ✅",
                        action: handleContinue,
                        isDisabled: selectedSaveMethods.isEmpty
                    )
                    .opacity(selectedSaveMethods.isEmpty ? 0.5 : 1.0)
                    
                    if selectedSaveMethods.isEmpty {
                        Text("⚠️ Выберите хотя бы 1 способ сохранения")
                            .font(.caption)
                            .foregroundColor(.dangerRed)
                            .transition(.opacity)
                    }
                }
                .padding(Spacing.xl)
            }
            .frame(width: 340, height: 600)
            .background(
                LinearGradient(
                    colors: [
                        Color(hex: "#0F172A"),  // Космический тёмный
                        Color(hex: "#1E3A8A"),  // Глубокий синий
                        Color(hex: "#3B82F6"),  // Электрический синий
                        Color(hex: "#1E40AF")   // Королевский синий
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
        .transition(.asymmetric(
            insertion: .scale(scale: 0.8).combined(with: .opacity),
            removal: .scale(scale: 0.8).combined(with: .opacity)
        ))
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: isPresented)
    }
    
    // MARK: - Actions
    
    private func toggleSaveMethod(_ method: SaveMethod) {
        if selectedSaveMethods.contains(method) {
            selectedSaveMethods.remove(method)
            if method == .email {
                showEmailInput = false
            }
        } else {
            selectedSaveMethods.insert(method)
            
            // Handle special methods
            switch method {
            case .clipboard:
                UIPasteboard.general.string = recoveryCode
                HapticFeedback.success()
                
            case .screenshot:
                // Trigger screenshot hint
                HapticFeedback.success()
                
            case .cloud:
                // Save to iCloud
                saveToiCloud()
                
            case .email:
                showEmailInput = true
            }
        }
        
        HapticFeedback.selection()
    }
    
    private func saveToiCloud() {
        let fileName = "aladdin_family_backup_\(Date().timeIntervalSince1970).txt"
        let content = """
        ALADDIN Family Security - Recovery Code
        
        Family ID: \(familyID)
        Recovery Code: \(recoveryCode)
        
        Created: \(Date())
        
        ⚠️ ВАЖНО: Храните этот код в надёжном месте!
        Этот код нужен для восстановления доступа к семье.
        """
        
        if let documentsURL = FileManager.default.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents") {
            let fileURL = documentsURL.appendingPathComponent(fileName)
            
            do {
                try content.write(to: fileURL, atomically: true, encoding: .utf8)
                print("✅ Saved to iCloud: \(fileName)")
            } catch {
                print("❌ Error saving to iCloud: \(error)")
            }
        }
    }
    
    private func handleContinue() {
        guard !selectedSaveMethods.isEmpty else { return }
        
        // Send email if selected
        if selectedSaveMethods.contains(.email) && !email.isEmpty {
            // TODO: Call API to send email
            print("📧 Sending recovery code to: \(email)")
        }
        
        HapticFeedback.success()
        onContinue()
    }
    
    // MARK: - QR Code Generation
    
    private func generateQRCode(from string: String) -> UIImage? {
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        
        let data = Data(string.utf8)
        filter.setValue(data, forKey: "inputMessage")
        filter.setValue("H", forKey: "inputCorrectionLevel")
        
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

// MARK: - Save Method Checkbox

struct SaveMethodCheckbox: View {
    let method: FamilyCreatedModal.SaveMethod
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                // Checkbox
                Image(systemName: isSelected ? "checkmark.square.fill" : "square")
                    .font(.system(size: 20))
                    .foregroundColor(isSelected ? .successGreen : .textSecondary)
                
                // Text
                Text(method.rawValue)
                    .font(.system(size: 14))
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                isSelected
                    ? Color.successGreen.opacity(0.15)
                    : Color.white.opacity(0.05)
            )
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(
                        isSelected ? Color.successGreen : Color.clear,
                        lineWidth: 1
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

struct FamilyCreatedModal_Previews: PreviewProvider {
    static var previews: some View {
        FamilyCreatedModal(
            isPresented: .constant(true),
            familyID: "FAM_A1B2C3D4E5F6",
            recoveryCode: "FAM-A1B2-C3D4-E5F6",
            onContinue: {}
        )
    }
}

