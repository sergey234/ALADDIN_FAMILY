# 📷 КАК ФОРМИРУЮТСЯ QR-КОДЫ В ALADDIN

## 🎯 ДВА ТИПА QR-КОДОВ

### QR #1: Для добавления членов семьи (временный)
- **Срок жизни:** 24 часа
- **Генерируется:** По требованию (Настройки → Семья → Добавить члена)
- **Назначение:** Присоединение новых членов

### QR #2: Для восстановления доступа (постоянный)
- **Срок жизни:** ВЕЧНЫЙ
- **Генерируется:** При создании семьи (ОДИН РАЗ!)
- **Назначение:** Восстановление при потере телефона

---

## 🔑 QR #2: ПРОЦЕСС ГЕНЕРАЦИИ (ПРИ СОЗДАНИИ СЕМЬИ)

### ЭТАП 1: Пользователь создаёт семью

```
Onboarding → Роль (Родитель) → Возраст (24-55) → Буква (А) → [СОЗДАТЬ СЕМЬЮ]
```

### ЭТАП 2: Мобильное приложение → Backend

```
POST /api/family/create

Request:
{
  "role": "parent",
  "age_group": "24-55",
  "personal_letter": "А",
  "device_type": "smartphone"
}
```

### ЭТАП 3: Python Backend генерирует данные

**Файл:** `security/family/family_registration.py`

```python
def create_family(self, registration_data: RegistrationData) -> Dict[str, str]:
    # 1. Генерируем анонимный ID семьи
    family_id = self._generate_anonymous_family_id()
    # Результат: "FAM_A1B2C3D4E5F6"
    
    # 2. Генерируем QR-код данные
    qr_code_data = self._generate_qr_code(family_id)
    # Результат: '{"family_id":"FAM_A1B2C3D4E5F6","timestamp":1729512000,"type":"family_registration"}'
    
    # 3. Генерируем короткий код
    short_code = self._generate_short_code(family_id)
    # Результат: "AB12"
    
    return {
        'family_id': family_id,
        'qr_code_data': qr_code_data,
        'short_code': short_code,
        'creator_member_id': 'MEM_X1Y2Z3W4'
    }
```

#### Функция `_generate_qr_code()`:

```python
def _generate_qr_code(self, family_id: str) -> str:
    qr_data = {
        'family_id': family_id,           # "FAM_A1B2C3D4E5F6"
        'timestamp': int(time.time()),    # 1729512000
        'type': 'family_registration'     # Тип QR-кода
    }
    return json.dumps(qr_data, ensure_ascii=False)
```

**Результат:** Строка JSON для кодирования в QR-код

### ЭТАП 4: Backend форматирует код

```python
def format_recovery_code(family_id: str) -> str:
    # "FAM_A1B2C3D4E5F6" → "FAM-A1B2-C3D4-E5F6"
    cleaned = family_id.replace("FAM_", "")  # "A1B2C3D4E5F6"
    parts = [cleaned[i:i+4] for i in range(0, len(cleaned), 4)]  # ["A1B2", "C3D4", "E5F6"]
    return "FAM-" + "-".join(parts)  # "FAM-A1B2-C3D4-E5F6"
```

### ЭТАП 5: API возвращает данные приложению

```json
Response:
{
  "success": true,
  "family_id": "FAM_A1B2C3D4E5F6",
  "recovery_code": "FAM-A1B2-C3D4-E5F6",    ← Для показа человеку
  "qr_code_data": "{\"family_id\":\"FAM_A1B2C3D4E5F6\",\"timestamp\":1729512000,\"type\":\"family_registration\"}",
  "short_code": "AB12",
  "member_id": "MEM_X1Y2Z3W4"
}
```

### ЭТАП 6: iOS/Android создаёт QR-код картинку

#### iOS (SwiftUI):

```swift
func generateQRCode(from string: String) -> UIImage? {
    let context = CIContext()
    let filter = CIFilter.qrCodeGenerator()
    
    // Конвертируем строку в Data
    let data = Data(string.utf8)
    filter.setValue(data, forKey: "inputMessage")
    filter.setValue("H", forKey: "inputCorrectionLevel")  // Высокая коррекция
    
    if let outputImage = filter.outputImage {
        // Масштабируем 10x для чёткости
        let transform = CGAffineTransform(scaleX: 10, y: 10)
        let scaledImage = outputImage.transformed(by: transform)
        
        if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
            return UIImage(cgImage: cgImage)
        }
    }
    
    return nil
}
```

**ВХОД:** `'{"family_id":"FAM_A1B2C3D4E5F6",...}'`  
**ВЫХОД:** UIImage 180×180pt

```
┌─────────────────────┐
│ ██  ██    ██  ██    │
│   ██  ████  ██      │
│ ██    ██  ██    ██  │  ← Чёрно-белый QR-код
│   ████    ████  ██  │
│ ██  ██  ██  ██  ██  │
│ ██      ████    ██  │
└─────────────────────┘
```

#### Android (Kotlin):

```kotlin
fun generateQRCode(text: String): Bitmap? {
    val writer = QRCodeWriter()
    val bitMatrix = writer.encode(
        text,
        BarcodeFormat.QR_CODE,
        512,  // width
        512   // height
    )
    
    val width = bitMatrix.width
    val height = bitMatrix.height
    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565)
    
    for (x in 0 until width) {
        for (y in 0 until height) {
            bitmap.setPixel(
                x, y,
                if (bitMatrix[x, y]) Color.BLACK else Color.WHITE
            )
        }
    }
    
    return bitmap
}
```

**Библиотека:** ZXing (Zebra Crossing) - `com.google.zxing:core:3.5.1`

### ЭТАП 7: Показывается пользователю

```
┌───────────────────────────────────────────────┐
│  🎉 СЕМЬЯ СОЗДАНА!                            │
│                                               │
│  🔑 Ваш код восстановления:                   │
│                                               │
│  ┌──────────────────────────┐                 │
│  │                          │                 │
│  │    [QR CODE IMAGE]       │  ← QR #2!       │
│  │                          │                 │
│  └──────────────────────────┘                 │
│                                               │
│  FAM-A1B2-C3D4-E5F6                           │
│                                               │
│  ⚠️ ВАЖНО: Сохраните этот код!                │
│                                               │
│  СПОСОБЫ СОХРАНЕНИЯ:                          │
│  [ ] 📋 Копировать                            │
│  [ ] 📸 Скриншот                              │
│  [ ] 💾 iCloud                                │
│  [ ] 📧 Email                                 │
│                                               │
│  [ПРОДОЛЖИТЬ] (выберите 1+ вариант)           │
└───────────────────────────────────────────────┘
```

---

## 📧 ОТПРАВКА QR-КОДА НА EMAIL

### ❓ НА КАКУЮ ПОЧТУ ОТПРАВЛЯЕТСЯ?

**ОТВЕТ: На почту, которую ВЫ вводите!**

### ПРОЦЕСС:

#### ШАГ 1: Пользователь выбирает Email

```
Окно #4 → Нажимаете на "📧 Email"
        ↓
Появляется поле ввода:
┌────────────────────────────────────┐
│ Введите email:                     │
│ ✉️ [sergej@example.com______]      │
└────────────────────────────────────┘
```

#### ШАГ 2: Вводит СВОЙ email

```
Вы вводите: sergej@example.com
           ✅ Это ВАША почта! Любая!
```

#### ШАГ 3: Приложение отправляет запрос

```
POST /api/family/send-recovery-email

Request:
{
  "email": "sergej@example.com",    ← ВАШ email!
  "family_id": "FAM_A1B2C3D4E5F6",
  "recovery_code": "FAM-A1B2-C3D4-E5F6",
  "qr_code_data": "{\"family_id\":\"FAM_A1B2C3D4E5F6\",...}"
}
```

#### ШАГ 4: Backend генерирует QR-код и отправляет письмо

```python
@app.post("/api/family/send-recovery-email")
async def send_recovery_email(request: SendRecoveryEmailRequest):
    # 1. Генерируем QR-код изображение
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(request.qr_code_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 2. Конвертируем в base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # 3. Отправляем письмо на sergej@example.com
    send_smtp_email(
        to=request.email,           # ← ВАША почта!
        subject="🔑 Код восстановления ALADDIN",
        html=email_html_with_qr_image
    )
    
    # 4. ✅ EMAIL НЕ СОХРАНЯЕТСЯ В БАЗЕ!
    # Письмо отправлено → email забыт
    
    return {
        "success": True,
        "message": "Email sent",
        "email_saved": False  # ✅ Подтверждаем!
    }
```

#### ШАГ 5: Вы получаете письмо

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
От: noreply@aladdin.family
Кому: sergej@example.com  ← ВАШ email!
Тема: 🔑 Код восстановления ALADDIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────┐
│  🔑 Код восстановления ALADDIN              │
│  Код восстановления вашей семьи             │
├─────────────────────────────────────────────┤
│                                             │
│  Ваш код восстановления:                    │
│  ┌──────────────────────────┐               │
│  │  FAM-A1B2-C3D4-E5F6      │               │
│  └──────────────────────────┘               │
│                                             │
│  Или отсканируйте QR-код:                   │
│  ┌──────────────────────────┐               │
│  │   [QR CODE IMAGE]        │               │
│  │   300×300px              │               │
│  └──────────────────────────┘               │
│                                             │
│  ⚠️ ВАЖНО: Храните этот код в безопасном    │
│  месте! Этот код нужен для восстановления   │
│  доступа к семье при потере телефона.       │
│                                             │
│  Как восстановить доступ:                   │
│  1. Установите ALADDIN на новом устройстве  │
│  2. Нажмите "ВОССТАНОВИТЬ"                  │
│  3. Выберите "Ввести код вручную"           │
│  4. Введите код: FAM-A1B2-C3D4-E5F6         │
│  5. Доступ восстановлен! ✅                 │
└─────────────────────────────────────────────┘
```

### ✅ ВАЖНО: EMAIL НЕ СОХРАНЯЕТСЯ!

```
Процесс:
1. Вы вводите: sergej@example.com
2. Backend отправляет письмо
3. Email УДАЛЯЕТСЯ из памяти
4. В базе данных НЕТ вашего email! ✅
```

**152-ФЗ соблюдён!** Мы не собираем персональные данные.

---

## 📱 QR #1: ГЕНЕРАЦИЯ КОДА ДЛЯ ПРИСОЕДИНЕНИЯ

### КОГДА ГЕНЕРИРУЕТСЯ:

```
Пользователь (уже в семье):
MainScreen → Настройки → Семья → [ДОБАВИТЬ ЧЛЕНА СЕМЬИ]
```

### ПРОЦЕСС:

#### ШАГ 1: Мобильное приложение → Backend

```
POST /api/family/generate-invitation-qr

Request:
{
  "family_id": "FAM_A1B2C3D4E5F6"
}
```

#### ШАГ 2: Backend генерирует временный QR

```python
def generate_invitation_qr(family_id: str) -> str:
    qr_data = {
        'family_id': family_id,           # "FAM_A1B2C3D4E5F6"
        'timestamp': int(time.time()),    # 1729512000
        'type': 'family_invitation',      # ← ДРУГОЙ тип!
        'expires_at': int(time.time()) + 86400  # +24 часа
    }
    return json.dumps(qr_data)
```

**Разница с QR #2:**
- `type`: `"family_invitation"` вместо `"family_registration"`
- `expires_at`: есть срок истечения (24 часа)

#### ШАГ 3: iOS/Android создаёт изображение

Та же функция `generateQRCode()`, но с другими данными:

**ВХОД:** `'{"family_id":"FAM_A1B2C3D4E5F6","type":"family_invitation","expires_at":1729598400}'`  
**ВЫХОД:** UIImage/Bitmap 180×180

#### ШАГ 4: Показывается в окне

```
┌────────────────────────────────────┐
│  👥 ДОБАВИТЬ ЧЛЕНА СЕМЬИ           │
│                                    │
│  Покажите этот QR-код новому       │
│  члену семьи для присоединения     │
│                                    │
│  ┌──────────────────────────┐      │
│  │                          │      │
│  │    [QR #1 ИЗОБРАЖЕНИЕ]   │      │
│  │                          │      │
│  └──────────────────────────┘      │
│                                    │
│  ⏱️ Действителен: 23ч 59мин        │
│                                    │
│  [ОБНОВИТЬ КОД]  [ЗАКРЫТЬ]        │
└────────────────────────────────────┘
```

### ШАГ 5: Новый член сканирует QR #1

```
Новый пользователь:
Onboarding → [У МЕНЯ ЕСТЬ КОД] → Сканирует QR #1
           ↓
Приложение декодирует:
{
  "family_id": "FAM_A1B2C3D4E5F6",
  "type": "family_invitation",
  "expires_at": 1729598400
}
           ↓
Проверяет:
✅ Тип = "family_invitation" (правильный!)
✅ expires_at > текущее время (не истёк!)
           ↓
Показывает окна: Роль → Возраст → Буква
           ↓
POST /api/family/join
           ↓
Присоединение к семье! ✅
```

---

## 📊 СРАВНЕНИЕ QR #1 vs QR #2

| Параметр | QR #1 (Invitation) | QR #2 (Recovery) |
|----------|-------------------|------------------|
| **Назначение** | Добавить члена семьи | Восстановить доступ |
| **Срок жизни** | 24 часа | Вечный |
| **Когда генерируется** | По требованию (многократно) | При создании семьи (1 раз!) |
| **Где генерируется** | Настройки → Добавить члена | Автоматически при создании |
| **Тип в JSON** | `family_invitation` | `family_registration` |
| **Есть `expires_at`?** | ✅ Да | ❌ Нет |
| **Можно обновить?** | ✅ Да ([ОБНОВИТЬ КОД]) | ❌ Нет (постоянный) |

---

## 🎨 ВИЗУАЛЬНОЕ ОТЛИЧИЕ

### QR #2 (Recovery):
```
Показывается в:
- Окно #4 "СЕМЬЯ СОЗДАНА!" (при создании)
- Email (если отправили)
- iCloud Drive (если сохранили)
- Скриншот в Фото (если сделали)

Цвет рамки: ЗОЛОТОЙ (#FCD34D)
Размер: 180×180pt
```

### QR #1 (Invitation):
```
Показывается в:
- Настройки → Семья → "Добавить члена"

Цвет рамки: СИНИЙ (#60A5FA)
Размер: 200×200pt
Таймер: ⏱️ 23ч 59мин
```

---

## 🔐 БЕЗОПАСНОСТЬ

### ✅ QR #2 безопасен, потому что:
- Генерируется ОДИН РАЗ
- Должен быть СОХРАНЁН пользователем
- Если потерян → нет восстановления (только через поддержку)

### ✅ QR #1 безопасен, потому что:
- Истекает через 24 часа
- Можно ОТМЕНИТЬ в любой момент
- Генерируется новый при каждом использовании

---

## 📧 EMAIL: ПОЛНЫЙ ПРОЦЕСС

### 1. Пользователь выбирает "📧 Email"

```
FamilyCreatedModal → Чекбокс "Email" → checked
                  ↓
Появляется поле:
┌────────────────────────────────────┐
│ Введите email:                     │
│ ✉️ [__________________________]    │
└────────────────────────────────────┘
```

### 2. Вводит свой email

```
Ввод: sergej@example.com
     ✅ Это ВАША почта!
     ✅ Любая почта, которую вы укажете!
```

### 3. Нажимает "ПРОДОЛЖИТЬ"

### 4. Приложение вызывает API

```swift
// iOS
func sendRecoveryEmail(email: String, familyID: String, recoveryCode: String, qrCodeData: String) {
    let request = SendRecoveryEmailRequest(
        email: email,
        familyID: familyID,
        recoveryCode: recoveryCode,
        qrCodeData: qrCodeData
    )
    
    APIService.shared.post("/api/family/send-recovery-email", body: request) { result in
        print("✅ Email sent to: \(email)")
    }
}
```

### 5. Backend создаёт QR-код и отправляет письмо

```python
# Python Backend
@app.post("/api/family/send-recovery-email")
async def send_recovery_email(request: SendRecoveryEmailRequest):
    # Генерируем QR-код картинку
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(request.qr_code_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Конвертируем в base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Отправляем красивое HTML письмо
    send_smtp_email(
        to=request.email,  # ← sergej@example.com
        subject="🔑 Код восстановления ALADDIN",
        html=email_template_with_qr_image
    )
    
    # ✅ EMAIL НЕ СОХРАНЯЕТСЯ!
    logger.info(f"✅ Email sent to: {request.email}")
    logger.info(f"⚠️ EMAIL НЕ СОХРАНЁН В БАЗЕ")
    
    return {
        "success": True,
        "email_saved": False  # ✅ Подтверждение!
    }
```

### 6. Вы получаете письмо

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Входящие → sergej@example.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

От: noreply@aladdin.family
Тема: 🔑 Код восстановления ALADDIN

[Красивое HTML письмо с:]
• Кодом: FAM-A1B2-C3D4-E5F6
• QR-кодом (изображение 300×300px)
• Инструкцией как восстановить
```

---

## ✅ РЕЗЮМЕ: ПРОСТЫМИ СЛОВАМИ

### QR-коды формируются так:

1. **Backend Python** генерирует JSON данные:
   ```json
   {"family_id":"FAM_A1B2C3D4E5F6","timestamp":1729512000,"type":"family_registration"}
   ```

2. **iOS/Android** превращает JSON в чёрно-белую картинку (QR-код)

3. **Показывает** пользователю на экране

### Email отправляется так:

1. **Вы вводите** свою почту: `sergej@example.com`

2. **Backend** создаёт QR-код картинку и отправляет красивое письмо

3. **Email НЕ сохраняется** в базе данных! ✅

4. **Вы получаете** письмо с кодом и QR-кодом

---

## 🔒 БЕЗОПАСНОСТЬ И СООТВЕТСТВИЕ ЗАКОНАМ

✅ **152-ФЗ (Россия):** Email не сохраняется → соответствует  
✅ **GDPR (Европа):** Минимальные данные → соответствует  
✅ **COPPA (США):** Анонимная система → соответствует

**Мы НЕ собираем персональные данные!** 🎯



