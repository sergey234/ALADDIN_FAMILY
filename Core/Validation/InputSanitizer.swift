import Foundation
import os.log

/**
 * 🛡️ Input Sanitizer
 * Санитизация пользовательского ввода для защиты от XSS, SQL-инъекций и других атак
 */
class InputSanitizer {

    // MARK: - Logger

    private static let sanitizerLogger = OSLog(
        subsystem: "com.aladdin.validation",
        category: "InputSanitizer"
    )

    // MARK: - Singleton

    static let shared = InputSanitizer()

    // MARK: - Validation Errors

    enum SanitizationError: LocalizedError {
        case invalidEmail
        case invalidPhone
        case invalidRecoveryCode
        case invalidFamilyId
        case containsMaliciousContent
        case tooLong(maxLength: Int)
        case tooShort(minLength: Int)
        case containsInvalidCharacters

        var errorDescription: String? {
            switch self {
            case .invalidEmail:
                return "Некорректный формат email адреса"
            case .invalidPhone:
                return "Некорректный формат номера телефона"
            case .invalidRecoveryCode:
                return "Некорректный формат кода восстановления"
            case .invalidFamilyId:
                return "Некорректный формат ID семьи"
            case .containsMaliciousContent:
                return "Ввод содержит недопустимый контент"
            case .tooLong(let maxLength):
                return "Текст слишком длинный (максимум \(maxLength) символов)"
            case .tooShort(let minLength):
                return "Текст слишком короткий (минимум \(minLength) символов)"
            case .containsInvalidCharacters:
                return "Текст содержит недопустимые символы"
            }
        }
    }

    // MARK: - Constants

    private let maxMessageLength = 2000
    private let maxNameLength = 100
    private let maxRecoveryCodeLength = 50
    private let maxFamilyIdLength = 50
    private let maxEmailLength = 254
    private let maxPhoneLength = 20

    private let minMessageLength = 1
    private let minNameLength = 1
    private let minRecoveryCodeLength = 6
    private let minFamilyIdLength = 6

    // MARK: - XSS Protection Patterns

    private let maliciousPatterns = [
        "<script[^>]*>.*?</script>",           // Script tags
        "<iframe[^>]*>.*?</iframe>",           // Iframe tags
        "<object[^>]*>.*?</object>",           // Object tags
        "<embed[^>]*>.*?</embed>",             // Embed tags
        "javascript:",                         // JavaScript protocol
        "vbscript:",                           // VBScript protocol
        "data:text/html",                      // Data URI HTML
        "on\\w+\\s*=",                        // Event handlers
        "expression\\s*\\(",                   // CSS expressions
        "<!--.*-->",                          // HTML comments with scripts
        "<link[^>]*rel\\s*=\\s*[\"']?stylesheet[\"']?[^>]*>", // External stylesheets
        "@import",                             // CSS imports
    ]

    // MARK: - SQL Injection Protection Patterns

    private let sqlInjectionPatterns = [
        "(\\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\\b)",
        "(\\b(OR|AND)\\b.*(=|>|<))",
        "--",                                  // SQL comments
        "#",                                   // MySQL comments
        "/\\*",                                 // Multi-line comments start
        "\\*/",                                // Multi-line comments end
        ";\\s*(SELECT|INSERT|UPDATE|DELETE)", // Multiple statements
    ]

    // MARK: - Public Methods

    /**
     * Санитизация текста сообщения (для AI чата)
     */
    func sanitizeMessage(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines)

        // Проверка длины
        guard trimmed.count >= minMessageLength else {
            throw SanitizationError.tooShort(minLength: minMessageLength)
        }
        guard trimmed.count <= maxMessageLength else {
            throw SanitizationError.tooLong(maxLength: maxMessageLength)
        }

        // Проверка на вредоносный контент
        try validateNoMaliciousContent(trimmed)

        // Очистка от потенциально опасных символов
        let sanitized = removePotentiallyDangerousCharacters(trimmed)

        #if DEBUG
        print("🛡️ InputSanitizer: Сообщение санитизировано (\(input.count) -> \(sanitized.count) символов)")
        #endif

        os_log("🛡️ Message sanitized: %d -> %d chars", log: Self.sanitizerLogger, type: .info, input.count, sanitized.count)

        return sanitized
    }

    /**
     * Санитизация имени
     */
    func sanitizeName(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines)

        // Проверка длины
        guard trimmed.count >= minNameLength else {
            throw SanitizationError.tooShort(minLength: minNameLength)
        }
        guard trimmed.count <= maxNameLength else {
            throw SanitizationError.tooLong(maxLength: maxNameLength)
        }

        // Проверка на вредоносный контент
        try validateNoMaliciousContent(trimmed)

        // Разрешаем только буквы, пробелы, дефисы, апострофы
        let allowedCharacterSet = CharacterSet.letters.union(.whitespaces).union(CharacterSet(charactersIn: "-'"))
        let filtered = trimmed.filter { allowedCharacterSet.contains($0.unicodeScalars.first!) }

        guard !filtered.isEmpty else {
            throw SanitizationError.containsInvalidCharacters
        }

        #if DEBUG
        print("🛡️ InputSanitizer: Имя санитизировано: '\(filtered)'")
        #endif

        return filtered
    }

    /**
     * Санитизация email адреса
     */
    func sanitizeEmail(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()

        // Проверка длины
        guard trimmed.count <= maxEmailLength else {
            throw SanitizationError.tooLong(maxLength: maxEmailLength)
        }

        // Проверка формата email
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)

        guard emailPredicate.evaluate(with: trimmed) else {
            throw SanitizationError.invalidEmail
        }

        // Проверка на вредоносный контент
        try validateNoMaliciousContent(trimmed)

        #if DEBUG
        print("🛡️ InputSanitizer: Email санитизирован: '\(trimmed)'")
        #endif

        return trimmed
    }

    /**
     * Санитизация номера телефона
     */
    func sanitizePhone(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines)

        // Проверка длины
        guard trimmed.count <= maxPhoneLength else {
            throw SanitizationError.tooLong(maxLength: maxPhoneLength)
        }

        // Очистка от всех нецифровых символов кроме +
        let digitsOnly = trimmed.filter { $0.isNumber || $0 == "+" }

        // Проверка, что начинается с + или цифры
        guard !digitsOnly.isEmpty, digitsOnly.first == "+" || digitsOnly.first!.isNumber else {
            throw SanitizationError.invalidPhone
        }

        // Проверка минимальной длины (без учета +)
        let digitsCount = digitsOnly.filter { $0.isNumber }.count
        guard digitsCount >= 7 else { // Минимум 7 цифр для международного формата
            throw SanitizationError.tooShort(minLength: 7)
        }

        #if DEBUG
        print("🛡️ InputSanitizer: Телефон санитизирован: '\(digitsOnly)'")
        #endif

        return digitsOnly
    }

    /**
     * Санитизация кода восстановления
     */
    func sanitizeRecoveryCode(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()

        // Проверка длины
        guard trimmed.count >= minRecoveryCodeLength else {
            throw SanitizationError.tooShort(minLength: minRecoveryCodeLength)
        }
        guard trimmed.count <= maxRecoveryCodeLength else {
            throw SanitizationError.tooLong(maxLength: maxRecoveryCodeLength)
        }

        // Разрешаем только буквы и цифры
        let allowedCharacterSet = CharacterSet.alphanumerics
        let filtered = trimmed.filter { allowedCharacterSet.contains($0.unicodeScalars.first!) }

        guard filtered.count == trimmed.count else {
            throw SanitizationError.containsInvalidCharacters
        }

        #if DEBUG
        print("🛡️ InputSanitizer: Код восстановления санитизирован")
        #endif

        return filtered
    }

    /**
     * Санитизация ID семьи
     */
    func sanitizeFamilyId(_ input: String) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()

        // Проверка длины
        guard trimmed.count >= minFamilyIdLength else {
            throw SanitizationError.tooShort(minLength: minFamilyIdLength)
        }
        guard trimmed.count <= maxFamilyIdLength else {
            throw SanitizationError.tooLong(maxLength: maxFamilyIdLength)
        }

        // Разрешаем только буквы и цифры
        let allowedCharacterSet = CharacterSet.alphanumerics
        let filtered = trimmed.filter { allowedCharacterSet.contains($0.unicodeScalars.first!) }

        guard filtered.count == trimmed.count else {
            throw SanitizationError.containsInvalidCharacters
        }

        #if DEBUG
        print("🛡️ InputSanitizer: ID семьи санитизирован")
        #endif

        return filtered
    }

    /**
     * Санитизация произвольного текста (для поиска, фильтров и т.д.)
     */
    func sanitizeText(_ input: String, maxLength: Int = 500) throws -> String {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines)

        // Проверка длины
        guard trimmed.count <= maxLength else {
            throw SanitizationError.tooLong(maxLength: maxLength)
        }

        // Проверка на вредоносный контент
        try validateNoMaliciousContent(trimmed)

        // Очистка от потенциально опасных символов
        let sanitized = removePotentiallyDangerousCharacters(trimmed)

        return sanitized
    }

    // MARK: - Private Methods

    /**
     * Проверка на вредоносный контент
     */
    private func validateNoMaliciousContent(_ input: String) throws {
        let lowercased = input.lowercased()

        // Проверка XSS паттернов
        for pattern in maliciousPatterns {
            let regex = try NSRegularExpression(pattern: pattern, options: [.caseInsensitive, .dotMatchesLineSeparators])
            let matches = regex.matches(in: lowercased, options: [], range: NSRange(location: 0, length: lowercased.count))
            if !matches.isEmpty {
                os_log("🚨 Malicious content detected (XSS): %{public}@", log: Self.sanitizerLogger, type: .error, pattern)
                throw SanitizationError.containsMaliciousContent
            }
        }

        // Проверка SQL injection паттернов
        for pattern in sqlInjectionPatterns {
            let regex = try NSRegularExpression(pattern: pattern, options: [.caseInsensitive])
            let matches = regex.matches(in: lowercased, options: [], range: NSRange(location: 0, length: lowercased.count))
            if !matches.isEmpty {
                os_log("🚨 Malicious content detected (SQLi): %{public}@", log: Self.sanitizerLogger, type: .error, pattern)
                throw SanitizationError.containsMaliciousContent
            }
        }
    }

    /**
     * Удаление потенциально опасных символов
     */
    private func removePotentiallyDangerousCharacters(_ input: String) -> String {
        var result = input

        // Удаляем или экранируем опасные символы
        let dangerousChars = ["<", ">", "\"", "'", "&", "|", ";", "`", "$", "(", ")", "{", "}", "[", "]"]
        for char in dangerousChars {
            result = result.replacingOccurrences(of: char, with: "")
        }

        return result
    }
}

// MARK: - String Extensions

extension String {

    /**
     * Санитизация сообщения
     */
    func sanitizedAsMessage() throws -> String {
        return try InputSanitizer.shared.sanitizeMessage(self)
    }

    /**
     * Санитизация имени
     */
    func sanitizedAsName() throws -> String {
        return try InputSanitizer.shared.sanitizeName(self)
    }

    /**
     * Санитизация email
     */
    func sanitizedAsEmail() throws -> String {
        return try InputSanitizer.shared.sanitizeEmail(self)
    }

    /**
     * Санитизация телефона
     */
    func sanitizedAsPhone() throws -> String {
        return try InputSanitizer.shared.sanitizePhone(self)
    }

    /**
     * Санитизация кода восстановления
     */
    func sanitizedAsRecoveryCode() throws -> String {
        return try InputSanitizer.shared.sanitizeRecoveryCode(self)
    }

    /**
     * Санитизация ID семьи
     */
    func sanitizedAsFamilyId() throws -> String {
        return try InputSanitizer.shared.sanitizeFamilyId(self)
    }

    /**
     * Санитизация текста
     */
    func sanitizedAsText(maxLength: Int = 500) throws -> String {
        return try InputSanitizer.shared.sanitizeText(self, maxLength: maxLength)
    }
}