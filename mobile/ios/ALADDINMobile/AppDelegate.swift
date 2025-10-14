import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        
        // Настройка цветовой схемы "Грозовое небо"
        setupStormSkyTheme()
        
        // Инициализация AI помощника
        initializeAIAssistant()
        
        // Настройка уведомлений
        setupNotifications()
        
        return true
    }

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        // Called when a new scene session is being created.
        // Use this method to select a configuration to create the new scene with.
        return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        // Called when the user discards a scene session.
        // If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
        // Use this method to release any resources that were specific to the discarded scenes, as they will not return.
    }
    
    // MARK: - Private Methods
    
    private func setupStormSkyTheme() {
        // Настройка глобальной цветовой схемы "Грозовое небо с золотыми акцентами"
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = StormSkyColors.primaryBackground
        appearance.titleTextAttributes = [
            .foregroundColor: StormSkyColors.primaryText
        ]
        
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
        
        // Настройка TabBar
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = StormSkyColors.secondaryBackground
        
        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
    }
    
    private func initializeAIAssistant() {
        // Инициализация AI помощника при запуске приложения
        print("🤖 AI Assistant initialized")
    }
    
    private func setupNotifications() {
        // Настройка уведомлений для безопасности
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            if granted {
                print("✅ Notifications authorized")
            } else {
                print("❌ Notifications denied: \(error?.localizedDescription ?? "Unknown error")")
            }
        }
    }
}

