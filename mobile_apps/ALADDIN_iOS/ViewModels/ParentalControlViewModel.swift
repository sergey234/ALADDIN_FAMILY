import SwiftUI
import Combine

/// 👶 Parental Control View Model
/// Логика для родительского контроля
class ParentalControlViewModel: ObservableObject {
    
    @Published var selectedChild: Child?
    @Published var children: [Child] = []
    @Published var isContentFilterEnabled: Bool = true
    @Published var isAppBlockingEnabled: Bool = true
    @Published var screenTimeLimit: Double = 3
    @Published var allowedApps: [String] = []
    @Published var blockedSitesToday: Int = 12
    @Published var screenTimeToday: String = "2:45"
    
    struct Child: Identifiable {
        let id = UUID()
        let name: String
        let age: Int
        let avatar: String
        let screenTimeToday: String
        let threatsBlocked: Int
    }
    
    init() {
        loadChildren()
    }
    
    func loadChildren() {
        children = [
            Child(name: "Маша", age: 10, avatar: "👧", screenTimeToday: "2:45", threatsBlocked: 23),
            Child(name: "Петя", age: 7, avatar: "👦", screenTimeToday: "1:30", threatsBlocked: 8)
        ]
        selectedChild = children.first
    }
    
    func toggleContentFilter() {
        isContentFilterEnabled.toggle()
    }
    
    func toggleAppBlocking() {
        isAppBlockingEnabled.toggle()
    }
    
    func updateScreenTimeLimit(_ value: Double) {
        screenTimeLimit = value
    }
    
    func addTime(minutes: Int) {
        print("Add \(minutes) minutes to screen time")
    }
    
    func blockDevice() {
        print("Block child device immediately")
    }
    
    func showLocation() {
        print("Show child location on map")
    }
}




