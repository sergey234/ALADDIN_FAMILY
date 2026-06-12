import Foundation
import UIKit

/**
 * 🛡️ Log Sanitizer - Защита чувствительных данных в логах
 *
 * Автоматически маскирует:
 * - JWT токены
 * - Email адреса
 * - Номера кредитных карт
 * - Пароли и PIN
 * - API ключи
 * - Номера телефонов
 *
 * Используется MasterLogger для безопасного логирования.
 */
class LogSanitizer {

    // MARK: - String Sanitization

    /// Санитизация строки от чувствительных данных
    static func sanitizeString(_ input: String) -> String {
        // 🔒 ЗАЩИТА: Ограничить длину входной строки
        let safeInput = input.count > 10000 ? String(input.prefix(10000)) + "..." : input

        var result = safeInput

        // 🔒 ЗАЩИТА: Try-catch вокруг каждого метода санитизации
        do {
            // 1. JWT токены (eyJ... алгоритм)
            result = try sanitizeJWT(result)
        } catch {
            print("⚠️ LogSanitizer.JWT error: \(error.localizedDescription)")
        }

        do {
            // 2. Email адреса
            result = try sanitizeEmail(result)
        } catch {
            print("⚠️ LogSanitizer.Email error: \(error.localizedDescription)")
        }

        do {
            // 3. Номера кредитных карт
            result = try sanitizeCreditCard(result)
        } catch {
            print("⚠️ LogSanitizer.CreditCard error: \(error.localizedDescription)")
        }

        do {
            // 4. Номера телефонов
            result = try sanitizePhone(result)
        } catch {
            print("⚠️ LogSanitizer.Phone error: \(error.localizedDescription)")
        }

        do {
            // 5. Пароли (password, pwd, pin)
            result = try sanitizePasswords(result)
        } catch {
            print("⚠️ LogSanitizer.Password error: \(error.localizedDescription)")
        }

        do {
            // 6. API ключи
            result = try sanitizeAPIKeys(result)
        } catch {
            print("⚠️ LogSanitizer.APIKeys error: \(error.localizedDescription)")
        }

        return result
    }

    // MARK: - JWT Tokens

    private static func sanitizeJWT(_ input: String) throws -> String {
        // JWT паттерн: header.payload.signature
        let jwtPattern = #"eyJ[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*"#
        return input.replacingOccurrences(of: jwtPattern, with: "<jwt-token>", options: .regularExpression)
    }

    // MARK: - Email

    private static func sanitizeEmail(_ input: String) throws -> String {
        let emailPattern = #"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"#
        return input.replacingOccurrences(of: emailPattern, with: "***@***.***", options: .regularExpression)
    }

    // MARK: - Credit Cards

    private static func sanitizeCreditCard(_ input: String) throws -> String {
        // Visa, Mastercard, Amex паттерны
        let patterns = [
            #"4[0-9]{12}(?:[0-9]{3})?"#,  // Visa
            #"5[1-5][0-9]{14}"#,         // Mastercard
            #"3[47][0-9]{13}"#,          // Amex
            #"6(?:011|5[0-9]{2})[0-9]{12}"# // Discover
        ]

        var result = input
        for pattern in patterns {
            // Находим все совпадения и маскируем каждое
            let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive])
            if let regex = regex {
                let matches = regex.matches(in: result, options: [], range: NSRange(location: 0, length: result.count))
                for match in matches.reversed() {
                    if let range = Range(match.range, in: result) {
                        let matchedText = String(result[range])
                        let masked = maskCreditCard(matchedText)
                        result = result.replacingOccurrences(of: matchedText, with: masked)
                    }
                }
            }
        }

        return result
    }

    private static func maskCreditCard(_ cardNumber: String) -> String {
        let cleanNumber = cardNumber.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
        guard cleanNumber.count >= 4 else { return "****" }

        let last4 = String(cleanNumber.suffix(4))
        return "**** **** **** \(last4)"
    }

    // MARK: - Phone Numbers

    private static func sanitizePhone(_ input: String) throws -> String {
        // Российские номера: +7, 8, и международные
        let phonePatterns = [
            #"\+7[0-9]{10}"#,           // +7XXXXXXXXXX
            #"8[0-9]{10}"#,             // 8XXXXXXXXXX
            #"\+[1-9][0-9]{7,14}"#      // Международные номера
        ]

        var result = input
        for pattern in phonePatterns {
            result = result.replacingOccurrences(of: pattern, with: "***-***-****", options: .regularExpression)
        }

        return result
    }

    // MARK: - Passwords

    private static func sanitizePasswords(_ input: String) throws -> String {
        var result = input

        // Пароли в JSON и формах
        let passwordKeys = ["password", "pwd", "pass", "pin", "cvv", "secret"]
        for key in passwordKeys {
            let patterns = [
                #""\#(key)"\s*:\s*"[^"]*""#,     // JSON: "password": "value"
                #""\#(key)"\s*:\s*'[^']*'"#,     // JSON: "password": 'value'
                #"\#(key)=\w+"#,                 // Form: password=value
                #"\#(key):\s*\w+"#               // Form: password: value
            ]

            for pattern in patterns {
                result = result.replacingOccurrences(of: pattern, with: "\"\(key)\": \"<redacted>\"", options: .regularExpression)
            }
        }

        return result
    }

    // MARK: - API Keys

    private static func sanitizeAPIKeys(_ input: String) throws -> String {
        var result = input

        // API ключи в заголовках и параметрах
        let apiKeyPatterns = [
            #"x-api-key\s*:\s*\w+"#,
            #"authorization\s*:\s*bearer\s+\w+"#,
            #"api[_-]?key\s*[:=]\s*\w+"#,
            #"client[_-]?secret\s*[:=]\s*\w+"#
        ]

        for pattern in apiKeyPatterns {
            result = result.replacingOccurrences(of: pattern, with: "<api-key-redacted>", options: .regularExpression)
        }

        return result
    }

    // MARK: - Headers Sanitization

    /// Санитизация HTTP заголовков
    static func sanitizeHeaders(_ headers: [String: String]) -> [String: String] {
        var sanitized = headers

        // Список чувствительных заголовков
        let sensitiveHeaders = [
            "authorization",
            "x-api-key",
            "x-auth-token",
            "x-client-secret",
            "cookie",
            "set-cookie",
            "x-csrf-token",
            "x-xsrf-token"
        ]

        for (key, value) in headers {
            if sensitiveHeaders.contains(key.lowercased()) {
                sanitized[key] = "<redacted>"
            } else {
                // Санитизация значения даже для нечувствительных заголовков
                sanitized[key] = sanitizeString(value)
            }
        }

        return sanitized
    }

    // MARK: - JSON Sanitization

    /// Санитизация JSON строки
    static func sanitizeJSON(_ jsonString: String) -> String {
        guard let data = jsonString.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            // Если не JSON, санитизировать как обычную строку
            return sanitizeString(jsonString)
        }

        let sanitized = sanitizeJSONObject(json)

        // Сериализация обратно в JSON
        if let data = try? JSONSerialization.data(withJSONObject: sanitized, options: .prettyPrinted),
           let result = String(data: data, encoding: .utf8) {
            return result
        }

        return "<json-sanitized>"
    }

    /// Рекурсивная санитизация JSON объекта
    private static func sanitizeJSONObject(_ object: Any) -> Any {
        if let dict = object as? [String: Any] {
            var result = [String: Any]()

            for (key, value) in dict {
                let lowerKey = key.lowercased()

                // Полностью чувствительные поля
                if ["password", "pin", "cvv", "secret", "token", "refresh_token", "access_token"].contains(lowerKey) {
                    result[key] = "<redacted>"
                }
                // Частично чувствительные поля
                else if lowerKey == "email" {
                    result[key] = "***@***.***"
                }
                else if lowerKey == "phone" || lowerKey == "phone_number" {
                    result[key] = "***-***-****"
                }
                else if lowerKey.contains("card") && lowerKey.contains("number") {
                    if let cardValue = value as? String {
                        result[key] = maskCreditCard(cardValue)
                    } else {
                        result[key] = value
                    }
                }
                else {
                    // Рекурсивная обработка вложенных объектов
                    result[key] = sanitizeJSONObject(value)
                }
            }

            return result
        }
        else if let array = object as? [Any] {
            return array.map { sanitizeJSONObject($0) }
        }
        else if let string = object as? String {
            return sanitizeString(string)
        }
        else {
            return object
        }
    }

    // MARK: - URL Sanitization

    /// Санитизация URL с параметрами
    static func sanitizeURL(_ url: String) -> String {
        var result = url

        // Санитизация query параметров
        if let urlComponents = URLComponents(string: url) {
            var sanitizedComponents = urlComponents

            if let queryItems = urlComponents.queryItems {
                sanitizedComponents.queryItems = queryItems.map { item in
                    var newItem = item

                    // Санитизация чувствительных параметров
                    if ["token", "key", "secret", "password", "api_key"].contains(item.name.lowercased()) {
                        newItem.value = "<redacted>"
                    } else if let value = item.value {
                        newItem.value = sanitizeString(value)
                    }

                    return newItem
                }
            }

            if let sanitizedURL = sanitizedComponents.url?.absoluteString {
                result = sanitizedURL
            }
        }

        return result
    }
}

// MARK: - SF Symbol fallbacks (iOS 17+, fix-sf)

enum SFSymbolCompat {
    static func resolve(_ preferred: String, fallback: String) -> String {
        if UIImage(systemName: preferred) != nil { return preferred }
        return fallback
    }

    static var joinDevice: String {
        resolve("iphone.and.arrow.forward.inward", fallback: "iphone.and.arrow.forward")
    }

    static var voiceNotes: String {
        resolve("waveform.badge.mic", fallback: "waveform")
    }
}