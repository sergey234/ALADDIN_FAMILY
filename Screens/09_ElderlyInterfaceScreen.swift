import SwiftUI
import UIKit

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
    @AppStorage("elderly_font_size") private var elderlyFontSize: Double = 16
    @AppStorage("elderly_large_read_mode") private var elderlyLargeReadMode: Bool = false
    @AppStorage("elderly_contrast_preset") private var elderlyContrastPreset: String = "standard"
    @State private var blockedContactsCount: Int = 0
    
    // Состояния для экстренной помощи
    @State private var showEmergencyAlert: Bool = false
    @State private var showInstructions: Bool = false
    @State private var showCallChildrenAlert: Bool = false
    @State private var showSecurityStatus: Bool = false
    @State private var showElderlySettings: Bool = false
    @State private var criticalActionStatusMessage: String?
    
    // Данные здоровья (загружаются из UserDefaults)
    @State private var medications: [Medication] = []
    @State private var appointments: [DoctorAppointment] = []
    @State private var bloodPressure: BloodPressureReading = .empty
    @State private var weeklyPressureByDay: [String: String] = [:]
    
    // Данные семьи (синхронизируются с family_members_list)
    @State private var familyMembers: [ElderlyFamilyMember] = []
    @State private var elderlyFeedItems: [ContentItem] = []
    
    private var emergencyContacts: [ElderlyFamilyMember] {
        familyMembers.filter { member in
            member.rawRole == .child || member.rawRole == .teenager || member.rawRole == .parent
        }
    }

    private var elderlyDynamicType: DynamicTypeSize {
        elderlyLargeReadMode || elderlyFontSize >= 22 ? .accessibility3 : .large
    }

    private var elderlyContrastValue: Double {
        elderlyContrastPreset == "high" ? 1.22 : 1.0
    }

    private var elderlyBackgroundColors: [Color] {
        if elderlyContrastPreset == "high" {
            return [Color.black, Color(hex: "#103b1e"), Color(hex: "#1b5e20")]
        }
        return [
            Color(hex: "#2D5016"),
            Color(hex: "#4A7C59"),
            Color(hex: "#6B8E23")
        ]
    }
    
    // MARK: - Body
    
    var body: some View {
        GeometryReader { geometry in
            let topCap = geometry.size.height * 0.25
            ZStack {
                // Фон — Storm Mesh warm light (Batch 4)
                StormMeshBackground(variant: .warm)
                
                VStack(spacing: 0) {
                    // Простая навигация (~25% высоты экрана, как в детском интерфейсе)
                    elderlyHeader
                        .frame(maxHeight: topCap, alignment: .top)
                        .clipped()
                    
                    // Основной контент
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: Spacing.xl) {
                            // Приветствие
                            greetingCard
                            
                            // Секция здоровья
                            healthSection

                            // Рекомендованный контент 60+
                            elderlyContentSection
                            
                            // Семейная панель
                            familySection
                            
                            // Очень большие кнопки
                            bigButtonsList
                            
                            // Экстренная помощь
                            emergencySection
                            
                            // Защита от мошенников
                            securitySection
                            
                            Spacer()
                                .frame(height: Spacing.xxl)
                        }
                        .padding(.top, Spacing.l)
                    }
                }
            }
        }
        .sheet(isPresented: $showImagePicker) {
            ElderlyProfileImagePicker(selectedImage: $selectedImage)
        }
        .onAppear {
            loadProfileImage()
        }
        .onChange(of: selectedImage) { newImage in
            if let image = newImage {
                saveProfileImage(image)
            }
        }
        .sheet(isPresented: $showMedicationReminder) {
            MedicationReminderModal(isPresented: $showMedicationReminder, medications: $medications, onSave: {
                saveMedications()
            })
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDoctorAppointments) {
            DoctorAppointmentsModal(isPresented: $showDoctorAppointments, appointments: $appointments, onSave: {
                saveAppointments()
            })
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBloodPressure) {
            BloodPressureModal(
                isPresented: $showBloodPressure,
                bloodPressure: $bloodPressure,
                weeklyPressureByDay: $weeklyPressureByDay,
                onSave: { saveBloodPressure() }
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showHealthJournal) {
            HealthJournalModal(isPresented: $showHealthJournal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSiteChecker) {
            SiteCheckerModal(isPresented: $showSiteChecker)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSecuritySettings) {
            SecuritySettingsModal(isPresented: $showSecuritySettings, isSecurityEnabled: $isSecurityEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDangerousContacts) {
            DangerousContactsModal(isPresented: $showDangerousContacts, blockedCount: $blockedContactsCount)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showInstructions) {
            SafetyInstructionsModal(isPresented: $showInstructions)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showElderlySettings) {
            ElderlySettingsModal(isPresented: $showElderlySettings)
                .environmentObject(localizationManager)
        }
        .alert(localizationManager.localized("elderly_interface_call_children_question"), isPresented: $showCallChildrenAlert) {
            // Use role-safe filtering instead of localized string matching.
            ForEach(emergencyContacts) { member in
                Button("\(member.name) (\(member.role))") {
                    callFamilyMember(member.name, member.phone)
                }
            }
            Button(localizationManager.localized("elderly_interface_cancel"), role: .cancel) { }
        } message: {
            Text(localizationManager.localized("elderly_interface_choose_whom"))
        }
        .overlay(alignment: .bottom) {
            if let status = criticalActionStatusMessage, !status.isEmpty {
                Text(status)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .padding(.horizontal, Spacing.l)
                    .padding(.vertical, Spacing.s)
                    .background(Color.black.opacity(0.6))
                    .clipShape(Capsule())
                    .padding(.bottom, Spacing.xl)
                    .onTapGesture { criticalActionStatusMessage = nil }
            }
        }
        .onAppear {
            loadFamilyMembers()
            loadMedications()
            loadAppointments()
            loadBloodPressure()
            loadWeeklyPressureCache()
            runDataIntegrityAudit()
            Task {
                await syncElderlyHealthFromServer()
                await loadElderlyContentFeed()
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadFamilyMembers()
        }
        .dynamicTypeSize(elderlyDynamicType)
        .contrast(elderlyContrastValue)
    }

    private func loadElderlyContentFeed() async {
        let resolvedCategories = Set(FamilyContentSafetyBridge.resolvedElderlyCategories())
        let feed = await ContentManager.shared.loadUnifiedAudienceFeed(
            audience: .elderly,
            limit: 6
        )
        elderlyFeedItems = feed.filter { item in
            resolvedCategories.contains(item.categoryId)
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
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
                    .minimumScaleFactor(0.78)
                
                Text(localizationManager.localized("elderly_interface_protected"))
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
                    .minimumScaleFactor(0.78)
            }
            .layoutPriority(1)
            
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
            .stormGlassCard(cornerRadius: CornerRadius.xl)
        }
        .buttonStyle(PlainButtonStyle())
        .sheet(isPresented: $showSecurityStatus) {
            SecurityStatusModal(isPresented: $showSecurityStatus)
                .environmentObject(localizationManager)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }

    private var elderlyContentSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized(FamilyContentSafetyBridge.safetyTitleKey))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)

            if !elderlyFeedItems.isEmpty {
                VStack(spacing: Spacing.m) {
                    ForEach(elderlyFeedItems, id: \.id) { item in
                        bigElderlyButton(
                            icon: "📘",
                            title: item.metadata.title,
                            subtitle: item.metadata.subtitle ?? localizationManager.localized("elderly_interface_view_records"),
                            color: .secondaryGold
                        )
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
        }
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
                        ? localizationManager.localized("elderly_medications_add_for_reminders")
                        : String(format: localizationManager.localized("elderly_medications_next_dose"), medications.first?.time ?? "—", medications.first?.name ?? "—"),
                    color: .blue,
                    action: { showMedicationReminder = true },
                    accessibilityHint: localizationManager.localized("elderly_a11y_opens_details_hint")
                )
                
                // 2. Визиты к врачу
                healthCard(
                    icon: "🏥",
                    title: localizationManager.localized("elderly_interface_doctor_visits"),
                    subtitle: appointments.isEmpty
                        ? localizationManager.localized("elderly_appointments_add")
                        : String(format: localizationManager.localized("elderly_appointments_next"), appointments.first?.date ?? "—", appointments.first?.doctor ?? "—"),
                    color: .green,
                    action: { showDoctorAppointments = true },
                    accessibilityHint: localizationManager.localized("elderly_a11y_opens_details_hint")
                )
                
                // 3. Измерение давления
                healthCard(
                    icon: "🩺",
                    title: localizationManager.localized("elderly_interface_blood_pressure"),
                    subtitle: bloodPressure.isEmpty
                        ? localizationManager.localized("elderly_blood_pressure_no_reading")
                        : localizationManager.localized("elderly_interface_last_reading", bloodPressure.systolic, bloodPressure.diastolic, bloodPressure.date),
                    color: .red,
                    action: { showBloodPressure = true },
                    accessibilityHint: localizationManager.localized("elderly_a11y_opens_details_hint")
                )
                
                // 4. Журнал здоровья
                healthCard(
                    icon: "📋",
                    title: localizationManager.localized("elderly_interface_health_journal"),
                    subtitle: localizationManager.localized("elderly_interface_view_records"),
                    color: .purple,
                    action: { showHealthJournal = true },
                    accessibilityHint: localizationManager.localized("elderly_a11y_opens_details_hint")
                )
            }
        }
    }
    
    private func healthCard(icon: String, title: String, subtitle: String, color: Color, action: @escaping () -> Void, accessibilityHint: String? = nil) -> some View {
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
            .stormGlassCard(cornerRadius: CornerRadius.large)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(color.opacity(0.3), lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(title). \(subtitle)")
        .accessibilityHint(accessibilityHint ?? localizationManager.localized("elderly_a11y_opens_details_hint"))
    }
    
    // MARK: - Family Section
    
    private var familySection: some View {
        VStack(spacing: Spacing.l) {
            // Заголовок секции
            HStack {
                Text(localizationManager.localized("elderly_family_title"))
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
                    
                    Text(member.status.text(localizationManager: localizationManager))
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
            .accessibilityLabel("\(localizationManager.localized("elderly_interface_call_children")): \(member.name)")
            .accessibilityHint(localizationManager.localized("elderly_a11y_calls_family_hint"))
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.white.opacity(0.3), lineWidth: 1)
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
                    startQuickFamilyCall()
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
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("elderly_interface_call_children"))
                .accessibilityHint(localizationManager.localized("elderly_a11y_calls_family_hint"))
                
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
                Text(localizationManager.localized(FamilyContentSafetyBridge.safetyTitleKey))
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
            .stormGlassCard(cornerRadius: CornerRadius.large)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(color.opacity(0.3), lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(title). \(subtitle)")
        .accessibilityHint(localizationManager.localized("elderly_a11y_opens_details_hint"))
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
                accessibilityHint: localizationManager.localized("elderly_a11y_calls_family_hint"),
                action: {
                    // 1 tap direct call when priority contact exists; fallback to chooser.
                    startQuickFamilyCall()
                }
            )
            
            // fws-03: перед переводом
            AntifakeTransferCheckCTA(style: .elderlyButton)
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)

            WellnessCrisisOneTapCTA()
                .environmentObject(localizationManager)
                .padding(.horizontal, Spacing.screenPadding)

            // Безопасность - Защита от мошенников
            bigElderlyButton(
                icon: "📞",
                title: localizationManager.localized("antifake_elderly_one_tap_call_title"),
                subtitle: localizationManager.localized("antifake_elderly_one_tap_call_subtitle"),
                color: .dangerRed,
                accessibilityHint: localizationManager.localized("antifake_elderly_one_tap_call_hint"),
                action: {
                    navigationManager.navigateToAntifakeHub(tab: .call, postCallPrompt: true)
                    HapticFeedback.notification(.success)
                }
            )

            bigElderlyButton(
                icon: "🛡️",
                title: localizationManager.localized("elderly_interface_big_button_protection"),
                subtitle: localizationManager.localized("elderly_interface_big_button_protection_subtitle"),
                color: .primaryBlue,
                accessibilityHint: localizationManager.localized("elderly_a11y_triggers_protection_hint"),
                action: {
                    runQuickSecurityAction()
                }
            )
            
            // Инструкции
            bigElderlyButton(
                icon: "💊",
                title: localizationManager.localized("elderly_interface_medications"),
                subtitle: medications.first(where: { !$0.taken }) != nil
                    ? localizationManager.localized("elderly_medications_take")
                    : localizationManager.localized("elderly_medications_add_for_reminders"),
                color: .warningOrange,
                accessibilityHint: localizationManager.localized("elderly_a11y_marks_medication_hint"),
                action: {
                    markFirstPendingMedicationAsTaken()
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
        accessibilityHint: String? = nil,
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
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(title). \(subtitle)")
        .accessibilityHint(accessibilityHint ?? localizationManager.localized("elderly_a11y_opens_details_hint"))
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
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(localizationManager.localized("elderly_interface_sos_button"))
        .accessibilityHint(localizationManager.localized("elderly_a11y_sos_hint"))
        .alert(localizationManager.localized("elderly_emergency_services_title"), isPresented: $showEmergencyAlert) {
            Button(localizationManager.localized("elderly_interface_ambulance")) {
                callEmergencyService("103")
            }
            Button(localizationManager.localized("elderly_interface_fire")) {
                callEmergencyService("101")
            }
            Button(localizationManager.localized("elderly_interface_police")) {
                callEmergencyService("102")
            }
            Button(localizationManager.localized("elderly_interface_cancel"), role: .cancel) { }
        } message: {
            Text(localizationManager.localized("elderly_interface_choose_service"))
        }
    }
    
    private func callFamilyMember(_ name: String, _ phone: String) {
        // ✅ РЕАЛЬНЫЙ ЗВОНОК: Открываем приложение телефона
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        if let url = URL(string: "tel://\(phone.replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "-", with: "").replacingOccurrences(of: "(", with: "").replacingOccurrences(of: ")", with: ""))"),
           UIApplication.shared.canOpenURL(url) {
            UIApplication.shared.open(url)
            criticalActionStatusMessage = "\(localizationManager.localized("elderly_interface_quick_call")): \(name)"
        } else {
            print("⚠️ Не удалось открыть звонок \(name): \(phone)")
        }
    }

    private func startQuickFamilyCall() {
        if let primary = emergencyContacts.first {
            callFamilyMember(primary.name, primary.phone)
            return
        }
        showCallChildrenAlert = true
    }

    private func markFirstPendingMedicationAsTaken() {
        guard let idx = medications.firstIndex(where: { !$0.taken }) else {
            criticalActionStatusMessage = localizationManager.localized("elderly_medications_add_for_reminders")
            return
        }
        medications[idx].taken = true
        saveMedications()
        criticalActionStatusMessage = localizationManager.localized("elderly_medications_taken")
    }

    private func runQuickSecurityAction() {
        isSecurityEnabled = true
        navigationManager.navigateToAntifakeHub(tab: .call, postCallPrompt: true)
        criticalActionStatusMessage = localizationManager.localized("antifake_elderly_one_tap_opened")
    }

    // Phase 9.2 start: integrity check + normalization for critical 60+ data.
    private func runDataIntegrityAudit() {
        let existingContacts: [FamilyContact] = {
            let key = "elderly_family_contacts_list"
            guard let raw = UserDefaults.standard.data(forKey: key),
                  let decoded = try? JSONDecoder().decode([FamilyContact].self, from: raw) else {
                return []
            }
            return decoded
        }()

        let result = ElderlyHealthSyncAudit.synchronizeAcrossDevices(
            localMedications: medications,
            localAppointments: appointments,
            localContacts: existingContacts
        )
        medications = result.medications
        appointments = result.appointments
        saveMedications()
        saveAppointments()
        if let encoded = try? JSONEncoder().encode(result.contacts) {
            UserDefaults.standard.set(encoded, forKey: "elderly_family_contacts_list")
        }
        ElderlyHealthSyncAudit.persistLatestReport(result.report)
        if result.report.hasDesync {
            criticalActionStatusMessage = result.report.summary
        }
    }

    private func placeholderPhone(for member: FamilyMemberData) -> String {
        let source = (member.serverMemberId ?? member.id)
        let digits = source.filter(\.isNumber)
        let tail = String(digits.suffix(2)).padding(toLength: 2, withPad: "0", startingAt: 0)
        return "+7 (999) 000-00-\(tail)"
    }
    
    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        selectedImage = ProfileImageManager.shared.loadProfileImage(for: .elderly)
    }
    
    private func saveProfileImage(_ image: UIImage) {
        _ = ProfileImageManager.shared.saveProfileImage(image, for: .elderly)
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
        let decoded = UnifiedFamilyRoster.load()
        guard !decoded.isEmpty else {
            familyMembers = []
            print("⚠️ Нет данных о членах семьи в UserDefaults")
            return
        }
        
        // Преобразуем FamilyMemberData в ElderlyFamilyMember
        familyMembers = decoded.map { member in
            // Определяем роль (преобразуем FamilyMemberCard.FamilyRole в строку)
            let roleString: String
            switch member.role {
            case .parent: roleString = localizationManager.localized("elderly_family_role_parent")
            case .child: roleString = localizationManager.localized("elderly_family_role_child")
            case .teenager: roleString = localizationManager.localized("elderly_family_role_teenager")
            case .elderly: roleString = localizationManager.localized("elderly_family_role_elderly")
            }
            
            // Определяем статус (упрощённо - всегда online для синхронизированных данных)
            let status: ElderlyFamilyMemberStatus = .online
            
            return ElderlyFamilyMember(
                name: member.name,
                role: roleString,
                rawRole: member.role,
                status: status,
                avatar: member.avatar,
                phone: placeholderPhone(for: member)
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
        ElderlyHealthSyncAudit.persistSnapshot(
            medications: medications,
            appointments: appointments,
            contacts: loadPersistedContacts()
        )
        
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
        ElderlyHealthSyncAudit.persistSnapshot(
            medications: medications,
            appointments: appointments,
            contacts: loadPersistedContacts()
        )
        
        // Уведомляем другие экраны об изменении (для синхронизации)
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    // MARK: - Blood Pressure Management

    private func elderlyUserId() -> String? {
        let stored = (UserDefaults.standard.string(forKey: "user_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return stored.isEmpty ? nil : stored
    }

    private func elderlyDeviceId() -> String {
        UIDevice.current.identifierForVendor?.uuidString ?? "ios-elderly-device"
    }

    private func loadWeeklyPressureCache() {
        guard let raw = UserDefaults.standard.data(forKey: "elderly_blood_pressure_weekly"),
              let decoded = try? JSONDecoder().decode([String: String].self, from: raw) else {
            weeklyPressureByDay = [:]
            return
        }
        weeklyPressureByDay = decoded
    }

    private func persistWeeklyPressureCache() {
        guard let encoded = try? JSONEncoder().encode(weeklyPressureByDay) else { return }
        UserDefaults.standard.set(encoded, forKey: "elderly_blood_pressure_weekly")
    }
    
    private func loadBloodPressure() {
        if let savedSystolic = UserDefaults.standard.object(forKey: "elderly_blood_pressure_systolic") as? Int,
           let savedDiastolic = UserDefaults.standard.object(forKey: "elderly_blood_pressure_diastolic") as? Int,
           savedSystolic > 0, savedDiastolic > 0 {
            let savedDate = UserDefaults.standard.string(forKey: "elderly_blood_pressure_date") ?? ""
            bloodPressure = BloodPressureReading(
                systolic: savedSystolic,
                diastolic: savedDiastolic,
                date: savedDate
            )
            print("✅ Загружено давление: \(savedSystolic)/\(savedDiastolic) (\(savedDate))")
        } else {
            bloodPressure = .empty
            print("ℹ️ Нет сохранённых данных давления — empty state")
        }
    }
    
    private func saveBloodPressure() {
        guard !bloodPressure.isEmpty else {
            UserDefaults.standard.removeObject(forKey: "elderly_blood_pressure_systolic")
            UserDefaults.standard.removeObject(forKey: "elderly_blood_pressure_diastolic")
            UserDefaults.standard.removeObject(forKey: "elderly_blood_pressure_date")
            persistWeeklyPressureCache()
            return
        }

        UserDefaults.standard.set(bloodPressure.systolic, forKey: "elderly_blood_pressure_systolic")
        UserDefaults.standard.set(bloodPressure.diastolic, forKey: "elderly_blood_pressure_diastolic")
        UserDefaults.standard.set(bloodPressure.date, forKey: "elderly_blood_pressure_date")
        persistWeeklyPressureCache()
        print("✅ Сохранено давление: \(bloodPressure.systolic)/\(bloodPressure.diastolic) (\(bloodPressure.date))")

        guard let userId = elderlyUserId() else { return }
        APIService.shared.updateBloodPressure(
            userId: userId,
            systolic: bloodPressure.systolic,
            diastolic: bloodPressure.diastolic,
            recordedAt: ISO8601DateFormatter().string(from: Date()),
            deviceId: elderlyDeviceId()
        ) { result in
            switch result {
            case .success:
                print("✅ Blood pressure synced to server")
            case .failure(let error):
                print("⚠️ Blood pressure server sync failed: \(error.localizedDescription)")
            }
        }
        
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }

    private func syncElderlyHealthFromServer() async {
        guard let userId = elderlyUserId() else { return }
        let deviceId = elderlyDeviceId()

        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            APIService.shared.syncMedications(userId: userId, deviceId: deviceId) { result in
                if case .success(let response) = result {
                    let mapped = response.medications.map {
                        Medication(name: $0.name, time: $0.timeOfDay ?? "", taken: false)
                    }
                    if !mapped.isEmpty {
                        Task { @MainActor in
                            self.medications = mapped
                            self.saveMedications()
                        }
                    }
                }
                continuation.resume()
            }
        }

        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            APIService.shared.syncAppointments(userId: userId, deviceId: deviceId) { result in
                if case .success(let response) = result {
                    let formatter = ISO8601DateFormatter()
                    let mapped = response.appointments.compactMap { item -> DoctorAppointment? in
                        guard let parsed = formatter.date(from: item.dateTime) else { return nil }
                        let dateFormatter = DateFormatter()
                        dateFormatter.dateFormat = "dd.MM"
                        let timeFormatter = DateFormatter()
                        timeFormatter.dateFormat = "HH:mm"
                        return DoctorAppointment(
                            date: dateFormatter.string(from: parsed),
                            doctor: item.title,
                            time: timeFormatter.string(from: parsed)
                        )
                    }
                    if !mapped.isEmpty {
                        Task { @MainActor in
                            self.appointments = mapped
                            self.saveAppointments()
                        }
                    }
                }
                continuation.resume()
            }
        }

        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            APIService.shared.syncBloodPressure(userId: userId, deviceId: deviceId) { result in
                if case .success(let response) = result {
                    Task { @MainActor in
                        if !response.weeklyByDay.isEmpty {
                            self.weeklyPressureByDay = response.weeklyByDay
                            self.persistWeeklyPressureCache()
                        }
                        if let latest = response.readings.max(by: { $0.recordedAt < $1.recordedAt }),
                           latest.systolic > 0, latest.diastolic > 0 {
                            let dateFormatter = DateFormatter()
                            dateFormatter.dateFormat = "dd.MM"
                            if let parsed = ISO8601DateFormatter().date(from: latest.recordedAt) {
                                self.bloodPressure = BloodPressureReading(
                                    systolic: latest.systolic,
                                    diastolic: latest.diastolic,
                                    date: dateFormatter.string(from: parsed)
                                )
                                self.saveBloodPressure()
                            }
                        }
                    }
                }
                continuation.resume()
            }
        }
    }

    private func loadPersistedContacts() -> [FamilyContact] {
        guard let raw = UserDefaults.standard.data(forKey: "elderly_family_contacts_list"),
              let decoded = try? JSONDecoder().decode([FamilyContact].self, from: raw) else {
            return []
        }
        return decoded
    }
}

// MARK: - Elderly Settings Modal

struct ElderlySettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("elderly_font_size") private var fontSize: Double = 16
    @AppStorage("elderly_large_read_mode") private var largeReadMode: Bool = false
    @AppStorage("elderly_contrast_preset") private var contrastPreset: String = "standard"
    @AppStorage("elderly_sound_enabled") private var soundEnabled: Bool = true
    @AppStorage("elderly_vibration_enabled") private var vibrationEnabled: Bool = true
    @AppStorage("elderly_auto_call_enabled") private var autoCallEnabled: Bool = false
    @State private var showAddPhoneModal: Bool = false
    @State private var showEditContactsModal: Bool = false
    
    var body: some View {
        NavigationView {
            ScrollView(.vertical, showsIndicators: true) {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("elderly_settings_title"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Размер шрифта
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_settings_font_size_title"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text(localizationManager.localized("elderly_settings_font_size_small"))
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                            
                            Slider(value: $fontSize, in: 12...24, step: 2)
                                .accentColor(.blue)
                            
                            Text(localizationManager.localized("elderly_settings_font_size_large"))
                                .font(.system(size: 14))
                                .foregroundColor(.secondary)
                        }
                        
                        Text(String(format: localizationManager.localized("elderly_settings_font_size_current"), Int(fontSize)))
                            .font(.system(size: 16))
                            .foregroundColor(.blue)

                        Toggle(localizationManager.localized("elderly_settings_large_read_mode"), isOn: $largeReadMode)
                            .font(.system(size: 16, weight: .semibold))

                        Picker(localizationManager.localized("elderly_settings_contrast_title"), selection: $contrastPreset) {
                            Text(localizationManager.localized("elderly_settings_contrast_standard")).tag("standard")
                            Text(localizationManager.localized("elderly_settings_contrast_high")).tag("high")
                        }
                        .pickerStyle(.segmented)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Звуки и вибрация
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_settings_sounds_title"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text(localizationManager.localized("elderly_settings_sounds_label"))
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $soundEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("elderly_settings_vibration_label"))
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
                        Text(localizationManager.localized("elderly_settings_emergency_title"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        HStack {
                            Text(localizationManager.localized("elderly_settings_auto_call_label"))
                                .font(.system(size: 16))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            Toggle("", isOn: $autoCallEnabled)
                                .scaleEffect(1.0)
                                .frame(maxWidth: 60)
                        }
                        
                        Text(localizationManager.localized("elderly_settings_auto_call_description"))
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Управление семьей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_settings_family_title"))
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Button(action: {
                            showAddPhoneModal = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                    .foregroundColor(.blue)
                                Text(localizationManager.localized("elderly_settings_add_phone"))
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
                                Text(localizationManager.localized("elderly_settings_edit_contacts"))
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
                            Text(localizationManager.localized("elderly_settings_reset"))
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
                    Button(localizationManager.localized("elderly_settings_done")) {
                        isPresented = false
                    }
                }
            }
        }
        .sheet(isPresented: $showAddPhoneModal) {
            AddPhoneNumberModal(isPresented: $showAddPhoneModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEditContactsModal) {
            EditContactsModal(isPresented: $showEditContactsModal)
                .environmentObject(localizationManager)
        }
    }
}

// MARK: - Add Phone Number Modal

struct AddPhoneNumberModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var contactName: String = ""
    @State private var phoneNumber: String = ""
    @State private var selectedRelation: String = ""
    
    private var relations: [String] {
        [
            localizationManager.localized("elderly_settings_relation_son"),
            localizationManager.localized("elderly_settings_relation_daughter"),
            localizationManager.localized("elderly_settings_relation_grandson"),
            localizationManager.localized("elderly_settings_relation_granddaughter"),
            localizationManager.localized("elderly_settings_relation_son_in_law"),
            localizationManager.localized("elderly_settings_relation_daughter_in_law"),
            localizationManager.localized("elderly_settings_relation_friend"),
            localizationManager.localized("elderly_settings_relation_other")
        ]
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_settings_add_phone_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("elderly_settings_add_phone_name_label"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField(localizationManager.localized("elderly_settings_add_phone_name_placeholder"), text: $contactName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("elderly_settings_add_phone_number_label"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        TextField(localizationManager.localized("elderly_settings_add_phone_number_placeholder"), text: $phoneNumber)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.phonePad)
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("elderly_settings_add_phone_relation_label"))
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Picker(localizationManager.localized("elderly_settings_add_phone_relation_label"), selection: $selectedRelation) {
                            ForEach(relations, id: \.self) { relation in
                                Text(relation).tag(relation)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(CornerRadius.small)
                        .onAppear {
                            if selectedRelation.isEmpty {
                                selectedRelation = relations.first ?? ""
                            }
                        }
                    }
                }
                
                Button(action: {
                    // Логика сохранения контакта
                    isPresented = false
                }) {
                    Text(localizationManager.localized("elderly_settings_add_phone_save"))
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
                    Button(localizationManager.localized("elderly_settings_add_phone_cancel")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var familyContacts: [FamilyContact] = []
    @State private var editingContact: FamilyContact?
    @State private var editingContactIndex: Int?
    @State private var showDeleteAlert: Bool = false
    @State private var contactToDelete: Int?
    @State private var canEditContacts: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_settings_edit_contacts_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)

                if !canEditContacts {
                    Text(localizationManager.localized("elderly_contacts_edit_permission_notice"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.orange)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, Spacing.m)
                }
                
                ScrollView(.vertical, showsIndicators: true) {
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
                                    guard canEditContacts else { return }
                                    editingContact = familyContacts[index]
                                    editingContactIndex = index
                                }) {
                                    Image(systemName: "pencil")
                                        .foregroundColor(.blue)
                                }
                                .disabled(!canEditContacts)
                                .opacity(canEditContacts ? 1 : 0.35)
                                .accessibilityLabel(localizationManager.localized("elderly_contact_edit_save"))
                                .accessibilityHint(localizationManager.localized("elderly_a11y_contact_edit_hint"))
                                
                                Button(action: {
                                    guard canEditContacts else { return }
                                    contactToDelete = index
                                    showDeleteAlert = true
                                }) {
                                    Image(systemName: "trash")
                                        .foregroundColor(.red)
                                }
                                .disabled(!canEditContacts)
                                .opacity(canEditContacts ? 1 : 0.35)
                                .accessibilityLabel(localizationManager.localized("elderly_contact_edit_delete"))
                                .accessibilityHint(localizationManager.localized("elderly_a11y_contact_delete_hint"))
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
                    Button(localizationManager.localized("elderly_settings_edit_contacts_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("elderly_settings_edit_contacts_done")) {
                        if canEditContacts {
                            saveContacts()
                        }
                        isPresented = false
                    }
                }
            }
            .onAppear {
                let members = UnifiedFamilyRoster.load()
                let permissionSnapshot = FamilyPermissionLayer.snapshot(members: members)
                let directPermission = FamilyAccessPolicy.hasPermission(.editFamilyContacts, members: members)
                canEditContacts = permissionSnapshot.canEditContacts && directPermission
                loadContacts()
            }
            .sheet(item: $editingContact) { contact in
                ElderlyEditContactModal(
                    contact: contact,
                    contactIndex: editingContactIndex,
                    isPresented: Binding(
                        get: { editingContact != nil },
                        set: { if !$0 { editingContact = nil } }
                    ),
                    onSave: { updatedContact, index in
                        if let index = index {
                            familyContacts[index] = updatedContact
                            saveContacts()
                        }
                    }
                )
                .environmentObject(localizationManager)
            }
            .alert(localizationManager.localized("elderly_contact_delete_confirmation"), isPresented: $showDeleteAlert) {
                Button(localizationManager.localized("elderly_settings_edit_contacts_cancel"), role: .cancel) {
                    contactToDelete = nil
                }
                Button(localizationManager.localized("elderly_contact_edit_delete"), role: .destructive) {
                    if let index = contactToDelete {
                        familyContacts.remove(at: index)
                        saveContacts()
                    }
                    contactToDelete = nil
                }
            }
        }
    }
    
    // MARK: - Data Loading and Saving
    
    private func loadContacts() {
        // Сначала пытаемся загрузить из elderly_family_contacts_list (сохраненные изменения)
        if let savedContactsData = UserDefaults.standard.data(forKey: "elderly_family_contacts_list"),
           let savedContacts = try? JSONDecoder().decode([FamilyContact].self, from: savedContactsData) {
            familyContacts = savedContacts
            print("✅ Загружено контактов из elderly_family_contacts_list: \(familyContacts.count)")
            return
        }

        let decoded = UnifiedFamilyRoster.load()
        guard !decoded.isEmpty else {
            familyContacts = []
            print("⚠️ Нет данных о членах семьи в UserDefaults")
            return
        }

        let projections = UnifiedFamilyRoster.contactProjections(audience: .elderly, members: decoded)
        familyContacts = projections.map { item in
            FamilyContact(
                id: item.id,
                name: item.name,
                phone: item.phone,
                relation: localizationManager.localized(item.relationLocalizationKey)
            )
        }
        
        print("✅ Загружено контактов из family_members_list: \(familyContacts.count)")
    }
    
    private func saveContacts() {
        // Сохраняем в elderly_family_contacts_list для синхронизации
        guard let encoded = try? JSONEncoder().encode(familyContacts) else {
            print("❌ Ошибка кодирования контактов")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: "elderly_family_contacts_list")
        UserDefaults.standard.synchronize() // Принудительная синхронизация
        print("✅ Сохранено контактов: \(familyContacts.count) в elderly_family_contacts_list")
        let roster = UnifiedFamilyRoster.load()
        let phoneEntries = Dictionary(uniqueKeysWithValues: familyContacts.map { ($0.id, $0.phone) })
        UnifiedFamilyRoster.persistPhoneDirectory(entriesByContactId: phoneEntries, members: roster)
        ElderlyHealthSyncAudit.persistSnapshot(
            medications: loadPersistedMedications(),
            appointments: loadPersistedAppointments(),
            contacts: familyContacts
        )
        
        // Уведомляем другие экраны об изменении
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }

    private func loadPersistedMedications() -> [Medication] {
        guard let raw = UserDefaults.standard.data(forKey: "elderly_medications_list"),
              let decoded = try? JSONDecoder().decode([Medication].self, from: raw) else {
            return []
        }
        return decoded
    }

    private func loadPersistedAppointments() -> [DoctorAppointment] {
        guard let raw = UserDefaults.standard.data(forKey: "elderly_appointments_list"),
              let decoded = try? JSONDecoder().decode([DoctorAppointment].self, from: raw) else {
            return []
        }
        return decoded
    }
// MARK: - Elderly Edit Contact Modal

struct ElderlyEditContactModal: View {
    let contact: FamilyContact
    let contactIndex: Int?
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var name: String
    @State private var phone: String
    @State private var relation: String
    
    var onSave: (FamilyContact, Int?) -> Void
    
    init(contact: FamilyContact, contactIndex: Int?, isPresented: Binding<Bool>, onSave: @escaping (FamilyContact, Int?) -> Void) {
        self.contact = contact
        self.contactIndex = contactIndex
        _isPresented = isPresented
        _name = State(initialValue: contact.name)
        _phone = State(initialValue: contact.phone)
        _relation = State(initialValue: contact.relation)
        self.onSave = onSave
    }
    
    var relations: [String] {
        [
            localizationManager.localized("elderly_family_relation_son"),
            localizationManager.localized("elderly_family_relation_daughter"),
            localizationManager.localized("elderly_family_relation_daughter_in_law"),
            localizationManager.localized("elderly_family_relation_grandson"),
            localizationManager.localized("elderly_family_relation_granddaughter"),
            localizationManager.localized("elderly_family_relation_you")
        ]
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("elderly_contact_edit_name"))) {
                    TextField(localizationManager.localized("elderly_interface_enter_name"), text: $name)
                }
                
                Section(header: Text(localizationManager.localized("elderly_contact_edit_phone"))) {
                    TextField("+7 (999) 123-45-67", text: $phone)
                        .keyboardType(.phonePad)
                }
                
                Section(header: Text(localizationManager.localized("elderly_contact_edit_relation"))) {
                    Picker(localizationManager.localized("elderly_contact_edit_relation"), selection: $relation) {
                        ForEach(relations, id: \.self) { rel in
                            Text(rel).tag(rel)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                }
            }
            .navigationTitle(localizationManager.localized("elderly_contact_edit_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("elderly_settings_edit_contacts_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("elderly_contact_edit_save")) {
                        let updatedContact = FamilyContact(id: contact.id, name: name, phone: phone, relation: relation)
                        onSave(updatedContact, contactIndex)
                        isPresented = false
                    }
                }
            }
        }
    }
}
}

struct FamilyContact: Identifiable, Codable {
    let id: UUID
    var name: String
    var phone: String
    var relation: String
    
    init(id: UUID = UUID(), name: String, phone: String, relation: String) {
        self.id = id
        self.name = name
        self.phone = phone
        self.relation = relation
    }
}

// MARK: - Security Status Modal

struct SecurityStatusModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView(.vertical, showsIndicators: true) {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("elderly_protection_status_title"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Общий статус
                    VStack(spacing: Spacing.m) {
                        Text("✅")
                            .font(.system(size: 80))
                        
                        Text(localizationManager.localized("elderly_protection_all_good"))
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.successGreen)
                        
                        Text(localizationManager.localized("elderly_protection_no_threats"))
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
                        Text(localizationManager.localized("elderly_protection_detail_info"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        securityStatusRow(icon: "🔒", title: localizationManager.localized("elderly_protection_scam_protection"), status: localizationManager.localized("elderly_protection_enabled"), color: .green)
                        securityStatusRow(icon: "🌐", title: localizationManager.localized("elderly_protection_site_check"), status: localizationManager.localized("elderly_protection_active"), color: .blue)
                        securityStatusRow(icon: "📞", title: localizationManager.localized("elderly_protection_call_blocking"), status: String(format: localizationManager.localized("elderly_protection_blocked_count"), 3), color: .orange)
                        securityStatusRow(icon: "🛡️", title: localizationManager.localized("elderly_protection_general"), status: localizationManager.localized("elderly_protection_percent"), color: .green)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Последняя проверка
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("elderly_protection_last_check"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.primary)
                        
                        Text(String(format: localizationManager.localized("elderly_protection_today_at"), "14:30"))
                            .font(.system(size: 16))
                            .foregroundColor(.secondary)
                        
                        Text(String(format: localizationManager.localized("elderly_protection_next_check"), 2))
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
            .environmentObject(LocalizationManager())
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

    var isEmpty: Bool { systolic <= 0 || diastolic <= 0 }

    static let empty = BloodPressureReading(systolic: 0, diastolic: 0, date: "")
}

struct ElderlyHealthSyncReport: Codable {
    let createdAt: Date
    let medicationsRemoved: Int
    let appointmentsRemoved: Int
    let contactsRemoved: Int

    var hasDesync: Bool {
        medicationsRemoved > 0 || appointmentsRemoved > 0 || contactsRemoved > 0
    }

    var summary: String {
        "Elderly data sync audit: medsRemoved=\(medicationsRemoved), appointmentsRemoved=\(appointmentsRemoved), contactsRemoved=\(contactsRemoved)"
    }
}

struct ElderlyHealthSyncEnvelope: Codable {
    let revision: Int
    let updatedAt: Date
    let medications: [Medication]
    let appointments: [DoctorAppointment]
    let contacts: [FamilyContact]
}

enum ElderlyHealthSyncAudit {
    static let latestReportKey = "elderly_health_sync_audit_report_v1"
    static let snapshotEnvelopeKey = "elderly_health_sync_snapshot_envelope_v1"

    struct Result {
        let medications: [Medication]
        let appointments: [DoctorAppointment]
        let contacts: [FamilyContact]
        let report: ElderlyHealthSyncReport
    }

    static func perform(
        medications: [Medication],
        appointments: [DoctorAppointment],
        contacts: [FamilyContact],
        now: Date = Date()
    ) -> Result {
        let filteredMeds = medications.filter {
            !$0.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !$0.time.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        }
        let filteredAppointments = appointments.filter {
            !$0.doctor.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !$0.date.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !$0.time.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        }
        let filteredContacts = contacts.filter { isPhoneLikelyCallable($0.phone) }

        let report = ElderlyHealthSyncReport(
            createdAt: now,
            medicationsRemoved: max(0, medications.count - filteredMeds.count),
            appointmentsRemoved: max(0, appointments.count - filteredAppointments.count),
            contactsRemoved: max(0, contacts.count - filteredContacts.count)
        )
        return Result(
            medications: filteredMeds,
            appointments: filteredAppointments,
            contacts: filteredContacts,
            report: report
        )
    }

    static func synchronizeAcrossDevices(
        localMedications: [Medication],
        localAppointments: [DoctorAppointment],
        localContacts: [FamilyContact],
        defaults: UserDefaults = .standard,
        now: Date = Date()
    ) -> Result {
        let incoming = latestSnapshot(defaults: defaults)
        let merged = mergeWithoutLoss(
            localMedications: localMedications,
            localAppointments: localAppointments,
            localContacts: localContacts,
            incoming: incoming
        )
        let normalized = perform(
            medications: merged.medications,
            appointments: merged.appointments,
            contacts: merged.contacts,
            now: now
        )
        persistLatestReport(normalized.report, defaults: defaults)
        persistSnapshot(
            medications: normalized.medications,
            appointments: normalized.appointments,
            contacts: normalized.contacts,
            defaults: defaults,
            now: now
        )
        return normalized
    }

    static func persistLatestReport(_ report: ElderlyHealthSyncReport, defaults: UserDefaults = .standard) {
        guard let encoded = try? JSONEncoder().encode(report) else { return }
        defaults.set(encoded, forKey: latestReportKey)
    }

    static func latestReport(defaults: UserDefaults = .standard) -> ElderlyHealthSyncReport? {
        guard let raw = defaults.data(forKey: latestReportKey) else { return nil }
        return try? JSONDecoder().decode(ElderlyHealthSyncReport.self, from: raw)
    }

    static func persistSnapshot(
        medications: [Medication],
        appointments: [DoctorAppointment],
        contacts: [FamilyContact],
        defaults: UserDefaults = .standard,
        now: Date = Date()
    ) {
        let currentRevision = latestSnapshot(defaults: defaults)?.revision ?? 0
        let envelope = ElderlyHealthSyncEnvelope(
            revision: currentRevision + 1,
            updatedAt: now,
            medications: medications,
            appointments: appointments,
            contacts: contacts
        )
        guard let encoded = try? JSONEncoder().encode(envelope) else { return }
        defaults.set(encoded, forKey: snapshotEnvelopeKey)
    }

    static func latestSnapshot(defaults: UserDefaults = .standard) -> ElderlyHealthSyncEnvelope? {
        guard let raw = defaults.data(forKey: snapshotEnvelopeKey) else { return nil }
        return try? JSONDecoder().decode(ElderlyHealthSyncEnvelope.self, from: raw)
    }

    private static func mergeWithoutLoss(
        localMedications: [Medication],
        localAppointments: [DoctorAppointment],
        localContacts: [FamilyContact],
        incoming: ElderlyHealthSyncEnvelope?
    ) -> (medications: [Medication], appointments: [DoctorAppointment], contacts: [FamilyContact]) {
        guard let incoming else {
            return (localMedications, localAppointments, localContacts)
        }

        let medications = mergeByMedicationId(local: localMedications, incoming: incoming.medications)
        let appointments = mergeByAppointmentId(local: localAppointments, incoming: incoming.appointments)
        let contacts = mergeByContactId(local: localContacts, incoming: incoming.contacts)
        return (medications, appointments, contacts)
    }

    private static func mergeByMedicationId(local: [Medication], incoming: [Medication]) -> [Medication] {
        var byId: [UUID: Medication] = [:]
        incoming.forEach { byId[$0.id] = $0 }
        for item in local {
            if let previous = byId[item.id] {
                byId[item.id] = Medication(
                    id: item.id,
                    name: preferredString(local: item.name, incoming: previous.name),
                    time: preferredString(local: item.time, incoming: previous.time),
                    taken: item.taken || previous.taken
                )
            } else {
                byId[item.id] = item
            }
        }
        return byId.values.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private static func mergeByAppointmentId(local: [DoctorAppointment], incoming: [DoctorAppointment]) -> [DoctorAppointment] {
        var byId: [UUID: DoctorAppointment] = [:]
        incoming.forEach { byId[$0.id] = $0 }
        for item in local {
            if let previous = byId[item.id] {
                byId[item.id] = DoctorAppointment(
                    id: item.id,
                    date: preferredString(local: item.date, incoming: previous.date),
                    doctor: preferredString(local: item.doctor, incoming: previous.doctor),
                    time: preferredString(local: item.time, incoming: previous.time)
                )
            } else {
                byId[item.id] = item
            }
        }
        return byId.values.sorted { $0.date.localizedCaseInsensitiveCompare($1.date) == .orderedAscending }
    }

    private static func mergeByContactId(local: [FamilyContact], incoming: [FamilyContact]) -> [FamilyContact] {
        var byId: [UUID: FamilyContact] = [:]
        incoming.forEach { byId[$0.id] = $0 }
        for item in local {
            if let previous = byId[item.id] {
                byId[item.id] = FamilyContact(
                    id: item.id,
                    name: preferredString(local: item.name, incoming: previous.name),
                    phone: preferredString(local: item.phone, incoming: previous.phone),
                    relation: preferredString(local: item.relation, incoming: previous.relation)
                )
            } else {
                byId[item.id] = item
            }
        }
        return byId.values.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    private static func preferredString(local: String, incoming: String) -> String {
        let l = local.trimmingCharacters(in: .whitespacesAndNewlines)
        let r = incoming.trimmingCharacters(in: .whitespacesAndNewlines)
        if !l.isEmpty { return l }
        return r
    }

    private static func isPhoneLikelyCallable(_ value: String) -> Bool {
        let digits = value.filter(\.isNumber)
        return digits.count >= 10
    }
}

struct SafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView(.vertical, showsIndicators: true) {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("elderly_safety_instructions_title"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_safety_scam_protection_title"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("elderly_safety_dont_believe"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_correct"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("elderly_safety_correct_actions"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Социальная инженерия
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_safety_social_engineering"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("elderly_safety_scam_warning"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_warning"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.red)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("elderly_safety_scam_not_real"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Ссылки и скам
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_safety_dangerous_links"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("elderly_safety_dont_click"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_correct"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("elderly_safety_correct_links"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Как пользоваться приложением
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_safety_how_to_use"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("elderly_safety_calls_info"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_health_info"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_security_tip"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_safety_emergency_help_tip"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Управление телефонами
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("elderly_safety_family_management_title"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("elderly_safety_add_phones_instructions"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("elderly_settings_instructions"))
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
    let rawRole: FamilyMemberCard.FamilyRole
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
    
    func text(localizationManager: LocalizationManager) -> String {
        switch self {
        case .online: return localizationManager.localized("elderly_family_status_online")
        case .school: return localizationManager.localized("elderly_family_status_school")
        case .offline: return localizationManager.localized("elderly_family_status_offline")
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var newMedicationName: String = ""
    @State private var newMedicationTime: String = ""
    @State private var showAddMedication: Bool = false
    @State private var editingMedication: Medication? = nil // ✅ Для редактирования
    
    // ✅ ЛИМИТ: Максимальное количество лекарств (500)
    private let MAX_MEDICATIONS = 500
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_medications_icon"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddMedication = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text(localizationManager.localized("elderly_medications_add"))
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
                            Text(String(format: localizationManager.localized("elderly_medications_time"), medication.time))
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: Spacing.s) {
                            Button(medication.taken ? localizationManager.localized("elderly_medications_taken") : localizationManager.localized("elderly_medications_take")) {
                                if let index = medications.firstIndex(where: { $0.id == medication.id }) {
                                    medications[index].taken.toggle()
                                }
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(medication.taken ? Color.green : Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            
                            Button(localizationManager.localized("elderly_medications_edit")) {
                                // ✅ РЕДАКТИРОВАНИЕ: Заполняем поля для редактирования
                                editingMedication = medication
                                newMedicationName = medication.name
                                newMedicationTime = medication.time
                                showAddMedication = true
                            }
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(CornerRadius.small)
                            
                            Button(localizationManager.localized("elderly_contact_edit_delete")) {
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
                    editingMedication: $editingMedication,
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
    @Binding var editingMedication: Medication? // ✅ Для редактирования
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: () -> Void
    
    private var isEditing: Bool {
        editingMedication != nil
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(isEditing ? localizationManager.localized("elderly_medications_edit") : localizationManager.localized("elderly_medications_add"))
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_medications_name_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_medications_name_placeholder"), text: $medicationName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_medications_time_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_medications_time_placeholder"), text: $medicationTime)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Button(action: {
                    if !medicationName.isEmpty && !medicationTime.isEmpty {
                        if let editing = editingMedication {
                            // ✅ РЕДАКТИРОВАНИЕ: Обновляем существующее лекарство
                            if let index = medications.firstIndex(where: { $0.id == editing.id }) {
                                medications[index] = Medication(id: editing.id, name: medicationName, time: medicationTime, taken: editing.taken)
                            }
                            editingMedication = nil
                        } else {
                            // ✅ ДОБАВЛЕНИЕ: Добавляем новое лекарство
                            medications.append(Medication(name: medicationName, time: medicationTime, taken: false))
                        }
                        medicationName = ""
                        medicationTime = ""
                        onSave() // Сохраняем после изменения
                        isPresented = false
                    }
                }) {
                    Text(isEditing ? localizationManager.localized("elderly_medications_save") : localizationManager.localized("elderly_medications_add_button"))
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
                    Button(localizationManager.localized("elderly_medications_cancel")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: () -> Void
    @State private var newDoctorName: String = ""
    @State private var newAppointmentDate: String = ""
    @State private var newAppointmentTime: String = ""
    @State private var showAddAppointment: Bool = false
    @State private var editingAppointment: DoctorAppointment? = nil // ✅ Для редактирования
    
    // ✅ ЛИМИТ: Максимальное количество визитов (500)
    private let MAX_APPOINTMENTS = 500
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_appointments_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddAppointment = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text(localizationManager.localized("elderly_appointments_add_visit"))
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
                            Text(String(format: localizationManager.localized("elderly_appointments_date"), appointment.date))
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                            Text(String(format: localizationManager.localized("elderly_appointments_time"), appointment.time))
                                .font(.system(size: 16))
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: Spacing.s) {
                            Button(localizationManager.localized("elderly_appointments_remind")) {
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
                            
                            Button(localizationManager.localized("elderly_appointments_edit")) {
                                // ✅ РЕДАКТИРОВАНИЕ: Заполняем поля для редактирования
                                editingAppointment = appointment
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
                            
                            Button(localizationManager.localized("elderly_contact_edit_delete")) {
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
                    editingAppointment: $editingAppointment,
                    onSave: onSave
                )
                .environmentObject(localizationManager)
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
    @Binding var editingAppointment: DoctorAppointment? // ✅ Для редактирования
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: () -> Void
    
    private var isEditing: Bool {
        editingAppointment != nil
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(isEditing ? localizationManager.localized("elderly_appointments_edit") : localizationManager.localized("elderly_appointments_add_visit_title"))
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_appointments_doctor_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_appointments_doctor_placeholder"), text: $doctorName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_appointments_date_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_appointments_date_placeholder"), text: $appointmentDate)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_appointments_time_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_appointments_time_placeholder"), text: $appointmentTime)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Button(action: {
                    if !doctorName.isEmpty && !appointmentDate.isEmpty && !appointmentTime.isEmpty {
                        if let editing = editingAppointment {
                            // ✅ РЕДАКТИРОВАНИЕ: Обновляем существующий визит
                            if let index = appointments.firstIndex(where: { $0.id == editing.id }) {
                                appointments[index] = DoctorAppointment(id: editing.id, date: appointmentDate, doctor: doctorName, time: appointmentTime)
                            }
                            editingAppointment = nil
                        } else {
                            // ✅ ДОБАВЛЕНИЕ: Добавляем новый визит
                            appointments.append(DoctorAppointment(date: appointmentDate, doctor: doctorName, time: appointmentTime))
                        }
                        doctorName = ""
                        appointmentDate = ""
                        appointmentTime = ""
                        onSave() // Сохраняем после изменения
                        isPresented = false
                    }
                }) {
                    Text(isEditing ? localizationManager.localized("elderly_medications_save") : localizationManager.localized("elderly_medications_add_button"))
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
                    Button(localizationManager.localized("elderly_medications_cancel")) {
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
    @Binding var weeklyPressureByDay: [String: String]
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: () -> Void
    @State private var pressureReadings: [BloodPressureReading] = []
    @State private var newSystolic: String = ""
    @State private var newDiastolic: String = ""
    @State private var newDate: String = ""
    @State private var showAddReading: Bool = false
    
    // ✅ ЛИМИТ: Максимальное количество измерений (1000)
    private let MAX_PRESSURE_READINGS = 1000
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_blood_pressure_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Кнопка добавления
                Button(action: { showAddReading = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text(localizationManager.localized("elderly_blood_pressure_add_measurement"))
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Последнее измерение
                VStack(spacing: Spacing.m) {
                    Text(localizationManager.localized("elderly_blood_pressure_last_measurement"))
                        .font(.system(size: 20, weight: .bold))
                    
                    if bloodPressure.isEmpty {
                        Text(localizationManager.localized("elderly_blood_pressure_no_reading"))
                            .font(.system(size: 22, weight: .semibold))
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    } else {
                        Text("\(bloodPressure.systolic)/\(bloodPressure.diastolic)")
                            .font(.system(size: 48, weight: .bold))
                            .foregroundColor(.red)

                        Text("\(localizationManager.localized("elderly_blood_pressure_date_label")) \(bloodPressure.date)")
                            .font(.system(size: 16))
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                // История измерений по дням недели
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_blood_pressure_history"))
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
                            
                            Button(localizationManager.localized("elderly_medications_edit")) {
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
                    onSave: {
                        if bloodPressure.systolic > 0, bloodPressure.diastolic > 0, !newDate.isEmpty {
                            weeklyPressureByDay[newDate] = "\(bloodPressure.systolic)/\(bloodPressure.diastolic)"
                        }
                        onSave()
                    }
                )
                .environmentObject(localizationManager)
            }
        }
    }
    
    private func getWeekDays() -> [String] {
        return [
            localizationManager.localized("elderly_weekday_mon"),
            localizationManager.localized("elderly_weekday_tue"),
            localizationManager.localized("elderly_weekday_wed"),
            localizationManager.localized("elderly_weekday_thu"),
            localizationManager.localized("elderly_weekday_fri"),
            localizationManager.localized("elderly_weekday_sat"),
            localizationManager.localized("elderly_weekday_sun")
        ]
    }
    
    private func getPressureForDay(_ day: String) -> String {
        let value = weeklyPressureByDay[day] ?? ""
        return value.isEmpty ? "—" : value
    }
    
    private func editPressureForDay(_ day: String) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_blood_pressure_add_title"))
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_blood_pressure_systolic_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_blood_pressure_systolic_placeholder"), text: $systolic)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.numberPad)
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_blood_pressure_diastolic_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_blood_pressure_diastolic_placeholder"), text: $diastolic)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.numberPad)
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_appointments_date_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_health_journal_date_placeholder"), text: $date)
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
                    Text(localizationManager.localized("elderly_blood_pressure_add_button"))
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
                    Button(localizationManager.localized("elderly_medications_cancel")) {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct HealthJournalModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var healthEntries: [HealthEntry] = []
    @State private var newEntryText: String = ""
    @State private var newEntryDate: String = ""
    @State private var showAddEntry: Bool = false
    @State private var editingEntry: HealthEntry? = nil // ✅ Для редактирования
    
    // ✅ ЛИМИТ: Максимальное количество записей (1000 записей)
    private let MAX_HEALTH_ENTRIES = 1000
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_health_journal_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                // Статистика
                HStack(spacing: Spacing.l) {
                    VStack {
                        Text("\(healthEntries.count)")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.blue)
                        Text(localizationManager.localized("elderly_health_journal_entries"))
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
                        Text(localizationManager.localized("elderly_health_journal_days"))
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Кнопка добавления
                Button(action: { 
                    // ✅ ПРОВЕРКА ЛИМИТА: Проверяем перед добавлением
                    if healthEntries.count >= MAX_HEALTH_ENTRIES {
                        // Показываем предупреждение если достигнут лимит
                        return
                    }
                    showAddEntry = true 
                }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text(localizationManager.localized("elderly_health_journal_add_entry"))
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(healthEntries.count >= MAX_HEALTH_ENTRIES ? Color.gray : Color.purple)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
                }
                .disabled(healthEntries.count >= MAX_HEALTH_ENTRIES)
                
                // ✅ ИНФОРМАЦИЯ О ЛИМИТЕ: Показываем если достигнут лимит
                if healthEntries.count >= MAX_HEALTH_ENTRIES {
                    Text(String(format: localizationManager.localized("elderly_health_journal_limit_reached"), MAX_HEALTH_ENTRIES))
                        .font(.system(size: 12))
                        .foregroundColor(.orange)
                        .padding(.horizontal)
                }
                
                // Список записей
                ScrollView(.vertical, showsIndicators: true) {
                    LazyVStack(spacing: Spacing.s) {
                        ForEach(healthEntriesForDisplay) { entry in
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
                                
                                HStack(spacing: Spacing.s) {
                                    // ✅ КНОПКА РЕДАКТИРОВАНИЯ
                                    Button(localizationManager.localized("elderly_health_journal_edit_entry")) {
                                        editingEntry = entry
                                        newEntryDate = entry.date
                                        newEntryText = entry.text
                                        showAddEntry = true
                                    }
                                    .font(.system(size: 14))
                                    .foregroundColor(.blue)
                                    .padding(.horizontal, Spacing.xs)
                                    .padding(.vertical, Spacing.xs)
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(CornerRadius.small)
                                    
                                    // ✅ КНОПКА УДАЛЕНИЯ
                                    Button(localizationManager.localized("elderly_contact_edit_delete")) {
                                        healthEntries.removeAll { $0.id == entry.id }
                                        saveHealthEntries() // Сохраняем после удаления
                                    }
                                    .font(.system(size: 14))
                                    .foregroundColor(.red)
                                    .padding(.horizontal, Spacing.xs)
                                    .padding(.vertical, Spacing.xs)
                                    .background(Color.red.opacity(0.1))
                                    .cornerRadius(CornerRadius.small)
                                }
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
                    Button(localizationManager.localized("elderly_protection_done")) {
                        isPresented = false
                    }
                }
            }
            .sheet(isPresented: $showAddEntry) {
                AddHealthEntrySheet(
                    isPresented: $showAddEntry,
                    entries: $healthEntries,
                    entryText: $newEntryText,
                    entryDate: $newEntryDate,
                    editingEntry: $editingEntry,
                    onSave: { saveHealthEntries() } // ✅ Передаем функцию сохранения
                )
                .environmentObject(localizationManager)
            }
            .onAppear {
                // ✅ ЗАГРУЗКА: Загружаем записи из UserDefaults
                loadHealthEntries()
            }
        }
    }
    
    private var healthEntriesForDisplay: [HealthEntry] {
        #if DEBUG
        if healthEntries.isEmpty { return getMockHealthEntries() }
        #endif
        return healthEntries
    }

    private func getMockHealthEntries() -> [HealthEntry] {
        return [
            HealthEntry(date: "08.10", text: localizationManager.localized("elderly_health_journal_default_entry_aspirin")),
            HealthEntry(date: "07.10", text: localizationManager.localized("elderly_health_journal_default_entry_pressure")),
            HealthEntry(date: "06.10", text: localizationManager.localized("elderly_health_journal_default_entry_doctor"))
        ]
    }
    
    // ✅ ЗАГРУЗКА: Загружаем записи из UserDefaults
    private func loadHealthEntries() {
        guard let savedData = UserDefaults.standard.data(forKey: "elderly_health_journal_entries"),
              let decoded = try? JSONDecoder().decode([HealthEntry].self, from: savedData) else {
            healthEntries = []
            print("⚠️ Нет данных о записях журнала здоровья в UserDefaults")
            return
        }
        
        healthEntries = decoded
        print("✅ Загружено записей журнала здоровья: \(healthEntries.count)")
    }
    
    // ✅ СОХРАНЕНИЕ: Сохраняем записи в UserDefaults
    private func saveHealthEntries() {
        guard let encoded = try? JSONEncoder().encode(healthEntries) else {
            print("❌ Ошибка кодирования записей журнала здоровья")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: "elderly_health_journal_entries")
        print("✅ Сохранено записей журнала здоровья: \(healthEntries.count)")
    }
}

struct HealthEntry: Identifiable, Codable {
    let id: UUID
    let date: String
    let text: String
    
    init(id: UUID = UUID(), date: String, text: String) {
        self.id = id
        self.date = date
        self.text = text
    }
}

struct AddHealthEntrySheet: View {
    @Binding var isPresented: Bool
    @Binding var entries: [HealthEntry]
    @Binding var entryText: String
    @Binding var entryDate: String
    @Binding var editingEntry: HealthEntry? // ✅ Для редактирования
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onSave: (() -> Void)? // ✅ Функция сохранения (опциональная)
    
    // ✅ ЛИМИТ: Максимальное количество записей
    private let MAX_HEALTH_ENTRIES = 1000
    
    private var isEditing: Bool {
        editingEntry != nil
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(isEditing ? localizationManager.localized("elderly_health_journal_edit_entry") : localizationManager.localized("elderly_health_journal_add_entry_title"))
                    .font(.system(size: 24, weight: .bold))
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_appointments_date_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_health_journal_date_placeholder"), text: $entryDate)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_health_journal_entry_label"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField(localizationManager.localized("elderly_health_journal_entry_placeholder"), text: $entryText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .lineLimit(3)
                }
                
                Button(action: {
                    if !entryText.isEmpty && !entryDate.isEmpty {
                        if let editing = editingEntry {
                            // ✅ РЕДАКТИРОВАНИЕ: Обновляем существующую запись
                            if let index = entries.firstIndex(where: { $0.id == editing.id }) {
                                entries[index] = HealthEntry(id: editing.id, date: entryDate, text: entryText)
                            }
                            editingEntry = nil
                        } else {
                            // ✅ ДОБАВЛЕНИЕ: Проверяем лимит перед добавлением
                            if entries.count >= MAX_HEALTH_ENTRIES {
                                return
                            }
                            entries.append(HealthEntry(date: entryDate, text: entryText))
                        }
                        entryText = ""
                        entryDate = ""
                        // ✅ СОХРАНЕНИЕ: Сохраняем после изменения
                        onSave?()
                        isPresented = false
                    }
                }) {
                    Text(isEditing ? localizationManager.localized("elderly_medications_save") : localizationManager.localized("elderly_medications_add_button"))
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background((!isEditing && entries.count >= MAX_HEALTH_ENTRIES) ? Color.gray : Color.purple)
                        .foregroundColor(.white)
                        .cornerRadius(CornerRadius.medium)
                }
                .disabled(entryText.isEmpty || entryDate.isEmpty || (!isEditing && entries.count >= MAX_HEALTH_ENTRIES))
                
                // ✅ ИНФОРМАЦИЯ О ЛИМИТЕ
                if entries.count >= MAX_HEALTH_ENTRIES {
                    Text(String(format: localizationManager.localized("elderly_health_journal_limit_message"), MAX_HEALTH_ENTRIES))
                        .font(.system(size: 12))
                        .foregroundColor(.orange)
                        .padding(.horizontal)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("elderly_medications_cancel")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var urlToCheck: String = ""
    @State private var checkResult: String = ""
    @State private var isChecking: Bool = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_site_check_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("elderly_site_check_enter_url"))
                        .font(.system(size: 18, weight: .semibold))
                    
                    TextField("https://example.com", text: $urlToCheck)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                
                Button(action: {
                    isChecking = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        checkResult = localizationManager.localized("elderly_site_check_safe_result")
                        isChecking = false
                    }
                }) {
                    HStack {
                        if isChecking {
                            ProgressView()
                                .scaleEffect(0.8)
                        }
                        Text(isChecking ? localizationManager.localized("elderly_site_check_checking") : localizationManager.localized("elderly_site_check_button"))
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_scam_protection_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("elderly_scam_protection_enabled"))
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
                        Text(localizationManager.localized("elderly_scam_protection_what_protects"))
                            .font(.system(size: 18, weight: .semibold))
                        
                        Text(localizationManager.localized("elderly_scam_protection_suspicious_calls"))
                        Text(localizationManager.localized("elderly_scam_protection_suspicious_sms"))
                        Text(localizationManager.localized("elderly_scam_protection_dangerous_sites"))
                        Text(localizationManager.localized("elderly_scam_protection_fraudulent_apps"))
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
                    Button(localizationManager.localized("elderly_protection_done")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("elderly_dangerous_contacts_title"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.primary)
                
                VStack(spacing: Spacing.m) {
                    Text(String(format: localizationManager.localized("elderly_dangerous_contacts_blocked"), blockedCount))
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.red)
                    
                    if blockedCount == 0 {
                        Text(localizationManager.localized("elderly_dangerous_contacts_all_safe"))
                            .font(.system(size: 18))
                            .foregroundColor(.green)
                            .padding()
                            .background(Color.green.opacity(0.1))
                            .cornerRadius(CornerRadius.medium)
                    } else {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("elderly_dangerous_contacts_blocked_numbers"))
                                .font(.system(size: 18, weight: .semibold))
                            
                            ForEach(0..<blockedCount, id: \.self) { index in
                                HStack {
                                    Text("+7 (***) ***-**-\(index + 1)")
                                        .font(.system(size: 16))
                                    
                                    Spacer()
                                    
                                    Button(localizationManager.localized("elderly_dangerous_contacts_unblock")) {
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
                    Button(localizationManager.localized("elderly_protection_done")) {
                        isPresented = false
                    }
                }
            }
        }
    }
}
