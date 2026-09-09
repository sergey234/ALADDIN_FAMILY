#!/usr/bin/env python3
"""Static release gate for ALADDIN's App Store-only feature contract."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []

    app_config = read("Core/Config/AppConfig.swift")
    project = read("ALADDIN.xcodeproj/project.pbxproj")
    entitlements = read("ALADDIN.entitlements")
    info_plist = read("Info.plist")
    dns_manager = read("Core/Managers/DNSProtectionManager.swift")
    tariffs = read("Screens/10_TariffsScreen.swift")
    family = read("Screens/02_FamilyScreen.swift")
    protection = read("Screens/03_NetworkProtectionScreen.swift")
    app_root = read("ALADDINApp.swift")
    navigation = read("Core/Navigation/NavigationManager.swift")
    privacy = read("Screens/18_PrivacyPolicyScreen.swift")
    terms = read("Screens/19_TermsOfServiceScreen.swift")
    support = read("Screens/13_SupportScreen.swift")
    additional_features = read("Shared/Models/AdditionalFeature.swift")
    settings = read("Screens/05_SettingsScreen.swift")
    simple_home = read("Screens/SimpleHomeScreen.swift")
    parental_screen = read("Screens/07_ParentalControlScreen.swift")
    parental_manager = read("Core/Managers/ParentalControlManager.swift")
    family_modals = read("Screens/FamilyModals.swift")
    tariff_card = read("Shared/Models/TariffCard.swift")
    tariff_card_view = read("Components/TariffCardView.swift")
    localization = read("Core/Localization/LocalizationManager.swift")
    health_sleep = read("Core/Services/WellnessHealthSleepReader.swift")
    health_fall = read("Core/Elderly/ElderlyFallDetectionService.swift")
    ui_tests = read("Tests/UITests/NetworkProtectionScreenUITests.swift")

    require(
        "enum AppStoreBuildPolicy" in app_config,
        "AppStoreBuildPolicy is missing",
        failures,
    )
    require(
        "static let allowsAlternativePayments = false" in app_config,
        "App Store policy must explicitly deny alternative payments",
        failures,
    )
    require(
        "static let allowsSmartDNS = false" in app_config,
        "App Store policy must explicitly deny Smart DNS",
        failures,
    )
    require(
        "static let allowsSystemFamilyControls = false" in app_config,
        "App Store policy must deny unapproved system Family Controls",
        failures,
    )
    require(
        "static let allowsHealthKitIntegration = false" in app_config,
        "App Store policy must deny HealthKit until its capability is configured",
        failures,
    )
    require(
        "SWIFT_ACTIVE_COMPILATION_CONDITIONS = \"$(inherited) APP_STORE_BUILD\";" in project,
        "Release configuration must define APP_STORE_BUILD",
        failures,
    )
    require(
        "<key>aps-environment</key>" in entitlements
        and "<string>$(APS_ENVIRONMENT)</string>" in entitlements
        and "APS_ENVIRONMENT = production;" in project,
        "Release push entitlement must resolve to production",
        failures,
    )
    require(
        "<string>remote-notification</string>" in info_plist,
        "Info.plist must keep the remote-notification background mode",
        failures,
    )
    require(
        "#if !APP_STORE_BUILD\nimport NetworkExtension" in dns_manager,
        "NetworkExtension import must be excluded from APP_STORE_BUILD",
        failures,
    )
    require(
        "#if APP_STORE_BUILD" in dns_manager
        and "App Store build intentionally excludes system Smart DNS." in dns_manager,
        "DNS manager needs a harmless App Store implementation",
        failures,
    )
    require(
        "AppStoreBuildPolicy.allowsAlternativePayments" in tariffs,
        "Tariffs must use the centralized payment policy",
        failures,
    )
    require(
        tariffs.count("#if !APP_STORE_BUILD") >= 2
        and 'print("🍎 App Store purchase: opening StoreKit")' in tariffs,
        "External purchase branches must be compile-gated before StoreKit",
        failures,
    )
    require(
        "#if !APP_STORE_BUILD\n                    case .paymentQR:" in app_root,
        "PaymentQRScreen destination must be excluded from APP_STORE_BUILD",
        failures,
    )
    require(
        "#if !APP_STORE_BUILD\n                    case .activationCode:" in app_root,
        "External activation destination must be excluded from APP_STORE_BUILD",
        failures,
    )
    require(
        "resolved == .paymentQR, AppStoreBuildPolicy.isAppStoreBuild" in navigation,
        "NavigationManager must reject PaymentQR in APP_STORE_BUILD",
        failures,
    )
    require(
        "resolved == .activationCode, AppStoreBuildPolicy.isAppStoreBuild" in navigation,
        "NavigationManager must reject external activation in APP_STORE_BUILD",
        failures,
    )
    require(
        'accessibilityIdentifier("restore_purchases_button")' in tariffs,
        "Tariffs must provide an accessible Restore Purchases action",
        failures,
    )
    require(
        "AppStoreBuildPolicy.allowsSmartDNS" in family,
        "Family UI must gate Smart DNS with the centralized policy",
        failures,
    )
    require(
        "secureConnectionStatusCard" not in protection
        and "vpn_connect_control" not in protection,
        "Legacy VPN connection card must be absent from Protection Center",
        failures,
    )
    require(
        "batterySavingTipCard" not in protection,
        "VPN-like battery/disconnect copy must be absent",
        failures,
    )
    require(
        "protection_capability_\\(titleKey)" in protection,
        "Protection Center must expose testable real-capability rows",
        failures,
    )
    require(
        "else if !AppStoreBuildPolicy.isAppStoreBuild" in privacy,
        "Legacy network privacy tab must be hidden in APP_STORE_BUILD",
        failures,
    )
    require(
        "$0 != .networkProtection" in terms,
        "Legacy network terms section must be hidden in APP_STORE_BUILD",
        failures,
    )
    require(
        "Digital subscriptions are purchased only through Apple In-App Purchase." in terms,
        "App Store terms must describe Apple In-App Purchase only",
        failures,
    )
    require(
        '$0.id.hasPrefix("network_protection_")' in additional_features
        and '$0.id == "anonymity_premium"' in additional_features,
        "Tariff gallery must remove network/anonymity claims in APP_STORE_BUILD",
        failures,
    )
    require(
        "if !AppStoreBuildPolicy.isAppStoreBuild" in settings,
        "Settings must hide the legacy network-protection toggle",
        failures,
    )
    require(
        'titleKey: "profile_security_title"' in simple_home
        and 'subtitleKey: "network_protection_security_features"' in simple_home,
        "Simple Home must label the destination as security tools",
        failures,
    )
    require(
        '"faq_aes256"' in support
        and '"faq_how_network_protection_works"' in support
        and "visibleEntries" in support,
        "VPN/AES FAQ entries must be filtered from APP_STORE_BUILD",
        failures,
    )
    require(
        "testProtectionCenterShowsRealCapabilitiesAndNoVPNControl" in ui_tests,
        "App Store protection UI regression test is missing",
        failures,
    )
    require(
        "if AppStoreBuildPolicy.allowsSystemFamilyControls" in parental_screen
        and 'UserDefaults.standard.set("parent", forKey: "current_user_role")' not in parental_screen,
        "Parental UI must hide system controls and must never self-promote the role",
        failures,
    )
    require(
        "guard AppStoreBuildPolicy.allowsSystemFamilyControls else { return [] }"
        in tariff_card
        and "$0 != .parental || AppStoreBuildPolicy.allowsSystemFamilyControls"
        in tariff_card_view,
        "App Store tariffs must not sell unavailable Family Controls",
        failures,
    )
    require(
        parental_screen.count("if AppStoreBuildPolicy.allowsSystemFamilyControls") >= 2,
        "Parental screen must hide bypass claims with unavailable system controls",
        failures,
    )
    require(
        "@State private var attemptsWeek: Int = 0" in family_modals
        and "@State private var incognitoAttempts: Int = 0" in family_modals
        and "@State private var torAttempts: Int = 0" in family_modals
        and "@State private var proxyAttempts: Int = 0" in family_modals,
        "Bypass UI must never ship fabricated statistics",
        failures,
    )
    require(
        "if AppStoreBuildPolicy.isAppStoreBuild" in privacy
        and "ALADDIN обрабатывает только данные" in localization
        and "ALADDIN processes only data needed" in localization,
        "App Store privacy UI must disclose actual server processing in RU and EN",
        failures,
    )
    require(
        health_sleep.count("#if canImport(HealthKit) && !APP_STORE_BUILD") >= 3
        and health_fall.count("#if canImport(HealthKit) && !APP_STORE_BUILD") >= 4,
        "HealthKit code must be excluded from APP_STORE_BUILD without entitlement",
        failures,
    )
    require(
        "APCB0022F90000200C7D34B" in project,
        "Content Blocker privacy manifest must be embedded",
        failures,
    )
    require(
        parental_manager.count("AppStoreBuildPolicy.allowsSystemFamilyControls") >= 3
        and "system_family_controls_not_available_in_build" in parental_manager,
        "FamilyControls runtime calls must fail closed in APP_STORE_BUILD",
        failures,
    )

    if failures:
        print("APP_STORE_BUILD POLICY: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("APP_STORE_BUILD POLICY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
