import SwiftUI

struct FamilyCreatedModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_created_title"))
                .font(.title2)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("family_created_subtitle"))
                .foregroundColor(.gray)
            
            Button(localizationManager.localized("ai_assistant_feedback_rating_excellent")) {
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
            .environmentObject(LocalizationManager.shared)
    }
}
