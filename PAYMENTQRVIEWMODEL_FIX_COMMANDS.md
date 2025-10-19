# PAYMENTQRVIEWMODEL FIX COMMANDS - КОМАНДЫ ДЛЯ ИСПРАВЛЕНИЯ

## 🎯 ЦЕЛЬ
Исправить все ошибки в `ViewModels/PaymentQRViewModel.swift` без удаления файла

## 📋 ТЕКУЩИЕ ОШИБКИ
1. `declaration is only valid at file scope` (строка 356)
2. `cannot find type 'AnyCancellable' in scope` (строка 153)
3. `cannot find type 'AnyPublisher' in scope` (строка 366)
4. `cannot find type 'PaymentMethod' in scope` (строка 363)
5. `cannot find type 'MerchantInfo' in scope` (строка 364)

## 🔧 КОМАНДЫ ИСПРАВЛЕНИЯ

### Шаг 1: Добавить недостающие импорты
```bash
# Добавляем импорт Combine после Foundation
sed -i '' '/import Foundation/a\
import Combine\
import SwiftUI' ViewModels/PaymentQRViewModel.swift
```

### Шаг 2: Найти конец класса PaymentQRViewModel
```bash
# Ищем конец класса
grep -n "class PaymentQRViewModel\|^}" ViewModels/PaymentQRViewModel.swift | tail -3
```

### Шаг 3: Переместить extension APIService после класса
```bash
# Удаляем extension из текущего места (после строки 355)
sed -i '' '356,434d' ViewModels/PaymentQRViewModel.swift

# Добавляем extension в правильное место (после класса)
cat >> ViewModels/PaymentQRViewModel.swift << 'EOF'

// MARK: - API Service Extension
extension APIService {
    
    /**
     * Создание QR-платежа
     */
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
    
    /**
     * Проверка статуса QR-платежа
     */
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

### Шаг 4: Проверить, что все типы определены
```bash
# Проверяем, что PaymentMethod определен
grep -n "enum PaymentMethod" ViewModels/PaymentQRViewModel.swift

# Проверяем, что MerchantInfo определен
grep -n "struct MerchantInfo" ViewModels/PaymentQRViewModel.swift
```

### Шаг 5: Тестирование
```bash
# Запускаем сборку и проверяем ошибки
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "PaymentQRViewModel" | grep "error:" | head -5
```

## 🧪 ПОЛНЫЙ АЛГОРИТМ ИСПРАВЛЕНИЯ

```bash
#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ PAYMENTQRVIEWMODEL"

# Шаг 1: Добавляем импорты
echo "1. Добавляем импорты..."
sed -i '' '/import Foundation/a\
import Combine\
import SwiftUI' ViewModels/PaymentQRViewModel.swift

# Шаг 2: Находим конец класса
echo "2. Находим конец класса..."
CLASS_END=$(grep -n "class PaymentQRViewModel\|^}" ViewModels/PaymentQRViewModel.swift | tail -1 | cut -d: -f1)
echo "Класс заканчивается на строке: $CLASS_END"

# Шаг 3: Удаляем extension из неправильного места
echo "3. Удаляем extension из неправильного места..."
sed -i '' '356,434d' ViewModels/PaymentQRViewModel.swift

# Шаг 4: Добавляем extension в правильное место
echo "4. Добавляем extension в правильное место..."
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

# Шаг 5: Тестируем
echo "5. Тестируем исправления..."
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "PaymentQRViewModel" | grep "error:" | head -5

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО"
```

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **НЕ УДАЛЯТЬ ФАЙЛ** - файл содержит важную функциональность
2. **СОЗДАТЬ РЕЗЕРВНУЮ КОПИЮ** перед исправлениями
3. **ТЕСТИРОВАТЬ ПОСЛЕ КАЖДОГО ШАГА** - проверять результат
4. **СОХРАНЯТЬ ФУНКЦИОНАЛЬНОСТЬ** - не нарушать существующую логику

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения всех команд:
- ✅ Все ошибки компиляции исправлены
- ✅ Файл компилируется без ошибок
- ✅ Функциональность работает корректно
- ✅ Архитектура соответствует принципам SOLID
