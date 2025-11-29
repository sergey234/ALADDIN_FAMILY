import SwiftUI

struct RegistrationSuccessModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🎉 Регистрация успешна!")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Добро пожаловать в ALADDIN!")
                .foregroundColor(.gray)
            
            Button("Начать") {
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

struct RegistrationSuccessModal_Previews: PreviewProvider {
    static var previews: some View {
        RegistrationSuccessModal(isPresented: .constant(true))
    }
}