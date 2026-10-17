import ManagedSettings
import ManagedSettingsUI
import UIKit

final class ShieldConfigurationExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemThickMaterial,
            backgroundColor: UIColor(red: 0.08, green: 0.10, blue: 0.18, alpha: 1),
            icon: UIImage(systemName: "shield.checkered"),
            title: ShieldConfiguration.Label(
                text: "ALADDIN",
                color: UIColor(red: 0.95, green: 0.78, blue: 0.35, alpha: 1)
            ),
            subtitle: ShieldConfiguration.Label(
                text: appSubtitle,
                color: .white
            ),
            primaryButtonLabel: ShieldConfiguration.Label(
                text: closeLabel,
                color: .white
            ),
            primaryButtonBackgroundColor: UIColor(red: 0.25, green: 0.35, blue: 0.65, alpha: 1),
            secondaryButtonLabel: ShieldConfiguration.Label(
                text: askParentLabel,
                color: UIColor(red: 0.95, green: 0.78, blue: 0.35, alpha: 1)
            )
        )
    }

    override func configuration(shielding application: Application, in category: ActivityCategory) -> ShieldConfiguration {
        configuration(shielding: application)
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemThickMaterial,
            backgroundColor: UIColor(red: 0.08, green: 0.10, blue: 0.18, alpha: 1),
            title: ShieldConfiguration.Label(text: "ALADDIN", color: UIColor(red: 0.95, green: 0.78, blue: 0.35, alpha: 1)),
            subtitle: ShieldConfiguration.Label(
                text: webSubtitle,
                color: .white
            ),
            primaryButtonLabel: ShieldConfiguration.Label(text: closeLabel, color: .white),
            primaryButtonBackgroundColor: UIColor(red: 0.25, green: 0.35, blue: 0.65, alpha: 1),
            secondaryButtonLabel: ShieldConfiguration.Label(
                text: askParentLabel,
                color: UIColor(red: 0.95, green: 0.78, blue: 0.35, alpha: 1)
            )
        )
    }

    /// Appex has no LocalizationManager — RU/EN from preferred languages.
    private var prefersRussian: Bool {
        Locale.preferredLanguages.first?.hasPrefix("ru") == true
    }

    private var closeLabel: String { prefersRussian ? "Закрыть" : "Close" }
    private var askParentLabel: String { prefersRussian ? "Спросить родителя" : "Ask parent" }
    private var appSubtitle: String {
        prefersRussian ? "Это приложение ограничено родителем" : "This app is limited by a parent"
    }
    private var webSubtitle: String {
        prefersRussian ? "Сайт ограничен родителем" : "This site is limited by a parent"
    }
}
