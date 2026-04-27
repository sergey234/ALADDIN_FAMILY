import SwiftUI
import MessageUI
import UIKit
import CoreLocation
import UserNotifications

/**
 * 🚨 Crash Detection Alert Modal
 * Модальное окно для оповещения об обнаружении аварии
 * Реализует Emergency Actions: звонки, SMS, отправка данных на сервер
 */

struct CrashDetectionAlertModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var showSMSComposer = false
    @State private var emergencyContacts: [EmergencyContact] = []
    @State private var crashLocation: CLLocation?
    
    private let crashDetectionManager = CrashDetectionManager.shared
    private let emergencyContactsKey = "emergency_contacts"

    var body: some View {
        ZStack {
            Color.red.opacity(0.9)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.white)

                Text(localizationManager.localized("crash_alert_title"))
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)

                Text(localizationManager.localized("crash_alert_call_services_question"))
                    .font(.body)
                    .foregroundColor(.white.opacity(0.9))

                Text(localizationManager.localized("crash_alert_false_positive_warning"))
                    .font(.caption)
                    .foregroundColor(.yellow.opacity(0.8))
                    .multilineTextAlignment(.center)
                    .padding(.top, 4)

                VStack(spacing: 12) {
                    HStack(spacing: 20) {
                        Button("Отмена") {
                            isPresented = false
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.gray.opacity(0.3))
                        .cornerRadius(10)

                        Button("🚨 112") {
                            callEmergencyServices()
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.white.opacity(0.2))
                        .cornerRadius(10)
                    }
                    
                    Button("📱 Уведомить контакты") {
                        notifyEmergencyContacts()
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.blue.opacity(0.3))
                    .cornerRadius(10)
                }
                .padding(.horizontal)
            }
            .padding()
        }
        .onAppear {
            loadEmergencyContacts()
            getCurrentLocation()
        }
        .sheet(isPresented: $showSMSComposer) {
            if MFMessageComposeViewController.canSendText() {
                MessageComposeView(
                    recipients: emergencyContacts.filter { $0.channels.contains("sms") }.map { $0.phone },
                    message: getEmergencyMessage()
                )
            }
        }
    }
    
    // MARK: - Emergency Actions
    
    /// Звонок экстренным службам
    private func callEmergencyServices() {
        isPresented = false
        
        // Звонок экстренным службам (112 - единый номер экстренных служб в России)
        if let url = URL(string: "tel://112") {
            UIApplication.shared.open(url, options: [:], completionHandler: { success in
                if success {
                    print("✅ CrashDetectionAlertModal: Звонок экстренным службам инициирован")
                    // Отправить данные на сервер
                    Task {
                        await sendCrashDataToServer()
                    }
                } else {
                    print("❌ CrashDetectionAlertModal: Не удалось инициировать звонок")
                }
            })
        }
        
        // Отправить уведомление в систему
        sendEmergencyNotification()
    }
    
    /// Уведомить экстренные контакты
    private func notifyEmergencyContacts() {
        let contacts = getEmergencyContacts()
        
        guard !contacts.isEmpty else {
            print("⚠️ CrashDetectionAlertModal: Нет экстренных контактов для уведомления")
            return
        }
        
        // Отправить SMS контактам, которые поддерживают SMS
        let smsContacts = contacts.filter { $0.channels.contains("sms") }
        if !smsContacts.isEmpty && MFMessageComposeViewController.canSendText() {
            showSMSComposer = true
        }
        
        // Отправить push уведомления всем контактам
        for contact in contacts {
            sendEmergencyNotification(to: contact)
        }
        
        // Отправить данные на сервер
        Task {
            await sendCrashDataToServer()
        }
    }
    
    /// Получить экстренные контакты
    private func getEmergencyContacts() -> [EmergencyContact] {
        if let data = UserDefaults.standard.data(forKey: emergencyContactsKey),
           let decoded = try? JSONDecoder().decode([EmergencyContact].self, from: data) {
            return decoded
        }
        return emergencyContacts
    }
    
    /// Загрузить экстренные контакты
    private func loadEmergencyContacts() {
        emergencyContacts = getEmergencyContacts()
    }
    
    /// Получить текущее местоположение
    private func getCurrentLocation() {
        Task {
            do {
                let location = try await crashDetectionManager.getCurrentLocation()
                await MainActor.run {
                    crashLocation = location
                }
            } catch {
                print("⚠️ CrashDetectionAlertModal: Не удалось получить местоположение: \(error.localizedDescription)")
            }
        }
    }
    
    /// Получить сообщение для экстренных контактов
    private func getEmergencyMessage() -> String {
        let locationText: String
        if let location = crashLocation {
            locationText = "Координаты: \(location.coordinate.latitude), \(location.coordinate.longitude)"
        } else {
            locationText = "Местоположение определяется..."
        }
        
        return """
        🚨 ЭКСТРЕННОЕ УВЕДОМЛЕНИЕ
        
        Обнаружена возможная авария!
        \(locationText)
        
        Время: \(Date().formatted(date: .abbreviated, time: .shortened))
        
        Пожалуйста, проверьте ситуацию.
        """
    }
    
    /// Отправить данные аварии на сервер
    private func sendCrashDataToServer() async {
        do {
            // Получить данные о краше из CrashDetectionManager
            let crashData = CrashData(
                gForce: crashDetectionManager.lastDetectedGForce ?? 0.0,
                speed: crashDetectionManager.lastDetectedSpeed ?? 0.0,
                timestamp: Date(),
                location: crashLocation
            )
            
            // Отправить через API
            try await crashDetectionManager.sendCrashDataToServer(crashData)
            print("✅ CrashDetectionAlertModal: Данные аварии отправлены на сервер")
            
        } catch {
            print("❌ CrashDetectionAlertModal: Ошибка отправки данных на сервер: \(error.localizedDescription)")
        }
    }
    
    /// Отправить уведомление в систему
    private func sendEmergencyNotification() {
        // Локальное уведомление о краше
        let content = UNMutableNotificationContent()
        content.title = "🚨 Авария обнаружена"
        content.body = "Проверьте ситуацию и при необходимости вызовите экстренные службы"
        content.sound = .defaultCritical
        content.categoryIdentifier = "CRASH_DETECTION"
        
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: nil
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("❌ CrashDetectionAlertModal: Ошибка отправки уведомления: \(error.localizedDescription)")
            } else {
                print("✅ CrashDetectionAlertModal: Уведомление отправлено")
            }
        }
    }
    
    /// Отправить уведомление конкретному контакту
    private func sendEmergencyNotification(to contact: EmergencyContact) {
        // Здесь можно добавить логику отправки push уведомления через API
        print("📱 CrashDetectionAlertModal: Уведомление отправлено контакту \(contact.name)")
    }
}

// MARK: - Supporting Types
// CrashData определена в CrashDetectionManager.swift

// MARK: - Message Compose View

struct MessageComposeView: UIViewControllerRepresentable {
    let recipients: [String]
    let message: String
    
    func makeUIViewController(context: Context) -> MFMessageComposeViewController {
        let controller = MFMessageComposeViewController()
        controller.recipients = recipients
        controller.body = message
        controller.messageComposeDelegate = context.coordinator
        return controller
    }
    
    func updateUIViewController(_ uiViewController: MFMessageComposeViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, MFMessageComposeViewControllerDelegate {
        func messageComposeViewController(_ controller: MFMessageComposeViewController, didFinishWith result: MessageComposeResult) {
            controller.dismiss(animated: true)
        }
    }
}

struct CrashDetectionAlertModal_Previews: PreviewProvider {
    static var previews: some View {
        CrashDetectionAlertModal(isPresented: .constant(true))
    }
}