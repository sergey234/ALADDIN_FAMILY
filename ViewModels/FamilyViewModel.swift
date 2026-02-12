import SwiftUI
import Combine

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
        loadFamilyMembers()
    }
    
    // MARK: - Public Methods
    
    /// ✅ ИСПРАВЛЕНО: Загрузка списка членов семьи с реального API
    func loadFamilyMembers() {
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
                            avatar: member.avatar,
                            status: member.status,
                            threatsBlocked: member.threatsBlocked,
                            lastActive: member.lastActive,
                            devices: member.devices
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
    private func loadFamilyStats() {
        apiService.getFamilyStats { [weak self] result in
            DispatchQueue.main.async {
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



