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
    var qrPayload: String? = nil
    var onComplete: (() -> Void)? = nil
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showShareSheet = false
    @State private var showSuccessAlert = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ScrollView(.vertical, showsIndicators: true) {
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
                        if let qrCodeImage = generateQRCode(from: qrPayload ?? recoveryCode) {
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
                        
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #3: Вызываем onComplete перед закрытием
                        onComplete?()
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
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #3: Вызываем onComplete перед закрытием
                        onComplete?()
                        isPresented = false
                    }
                }
            }
            .onChange(of: isPresented) { newValue in
                // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #3: Если модал закрывается (свайп вниз), вызываем onComplete
                if !newValue {
                    onComplete?()
                }
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheet(activityItems: getShareItems())
            }
        }
    }
    
    // MARK: - Helper Functions
    
    private func getShareItems() -> [Any] {
        let shareText = String(
            format: localizationManager.localized("recovery_share_text_family_link"),
            recoveryCode,
            familyInviteLink
        )
        var shareItems: [Any] = [shareText]
        
        // Добавляем QR-код как изображение
        if let qrCodeImage = generateQRCode(from: qrPayload ?? recoveryCode) {
            shareItems.append(qrCodeImage)
        }
        
        return shareItems
    }

    private var familyInviteLink: String {
        let encodedCode = recoveryCode.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? recoveryCode
        return "https://aladdin-ai.ru/family/invite/\(encodedCode)"
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

// MARK: - Family Invite Share Modal

/// Owner flow for an existing family: generate a fresh FAM invite and show QR/code/link.
struct FamilyInviteShareModal: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    let familyId: String

    @State private var invite: FamilyInviteResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showShareSheet = false

    private var displayCode: String {
        guard let invite else { return "" }
        return FamilyInviteCodeParser.parse(invite.invite_code)?.displayCode
            ?? FamilyInviteCodeParser.displayCode(fromFamilyId: invite.family_id)
            ?? invite.invite_code
    }

    private var inviteLink: String {
        let encoded = displayCode.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? displayCode
        return "https://aladdin-ai.ru/family/invite/\(encoded)"
    }

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .family)
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 18) {
                        if isLoading {
                            ProgressView()
                                .tint(.secondaryGold)
                            Text(localizationManager.localized("family_invite_loading"))
                                .foregroundColor(.white.opacity(0.78))
                        } else if let invite {
                            inviteContent(invite)
                        } else if let errorMessage {
                            VStack(spacing: 12) {
                                Text(errorMessage)
                                    .font(.subheadline)
                                    .foregroundColor(.warningOrange)
                                    .multilineTextAlignment(.center)
                                Button(localizationManager.localized("common_retry")) {
                                    loadInvite()
                                }
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.horizontal, 18)
                                .padding(.vertical, 10)
                                .background(Color.secondaryGold)
                                .clipShape(Capsule())
                            }
                        }
                    }
                    .padding(20)
                }
            }
            .navigationTitle(localizationManager.localized("family_invite_share_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_close")) {
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            if invite == nil && !isLoading {
                loadInvite()
            }
        }
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(activityItems: shareItems())
        }
    }

    @ViewBuilder
    private func inviteContent(_ invite: FamilyInviteResponse) -> some View {
        VStack(spacing: 16) {
            Text(localizationManager.localized("family_invite_share_subtitle"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.78))
                .multilineTextAlignment(.center)

            if let qrImage = generateQRCode(from: invite.qr_code_data) {
                Image(uiImage: qrImage)
                    .interpolation(.none)
                    .resizable()
                    .scaledToFit()
                    .frame(width: 220, height: 220)
                    .padding(12)
                    .background(Color.white)
                    .cornerRadius(18)
            }

            Text(displayCode)
                .font(.system(size: 20, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(Color.white.opacity(0.10))
                .cornerRadius(12)

            Text(String(format: localizationManager.localized("family_invite_expires_at_fmt"), formattedExpiration(invite.expires_at)))
                .font(.caption)
                .foregroundColor(.white.opacity(0.68))
                .multilineTextAlignment(.center)

            HStack(spacing: 12) {
                Button(localizationManager.localized("recovery_copy")) {
                    UIPasteboard.general.string = displayCode
                    HapticFeedback.notification(.success)
                }
                .font(.headline)
                .foregroundColor(.secondaryGold)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.white.opacity(0.10))
                .cornerRadius(12)

                Button(localizationManager.localized("recovery_share")) {
                    showShareSheet = true
                }
                .font(.headline)
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.secondaryGold)
                .cornerRadius(12)
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.08))
        .cornerRadius(20)
    }

    private func loadInvite() {
        let cleanFamilyId = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !cleanFamilyId.isEmpty else {
            errorMessage = localizationManager.localized("family_invite_missing_family")
            return
        }

        isLoading = true
        errorMessage = nil
        APIService.shared.createFamilyInvite(
            request: FamilyInviteCreateRequest(family_id: cleanFamilyId)
        ) { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success(let response):
                    invite = response
                case .failure:
                    errorMessage = localizationManager.localized("family_invite_create_failed")
                }
            }
        }
    }

    private func shareItems() -> [Any] {
        let text = String(
            format: localizationManager.localized("recovery_share_text_family_link"),
            displayCode,
            inviteLink
        )
        var items: [Any] = [text]
        if let invite, let qrImage = generateQRCode(from: invite.qr_code_data) {
            items.append(qrImage)
        }
        return items
    }

    private func formattedExpiration(_ raw: String) -> String {
        DateFormatterService.shared.formatExpirationDate(
            from: raw,
            language: localizationManager.currentLanguage
        ) ?? raw
    }

    private func generateQRCode(from string: String) -> UIImage? {
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        filter.message = Data(string.utf8)
        filter.correctionLevel = "M"
        guard let outputImage = filter.outputImage else { return nil }
        let transform = CGAffineTransform(scaleX: 10, y: 10)
        let scaledImage = outputImage.transformed(by: transform)
        guard let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) else { return nil }
        return UIImage(cgImage: cgImage)
    }
}
