import SwiftUI

/**
 * 📞 Emergency Contacts View
 * Экран управления экстренными контактами
 * Компонент: emergency_contact_manager
 */

struct EmergencyContactsView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    
    @State private var contacts: [EmergencyContact] = []
    @State private var isLoading: Bool = false
    @State private var showAddContact: Bool = false
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: localizationManager.localized("component_emergency_contact_manager_title"),
                    subtitle: localizationManager.localized("component_emergency_contact_manager_description"),
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                // Content
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Info Card
                        infoCard
                        
                        // Contacts List
                        if isLoading {
                            ProgressView()
                                .padding()
                        } else if contacts.isEmpty {
                            emptyState
                        } else {
                            contactsList
                        }
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            loadContacts()
        }
        .sheet(isPresented: $showAddContact) {
            AddEmergencyContactView(
                onSave: { contact in
                    contacts.append(contact)
                    saveContacts()
                }
            )
        }
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Image(systemName: "info.circle.fill")
                    .foregroundColor(.primaryBlue)
                Text(localizationManager.localized("emergency_contacts_info_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            Text(localizationManager.localized("emergency_contacts_info_text"))
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.primaryBlue.opacity(0.1))
        )
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "person.2.fill")
                .font(.system(size: 48))
                .foregroundColor(.textSecondary)
            Text(localizationManager.localized("emergency_contacts_empty"))
                .font(.body)
                .foregroundColor(.textSecondary)
            Button(action: { showAddContact = true }) {
                Text(localizationManager.localized("emergency_contacts_add_first"))
                    .font(.bodyBold)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.primaryBlue)
                    .cornerRadius(CornerRadius.medium)
            }
        }
        .padding()
    }
    
    // MARK: - Contacts List
    
    private var contactsList: some View {
        VStack(spacing: Spacing.m) {
            ForEach(contacts) { contact in
                ContactRow(contact: contact) {
                    deleteContact(contact)
                }
            }
            
            Button(action: { showAddContact = true }) {
                HStack {
                    Image(systemName: "plus.circle.fill")
                    Text(localizationManager.localized("emergency_contacts_add"))
                }
                .font(.bodyBold)
                .foregroundColor(.primaryBlue)
                .frame(maxWidth: .infinity)
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.primaryBlue, lineWidth: 2)
                )
            }
        }
    }
    
    // MARK: - Methods
    
    private func loadContacts() {
        isLoading = true
        Task {
            // ✅ Загрузить из UserDefaults
            if let data = UserDefaults.standard.data(forKey: "component_emergency_contact_manager_contacts"),
               let decoded = try? JSONDecoder().decode([EmergencyContact].self, from: data) {
                await MainActor.run {
                    contacts = decoded
                    isLoading = false
                }
            } else {
                // ✅ Попробовать загрузить через ComponentConfigurationService
                do {
                    let config = try await configurationService.getConfiguration(for: "emergency_contact_manager")
                    if let settings = config.additionalSettings,
                       let contactsData = settings["contacts"]?.value as? [[String: Any]] {
                        // Конвертировать из словарей в EmergencyContact
                        let loadedContacts: [EmergencyContact] = contactsData.compactMap { contactDict in
                            guard let name = contactDict["name"] as? String,
                                  let phone = contactDict["phone"] as? String else {
                                return nil
                            }
                            return EmergencyContact(
                                name: name,
                                phone: phone,
                                priority: contactDict["priority"] as? Int ?? 1,
                                channels: contactDict["channels"] as? [String] ?? ["call", "sms"]
                            )
                        }
                        await MainActor.run {
                            contacts = loadedContacts
                            isLoading = false
                        }
                    } else {
                        await MainActor.run {
                            isLoading = false
                        }
                    }
                } catch {
                    await MainActor.run {
                        isLoading = false
                    }
                }
            }
        }
    }
    
    // ✅ Сохранение контактов через ComponentConfigurationService и UserDefaults
    private func saveContacts() {
        Task {
            // 1. Сохранить в UserDefaults (локально, мгновенно)
            if let encoded = try? JSONEncoder().encode(contacts) {
                UserDefaults.standard.set(encoded, forKey: "component_emergency_contact_manager_contacts")
            }
            
            // 2. Сохранить через ComponentConfigurationService (синхронизация с сервером)
            do {
                // Получить текущий статус компонента через метод (правильный доступ к @MainActor)
                let isComponentEnabled = await MainActor.run {
                    ComponentStatusService.shared.getComponentEnabledStatus(componentId: "emergency_contact_manager")
                }
                
                // Конвертировать контакты в словари для сохранения
                let contactsDict = contacts.map { contact in
                    [
                        "id": contact.id.uuidString,
                        "name": contact.name,
                        "phone": contact.phone,
                        "priority": contact.priority,
                        "channels": contact.channels
                    ] as [String: Any]
                }
                
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "contacts": AnyCodable(contactsDict)
                    ]
                )
                
                try await configurationService.saveConfiguration(
                    componentId: "emergency_contact_manager",
                    configuration: config
                )
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                }
            } catch {
                // Настройки уже сохранены локально в UserDefaults
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                }
            }
        }
    }
    
    private func deleteContact(_ contact: EmergencyContact) {
        contacts.removeAll { $0.id == contact.id }
        saveContacts()
    }
}

// MARK: - Emergency Contact Model

struct EmergencyContact: Identifiable, Codable {
    var id: UUID
    var name: String
    var phone: String
    var priority: Int // 1 = основной, 2 = резервный
    var channels: [String] // ["call", "sms", "messenger"]
    
    init(id: UUID = UUID(), name: String, phone: String, priority: Int = 1, channels: [String] = ["call", "sms"]) {
        self.id = id
        self.name = name
        self.phone = phone
        self.priority = priority
        self.channels = channels
    }
}

// MARK: - Contact Row

struct ContactRow: View {
    let contact: EmergencyContact
    let onDelete: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Circle()
                .fill(Color.primaryBlue.opacity(0.2))
                .frame(width: 50, height: 50)
                .overlay(
                    Text(String(contact.name.prefix(1)))
                        .font(.headline)
                        .foregroundColor(.primaryBlue)
                )
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(contact.name)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                Text(contact.phone)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Button(action: onDelete) {
                Image(systemName: "trash")
                    .foregroundColor(.dangerRed)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}

// MARK: - Add Contact View

struct AddEmergencyContactView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    let onSave: (EmergencyContact) -> Void
    
    @State private var name: String = ""
    @State private var phone: String = ""
    @State private var priority: Int = 1
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("emergency_contacts_add_title"))) {
                    TextField(localizationManager.localized("emergency_contacts_name"), text: $name)
                    TextField(localizationManager.localized("emergency_contacts_phone"), text: $phone)
                        .keyboardType(.phonePad)
                }
            }
            .navigationTitle(localizationManager.localized("emergency_contacts_add"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_cancel")) {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("common_save")) {
                        let contact = EmergencyContact(
                            name: name,
                            phone: phone,
                            priority: priority,
                            channels: ["call", "sms"]
                        )
                        onSave(contact)
                        dismiss()
                    }
                    .disabled(name.isEmpty || phone.isEmpty)
                }
            }
        }
    }
}

