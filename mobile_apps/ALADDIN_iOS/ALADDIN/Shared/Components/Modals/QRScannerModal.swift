import SwiftUI
import AVFoundation

/**
 * 📱 QR Scanner Modal
 * Модальное окно сканирования QR кодов
 */
struct QRScannerModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    let onQRScanned: (String) -> Void
    
    @State private var isScanning = false
    @State private var scannedCode: String?
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .onTapGesture {
                    isPresented = false
                }
            
            // Модальное окно
            VStack(spacing: Spacing.l) {
                // Заголовок
                Text("Сканирование QR кода")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                
                // Сканер
                ZStack {
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium)
                        .frame(height: 200)
                    
                    if isScanning {
                        VStack {
                            Text("Наведите камеру на QR код")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            Text("📱")
                                .font(.system(size: 60))
                            
                            Spacer()
                        }
                        .padding()
                    } else {
                        VStack {
                            Text("Сканер не доступен")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            Text("📷")
                                .font(.system(size: 60))
                            
                            Spacer()
                        }
                        .padding()
                    }
                }
                
                // Кнопки
                HStack(spacing: Spacing.m) {
                    SecondaryButton("Отмена") {
                        isPresented = false
                    }
                    
                    PrimaryButton("Сканировать") {
                        startScanning()
                    }
                }
            }
            .padding(Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundLight)
            )
            .padding(Spacing.l)
        }
        .onAppear {
            checkCameraPermission()
        }
    }
    
    // MARK: - Methods
    
    private func checkCameraPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            isScanning = true
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async {
                    isScanning = granted
                }
            }
        default:
            isScanning = false
        }
    }
    
    private func startScanning() {
        // Здесь будет логика сканирования QR кода
        // Пока что симулируем успешное сканирование
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            let mockQRCode = "https://aladdin.family/join/12345"
            onQRScanned(mockQRCode)
            isPresented = false
        }
    }
}

#if DEBUG
struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal(
            isPresented: .constant(true),
            onQRScanned: { code in
                print("QR код: \(code)")
            }
        )
    }
}
#endif
