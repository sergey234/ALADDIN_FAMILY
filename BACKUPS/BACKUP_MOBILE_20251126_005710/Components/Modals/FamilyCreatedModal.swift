import SwiftUI

struct FamilyCreatedModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🎉 Семья создана!")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Семейная группа успешно создана")
                .foregroundColor(.gray)
            
            Button("Отлично") {
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

struct FamilyCreatedModal_Previews: PreviewProvider {
    static var previews: some View {
        FamilyCreatedModal(isPresented: .constant(true))
    }
}