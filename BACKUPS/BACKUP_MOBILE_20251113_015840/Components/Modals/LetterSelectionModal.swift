import SwiftUI

struct LetterSelectionModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Выберите букву")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Выберите первую букву имени")
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

struct LetterSelectionModal_Previews: PreviewProvider {
    static var previews: some View {
        LetterSelectionModal(isPresented: .constant(true))
    }
}