import SwiftUI

/// 📱 QR Scanner Modal
/// Модальное окно для сканирования QR-кода
struct QRScannerModal: View {
    @Binding var isPresented: Bool
    @State private var scannedCode: String = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("📱")
                    .font(.system(size: 64))
                
                Text("Сканирование QR-кода")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Наведите камеру на QR-код для присоединения к семье")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                
                // Placeholder для сканера
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 200)
                    .overlay(
                        VStack {
                            Image(systemName: "qrcode.viewfinder")
                                .font(.system(size: 48))
                                .foregroundColor(.gray)
                            Text("QR Scanner")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    )
                
                Spacer()
                
                Button("Отмена") {
                    isPresented = false
                }
                .buttonStyle(.bordered)
            }
            .padding()
            .navigationTitle("Сканер")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Закрыть") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

#if DEBUG
struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal(isPresented: .constant(true))
    }
}
#endif
