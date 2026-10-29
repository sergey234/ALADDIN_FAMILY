import Foundation

/// Pay-pains UI kill switch (X4).
///
/// Канон владельца 2026-10-29:
/// - По умолчанию пользователь всегда видит **новый** вход / порядок Семьи.
/// - Flag = аварийный откат на старый UI (не «прятать новое до QA»).
///
/// F3 / S читают `usesNewPayPainsHome` / `usesNewPayPainsFamily`.
/// Пока новый UI ещё не собран, оба пути могут выглядеть одинаково —
/// скелет нужен до смены лица экрана.
enum PayPainsUIFlags {
    /// UserDefaults key. `true` = новый UI (default). `false` = старый UI.
    static let newUIEnabledKey = "aladdin.payPains.newUIEnabled"

    /// Новый вход (три двери) и связанный shell. Default **вкл**.
    static var usesNewPayPainsHome: Bool {
        get {
            if UserDefaults.standard.object(forKey: newUIEnabledKey) == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: newUIEnabledKey)
        }
        set {
            UserDefaults.standard.set(newValue, forKey: newUIEnabledKey)
        }
    }

    /// Новый порядок экрана Семья. Пока один kill switch с входом.
    static var usesNewPayPainsFamily: Bool {
        get { usesNewPayPainsHome }
        set { usesNewPayPainsHome = newValue }
    }

    /// Аварийный откат: снова старый UI без hotfix / без git reset.
    static func disableNewUIForRollback() {
        usesNewPayPainsHome = false
    }

    /// Вернуть новый UI после отката (после QA / фикса).
    static func enableNewUI() {
        usesNewPayPainsHome = true
    }

    /// Стартовый вход: SimpleHome с тремя дверями (§10 / F3).
    /// При новом UI — по умолчанию для родителя/взрослого.
    /// При откате X4 — только если включён старый opt-in `aladdin.simpleHomePreferred`.
    /// Child / teen / elderly — не подменяем их вход.
    static func shouldOpenSimpleHomeAtLaunch(
        defaults: UserDefaults = .standard
    ) -> Bool {
        let role = (defaults.string(forKey: "current_user_role") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let blocked: Set<String> = ["child", "teenager", "teen", "elderly", "senior"]
        if blocked.contains(role) {
            return false
        }
        if usesNewPayPainsHome {
            return true
        }
        return defaults.bool(forKey: "aladdin.simpleHomePreferred")
    }
}
