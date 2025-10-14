# ИЕРАРХИЯ КЛАССОВ AUTHENTICATION_MANAGER.PY

## 📊 СТРУКТУРА КЛАССОВ

### 1. **AuthMethod(Enum)** - Методы аутентификации
- **Базовый класс**: Enum
- **Назначение**: Определяет доступные методы аутентификации
- **Значения**: PASSWORD, BIOMETRIC, MFA, SSO

### 2. **AuthStatus(Enum)** - Статусы аутентификации  
- **Базовый класс**: Enum
- **Назначение**: Определяет статусы аутентификации
- **Значения**: SUCCESS, FAILED, LOCKED, EXPIRED

### 3. **SecurityLevel(Enum)** - Уровни безопасности
- **Базовый класс**: Enum
- **Назначение**: Определяет уровни безопасности
- **Значения**: LOW, MEDIUM, HIGH, CRITICAL

### 4. **UserCredentials** - Учетные данные пользователя
- **Базовый класс**: dataclass
- **Назначение**: Хранение учетных данных пользователя
- **Атрибуты**: username, password_hash, salt, created_at, last_login

### 5. **AuthSession** - Сессия аутентификации
- **Базовый класс**: dataclass
- **Назначение**: Управление сессиями пользователей
- **Атрибуты**: session_id, username, auth_method, created_at, expires_at

### 6. **AuthResult** - Результат аутентификации
- **Базовый класс**: dataclass
- **Назначение**: Результат операции аутентификации
- **Атрибуты**: success, message, session_id, user_info

### 7. **AuthPolicy** - Политика безопасности
- **Базовый класс**: dataclass
- **Назначение**: Настройки политики безопасности
- **Атрибуты**: min_password_length, max_failed_attempts, session_timeout_minutes

### 8. **AuthenticationManager** - Основной менеджер
- **Базовый класс**: object
- **Назначение**: Главный класс для управления аутентификацией
- **Атрибуты**: users, sessions, policy, audit_log

## 🔗 СВЯЗИ МЕЖДУ КЛАССАМИ

```
AuthenticationManager
├── использует AuthPolicy для настроек
├── управляет UserCredentials для пользователей
├── создает AuthSession для сессий
├── возвращает AuthResult для результатов
├── использует AuthMethod для методов
├── использует AuthStatus для статусов
└── использует SecurityLevel для уровней
```

## 📈 НАСЛЕДОВАНИЕ

- **Enum классы**: AuthMethod, AuthStatus, SecurityLevel наследуются от Enum
- **Dataclass классы**: UserCredentials, AuthSession, AuthResult, AuthPolicy наследуются от dataclass
- **Основной класс**: AuthenticationManager наследуется от object

## 🎯 ПОЛИМОРФИЗМ

- Все Enum классы поддерживают полиморфизм через общий интерфейс Enum
- Dataclass классы поддерживают полиморфизм через общий интерфейс dataclass
- AuthenticationManager может работать с любыми типами Enum значений