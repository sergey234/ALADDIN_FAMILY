import SwiftUI
import AVFoundation
import Vision

/**
 * 📱 QR Scanner Modal
 * Модальное окно для сканирования QR-кода с реальной камерой
 * 
 * Функции:
 * - Реальная камера (AVFoundation)
 * - Распознавание QR-кодов (Vision)
 * - Автоматическая обработка
 * - Haptic feedback
 */

struct QRScannerModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    @StateObject private var scanner = QRScanner()
    
    var onCodeScanned: ((String) -> Void)?
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                // Камера
                CameraPreview(session: scanner.session)
                    .ignoresSafeArea()
                
                // Overlay
                VStack {
                    Spacer()
                    
                    // Инструкция
                    VStack(spacing: 12) {
                        Text("Наведите камеру на QR-код")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)
                        
                        Text("Код будет распознан автоматически")
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
                        isPresented = false
                    }) {
                        Text("Отмена")
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
            }
            .navigationBarHidden(true)
            .onAppear {
                scanner.startScanning { code in
                    // Haptic feedback
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)
                    
                    // Закрываем сканер
                    isPresented = false
                    
                    // Вызываем колбэк
                    onCodeScanned?(code)
                }
            }
            .onDisappear {
                scanner.stopScanning()
            }
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
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.session.startRunning()
        }
    }
    
    func stopScanning() {
        session.stopRunning()
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
    
    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: .zero)
        
        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer)
        
        DispatchQueue.main.async {
            previewLayer.frame = view.bounds
        }
        
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {}
}

// MARK: - Preview

struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal(isPresented: .constant(true))
    }
}
