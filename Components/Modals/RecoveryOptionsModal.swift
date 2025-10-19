import SwiftUI

struct RecoveryOptionsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🔐 Восстановление")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Выберите способ восстановления доступа")
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

struct RecoveryOptionsModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryOptionsModal(isPresented: .constant(true))
    }
}