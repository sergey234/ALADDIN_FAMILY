import SwiftUI
import AVFoundation

/**
 * 📱 QR Scanner Modal
 * Модальное окно для сканирования QR-кода с реальной камерой
 *
 * Закрытие: при маршруте `NavigationManager` → `.qrCode` вызывается `goBack()`; в `.sheet` — `dismiss()`.
 * Сессия AVCaptureSession — start/stop на main (рекомендация Apple, меньше зависаний).
 */

struct QRScannerModal: View {

    // MARK: - Properties

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var scanner = QRScanner()

    var onCodeScanned: ((String) -> Void)?

    // MARK: - Body

    var body: some View {
        ZStack {
            // Камера
            CameraPreview(session: scanner.session)
                .ignoresSafeArea()

            // Overlay
            VStack {
                    Spacer()

                    // Инструкция
                    VStack(spacing: 12) {
                        Text(localizationManager.localized("qr_scanner_instruction"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)

                        Text(localizationManager.localized("qr_scanner_auto_recognize"))
                            .font(.system(size: 14))
                            .foregroundColor(.white.opacity(0.8))
                    }
                    .padding(.vertical, 20)
                    .padding(.horizontal, 30)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color.black.opacity(0.6))
                    )
                    .padding(.bottom, 60)

                    // Кнопка отмены
                    Button(action: {
                        scanner.stopScanning()
                        dismissScanner()
                    }) {
                        Text(localizationManager.localized("common_cancel"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.red)
                            )
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 40)
            }
            .onAppear {
                scanner.startScanning { code in
                    // Haptic feedback
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)

                    scanner.stopScanning()

                    onCodeScanned?(code)

                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                        dismissScanner()
                    }
                }
            }
            .onDisappear {
                scanner.stopScanning()
            }
        }
    }

    private func dismissScanner() {
        if navigationManager.currentScreen == .qrCode {
            navigationManager.goBack()
        } else {
            dismiss()
        }
    }
}

// MARK: - QR Scanner Class

class QRScanner: NSObject, ObservableObject, AVCaptureMetadataOutputObjectsDelegate {

    let session = AVCaptureSession()
    private var metadataOutput = AVCaptureMetadataOutput()
    private var previewLayer: AVCaptureVideoPreviewLayer?

    var onCodeDetected: ((String) -> Void)?

    override init() {
        super.init()
        setupCamera()
    }

    private func setupCamera() {
        Task {
            guard await SensitivePermissionCoordinator.requestCameraIfNeeded() else { return }
            await MainActor.run {
                self.configureCaptureSession()
            }
        }
    }

    private func configureCaptureSession() {
        guard let videoCaptureDevice = AVCaptureDevice.default(for: .video) else { return }

        let videoInput: AVCaptureDeviceInput
        do {
            videoInput = try AVCaptureDeviceInput(device: videoCaptureDevice)
        } catch {
            return
        }

        if session.canAddInput(videoInput) {
            session.addInput(videoInput)
        }

        if session.canAddOutput(metadataOutput) {
            session.addOutput(metadataOutput)
            metadataOutput.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
            metadataOutput.metadataObjectTypes = [.qr]
        }
    }

    func startScanning(completion: @escaping (String) -> Void) {
        onCodeDetected = completion

        DispatchQueue.main.async { [weak self] in
            guard let self else { return }
            if !self.session.isRunning {
                self.session.startRunning()
            }
        }
    }

    func stopScanning() {
        DispatchQueue.main.async { [weak self] in
            guard let self else { return }
            if self.session.isRunning {
                self.session.stopRunning()
            }
        }
    }

    func metadataOutput(_ output: AVCaptureMetadataOutput, didOutput metadataObjects: [AVMetadataObject], from connection: AVCaptureConnection) {
        if let metadataObject = metadataObjects.first {
            guard let readableObject = metadataObject as? AVMetadataMachineReadableCodeObject,
                  let stringValue = readableObject.stringValue else { return }

            stopScanning()
            onCodeDetected?(stringValue)
        }
    }
}

// MARK: - Camera Preview

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewHostView {
        let view = PreviewHostView()
        view.videoPreviewLayer.session = session
        view.videoPreviewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(view.videoPreviewLayer)
        return view
    }

    func updateUIView(_ uiView: PreviewHostView, context: Context) {
        DispatchQueue.main.async {
            uiView.videoPreviewLayer.frame = uiView.bounds
        }
    }

    /// UIView, который корректно обновляет frame preview layer при изменении bounds.
    final class PreviewHostView: UIView {
        let videoPreviewLayer = AVCaptureVideoPreviewLayer()

        override func layoutSubviews() {
            super.layoutSubviews()
            videoPreviewLayer.frame = bounds
        }
    }
}

// MARK: - Preview

struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
