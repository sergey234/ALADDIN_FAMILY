import SwiftUI
import Combine

/// 👨‍👩‍👧‍👦 Family View Model
/// Логика для экрана семьи
/// Управляет списком членов семьи, их статусом, устройствами
class FamilyViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var familyMembers: [FamilyMember] = []
    @Published var totalThreatsBlocked: Int = 47
    @Published var totalDevices: Int = 8
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
    
    /// Загрузка списка членов семьи
    func loadFamilyMembers() {
        isLoading = true
        
        // Имитация данных (в реальности - API)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
            self?.familyMembers = [
                FamilyMember(name: "Сергей", role: "Родитель", avatar: "👨", status: "protected", threatsBlocked: 47, lastActive: "Сейчас", devices: 3),
                FamilyMember(name: "Мария", role: "Родитель", avatar: "👩", status: "protected", threatsBlocked: 32, lastActive: "5 мин назад", devices: 2),
                FamilyMember(name: "Маша", role: "Ребёнок", avatar: "👧", status: "warning", threatsBlocked: 23, lastActive: "10 мин назад", devices: 2),
                FamilyMember(name: "Бабушка", role: "Пожилой", avatar: "👵", status: "offline", threatsBlocked: 12, lastActive: "2 часа назад", devices: 1)
            ]
            self?.isLoading = false
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




