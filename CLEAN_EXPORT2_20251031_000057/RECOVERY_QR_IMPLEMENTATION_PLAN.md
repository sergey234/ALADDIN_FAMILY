# 🎯 ПЛАН: Реализация Recovery Code Modal и QR Scanner

## 📋 ЗАДАЧИ:

### ✅ ЗАДАЧА 1: Создать RecoveryCodeModal

**Что должно быть:**
1. Показать Recovery Code (FAM-A1B2-C3D4-E5F6)
2. Показать QR-код, сгенерированный из кода
3. Кнопка "Копировать код"
4. Кнопка "Поделиться"
5. Красивый дизайн в стиле ALADDIN

**Технологии:**
- CoreImage для генерации QR-кода
- UIPasteboard для копирования
- UIActivityViewController для шаринга

**Файл:** `Shared/Components/Modals/RecoveryCodeModal.swift`

---

### ✅ ЗАДАЧА 2: Обновить QRScannerModal

**Что должно быть:**
1. Реальная камера (AVFoundation)
2. Распознавание QR-кодов (Vision framework)
3. Автоматическая обработка распознанного кода
4. Открытие InvitationCodeInputModal после распознавания
5. Haptic feedback при распознавании

**Технологии:**
- AVCaptureSession для камеры
- VNDetectBarcodesRequest для распознавания
- Обработка разрешений камеры

**Файл:** `Shared/Components/Modals/QRScannerModal.swift` (обновить)

---

### ✅ ЗАДАЧА 3: Интегрировать в процесс регистрации

**Что должно быть:**
1. После создания семьи → показать RecoveryCodeModal
2. В AddMemberOptionsModal → вариант 3 открывает рабочий QRScannerModal
3. После сканирования → автоматически заполнить InvitationCodeInputModal

**Файлы для изменения:**
- `ViewModels/FamilyRegistrationViewModel.swift` (добавить показ RecoveryCodeModal)
- `Shared/Components/Modals/AddMemberOptionsModal.swift` (обновить навигацию)
- `Screens/MainScreenWithRegistration.swift` (показывать RecoveryCodeModal вместо простого текста)

---

## 🚀 ПОШАГОВЫЙ ПЛАН:

### **ЭТАП 1: Создать RecoveryCodeModal** (10 минут)
- Создать файл `RecoveryCodeModal.swift`
- Реализовать генерацию QR-кода
- Добавить кнопки копирования и шаринга
- Применить стиль ALADDIN

### **ЭТАП 2: Обновить QRScannerModal** (15 минут)
- Заменить placeholder на реальную камеру
- Добавить AVFoundation и Vision
- Реализовать распознавание QR-кодов
- Добавить обработку ошибок и разрешений

### **ЭТАП 3: Интегрировать в процесс** (5 минут)
- Обновить FamilyRegistrationViewModel
- Показывать RecoveryCodeModal после создания семьи
- Обновить AddMemberOptionsModal для работы с QR

### **ЭТАП 4: Тестирование** (5 минут)
- Проверить генерацию QR-кода
- Проверить копирование и шаринг
- Проверить сканирование QR
- Проверить интеграцию с InvitationCodeInputModal

---

## ⏱️ ВРЕМЯ ВЫПОЛНЕНИЯ: ~35 минут

## ✅ РЕЗУЛЬТАТ:
- RecoveryCodeModal: Полноценное модальное окно с QR-кодом, копированием и шарингом
- QRScannerModal: Рабочий сканер QR-кодов с камерой
- Интеграция: Всё работает в едином процессе регистрации
- Компиляция: Все файлы добавлены в Xcode, ошибок нет

---

## 🎯 ГОТОВЫ НАЧАТЬ?
