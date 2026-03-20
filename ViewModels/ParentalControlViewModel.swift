import Foundation
import SwiftUI
import Combine
import FamilyControls

// Master Logger for parental control logging
private let logger = MasterLogger.shared

/**
 * 👶 Parental Control ViewModel
 * ViewModel для управления родительским контролем и 5 компонентами защиты детей
 * Использует ComponentStatusService для загрузки и обновления статусов
 */

@MainActor
class ParentalControlViewModel: ObservableObject {
    
    // MARK: - Published Properties - Child Data
    
    @Published var selectedChild: Child?
    @Published var children: [Child] = []
    @Published var isContentFilterEnabled: Bool = true
    @Published var isAppBlockingEnabled: Bool = true
    @Published var screenTimeLimit: Double = 3
    @Published var allowedApps: [String] = []
    @Published var blockedSitesToday: Int = 12
    @Published var screenTimeToday: String = "2:45"
    @Published var appUsage: [AppUsageStatistics] = []
    @Published var familyAuthStatus: AuthorizationStatus = .notDetermined
    @Published var isDNSProtectionEnabled: Bool = false
    @Published var isDNSLoading: Bool = false
    @Published var dailyReports: [ParentalReportItem] = []
    @Published var weeklyReports: [ParentalReportItem] = []
    
    // MARK: - Published Properties - Component Statuses (5 компонентов)
    
    // Защита детей (4 компонента)
    @Published var selfHarmDetectionEnabled: Bool = false
    @Published var groomingDetectionEnabled: Bool = false
    @Published var onlinePredatorsEnabled: Bool = false
    @Published var psychologicalSupportEnabled: Bool = false
    
    // Родительский контроль (1 компонент - улучшить)
    @Published var parentalControlBotEnabled: Bool = true
    
    // MARK: - Dependencies
    
    private let statusService: ComponentStatusService
    private let retryManager: RetryManager
    private let toastManager = ToastManager.shared
    
    // MARK: - Initialization
    
    init(
        statusService: ComponentStatusService = .shared,
        retryManager: RetryManager = .balanced()
    ) {
        self.statusService = statusService
        self.retryManager = retryManager
        
        loadChildren()
    }
    
    // MARK: - Component Methods
    
    /// Загрузить статусы всех компонентов
    func loadComponentStatuses() async {
        guard AppConfig.authToken != nil else { return }

        let componentIds: [(String, ComponentLoadPriority)] = [
            ("self_harm_detection_agent", .critical),
            ("grooming_detection_agent", .critical),
            ("online_predators_agent", .critical),
            ("parental_control_bot", .high),
            ("psychological_support_agent", .normal)
        ]
        
        let prioritizedItems: [PrioritizedLoadItem<ComponentStatus>] = componentIds.map { componentId, priority in
            PrioritizedLoadItem(id: componentId, priority: priority) { [weak self] in
                guard let self = self else { throw ComponentError.unknown(NSError(domain: "ParentalControlViewModel", code: -1)) }
                return try await self.statusService.getStatus(for: componentId)
            }
        }
        
        do {
            _ = try await ParallelLoader.executeWithLimit(items: prioritizedItems, maxConcurrent: 10) { [weak self] componentId, status in
                self?.updateStatusForComponent(componentId: componentId, status: status)
            }
        } catch {
            print("⚠️ ParentalControlViewModel: Error loading statuses: \(error)")
        }
    }

    // MARK: - Toggle Methods
    
    func toggleSelfHarmDetection(_ newValue: Bool) {
        Task { await toggleComponent(componentId: "self_harm_detection_agent", newValue: newValue) { [weak self] v in self?.selfHarmDetectionEnabled = v } }
    }
    
    func toggleGroomingDetection(_ newValue: Bool) {
        Task { await toggleComponent(componentId: "grooming_detection_agent", newValue: newValue) { [weak self] v in self?.groomingDetectionEnabled = v } }
    }
    
    func toggleOnlinePredators(_ newValue: Bool) {
        Task { await toggleComponent(componentId: "online_predators_agent", newValue: newValue) { [weak self] v in self?.onlinePredatorsEnabled = v } }
    }
    
    func togglePsychologicalSupport(_ newValue: Bool) {
        Task { await toggleComponent(componentId: "psychological_support_agent", newValue: newValue) { [weak self] v in self?.psychologicalSupportEnabled = v } }
    }
    
    func toggleParentalControlBot(_ newValue: Bool) {
        Task { await toggleComponent(componentId: "parental_control_bot", newValue: newValue) { [weak self] v in self?.parentalControlBotEnabled = v } }
    }
    
    // MARK: - Private Methods
    
    private func toggleComponent(componentId: String, newValue: Bool, updateClosure: @escaping (Bool) -> Void) async {
        guard AppConfig.authToken != nil else {
            updateClosure(!newValue)
            toastManager.showError("Требуется авторизация")
            return
        }
        
        updateClosure(newValue)

        let result: Result<Void, NetworkError> = await retryManager.execute(
            operation: {
                do {
                    try await self.statusService.updateStatus(componentId: componentId, isEnabled: newValue)
                } catch let error as ComponentError {
                    throw error.toNetworkError()
                } catch {
                    throw NetworkError.unknown(error)
                }
            },
            retryCondition: { $0.isRetryable }
        )

        if case .failure(let error) = result {
            updateClosure(!newValue)
            toastManager.showError(error.localizedDescription)
        }
    }
    
    private func updateStatusForComponent(componentId: String, status: ComponentStatus) {
        switch componentId {
        case "self_harm_detection_agent": selfHarmDetectionEnabled = status.isEnabled
        case "grooming_detection_agent": groomingDetectionEnabled = status.isEnabled
        case "online_predators_agent": onlinePredatorsEnabled = status.isEnabled
        case "psychological_support_agent": psychologicalSupportEnabled = status.isEnabled
        case "parental_control_bot": parentalControlBotEnabled = status.isEnabled
        default: break
        }
    }
    
    func loadChildren() {
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            self.children = decoded.filter { $0.role == .child || $0.role == .teenager }.map { member in
                Child(
                    id: member.id.uuidString,
                    name: member.name,
                    age: 10,
                    avatar: member.avatar,
                    screenTimeToday: "...",
                    threatsBlocked: member.threatsBlocked
                )
            }
            self.selectedChild = children.first
        }
        
        self.familyAuthStatus = AuthorizationCenter.shared.authorizationStatus
        self.isDNSProtectionEnabled = DNSProtectionManager.shared.isEnabled
        loadReports()
    }
    
    func loadReports() {
        let childIdStr = selectedChild?.id
        
        APIService.shared.getDailyReports(childId: childIdStr) { [weak self] result in
            if case .success(let reports) = result {
                Task { @MainActor [weak self] in
                    self?.dailyReports = reports
                }
            }
        }
        
        APIService.shared.getWeeklyReports(childId: childIdStr) { [weak self] result in
            if case .success(let reports) = result {
                Task { @MainActor [weak self] in
                    self?.weeklyReports = reports
                }
            }
        }
    }
    
    func toggleDNSProtection() {
        if isDNSProtectionEnabled {
            DNSProtectionManager.shared.disableProtection()
        } else {
            DNSProtectionManager.shared.enableProtection(childId: selectedChild?.id)
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.isDNSProtectionEnabled = DNSProtectionManager.shared.isEnabled
            self.isDNSLoading = DNSProtectionManager.shared.isLoading
        }
    }
    
    func requestScreenTimeAuthorization() {
        Task {
            do {
                try await ParentalControlManager.shared.requestFamilyAuthorization()
                self.familyAuthStatus = AuthorizationCenter.shared.authorizationStatus
            } catch {
                print("❌ ViewModel: Auth failed: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Child Model
    
    struct Child: Identifiable {
        let id: String
        let name: String
        let age: Int
        let avatar: String
        let screenTimeToday: String
        let threatsBlocked: Int
    }
}
