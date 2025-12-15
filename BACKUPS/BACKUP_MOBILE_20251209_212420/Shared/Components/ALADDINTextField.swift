//
//  ALADDINTextField.swift
//  ALADDIN
//
//  Created by AI Assistant on 2024
//  Кастомное текстовое поле в стиле ALADDIN
//

import SwiftUI

struct ALADDINTextField: View {
    @Binding var text: String
    let placeholder: String
    let isSecure: Bool
    
    init(_ placeholder: String, text: Binding<String>, isSecure: Bool = false) {
        self.placeholder = placeholder
        self._text = text
        self.isSecure = isSecure
    }
    
    var body: some View {
        Group {
            if isSecure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
            }
        }
        .padding(16)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
        .foregroundColor(.primary)
        .font(.body)
    }
}

// MARK: - Preview

struct ALADDINTextField_Previews: PreviewProvider {
    @State static var text = ""
    
    static var previews: some View {
        VStack(spacing: 16) {
            ALADDINTextField("Введите текст", text: $text)
            ALADDINTextField("Пароль", text: $text, isSecure: true)
        }
        .padding()
        .background(Color.black)
    }
}
