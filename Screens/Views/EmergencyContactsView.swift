import SwiftUI

/**
 * 📞 Emergency Contacts View
 * Экран управления экстренными контактами
 * Компонент: emergency_contact_manager
 */

struct EmergencyContactsView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var configurationService = ComponentConfigurationService.shared
    @StateObject private var toastManager = ToastManager.shared
    
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
            // TODO: Загрузить контакты через API
            try? await Task.sleep(nanoseconds: 500_000_000) // Симуляция загрузки
            isLoading = false
        }
    }
    
    private func saveContacts() {
        Task {
            // TODO: Сохранить контакты через API
            toastManager.showSuccess(localizationManager.localized("settings_saved_contacts"))
        }
    }
    
    private func deleteContact(_ contact: EmergencyContact) {
        contacts.removeAll { $0.id == contact.id }
        saveContacts()
    }
}

// MARK: - Emergency Contact Model

struct EmergencyContact: Identifiable {
    let id = UUID()
    var name: String
    var phone: String
    var priority: Int // 1 = основной, 2 = резервный
    var channels: [String] // ["call", "sms", "messenger"]
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

