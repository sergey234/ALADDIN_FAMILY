import SwiftUI

struct ConsentModal: View {
    @Binding var isPresented: Bool
    let onConsentGiven: () -> Void
    @State private var showFullConsent: Bool = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Заголовок
                    VStack(spacing: 12) {
                        Image(systemName: "hand.raised.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.blue)
                        
                        Text("Согласие на обработку данных")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("Для продолжения регистрации необходимо ваше согласие")
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    
                    // Текст согласия
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Согласие на обработку персональных данных")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Я даю согласие компании Aladdin на:")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.primary)
                            
                            VStack(alignment: .leading, spacing: 8) {
                                consentItem("Создание семейного аккаунта")
                                consentItem("Обработку данных о роли и возрасте")
                                consentItem("Генерацию QR-кода для доступа")
                                consentItem("Сохранение настроек безопасности")
                            }
                        }
                        
                        Text("Компания Aladdin гарантирует:")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.primary)
                            .padding(.top, 8)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            consentItem("Не собирает номера телефонов и email")
                            consentItem("Не передает данные третьим лицам")
                            consentItem("Использует данные только для работы приложения")
                            consentItem("Обеспечивает безопасность данных")
                        }
                    }
                    .padding(20)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                    // Кнопка "Читать полный текст"
                    Button(action: {
                        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                            showFullConsent.toggle()
                        }
                    }) {
                        HStack {
                            Text(showFullConsent ? "Скрыть полный текст" : "Читать полный текст согласия")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.blue)
                            
                            Image(systemName: showFullConsent ? "chevron.up" : "chevron.down")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.blue)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)
                    }
                    
                    // Раздвигающийся блок с полным текстом согласия
                    if showFullConsent {
                        VStack(alignment: .leading, spacing: 16) {
                            Text("Полное согласие на обработку персональных данных")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.primary)
                            
                            fullConsentText()
                        }
                        .padding(20)
                        .background(Color.blue.opacity(0.05))
                        .cornerRadius(12)
                        .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    // Кнопки
                    VStack(spacing: 12) {
                        Button(action: {
                            onConsentGiven()
                            isPresented = false
                        }) {
                            Text("Согласен и продолжаю")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                                .background(Color.blue)
                                .cornerRadius(12)
                        }
                        
                        Button("Отказаться") {
                            isPresented = false
                        }
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.secondary)
                    }
                }
                .padding(20)
            }
            .navigationTitle("Согласие")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Закрыть") {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    private func consentItem(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 14))
                .foregroundColor(.green)
                .padding(.top, 2)
            
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.primary)
        }
    }
    
    private func fullConsentText() -> some View {
        VStack(alignment: .leading, spacing: 12) {
            consentSection(
                title: "1. Предмет согласия",
                text: "Я даю свое согласие компании Aladdin на обработку персональных данных в целях использования приложения ALADDIN Family (далее - «Приложение»), создания семейного аккаунта, настройки функций безопасности и защиты семьи."
            )
            
            consentSection(
                title: "2. Персональные данные",
                text: "Обработке подлежат следующие персональные данные: роль в семье (родитель/ребенок/бабушка-дедушка), возрастная группа, личная буква для идентификации."
            )
            
            consentSection(
                title: "3. Способы обработки",
                text: "Персональные данные обрабатываются с использованием автоматизированных средств (приложение, сервер, база данных). Данные хранятся локально на устройстве пользователя и передаются на сервер компании для обеспечения работы семейного доступа."
            )
            
            consentSection(
                title: "4. Сроки обработки",
                text: "Персональные данные обрабатываются в течение всего срока использования Приложения и до момента отзыва согласия пользователем или до момента прекращения действия Приложения."
            )
            
            consentSection(
                title: "5. Права пользователя",
                text: "Я подтверждаю, что ознакомлен(а) с правами пользователя, предусмотренными Федеральным законом «О персональных данных» № 152-ФЗ, в том числе с правом на получение информации об обработке моих персональных данных, правом на доступ к моим персональным данным, правом на требование уточнения, блокирования или уничтожения моих персональных данных."
            )
            
            consentSection(
                title: "6. Согласие распространяется на:",
                text: "- Создание и управление семейным аккаунтом\n- Генерацию и использование QR-кодов для доступа\n- Сохранение настроек безопасности семьи\n- Использование данных для работы функций родительского контроля\n- Обработку данных о роли и возрасте для персонализации интерфейса"
            )
            
            consentSection(
                title: "7. Гарантии компании",
                text: "- Не собираем номер телефона, email, имя или другие персональные данные\n- Не передаем данные третьим лицам\n- Используем данные исключительно для работы функций Приложения\n- Обеспечиваем безопасное хранение данных\n- Соблюдаем требования законодательства о защите персональных данных"
            )
            
            consentSection(
                title: "8. Отзыв согласия",
                text: "Я понимаю, что вправе отозвать настоящее согласие на обработку персональных данных в любой момент, направив соответствующее уведомление в компанию Aladdin. При этом я понимаю, что отзыв согласия может повлечь невозможность использования Приложения."
            )
        }
    }
    
    private func consentSection(title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 15, weight: .semibold))
                .foregroundColor(.primary)
            
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.secondary)
                .lineSpacing(4)
        }
        .padding(.vertical, 8)
    }
}

struct ConsentModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        ConsentModal(
            isPresented: $isPresented,
            onConsentGiven: {
                print("Consent given")
            }
        )
    }
}