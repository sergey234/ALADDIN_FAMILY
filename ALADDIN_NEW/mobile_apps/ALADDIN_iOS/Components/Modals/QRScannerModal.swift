import SwiftUI
import AVFoundation

/**
 * 📷 QR Scanner Modal
 * Модальное окно для сканирования QR-кодов
 * Используется для:
 * - Присоединения к семье (QR #1)
 * - Восстановления доступа через члена семьи (QR #1)
 * - Восстановления через сохранённый QR #2
 */

struct QRScannerModal: View {
    
    @Binding var isPresented: Bool
    let mode: ScanMode
    var onCodeScanned: (String) -> Void
    
    @State private var showManualInput: Bool = false
    
    // MARK: - Scan Mode
    
    enum ScanMode {
        case joinFamily         // Присоединение к семье (QR #1)
        case recoveryFromFamily // Восстановление через члена семьи (QR #1)
        case recoveryQR         // Восстановление через сохранённый QR #2
    }
    
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
                    Text(headerIcon)
                        .font(.system(size: 40))
                    
                    Text(headerTitle)
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(headerColor)
                        .multilineTextAlignment(.center)
                    
                    if !headerInstructions.isEmpty {
                        Text(headerInstructions)
                            .font(.system(size: 13))
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                }
                .padding(.horizontal, Spacing.m)
                
                // Info card: What to scan?
                VStack(spacing: Spacing.s) {
                    Text("💡 Что сканировать?")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(Color(hex: "#FCD34D"))
                    
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Group {
                            Text("QR #1: Для присоединения к семье")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.white)
                            Text("(Попросите члена семьи: Настройки → Добавить члена)")
                                .font(.system(size: 11))
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer().frame(height: 8)
                        
                        Group {
                            Text("QR #2: Для восстановления доступа")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.white)
                            Text("(Ваш сохранённый код из iCloud/Email/Скриншота)")
                                .font(.system(size: 11))
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color(hex: "#FCD34D").opacity(0.15))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(hex: "#FCD34D"), lineWidth: 1)
                        )
                )
                .padding(.horizontal, Spacing.m)
                
                // Camera preview
                ZStack {
                    // Camera view
                    QRCodeScannerView(onCodeScanned: onCodeScanned)
                        .frame(width: 280, height: 280)
                        .cornerRadius(16)
                    
                    // Scan frame
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.secondaryGold, lineWidth: 3)
                        .frame(width: 180, height: 180)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 10)
                                .blur(radius: 10)
                        )
                        .shadow(color: Color.secondaryGold.opacity(0.5), radius: 20)
                }
                
                Text("Наведите на QR-код")
                    .font(.system(size: 14))
                    .foregroundColor(.textSecondary)
                
                // Divider
                HStack {
                    Rectangle()
                        .fill(Color.textTertiary)
                        .frame(height: 1)
                    Text("или")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Rectangle()
                        .fill(Color.textTertiary)
                        .frame(height: 1)
                }
                .padding(.horizontal, Spacing.xl)
                
                // Manual input button
                SecondaryButton(
                    title: "🔤 ВВЕСТИ КОД ВРУЧНУЮ",
                    icon: nil
                ) {
                    showManualInput = true
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
        .sheet(isPresented: $showManualInput) {
            ManualCodeInputModal(
                isPresented: $showManualInput,
                onCodeEntered: onCodeScanned
            )
        }
    }
    
    // MARK: - Computed Properties
    
    private var headerIcon: String {
        switch mode {
        case .joinFamily:
            return "📷"
        case .recoveryFromFamily:
            return "👨‍👩‍👧‍👦"
        case .recoveryQR:
            return "🔑"
        }
    }
    
    private var headerTitle: String {
        switch mode {
        case .joinFamily:
            return "ПРИСОЕДИНИТЬСЯ К СЕМЬЕ"
        case .recoveryFromFamily:
            return "ВОССТАНОВЛЕНИЕ ЧЕРЕЗ СЕМЬЮ"
        case .recoveryQR:
            return "СКАНИРОВАТЬ КОД ВОССТАНОВЛЕНИЯ"
        }
    }
    
    private var headerInstructions: String {
        switch mode {
        case .joinFamily:
            return "Попросите члена семьи показать QR-код:\nНастройки → Семья → \"Добавить члена\""
        case .recoveryFromFamily:
            return "Попросите члена семьи:\n1. Открыть ALADDIN\n2. Настройки → Семья\n3. \"Добавить члена семьи\"\n4. Показать вам QR-код"
        case .recoveryQR:
            return "Отсканируйте сохранённый QR-код\n(скриншот, печать, email)"
        }
    }
    
    private var headerColor: Color {
        switch mode {
        case .joinFamily:
            return .secondaryGold
        case .recoveryFromFamily:
            return .successGreen
        case .recoveryQR:
            return .primaryBlue
        }
    }
}

// MARK: - QR Code Scanner View (UIKit wrapper)

struct QRCodeScannerView: UIViewControllerRepresentable {
    
    var onCodeScanned: (String) -> Void
    
    func makeUIViewController(context: Context) -> QRScannerViewController {
        let controller = QRScannerViewController()
        controller.onCodeScanned = onCodeScanned
        return controller
    }
    
    func updateUIViewController(_ uiViewController: QRScannerViewController, context: Context) {}
}

class QRScannerViewController: UIViewController, AVCaptureMetadataOutputObjectsDelegate {
    
    var onCodeScanned: ((String) -> Void)?
    private var captureSession: AVCaptureSession?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
    }
    
    private func setupCamera() {
        captureSession = AVCaptureSession()
        
        guard let videoCaptureDevice = AVCaptureDevice.default(for: .video) else { return }
        let videoInput: AVCaptureDeviceInput
        
        do {
            videoInput = try AVCaptureDeviceInput(device: videoCaptureDevice)
        } catch {
            return
        }
        
        if (captureSession?.canAddInput(videoInput) ?? false) {
            captureSession?.addInput(videoInput)
        }
        
        let metadataOutput = AVCaptureMetadataOutput()
        
        if (captureSession?.canAddOutput(metadataOutput) ?? false) {
            captureSession?.addOutput(metadataOutput)
            
            metadataOutput.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
            metadataOutput.metadataObjectTypes = [.qr]
        }
        
        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession!)
        previewLayer?.frame = view.layer.bounds
        previewLayer?.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer!)
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }
    
    func metadataOutput(_ output: AVCaptureMetadataOutput, didOutput metadataObjects: [AVMetadataObject], from connection: AVCaptureConnection) {
        if let metadataObject = metadataObjects.first {
            guard let readableObject = metadataObject as? AVMetadataMachineReadableCodeObject else { return }
            guard let stringValue = readableObject.stringValue else { return }
            
            AudioServicesPlaySystemSound(SystemSoundID(kSystemSoundID_Vibrate))
            captureSession?.stopRunning()
            onCodeScanned?(stringValue)
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        captureSession?.stopRunning()
    }
}

// MARK: - Manual Code Input Modal

struct ManualCodeInputModal: View {
    
    @Binding var isPresented: Bool
    var onCodeEntered: (String) -> Void
    
    @State private var codePart1: String = ""
    @State private var codePart2: String = ""
    @State private var codePart3: String = ""
    @State private var codePart4: String = ""
    
    @FocusState private var focusedField: Int?
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Text("🔤")
                        .font(.system(size: 40))
                    
                    Text("ВВЕДИТЕ КОД ВОССТАНОВЛЕНИЯ")
                        .font(.h2)
                        .foregroundColor(.secondaryGold)
                        .multilineTextAlignment(.center)
                }
                
                // Code input
                HStack(spacing: 8) {
                    CodeSegmentField(text: $codePart1, placeholder: "FAM", fieldIndex: 0, focusedField: $focusedField)
                    Text("-").foregroundColor(.textSecondary)
                    CodeSegmentField(text: $codePart2, placeholder: "____", fieldIndex: 1, focusedField: $focusedField)
                    Text("-").foregroundColor(.textSecondary)
                    CodeSegmentField(text: $codePart3, placeholder: "____", fieldIndex: 2, focusedField: $focusedField)
                    Text("-").foregroundColor(.textSecondary)
                    CodeSegmentField(text: $codePart4, placeholder: "____", fieldIndex: 3, focusedField: $focusedField)
                }
                .padding(.horizontal, Spacing.m)
                
                // Submit button
                PrimaryButton(
                    title: "ВОССТАНОВИТЬ",
                    action: handleSubmit,
                    isDisabled: !isCodeComplete
                )
                .padding(.horizontal, Spacing.screenPadding)
                
                // Hint
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("💡 Код можно найти:")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Text("• В письме на email")
                    Text("• В скриншоте")
                    Text("• В облачном хранилище")
                    Text("• Попросить у других членов семьи")
                }
                .font(.caption)
                .foregroundColor(.textTertiary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, Spacing.screenPadding)
                
                // Back button
                Button(action: { isPresented = false }) {
                    Text("НАЗАД")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
            }
            .padding(Spacing.xl)
        }
        .onAppear {
            focusedField = 0
        }
    }
    
    // MARK: - Computed Properties
    
    private var isCodeComplete: Bool {
        !codePart1.isEmpty && !codePart2.isEmpty && !codePart3.isEmpty && !codePart4.isEmpty
    }
    
    private var fullCode: String {
        "\(codePart1)-\(codePart2)-\(codePart3)-\(codePart4)"
    }
    
    // MARK: - Actions
    
    private func handleSubmit() {
        guard isCodeComplete else { return }
        HapticFeedback.success()
        onCodeEntered(fullCode)
        isPresented = false
    }
}

// MARK: - Code Segment Field

struct CodeSegmentField: View {
    @Binding var text: String
    let placeholder: String
    let fieldIndex: Int
    @FocusState.Binding var focusedField: Int?
    
    var body: some View {
        TextField(placeholder, text: $text)
            .font(.system(size: 24, weight: .semibold, design: .monospaced))
            .foregroundColor(.white)
            .multilineTextAlignment(.center)
            .frame(width: 70, height: 56)
            .background(
                focusedField == fieldIndex
                    ? Color.primaryBlue.opacity(0.1)
                    : Color.white.opacity(0.1)
            )
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        focusedField == fieldIndex ? Color.primaryBlue : Color.white.opacity(0.2),
                        lineWidth: focusedField == fieldIndex ? 2 : 1
                    )
            )
            .focused($focusedField, equals: fieldIndex)
            .textInputAutocapitalization(.characters)
            .onChange(of: text) { newValue in
                // Auto-advance to next field
                if newValue.count >= 4 && fieldIndex < 3 {
                    focusedField = fieldIndex + 1
                }
            }
    }
}

// MARK: - Preview

struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal(
            isPresented: .constant(true),
            mode: .joinFamily,
            onCodeScanned: { _ in }
        )
    }
}

