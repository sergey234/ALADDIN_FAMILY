# PAYMENTQRVIEWMODEL ML INSTRUCTIONS - ИНСТРУКЦИИ ДЛЯ ML МОДЕЛИ

## 🎯 ЗАДАЧА
Исправить все ошибки в файле `ViewModels/PaymentQRViewModel.swift` без удаления файла

## 📋 КОНТЕКСТ
- **Проект:** ALADDIN iOS Security App
- **Файл:** `ViewModels/PaymentQRViewModel.swift`
- **Размер:** 434 строки
- **Тип:** ViewModel (MVVM Architecture)
- **Статус:** КРИТИЧЕСКИЕ ОШИБКИ КОМПИЛЯЦИИ

## 🚨 ТЕКУЩИЕ ОШИБКИ

### 1. declaration is only valid at file scope
**Строка:** 356  
**Тип:** КРИТИЧЕСКАЯ  
**Описание:** `extension APIService` находится внутри класса `PaymentQRViewModel`  
**Решение:** Переместить extension на уровень файла (после класса)  

### 2. cannot find type 'AnyCancellable' in scope
**Строка:** 153  
**Тип:** КРИТИЧЕСКАЯ  
**Описание:** Отсутствует импорт `Combine`  
**Решение:** Добавить `import Combine` в начало файла  

### 3. cannot find type 'AnyPublisher' in scope
**Строка:** 366  
**Тип:** КРИТИЧЕСКАЯ  
**Описание:** Отсутствует импорт `Combine`  
**Решение:** Добавить `import Combine` в начало файла  

### 4. cannot find type 'PaymentMethod' in scope
**Строка:** 363  
**Тип:** КРИТИЧЕСКАЯ  
**Описание:** Тип `PaymentMethod` не найден в области видимости  
**Решение:** Убедиться, что тип определен в правильном месте  

### 5. cannot find type 'MerchantInfo' in scope
**Строка:** 364  
**Тип:** КРИТИЧЕСКАЯ  
**Описание:** Тип `MerchantInfo` не найден в области видимости  
**Решение:** Убедиться, что тип определен в правильном месте  

## 🔧 АЛГОРИТМ ИСПРАВЛЕНИЯ

### Шаг 1: Создать резервную копию
```bash
cp ViewModels/PaymentQRViewModel.swift ViewModels/PaymentQRViewModel.swift.backup
```

### Шаг 2: Добавить недостающие импорты
```bash
# Добавляем импорты после Foundation
sed -i '' '/import Foundation/a\
import Combine\
import SwiftUI' ViewModels/PaymentQRViewModel.swift
```

### Шаг 3: Найти конец класса PaymentQRViewModel
```bash
# Ищем конец класса
grep -n "class PaymentQRViewModel\|^}" ViewModels/PaymentQRViewModel.swift | tail -3
```

### Шаг 4: Переместить extension APIService
```bash
# Удаляем extension из текущего места (после строки 355)
sed -i '' '356,434d' ViewModels/PaymentQRViewModel.swift

# Добавляем extension в правильное место (после класса)
cat >> ViewModels/PaymentQRViewModel.swift << 'EOF'

// MARK: - API Service Extension
extension APIService {
    
    func createQRPayment(
        amount: Double,
        method: PaymentMethod,
        merchantInfo: MerchantInfo,
        networkManager: NetworkManager
    ) -> AnyPublisher<CreateQRPaymentResponse, APIError> {
        
        guard let url = URL(string: "\(baseURL)/api/payments/qr/create") else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        let request = CreateQRPaymentRequest(
            amount: amount,
            method: method,
            merchantInfo: merchantInfo
        )
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: APIError.encodingFailed(error))
                .eraseToAnyPublisher()
        }
        
        return networkManager.session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: CreateQRPaymentResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else {
                    return APIError.unknown(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    func checkQRPaymentStatus(
        paymentId: String,
        networkManager: NetworkManager
    ) -> AnyPublisher<CheckQRPaymentStatusResponse, APIError> {
        
        guard let url = URL(string: "\(baseURL)/api/payments/qr/status/\(paymentId)") else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        return networkManager.session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: CheckQRPaymentStatusResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else {
                    return APIError.unknown(error)
                }
            }
            .eraseToAnyPublisher()
    }
}
EOF
```

### Шаг 5: Тестирование
```bash
# Запускаем сборку и проверяем ошибки
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "PaymentQRViewModel" | grep "error:" | head -5
```

## 📊 СТРУКТУРА ФАЙЛА

### Импорты (строки 1-3)
```swift
import Foundation
import Combine    // ← ДОБАВИТЬ
import SwiftUI    // ← ДОБАВИТЬ
```

### Типы данных (строки 4-103)
- `APIError` (enum)
- `MerchantInfo` (struct)
- `CreateQRPaymentRequest` (struct)
- `CreateQRPaymentResponse` (struct)
- `QRCodeData` (struct)
- `CheckQRPaymentStatusResponse` (struct)
- `PaymentMethod` (enum)
- `PaymentMethodInfo` (struct)

### Основной класс (строки 111-352)
```swift
class PaymentQRViewModel: ObservableObject {
    // Свойства
    // Методы
    // Инициализаторы
}
```

### Extension APIService (после класса)
```swift
extension APIService {
    // Методы для работы с API
}
```

## ⚠️ КРИТИЧЕСКИЕ ЗАМЕЧАНИЯ

1. **НЕ УДАЛЯТЬ ФАЙЛ** - файл содержит важную функциональность
2. **СОЗДАТЬ РЕЗЕРВНУЮ КОПИЮ** перед исправлениями
3. **ИСПРАВЛЯТЬ ПО ОЧЕРЕДИ** - исправлять ошибки по одной
4. **ТЕСТИРОВАТЬ ПОСЛЕ КАЖДОГО ИСПРАВЛЕНИЯ** - проверять результат
5. **СОХРАНЯТЬ ФУНКЦИОНАЛЬНОСТЬ** - не нарушать существующую логику

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:
- ✅ Все ошибки компиляции исправлены
- ✅ Файл компилируется без ошибок
- ✅ Функциональность работает корректно
- ✅ Архитектура соответствует принципам SOLID

## 🚀 ГОТОВНОСТЬ К ИСПРАВЛЕНИЮ

**Статус:** ГОТОВ К ИСПРАВЛЕНИЮ  
**Сложность:** СРЕДНЯЯ  
**Время:** 15-30 минут  
**Риск:** НИЗКИЙ (файл не будет удален)  

## 📋 ПРОВЕРКА РЕЗУЛЬТАТА

После исправления выполнить:
```bash
# Проверка ошибок
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "PaymentQRViewModel" | grep "error:"

# Ожидаемый результат: пустой вывод (нет ошибок)
```

## 🔄 ВОССТАНОВЛЕНИЕ

В случае проблем:
```bash
# Восстановление из резервной копии
cp ViewModels/PaymentQRViewModel.swift.backup ViewModels/PaymentQRViewModel.swift
```
