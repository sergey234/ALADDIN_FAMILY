import SwiftUI

struct QRScannerModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("📱 QR Сканер")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Наведите камеру на QR-код")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct QRScannerModal_Previews: PreviewProvider {
    static var previews: some View {
        QRScannerModal(isPresented: .constant(true))
    }
}