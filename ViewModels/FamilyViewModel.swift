import SwiftUI
import Combine

// Master Logger for family logic logging
private let logger = MasterLogger.shared

/// 👨‍👩‍👧‍👦 Family View Model
/// Логика для экрана семьи
/// Управляет списком членов семьи, их статусом, устройствами
class FamilyViewModel: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService = APIService.shared
    
    // MARK: - Published Properties
    
    @Published var familyMembers: [FamilyMember] = []
    @Published var totalThreatsBlocked: Int = 0
    @Published var totalDevices: Int = 0
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Models
    
    struct FamilyMember: Identifiable {
        let id = UUID()
        let name: String
        let role: String
        let avatar: String
        let status: String
        let threatsBlocked: Int
        let lastActive: String
        let devices: Int
    }
    
    // MARK: - Init
    
    init() {
        logger.business("Initializing FamilyViewModel")
        loadFamilyMembers()
    }
    
    // MARK: - Public Methods
    
    /// ✅ ИСПРАВЛЕНО: Загрузка списка членов семьи с реального API
    func loadFamilyMembers() {
        logger.business("Loading family members")
        isLoading = true
        errorMessage = nil

        // ✅ ЗАДАЧА 66: Начинаем отслеживание производительности загрузки семьи
        PerformanceMonitor.shared.startScreenLoad("FamilyScreen")
        
        // Загружаем членов семьи
        apiService.getFamilyMembers { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let members):
                    // Преобразуем FamilyMemberResponse в FamilyMember
                    self?.familyMembers = members.map { member in
                        FamilyMember(
                            name: member.name,
                            role: member.role,
                            avatar: member.avatar ?? "",
                            status: member.status ?? "protected",
                            threatsBlocked: member.threatsBlocked ?? 0,
                            lastActive: member.lastActive ?? "",
                            devices: member.devices ?? 0
                        )
                    }
                    self?.isLoading = false

                    // Загружаем статистику семьи
                    self?.loadFamilyStats()

                    // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности загрузки семьи
                    PerformanceMonitor.shared.endScreenLoad("FamilyScreen")

                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    self?.isLoading = false

                    // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности даже при ошибке
                    PerformanceMonitor.shared.endScreenLoad("FamilyScreen")
                    print("⚠️ FamilyViewModel: Ошибка загрузки членов семьи: \(error)")
                }
            }
        }
    }
    
    /// ✅ ДОБАВЛЕНО: Загрузка статистики семьи
    /// ✅ ЗАЩИТА ОТ РЕКУРСИИ: Флаг для предотвращения повторных вызовов
    private var isLoadingFamilyStats = false
    
    private func loadFamilyStats() {
        // ✅ ЗАЩИТА ОТ РЕКУРСИИ: Проверяем, не загружается ли уже статистика
        guard !isLoadingFamilyStats else {
            #if DEBUG
            print("⚠️ FamilyViewModel: Статистика уже загружается, пропускаем повторный вызов")
            #endif
            return
        }
        
        isLoadingFamilyStats = true
        logger.business("Loading family statistics")
        apiService.getFamilyStats { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoadingFamilyStats = false // Сбрасываем флаг в любом случае
                
                switch result {
                case .success(let stats):
                    self?.totalThreatsBlocked = stats.totalThreats
                    self?.totalDevices = stats.totalDevices
                case .failure(let error):
                    print("⚠️ FamilyViewModel: Ошибка загрузки статистики семьи: \(error)")
                    // Не показываем ошибку пользователю, статистика не критична
                }
            }
        }
    }
    
    /// Добавить члена семьи
    func addFamilyMember() {
        logger.business("Initiating add family member flow")
        print("Show add family member sheet")
    }
    
    /// Открыть профиль члена семьи
    func openMemberProfile(_ member: FamilyMember) {
        print("Open profile for \(member.name)")
    }
    
    /// Удалить члена семьи
    func removeFamilyMember(_ member: FamilyMember) {
        familyMembers.removeAll { $0.id == member.id }
    }
}



