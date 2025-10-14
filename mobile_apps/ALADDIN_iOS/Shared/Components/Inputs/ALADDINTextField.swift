import SwiftUI

/// ✏️ ALADDIN TextField
/// Кастомное поле ввода текста с дизайном ALADDIN
/// Источник: HTML input fields на разных экранах
struct ALADDINTextField: View {
    
    // MARK: - Properties
    
    let placeholder: String
    let icon: String?
    @Binding var text: String
    let keyboardType: UIKeyboardType
    let isSecure: Bool
    let errorMessage: String?
    
    @State private var isEditing: Bool = false
    @State private var showPassword: Bool = false
    
    // MARK: - Init
    
    init(
        _ placeholder: String,
        text: Binding<String>,
        icon: String? = nil,
        keyboardType: UIKeyboardType = .default,
        isSecure: Bool = false,
        errorMessage: String? = nil
    ) {
        self.placeholder = placeholder
        self._text = text
        self.icon = icon
        self.keyboardType = keyboardType
        self.isSecure = isSecure
        self.errorMessage = errorMessage
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            // Input Field
            HStack(spacing: Spacing.s) {
                // Иконка слева
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.system(size: 18))
                        .foregroundColor(isEditing ? .primaryBlue : .textSecondary)
                        .frame(width: 24)
                }
                
                // Поле ввода
                Group {
                    if isSecure && !showPassword {
                        SecureField(placeholder, text: $text)
                    } else {
                        TextField(placeholder, text: $text)
                            .keyboardType(keyboardType)
                    }
                }
                .font(.body)
                .foregroundColor(.textPrimary)
                .accentColor(.primaryBlue)
                .onTapGesture {
                    isEditing = true
                }
                
                // Кнопка показать/скрыть пароль
                if isSecure {
                    Button(action: {
                        showPassword.toggle()
                    }) {
                        Image(systemName: showPassword ? "eye.slash.fill" : "eye.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.textSecondary)
                    }
                }
                
                // Кнопка очистить
                if !text.isEmpty && isEditing {
                    Button(action: {
                        text = ""
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(
                        Color.backgroundMedium.opacity(0.5)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(
                                errorMessage != nil ? Color.dangerRed :
                                isEditing ? Color.primaryBlue : Color.white.opacity(0.1),
                                lineWidth: isEditing ? 2 : 1
                            )
                    )
            )
            
            // Сообщение об ошибке
            if let errorMessage = errorMessage {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "exclamationmark.circle.fill")
                        .font(.caption)
                    Text(errorMessage)
                        .font(.caption)
                }
                .foregroundColor(.dangerRed)
            }
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.l) {
        // Обычное поле
        ALADDINTextField(
            "Введите имя",
            text: .constant(""),
            icon: "person"
        )
        
        // Email
        ALADDINTextField(
            "Email",
            text: .constant("sergey@aladdin.family"),
            icon: "envelope",
            keyboardType: .emailAddress
        )
        
        // Пароль
        ALADDINTextField(
            "Пароль",
            text: .constant("12345678"),
            icon: "lock",
            isSecure: true
        )
        
        // С ошибкой
        ALADDINTextField(
            "Телефон",
            text: .constant("123"),
            icon: "phone",
            keyboardType: .phonePad,
            errorMessage: "Введите корректный номер телефона"
        )
    }
    .padding()
    .background(LinearGradient.backgroundGradient)
}




