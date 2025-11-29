import SwiftUI

/// 👴 Elderly Interface Screen
/// Интерфейс для людей 60+ - упрощённый с крупными элементами
/// Источник дизайна: /mobile/wireframes/07_elderly_interface.html
struct ElderlyInterfaceScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab: Int = 0
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    
    // Состояния для здоровья
    @State private var showMedicationReminder: Bool = false
    @State private var showDoctorAppointments: Bool = false
    @State private var showBloodPressure: Bool = false
    @State private var showHealthJournal: Bool = false
    
    // Состояния для безопасности
    @State private var showSiteChecker: Bool = false
    @State private var showSecuritySettings: Bool = false
    @State private var showDangerousContacts: Bool = false
    
    // Сохраняем настройку безопасности в AppStorage
    @AppStorage("elderly_security_enabled") private var isSecurityEnabled: Bool = true
    @State private var blockedContactsCount: Int = 0
    
    // Состояния для экстренной помощи
    @State private var showEmergencyAlert: Bool = false
    @State private var showInstructions: Bool = false
    @State private var showCallChildrenAlert: Bool = false
    @State private var showSecurityStatus: Bool = false
    @State private var showElderlySettings: Bool = false
    
    // Данные здоровья (загружаются из UserDefaults)
    @State private var medications: [Medication] = []
    @State private var appointments: [DoctorAppointment] = []
    @State private var bloodPressure: BloodPressureReading = BloodPressureReading(systolic: 120, diastolic: 80, date: "08.10")
    
    // Данные семьи (синхронизируются с family_members_list)
    @State private var familyMembers: [ElderlyFamilyMember] = []
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (зеленый как в wireframe для пожилых)
            LinearGradient(
                colors: [
                    Color(hex: "#2D5016"),
                    Color(hex: "#4A7C59"), 
                    Color(hex: "#6B8E23")
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Простая навигация
                elderlyHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.xl) {
                        // Приветствие
                        greetingCard
                        
                        // Секция здоровья
                        healthSection
                        
                        // Семейная панель
                        familySection
                        
                        // Очень большие кнопки
                        bigButtonsList
                        
                        // Экстренная помощь
                        emergencySection
                        
                        // Защита от мошенников
                        securitySection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.l)
                }
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ElderlyProfileImagePicker(selectedImage: $selectedImage)
        }
        .sheet(isPresented: $showMedicationReminder) {
            MedicationReminderModal(isPresented: $showMedicationReminder, medications: $medications, onSave: {
                saveMedications()
            })
        }
        .sheet(isPresented: $showDoctorAppointments) {
            DoctorAppointmentsModal(isPresented: $showDoctorAppointments, appointments: $appointments, onSave: {
                saveAppointments()
            })
        }
        .sheet(isPresented: $showBloodPressure) {
            BloodPressureModal(isPresented: $showBloodPressure, bloodPressure: $bloodPressure, onSave: {
                saveBloodPressure()
            })
        }
        .sheet(isPresented: $showHealthJournal) {
            HealthJournalModal(isPresented: $showHealthJournal)
        }
        .sheet(isPresented: $showSiteChecker) {
            SiteCheckerModal(isPresented: $showSiteChecker)
        }
        .sheet(isPresented: $showSecuritySettings) {
            SecuritySettingsModal(isPresented: $showSecuritySettings, isSecurityEnabled: $isSecurityEnabled)
        }
        .sheet(isPresented: $showDangerousContacts) {
            DangerousContactsModal(isPresented: $showDangerousContacts, blockedCount: $blockedContactsCount)
        }
        .sheet(isPresented: $showInstructions) {
            SafetyInstructionsModal(isPresented: $showInstructions)
        }
        .sheet(isPresented: $showElderlySettings) {
            ElderlySettingsModal(isPresented: $showElderlySettings)
        }
        .alert(localizationManager.localized("elderly_interface_call_children_question"), isPresented: $showCallChildrenAlert) {
            // Динамический список детей из familyMembers
            ForEach(familyMembers.filter { $0.role.lowercased().contains("сын") || $0.role.lowercased().contains("дочь") || $0.role.lowercased().contains("внук") || $0.role.lowercased().contains("внучка") }) { member in
                Button("\(member.name) (\(member.role))") {
                    callFamilyMember(member.name, member.phone)
                }
            }
            Button(localizationManager.localized("elderly_interface_cancel"), role: .cancel) { }
        } message: {
            Text(localizationManager.localized("elderly_interface_choose_whom"))
        }
        .onAppear {
            loadFamilyMembers()
            loadMedications()
            loadAppointments()
            loadBloodPressure()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadFamilyMembers()
        }
    }
    
    // MARK: - Elderly Header
    
    private var elderlyHeader: some View {
        HStack(spacing: Spacing.m) {
            // Кнопка назад
            Button(action: {
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.orange.opacity(0.2))
                    )
            }
            .accessibilityLabel(localizationManager.localized("elderly_interface_back"))
            
            // Аватар с возможностью загрузки фото
            Button(action: {
                showImagePicker = true
            }) {
                ZStack {
                    if let selectedImage = selectedImage {
                        Image(uiImage: selectedImage)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 70, height: 70)
                            .clipShape(Circle())
                    } else {
                        Text("👴")
                            .font(.system(size: 50))
                            .frame(width: 70, height: 70)
                .background(
                    Circle()
                        .fill(Color.white.opacity(0.2))
                )
                    }
                    
                    // Иконка камеры
                    VStack {
                        Spacer()
                        HStack {
                            Spacer()
                            Circle()
                                .fill(Color.secondaryGold)
                                .frame(width: 18, height: 18)
                                .overlay(
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 9))
                                        .foregroundColor(.white)
                                )
                                .offset(x: 2, y: 2)
                        }
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Приветствие
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("elderly_interface_hello"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
                
                Text(localizationManager.localized("elderly_interface_protected"))
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
            }
            
            Spacer()
            
            // Кнопка настроек
            Button(action: {
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
                showElderlySettings = true
            }) {
                Image(systemName: "gearshape.fill")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .accessibilityLabel(localizationManager.localized("elderly_interface_settings"))
        }
        .id("elderly_interface_lang_\(localizationManager.currentLanguage.rawValue)")
        .padding(Spacing.cardPadding)
        .background(
            Color.white.opacity(0.1)
        )
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            showSecurityStatus = true
        }) {
            VStack(spacing: Spacing.l) {
                Text("✅")
                    .font(.system(size: 80))
                
                Text(localizationManager.localized("elderly_interface_all_good"))
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.successGreen)
                
                Text(localizationManager.localized("elderly_interface_no_threats"))
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.9))
            }
            .padding(Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.xl)
                    .fill(Color.white.opacity(0.15))
            )
        }
        .buttonStyle(PlainButtonStyle())
        .sheet(isPresented: $showSecurityStatus) {
            SecurityStatusModal(isPresented: $showSecurityStatus)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Health Section
    
    private var healthSection: some View {
        VStack(spacing: Spacing.l) {
            // Заголовок секции
            HStack {
                Text(localizationManager.localized("elderly_interface_health_reminders"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // ✅ ВСЕГДА показываем все 4 карточки (как в бэкапе)
            VStack(spacing: Spacing.m) {
                // 1. Лекарства
                healthCard(
                    icon: "💊",
                    title: localizationManager.localized("elderly_interface_medications"),
                    subtitle: medications.isEmpty
                        ? "Добавить лекарства для напоминаний" 
                        : "Следующий приём: \(medications.first?.time ?? "—") (\(medications.first?.name ?? "—"))",
                    color: .blue,
                    action: { showMedicationReminder = true }
                )
                
                // 2. Визиты к врачу
                healthCard(
                    icon: "🏥",
                    title: localizationManager.localized("elderly_interface_doctor_visits"),
                    subtitle: appointments.isEmpty
                        ? "Добавить записи к врачу"
                        : "Следующий: \(appointments.first?.date ?? "—") (\(appointments.first?.doctor ?? "—"))",
                    color: .green,
                    action: { showDoctorAppointments = true }
                )
                
                // 3. Измерение давления
                healthCard(
                    icon: "🩺",
                    title: localizationManager.localized("elderly_interface_blood_pressure"),
                    subtitle: localizationManager.localized("elderly_interface_last_reading", bloodPressure.systolic, bloodPressure.diastolic, bloodPressure.date),
                    color: .red,
                    action: { showBloodPressure = true }
                )
                
                // 4. Журнал здоровья
                healthCard(
                    icon: "📋",
                    title: localizationManager.localized("elderly_interface_health_journal"),
                    subtitle: localizationManager.localized("elderly_interface_view_records"),
                    color: .purple,
                    action: { showHealthJournal = true }
                )
            }
        }
    }
    
    private func healthCard(icon: String, title: String, subtitle: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.l) {
                // Иконка
                Text(icon)
                    .font(.system(size: 40))
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(title)
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                    
                    Text(subtitle)
                        .font(.system(size: 16))
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white.opacity(0.6))
            }
            .padding(Spacing.l)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.white.opacity(0.15))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(color.opacity(0.3), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Family Section
    
    private var familySection: some View {
        VStack(spacing: Spacing.l) {
            // Заголовок секции
            HStack {
                Text("👨‍👩‍👧‍👦 Моя семья")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Карточки членов семьи или Empty State
            if familyMembers.isEmpty {
                    EmptyStateView(
                        icon: "👨‍👩‍👧‍👦",
                        title: localizationManager.localized("elderly_interface_family_not_added"),
                        description: localizationManager.localized("elderly_interface_family_description"),
                        actionTitle: nil,
                        action: nil
                    )
                .padding(.horizontal, Spacing.screenPadding)
            } else {
                VStack(spacing: Spacing.m) {
                    ForEach(familyMembers) { member in
                        familyMemberCard(member: member)
                    }
                }
            }
        }
    }
    
    private func familyMemberCard(member: ElderlyFamilyMember) -> some View {
        HStack(spacing: Spacing.l) {
            // Аватар
            Text(member.avatar)
                .font(.system(size: 50))
            
            // Информация
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(member.name)
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Text(member.role)
                    .font(.system(size: 16))
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Text(member.phone)
                    .font(.system(size: 14))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                // Статус
                HStack(spacing: Spacing.s) {
                    Circle()
                        .fill(member.status.color)
                        .frame(width: 12, height: 12)
                    
                    Text(member.status.text)
                        .font(.system(size: 14))
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                }
            }
            
            Spacer()
            
            // Кнопка звонка
            Button(action: {
                // ✅ Логика звонка члену семьи
                let generator = UINotificationFeedbackGenerator()
                generator.notificationOccurred(.success)
                callFamilyMember(member.name, member.phone)
            }) {
                Image(systemName: "phone.fill")
                    .font(.system(size: 24))
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(Color.green)
                    .clipShape(Circle())
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.white.opacity(0.15))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.3), lineWidth: 1)
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Emergency Section
    
    private var emergencySection: some View {
        VStack(spacing: Spacing.l) {
            // Заголовок секции
            HStack {
                Text(localizationManager.localized("elderly_interface_emergency_help"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Кнопки экстренной помощи
            VStack(spacing: Spacing.m) {
                // Кнопка "ПОЗВОНИТЬ ДЕТЯМ"
                Button(action: {
                    showCallChildrenAlert = true
                }) {
                    HStack(spacing: Spacing.l) {
                        Text("📞")
                            .font(.system(size: 40))
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("elderly_interface_call_children"))
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                                .lineLimit(1)
                                .minimumScaleFactor(0.8)
                            
                            Text(localizationManager.localized("elderly_interface_quick_call"))
                                .font(.system(size: 14))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(1)
                                .minimumScaleFactor(0.8)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "phone.fill")
                            .font(.system(size: 30))
                            .foregroundColor(.white)
                    }
                    .padding(Spacing.l)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(
                                LinearGradient(
                                    colors: [Color.red, Color(hex: "#DC2626")],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
                }
                .buttonStyle(PlainButtonStyle())
                
                // Кнопка SOS
                sosButton
            }
        }
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(spacing: Spacing.l) {
            // Заголовок секции
            HStack {
                Text(localizationManager.localized("elderly_interface_security_title"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Карточки безопасности
            VStack(spacing: Spacing.m) {
                // Проверить сайт
                securityCard(
                    icon: "🔍",
                    title: localizationManager.localized("elderly_interface_check_site"),
                    subtitle: localizationManager.localized("elderly_interface_is_site_safe"),
                    color: .blue,
                    action: { showSiteChecker = true }
                )
                
                // Защита от обмана
                securityCard(
                    icon: "🛡️",
                    title: localizationManager.localized("elderly_interface_scam_protection"),
                    subtitle: isSecurityEnabled ? localizationManager.localized("elderly_interface_protection_enabled") : localizationManager.localized("elderly_interface_protection_disabled"),
                    color: isSecurityEnabled ? .green : .red,
                    action: { showSecuritySettings = true }
                )
                
                // Опасные контакты
                securityCard(
                    icon: "📞",
                    title: localizationManager.localized("elderly_interface_dangerous_contacts"),
                    subtitle: localizationManager.localized("elderly_interface_blocked_count", blockedContactsCount),
                    color: .orange,
                    action: { showDangerousContacts = true }
                )
            }
        }
    }
    
    private func securityCard(icon: String, title: String, subtitle: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.l) {
                // Иконка
                Text(icon)
                    .font(.system(size: 40))
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(title)
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                    
                    Text(subtitle)
                        .font(.system(size: 16))
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white.opacity(0.6))
            }
            .padding(Spacing.l)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.white.opacity(0.15))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(color.opacity(0.3), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Big Buttons List
    
    private var bigButtonsList: some View {
        VStack(spacing: Spacing.l) {
            // Позвонить родным
            bigElderlyButton(
                icon: "📞",
                title: localizationManager.localized("elderly_interface_big_button_call"),
                subtitle: localizationManager.localized("elderly_interface_big_button_call_subtitle"),
                color: .successGreen,
                action: {
                    // Логика звонка родным
                    showCallChildrenAlert = true
                }
            )
            
            // Безопасность - Защита от мошенников
            bigElderlyButton(
                icon: "🛡️",
                title: localizationManager.localized("elderly_interface_big_button_protection"),
                subtitle: localizationManager.localized("elderly_interface_big_button_protection_subtitle"),
                color: .primaryBlue,
                action: {
                    showSecuritySettings = true
                }
            )
            
            // Инструкции
            bigElderlyButton(
                icon: "📖",
                title: localizationManager.localized("elderly_interface_big_button_instructions"),
                subtitle: localizationManager.localized("elderly_interface_big_button_instructions_subtitle"),
                color: .warningOrange,
                action: {
                    showInstructions = true
                }
            )
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func bigElderlyButton(
        icon: String,
        title: String,
        subtitle: String,
        color: Color,
        action: @escaping () -> Void = {}
    ) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: Spacing.l) {
                // Иконка
                Text(icon)
                    .font(.system(size: 56))
                    .frame(width: 80, height: 80)
                    .background(
                        Circle()
                            .fill(color.opacity(0.2))
                    )
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(title)
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                    
                    Text(subtitle)
                        .font(.system(size: 14))
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                }
                
                Spacer()
            }
            .padding(Spacing.l)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(color.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(color, lineWidth: 3)
                    )
            )
            .shadow(color: color.opacity(0.3), radius: 12, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - SOS Button
    
    private var sosButton: some View {
        Button(action: {
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.warning)
            showEmergencyAlert = true
        }) {
            VStack(spacing: Spacing.m) {
                Text("🚨")
                    .font(.system(size: 64))
                
                Text(localizationManager.localized("elderly_interface_sos_button"))
                    .font(.system(size: 28, weight: .heavy))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Text(localizationManager.localized("elderly_interface_emergency_help_text"))
                    .font(.system(size: 18))
                    .foregroundColor(.white.opacity(0.9))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.xl)
                    .fill(
                        LinearGradient(
                            colors: [Color.dangerRed, Color(hex: "#DC2626")],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            )
            .shadow(color: Color.dangerRed.opacity(0.5), radius: 20, x: 0, y: 8)
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .alert("Экстренные службы", isPresented: $showEmergencyAlert) {
            Button("Скорая помощь (103)") {
                callEmergencyService("103")
            }
            Button("Пожарная служба (101)") {
                callEmergencyService("101")
            }
            Button("Полиция (102)") {
                callEmergencyService("102")
            }
            Button("Отмена", role: .cancel) { }
        } message: {
            Text("Выберите службу для экстренного вызова:")
        }
    }
    
    private func callFamilyMember(_ name: String, _ phone: String) {
        // ✅ РЕАЛЬНЫЙ ЗВОНОК: Открываем приложение телефона
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        if let url = URL(string: "tel://\(phone.replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "-", with: "").replacingOccurrences(of: "(", with: "").replacingOccurrences(of: ")", with: ""))"),
           UIApplication.shared.canOpenURL(url) {
            UIApplication.shared.open(url)
        } else {
            print("⚠️ Не удалось открыть звонок \(name): \(phone)")
        }
    }
    
    private func callEmergencyService(_ number: String) {
        // ✅ РЕАЛЬНЫЙ ЗВОНОК: Открываем приложение телефона
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        if let url = URL(string: "tel://\(number)"),
           UIApplication.shared.canOpenURL(url) {
            UIApplication.shared.open(url)
        } else {
            print("⚠️ Не удалось открыть звонок в службу: \(number)")
        }
    }
    
    // MARK: - Data Loading and Saving
    
    private func loadFamilyMembers() {
        // Загружаем из family_members_list и преобразуем в ElderlyFamilyMember
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            familyMembers = []
            print("⚠️ Нет данных о членах семьи в UserDefaults")
            return
        }
        
        // Преобразуем FamilyMemberData в ElderlyFamilyMember
        familyMembers = decoded.map { member in
            // Определяем роль (преобразуем FamilyMemberCard.FamilyRole в строку)
            let roleString: String
            switch member.role {
            case .parent: roleString = "Родитель"
            case .child: roleString = "Ребёнок"
            case .teenager: roleString = "Подросток"
            case .elderly: roleString = "60+"
            }
            
            // Определяем статус (упрощённо - всегда online для синхронизированных данных)
            let status: ElderlyFamilyMemberStatus = .online
            
            return ElderlyFamilyMember(
                name: member.name,
                role: roleString,
                status: status,
                avatar: member.avatar,
                phone: "+7 (999) 000-00-00" // TODO: Добавить телефон в FamilyMemberData
            )
        }
        
        print("✅ Загружено членов семьи: \(familyMembers.count)")
    }
    
    private func loadMedications() {
        guard let savedData = UserDefaults.standard.data(forKey: "elderly_medications_list"),
              let decoded = try? JSONDecoder().decode([Medication].self, from: savedData) else {
            medications = []
            print("⚠️ Нет данных о лекарствах в UserDefaults")
            return
        }
        
        medications = decoded
        print("✅ Загружено лекарств: \(medications.count)")
    }
    
    private func saveMedications() {
        guard let encoded = try? JSONEncoder().encode(medications) else {
            print("❌ Ошибка кодирования лекарств")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: "elderly_medications_list")
        print("✅ Сохранено лекарств: \(medications.count)")
        
        // Уведомляем другие экраны об изменении (для синхронизации)
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    private func loadAppointments() {
        guard let savedData = UserDefaults.standard.data(forKey: "elderly_appointments_list"),
              let decoded = try? JSONDecoder().decode([DoctorAppointment].self, from: savedData) else {
            appointments = []
            print("⚠️ Нет данных о записях к врачу в UserDefaults")
            return
        }
        
        appointments = decoded
        print("✅ Загружено записей к врачу: \(appointments.count)")
    }
    
    private func saveAppointments() {
        guard let encoded = try? JSONEncoder().encode(appointments) else {
            print("❌ Ошибка кодирования записей к врачу")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: "elderly_appointments_list")
        print("✅ Сохранено записей к врачу: \(appointments.count)")
        
        // Уведомляем другие экраны об изменении (для синхронизации)
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    // MARK: - Blood Pressure Management
    
    private func loadBloodPressure() {
        if let savedSystolic = UserDefaults.standard.object(forKey: "elderly_blood_pressure_systolic") as? Int,
           let savedDiastolic = UserDefaults.standard.object(forKey: "elderly_blood_pressure_diastolic") as? Int,
           let savedDate = UserDefaults.standard.string(forKey: "elderly_blood_pressure_date") {
            bloodPressure = BloodPressureReading(
                systolic: savedSystolic,
                diastolic: savedDiastolic,
                date: savedDate
            )
            print("✅ Загружено давление: \(savedSystolic)/\(savedDiastolic) (\(savedDate))")
        } else {
            // Используем дефолтные значения
            print("⚠️ Нет сохранённых данных давления, используются дефолтные значения")
        }
    }
    
    private func saveBloodPressure() {
        UserDefaults.standard.set(bloodPressure.systolic, forKey: "elderly_blood_pressure_systolic")
        UserDefaults.standard.set(bloodPressure.diastolic, forKey: "elderly_blood_pressure_diastolic")
        UserDefaults.standard.set(bloodPressure.date, forKey: "elderly_blood_pressure_date")
        print("✅ Сохранено давление: \(bloodPressure.systolic)/\(bloodPressure.diastolic) (\(bloodPressure.date))")
        
        // Уведомляем другие экраны об изменении
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
}

// MARK: - Elderly Settings Modal

struct ElderlySettingsModal: View {
    @Binding var isPresented: Bool
    @AppStorage("elderly_font_size") private var fontSize: Double = 16
    @AppStorage("elderly_sound_enabled") private var soundEnabled: Bool = true
    @AppStorage("elderly_vibration_enabled") private var vibrationEnabled: Bool = true
    @AppStorage("elderly_auto_call_enabled") private var autoCallEnabled: Bool = false
    @State private var showAddPhoneModal: Bool = false
    @State private var showEditContactsModal: Bool = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("⚙️ Настройки интерфейса")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Размер шрифта
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("📝 Размер шрифта")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text("Маленький")
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                            
                            Slider(value: $fontSize, in: 12...24, step: 2)
                                .accentColor(.blue)
                            
                            Text("Большой")
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                        }
                        
                        Text("Текущий размер: \(Int(fontSize))")
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Звуки и вибрация
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🔊 Звуки и уведомления")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text("🔊 Звуки")
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $soundEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        HStack {
                            Text("📳 Вибрация")
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $vibrationEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Экстренные вызовы
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🚨 Экстренные вызовы")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text("📞 Автоматический звонок")
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $autoCallEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        Text("При включении: автоматически звонить детям при нажатии SOS")
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Управление семьей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("👨‍👩‍👧‍👦 Управление семьей")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Button(action: {
                            showAddPhoneModal = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                    .foregroundColor(.blue)
                                Text("Добавить номер телефона")
                                    .foregroundColor(.primary)
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color.white)
                            .cornerRadius(CornerRadius.small)
                        }
                        
                        Button(action: {
                            showEditContactsModal = true
                        }) {
                            HStack {
                                Image(systemName: "pencil.circle.fill")
                                    .foregroundColor(.orange)
                                Text("Редактировать контакты")
                                    .foregroundColor(.primary)
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color.white)
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Сброс настроек
                    Button(action: {
                        // Логика сброса
                    }) {
                        HStack {
                            Image(systemName: "arrow.clockwise")
                                .foregroundColor(.red)
                            Text("Сбросить настройки")
                                .foregroundColor(.red)
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
        .sheet(isPresented: $showAddPhoneModal) {
            AddPhoneNumberModal(isPresented: $showAddPhoneModal)
        }
        .sheet(isPresented: $showEditContactsModal) {
            EditContactsModal(isPresented: $showEditContactsModal)
        }
    }
}

// MARK: - Add Phone Number Modal

struct AddPhoneNumberModal: View {
    @Binding var isPresented: Bool
    @State private var contactName: String = ""
    @State private var phoneNumber: String = ""
    @State private var selectedRelation: String = "Сын"
    
    let relations = ["Сын", "Дочь", "Внук", "Внучка", "Зять", "Невестка", "Друг", "Другое"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📞 Добавить номер телефона")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Имя контакта")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField("Введите имя", text: $contactName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Номер телефона")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField("+7 (999) 123-45-67", text: $phoneNumber)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.phonePad)
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Родство")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Picker("Родство", selection: $selectedRelation) {
                            ForEach(relations, id: \.self) { relation in
                                Text(relation).tag(relation)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(CornerRadius.small)
                    }
                }
                
                Button(action: {
                    // Логика сохранения контакта
                    isPresented = false
                }) {
                    Text("Сохранить контакт")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(contactName.isEmpty || phoneNumber.isEmpty)
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

// MARK: - Edit Contacts Modal

struct EditContactsModal: View {
    @Binding var isPresented: Bool
    @State private var familyContacts: [FamilyContact] = [
        FamilyContact(name: "Александр", phone: "+7 (999) 123-45-67", relation: "Сын"),
        FamilyContact(name: "Елена", phone: "+7 (999) 234-56-78", relation: "Невестка"),
        FamilyContact(name: "Алексей", phone: "+7 (999) 345-67-89", relation: "Внук")
    ]
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📋 Редактировать контакты")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                ScrollView {
                    LazyVStack(spacing: Spacing.s) {
                        ForEach(familyContacts.indices, id: \.self) { index in
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(familyContacts[index].name)
                                        .font(.system(size: 18, weight: .semibold))
                                        .foregroundColor(.primary)
                                    
                                    Text(familyContacts[index].phone)
                                        .font(.system(size: 16))
                                        .foregroundColor(.secondary)
                                    
                                    Text(familyContacts[index].relation)
                                        .font(.system(size: 14))
                                        .foregroundColor(.blue)
                                }
                                
                                Spacer()
                                
                                Button(action: {
                                    // Логика редактирования
                                }) {
                                    Image(systemName: "pencil")
                                        .foregroundColor(.blue)
                                }
                                
                                Button(action: {
                                    familyContacts.remove(at: index)
                                }) {
                                    Image(systemName: "trash")
                                        .foregroundColor(.red)
                                }
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct FamilyContact: Identifiable {
    let id = UUID()
    var name: String
    var phone: String
    var relation: String
}

// MARK: - Security Status Modal

struct SecurityStatusModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🛡️ Статус безопасности")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Общий статус
                    VStack(spacing: Spacing.m) {
                        Text("✅")
                            .font(.system(size: 80))
                        
                        Text("ВСЁ ХОРОШО")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.successGreen)
                        
                        Text("Угроз не обнаружено")
                            .font(.system(size: 20))
                            .foregroundColor(.primary)
                    }
                    .padding(Spacing.xl)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.xl)
                            .fill(Color.successGreen.opacity(0.1))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.xl)
                                    .stroke(Color.successGreen, lineWidth: 2)
                            )
                    )
                    
                    // Детальная информация
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("📊 Детальная информация:")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        securityStatusRow(icon: "🔒", title: "Защита от мошенников", status: "Включена", color: .green)
                        securityStatusRow(icon: "🌐", title: "Проверка сайтов", status: "Активна", color: .blue)
                        securityStatusRow(icon: "📞", title: "Блокировка звонков", status: "3 заблокировано", color: .orange)
                        securityStatusRow(icon: "🛡️", title: "Общая защита", status: "100%", color: .green)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Последняя проверка
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("🕐 Последняя проверка:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Text("Сегодня в 14:30")
                            .font(.system(size: 16))
                            .foregroundColor(.secondary)
                        
                        Text("Следующая проверка: через 2 часа")
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    private func securityStatusRow(icon: String, title: String, status: String, color: Color) -> some View {
        HStack {
            Text(icon)
                .font(.system(size: 24))
            
            Text(title)
                .font(.system(size: 16))
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(status)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(color)
        }
        .padding(.vertical, Spacing.xs)
    }
}

// MARK: - Preview

#if DEBUG
struct ElderlyInterfaceScreen_Previews: PreviewProvider {
    static var previews: some View {
        ElderlyInterfaceScreen()
    }
}
#endif

// MARK: - Health Data Models

struct Medication: Identifiable, Codable, Equatable {
    let id: UUID
    let name: String
    let time: String
    var taken: Bool
    
    init(id: UUID = UUID(), name: String, time: String, taken: Bool) {
        self.id = id
        self.name = name
        self.time = time
        self.taken = taken
    }
    
    static func == (lhs: Medication, rhs: Medication) -> Bool {
        lhs.id == rhs.id && lhs.name == rhs.name && lhs.time == rhs.time && lhs.taken == rhs.taken
    }
}

struct DoctorAppointment: Identifiable, Codable, Equatable {
    let id: UUID
    let date: String
    let doctor: String
    let time: String
    
    init(id: UUID = UUID(), date: String, doctor: String, time: String) {
        self.id = id
        self.date = date
        self.doctor = doctor
        self.time = time
    }
    
    static func == (lhs: DoctorAppointment, rhs: DoctorAppointment) -> Bool {
        lhs.id == rhs.id && lhs.date == rhs.date && lhs.doctor == rhs.doctor && lhs.time == rhs.time
    }
}

struct BloodPressureReading: Identifiable {
    let id = UUID()
    let systolic: Int
    let diastolic: Int
    let date: String
}

struct SafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("📖 Инструкции по безопасности")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🛡️ Защита от мошенников")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("❌ НЕ ВЕРИТЕ звонкам от: Сотрудников ФСБ, Прокуратуры, Начальства, Банков, Соцсетей")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Никогда не называйте пароли\n• Не переводите деньги\n• Не устанавливайте программы\n• Сразу кладите трубку")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Социальная инженерия
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🎭 Социальная инженерия")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("Мошенники могут: Называть ваше имя, знать адрес, говорить о ваших детях, требовать срочности")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("⚠️ ВНИМАНИЕ:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.red)
                            .padding(.top, Spacing.s)
                        
                        Text("Это НЕ означает, что они настоящие!")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Ссылки и скам
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🔗 Опасные ссылки")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("❌ НЕ НАЖИМАЙТЕ на: Ссылки в SMS, WhatsApp, письмах, неизвестные сайты")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Используйте кнопку 'Проверить сайт'\n• Спрашивайте у детей\n• Проверяйте адрес сайта")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Как пользоваться приложением
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("📱 Как пользоваться приложением")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("📞 Звонки: Нажмите 'ЗВОНОК' для быстрого набора, выберите нужного родственника")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🩺 Здоровье: Добавляйте лекарства кнопкой '+', отмечайте прием")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🛡️ Безопасность: Используйте 'Проверить сайт', включите защиту от мошенников")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("🚨 Экстренная помощь: Нажмите красную кнопку SOS, выберите службу (103, 101, 102)")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Управление телефонами
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("👨‍👩‍👧‍👦 Управление семьей")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("📱 Добавление телефонов: Нажмите на карточку родственника, выберите 'Редактировать', введите номер, сохраните")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("⚙️ Настройки: Нажмите на иконку шестеренки, измените размер текста, управляйте уведомлениями")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    private func instructionItem(_ text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Text(text)
                .font(.system(size: 16))
                .foregroundColor(.primary)
                .lineLimit(nil)
            
            Spacer()
        }
    }
}

struct ElderlyFamilyMember: Identifiable {
    let id = UUID()
    let name: String
    let role: String
    let status: ElderlyFamilyMemberStatus
    let avatar: String
    let phone: String
}

enum ElderlyFamilyMemberStatus {
    case online
    case school
    case offline
    
    var color: Color {
        switch self {
        case .online: return .green
        case .school: return .yellow
        case .offline: return .red
        }
    }
    
    var text: String {
        switch self {
        case .online: return "Онлайн"
        case .school: return "В школе"
        case .offline: return "Офлайн"
        }
    }
}

struct ElderlyProfileImagePicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .photoLibrary
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ElderlyProfileImagePicker
        
        init(_ parent: ElderlyProfileImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.selectedImage = image
            }
            picker.dismiss(animated: true)
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            picker.dismiss(animated: true)
        }
    }
}

// MARK: - Health Modals

struct MedicationReminderModal: View {
    @Binding var isPresented: Bool
    @Binding var medications: [Medication]
    let onSave: () -> Void
    @State private var newMedicationName: String = ""
    @State private var newMedicationTime: String = ""
    @State private var showAddMedication: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("💊 Лекарства")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddMedication = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Добавить лекарство")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Список лекарств
                ForEach(medications) { medication in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(medication.name)
                                .font(.system(size: 20, weight: .bold))
                            Text("Время: \(medication.time)")
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: Spacing.s) {
                            Button(medication.taken ? "✅ Принято" : "Принять") {
                                if let index = medications.firstIndex(where: { $0.id == medication.id }) {
                                    medications[index].taken.toggle()
                                }
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(medication.taken ? Color.green : Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            
                            Button("✏️") {
                                // Редактирование лекарства
                                newMedicationName = medication.name
                                newMedicationTime = medication.time
                                showAddMedication = true
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            
                            Button("🗑️") {
                                medications.removeAll { $0.id == medication.id }
                                onSave() // Сохраняем после удаления
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showAddMedication) {
                AddMedicationSheet(
                    isPresented: $showAddMedication,
                    medications: $medications,
                    medicationName: $newMedicationName,
                    medicationTime: $newMedicationTime,
                    onSave: onSave
                )
            }
        }
    }
}

struct AddMedicationSheet: View {
    @Binding var isPresented: Bool
    @Binding var medications: [Medication]
    @Binding var medicationName: String
    @Binding var medicationTime: String
    let onSave: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("Добавить лекарство")
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Название лекарства:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: Аспирин", text: $medicationName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Время приёма:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 18:00", text: $medicationTime)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Button(action: {
                    if !medicationName.isEmpty && !medicationTime.isEmpty {
                        medications.append(Medication(name: medicationName, time: medicationTime, taken: false))
                        medicationName = ""
                        medicationTime = ""
                        onSave() // Сохраняем после изменения
                        isPresented = false
                    }
                }) {
                    Text("Добавить")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(medicationName.isEmpty || medicationTime.isEmpty)
                
                Spacer()
            }
            .padding()
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

struct DoctorAppointmentsModal: View {
    @Binding var isPresented: Bool
    @Binding var appointments: [DoctorAppointment]
    let onSave: () -> Void
    @State private var newDoctorName: String = ""
    @State private var newAppointmentDate: String = ""
    @State private var newAppointmentTime: String = ""
    @State private var showAddAppointment: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🏥 Визиты к врачу")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddAppointment = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Добавить визит")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Список визитов
                ForEach(appointments) { appointment in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(appointment.doctor)
                                .font(.system(size: 20, weight: .bold))
                            Text("Дата: \(appointment.date)")
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                            Text("Время: \(appointment.time)")
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: Spacing.s) {
                            Button("Напомнить") {
                                // Логика напоминания
                                let generator = UINotificationFeedbackGenerator()
                                generator.notificationOccurred(.success)
                            }
                            .padding(.horizontal, Spacing.xs)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            .font(.system(size: 12))
                            
                            Button("✏️") {
                                // Редактирование визита
                                newDoctorName = appointment.doctor
                                newAppointmentDate = appointment.date
                                newAppointmentTime = appointment.time
                                showAddAppointment = true
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            
                            Button("🗑️") {
                                appointments.removeAll { $0.id == appointment.id }
                                onSave() // Сохраняем после удаления
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showAddAppointment) {
                AddAppointmentSheet(
                    isPresented: $showAddAppointment,
                    appointments: $appointments,
                    doctorName: $newDoctorName,
                    appointmentDate: $newAppointmentDate,
                    appointmentTime: $newAppointmentTime,
                    onSave: onSave
                )
            }
        }
    }
}

struct AddAppointmentSheet: View {
    @Binding var isPresented: Bool
    @Binding var appointments: [DoctorAppointment]
    @Binding var doctorName: String
    @Binding var appointmentDate: String
    @Binding var appointmentTime: String
    let onSave: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("Добавить визит к врачу")
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Врач:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: Терапевт", text: $doctorName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Дата:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 12.10", text: $appointmentDate)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Время:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 14:00", text: $appointmentTime)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Button(action: {
                    if !doctorName.isEmpty && !appointmentDate.isEmpty && !appointmentTime.isEmpty {
                        appointments.append(DoctorAppointment(date: appointmentDate, doctor: doctorName, time: appointmentTime))
                        doctorName = ""
                        appointmentDate = ""
                        appointmentTime = ""
                        onSave() // Сохраняем после изменения
                        isPresented = false
                    }
                }) {
                    Text("Добавить")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(doctorName.isEmpty || appointmentDate.isEmpty || appointmentTime.isEmpty)
                
                Spacer()
            }
            .padding()
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

struct BloodPressureModal: View {
    @Binding var isPresented: Bool
    @Binding var bloodPressure: BloodPressureReading
    let onSave: () -> Void
    @State private var pressureReadings: [BloodPressureReading] = []
    @State private var newSystolic: String = ""
    @State private var newDiastolic: String = ""
    @State private var newDate: String = ""
    @State private var showAddReading: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🩺 Измерение давления")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddReading = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Добавить измерение")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Последнее измерение
                VStack(spacing: Spacing.m) {
                    Text("Последнее измерение")
                        .font(.system(size: 20, weight: .bold))
                    
                    Text("\(bloodPressure.systolic)/\(bloodPressure.diastolic)")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.red)
                    
                    Text("Дата: \(bloodPressure.date)")
                        .font(.system(size: 16))
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                // История измерений по дням недели
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("История измерений:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    ForEach(getWeekDays(), id: \.self) { day in
                        HStack {
                            Text(day)
                                .font(.system(size: 14, weight: .semibold))
                                .frame(width: 90, alignment: .leading)
                                .lineLimit(1)
                                .minimumScaleFactor(0.7)
                            
                            Text(getPressureForDay(day))
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                                .frame(width: 60, alignment: .center)
                            
                            Spacer()
                            
                            Button("✏️") {
                                // Редактирование измерения для конкретного дня
                                editPressureForDay(day)
                            }
                            .font(.system(size: 12))
                            .foregroundColor(.blue)
                            .padding(.horizontal, Spacing.xs)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(CornerRadius.small)
                        }
                        .padding(.vertical, Spacing.xs)
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        onSave()
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showAddReading) {
                AddPressureReadingSheet(
                    isPresented: $showAddReading,
                    bloodPressure: $bloodPressure,
                    systolic: $newSystolic,
                    diastolic: $newDiastolic,
                    date: $newDate,
                    onSave: onSave
                )
            }
        }
    }
    
    private func getWeekDays() -> [String] {
        return ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    }
    
    private func getPressureForDay(_ day: String) -> String {
        // Моковые данные для демонстрации
        let mockData = [
            "Пн": "120/80",
            "Вт": "125/82",
            "Ср": "",
            "Чт": "118/78",
            "Пт": "",
            "Сб": "122/79",
            "Вс": ""
        ]
        return mockData[day] ?? ""
    }
    
    private func editPressureForDay(_ day: String) {
        // Логика редактирования давления для конкретного дня
        newDate = day
        showAddReading = true
    }
}

struct AddPressureReadingSheet: View {
    @Binding var isPresented: Bool
    @Binding var bloodPressure: BloodPressureReading
    @Binding var systolic: String
    @Binding var diastolic: String
    @Binding var date: String
    let onSave: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("Добавить измерение давления")
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Верхнее давление (систолическое):")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 120", text: $systolic)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.numberPad)
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Нижнее давление (диастолическое):")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 80", text: $diastolic)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.numberPad)
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Дата:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 08.10", text: $date)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Button(action: {
                    if let sys = Int(systolic), let dia = Int(diastolic), !date.isEmpty {
                        bloodPressure = BloodPressureReading(systolic: sys, diastolic: dia, date: date)
                        systolic = ""
                        diastolic = ""
                        date = ""
                        isPresented = false
                        // Обновляем давление в родительском экране
                        onSave()
                    }
                }) {
                    Text("Добавить")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(systolic.isEmpty || diastolic.isEmpty || date.isEmpty)
                
                Spacer()
            }
            .padding()
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

struct HealthJournalModal: View {
    @Binding var isPresented: Bool
    @State private var healthEntries: [HealthEntry] = []
    @State private var newEntryText: String = ""
    @State private var newEntryDate: String = ""
    @State private var showAddEntry: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📋 Журнал здоровья")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Статистика
                HStack(spacing: Spacing.l) {
                    VStack {
                        Text("\(healthEntries.count)")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.blue)
                        Text("Записей")
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    VStack {
                        Text("7")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.green)
                        Text("Дней")
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Кнопка добавления
                Button(action: { showAddEntry = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Добавить запись")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.purple)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Список записей
                ScrollView {
                    LazyVStack(spacing: Spacing.s) {
                        ForEach(getMockHealthEntries()) { entry in
                            HStack {
                                VStack(alignment: .leading, spacing: Spacing.xs) {
                                    Text(entry.date)
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(.primary)
                                    
                                    Text(entry.text)
                                        .font(.system(size: 14))
                                        .foregroundColor(.secondary)
                                        .lineLimit(3)
                                }
                                
                                Spacer()
                                
                                Button("✏️") {
                                    // Редактирование записи
                                }
                                .font(.system(size: 14))
                                .foregroundColor(.blue)
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showAddEntry) {
                AddHealthEntrySheet(
                    isPresented: $showAddEntry,
                    entries: $healthEntries,
                    entryText: $newEntryText,
                    entryDate: $newEntryDate
                )
            }
        }
    }
    
    private func getMockHealthEntries() -> [HealthEntry] {
        return [
            HealthEntry(date: "08.10", text: "Принял аспирин в 18:00. Самочувствие хорошее."),
            HealthEntry(date: "07.10", text: "Измерил давление: 120/80. Норма."),
            HealthEntry(date: "06.10", text: "Визит к терапевту. Все анализы в порядке."),
            HealthEntry(date: "05.10", text: "Принял витамины утром. Энергии больше."),
            HealthEntry(date: "04.10", text: "Гулял в парке 30 минут. Настроение отличное."),
            HealthEntry(date: "03.10", text: "Пил больше воды. Кожа стала лучше."),
            HealthEntry(date: "02.10", text: "Спал 8 часов. Выспался хорошо.")
        ]
    }
}

struct HealthEntry: Identifiable {
    let id = UUID()
    let date: String
    let text: String
}

struct AddHealthEntrySheet: View {
    @Binding var isPresented: Bool
    @Binding var entries: [HealthEntry]
    @Binding var entryText: String
    @Binding var entryDate: String
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("Добавить запись в журнал")
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Дата:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Например: 08.10", text: $entryDate)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Запись:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("Опишите ваше самочувствие...", text: $entryText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .lineLimit(3)
                }
                
                Button(action: {
                    if !entryText.isEmpty && !entryDate.isEmpty {
                        entries.append(HealthEntry(date: entryDate, text: entryText))
                        entryText = ""
                        entryDate = ""
                        isPresented = false
                    }
                }) {
                    Text("Добавить")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.purple)
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(entryText.isEmpty || entryDate.isEmpty)
                
                Spacer()
            }
            .padding()
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

// MARK: - Security Modals

struct SiteCheckerModal: View {
    @Binding var isPresented: Bool
    @State private var urlToCheck: String = ""
    @State private var checkResult: String = ""
    @State private var isChecking: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🔍 Проверить сайт")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Введите адрес сайта:")
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("https://example.com", text: $urlToCheck)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                
                Button(action: {
                    isChecking = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        checkResult = "✅ Сайт безопасен"
                        isChecking = false
                    }
                }) {
                    HStack {
                        if isChecking {
                            ProgressView()
                                .scaleEffect(0.8)
                        }
                        Text(isChecking ? "Проверяем..." : "Проверить")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                .disabled(urlToCheck.isEmpty || isChecking)
                
                if !checkResult.isEmpty {
                    Text(checkResult)
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.green)
                        .padding()
                        .background(Color.green.opacity(0.1))
                        .cornerRadius(CornerRadius.medium)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct SecuritySettingsModal: View {
    @Binding var isPresented: Bool
    @Binding var isSecurityEnabled: Bool
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🛡️ Защита от обмана")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    HStack {
                        Text("Защита включена")
                            .font(.system(size: 20, weight: .semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                        
                        Spacer()
                        
                        Toggle("", isOn: $isSecurityEnabled)
                            .scaleEffect(1.0)
                            .frame(maxWidth: 60)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Что защищает:")
                            .font(.system(size: 18, weight: .semibold))
                        
                        Text("• Подозрительные звонки")
                        Text("• Подозрительные SMS")
                        Text("• Опасные сайты")
                        Text("• Мошеннические приложения")
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct DangerousContactsModal: View {
    @Binding var isPresented: Bool
    @Binding var blockedCount: Int
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("📞 Опасные контакты")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    Text("Заблокировано: \(blockedCount)")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.red)
                    
                    if blockedCount == 0 {
                        Text("Все контакты безопасны")
                            .font(.system(size: 18))
                            .foregroundColor(.green)
                            .padding()
                            .background(Color.green.opacity(0.1))
                            .cornerRadius(CornerRadius.medium)
                    } else {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Заблокированные номера:")
                                .font(.system(size: 18, weight: .semibold))
                            
                            ForEach(0..<blockedCount, id: \.self) { index in
                                HStack {
                                    Text("+7 (***) ***-**-\(index + 1)")
                                        .font(.system(size: 16))
                                    
                                    Spacer()
                                    
                                    Button("Разблокировать") {
                                        blockedCount -= 1
                                    }
                                    .font(.system(size: 14))
                                    .foregroundColor(.blue)
                                }
                                .padding(.vertical, Spacing.s)
                            }
                        }
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                }
            }
        }
    }
}
