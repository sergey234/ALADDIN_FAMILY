import SwiftUI

/**
 * 🔑 Recovery Options Modal
 * Модальное окно выбора способа восстановления доступа
 * Окно #6 - показывает 4 способа восстановления
 */

struct RecoveryOptionsModal: View {
    
    @Binding var isPresented: Bool
    
    @State private var showQRScanner: Bool = false
    @State private var showManualInput: Bool = false
    @State private var scannerMode: QRScannerModal.ScanMode = .recoveryQR
    
    var onRecoveryComplete: () -> Void
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
            
            // Modal content
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Text("🔑")
                        .font(.system(size: 40))
                    
                    Text("ВОССТАНОВИТЬ ДОСТУП")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.secondaryGold)
                    
                    Text("Как вы хотите восстановить?")
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                }
                
                // Recovery options
                VStack(spacing: Spacing.m) {
                    // Option 1: Through family member (BEST!)
                    RecoveryOptionButton(
                        icon: "👨‍👩‍👧‍👦",
                        title: "ЧЕРЕЗ ЧЛЕНА СЕМЬИ",
                        subtitle: "(если у кого-то есть доступ)",
                        color: .successGreen
                    ) {
                        scannerMode = .recoveryFromFamily
                        showQRScanner = true
                    }
                    
                    // Option 2: Scan saved QR #2
                    RecoveryOptionButton(
                        icon: "📷",
                        title: "СКАНИРОВАТЬ QR #2",
                        subtitle: "(сохранённый код восстановления)",
                        color: .primaryBlue
                    ) {
                        scannerMode = .recoveryQR
                        showQRScanner = true
                    }
                    
                    // Option 3: Enter code manually
                    RecoveryOptionButton(
                        icon: "🔤",
                        title: "ВВЕСТИ КОД ВРУЧНУЮ",
                        subtitle: "(FAM-A1B2-C3D4-E5F6)",
                        color: .secondaryGold
                    ) {
                        showManualInput = true
                    }
                    
                    // Option 4: Contact support
                    RecoveryOptionButton(
                        icon: "📧",
                        title: "ОБРАТИТЬСЯ В ПОДДЕРЖКУ",
                        subtitle: "(если всё потеряно)",
                        color: .dangerRed
                    ) {
                        contactSupport()
                    }
                }
                
                // Back button
                Button(action: { isPresented = false }) {
                    Text("НАЗАД")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
            }
            .padding(Spacing.xl)
            .frame(width: 340)
            .background(
                LinearGradient(
                    colors: [Color(hex: "#1e3a5f"), Color(hex: "#2e5090")],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
        .sheet(isPresented: $showQRScanner) {
            QRScannerModal(
                isPresented: $showQRScanner,
                mode: scannerMode,
                onCodeScanned: handleCodeScanned
            )
        }
        .sheet(isPresented: $showManualInput) {
            ManualCodeInputModal(
                isPresented: $showManualInput,
                onCodeEntered: handleCodeScanned
            )
        }
    }
    
    // MARK: - Actions
    
    private func handleCodeScanned(_ code: String) {
        // TODO: Validate and restore family
        print("✅ Code scanned: \(code)")
        isPresented = false
        onRecoveryComplete()
    }
    
    private func contactSupport() {
        if let url = URL(string: "mailto:support@aladdin.family?subject=Восстановление доступа к семье") {
            UIApplication.shared.open(url)
        }
    }
}

// MARK: - Recovery Option Button

struct RecoveryOptionButton: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                // Icon
                Text(icon)
                    .font(.system(size: 32))
                
                // Text
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 15, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text(subtitle)
                        .font(.system(size: 12))
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                // Arrow
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .frame(height: 72)
            .padding(.horizontal, Spacing.m)
            .background(color.opacity(0.15))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(color, lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

struct RecoveryOptionsModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryOptionsModal(
            isPresented: .constant(true),
            onRecoveryComplete: {}
        )
    }
}



