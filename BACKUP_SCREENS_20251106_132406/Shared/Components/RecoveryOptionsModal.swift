import SwiftUI

/// 🔐 Recovery Options Modal
/// Модальное окно для восстановления доступа
struct RecoveryOptionsModal: View {
    @Binding var isPresented: Bool
    @State private var selectedOption: RecoveryOption = .email
    
    enum RecoveryOption: String, CaseIterable {
        case email = "email"
        case phone = "phone"
        case backup = "backup"
        
        var displayName: String {
            switch self {
            case .email: return "Email"
            case .phone: return "Телефон"
            case .backup: return "Резервная копия"
            }
        }
        
        var icon: String {
            switch self {
            case .email: return "envelope"
            case .phone: return "phone"
            case .backup: return "externaldrive"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("🔐")
                    .font(.system(size: 64))
                
                Text("Восстановление доступа")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Выберите способ восстановления доступа к аккаунту")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                
                VStack(spacing: 12) {
                    ForEach(RecoveryOption.allCases, id: \.self) { option in
                        Button(action: {
                            selectedOption = option
                        }) {
                            HStack {
                                Image(systemName: option.icon)
                                    .font(.title2)
                                    .foregroundColor(selectedOption == option ? .white : .blue)
                                    .frame(width: 30)
                                
                                Text(option.displayName)
                                    .font(.body)
                                    .foregroundColor(selectedOption == option ? .white : .primary)
                                
                                Spacer()
                                
                                if selectedOption == option {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.white)
                                }
                            }
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(selectedOption == option ? Color.blue : Color.gray.opacity(0.1))
                            )
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                }
                
                Spacer()
                
                Button("Продолжить") {
                    // Обработка восстановления
                    isPresented = false
                }
                .buttonStyle(.bordered)
                .disabled(false)
            }
            .padding()
            .navigationTitle("Восстановление")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

#if DEBUG
struct RecoveryOptionsModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryOptionsModal(isPresented: .constant(true))
    }
}
#endif
