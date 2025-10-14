# 🤖 Как запустить Android приложение в Android Studio

## ✅ ШАГ 1: Открыть Android Studio

1. Откройте **Android Studio** (если нет - скачайте с https://developer.android.com)
2. Выберите: **File → New → New Project**

---

## ✅ ШАГ 2: Создать новый проект

1. Выберите **Empty Compose Activity**
2. Нажмите **Next**

3. Заполните параметры:
   - **Name**: `ALADDIN`
   - **Package name**: `family.aladdin.android`
   - **Save location**: `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_PROJECT`
   - **Language**: **Kotlin** ✅
   - **Minimum SDK**: **API 24 (Android 7.0)** ✅
   - **Build configuration language**: **Kotlin DSL**

4. Нажмите **Finish**

---

## ✅ ШАГ 3: Настроить build.gradle.kts

1. Откройте `app/build.gradle.kts`

2. Добавьте зависимости в блок `dependencies`:

```kotlin
dependencies {
    // Jetpack Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.activity:activity-compose:1.8.0")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.5")
    
    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
    
    // Retrofit (HTTP клиент)
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Gson
    implementation("com.google.code.gson:gson:2.10.1")
}
```

3. Нажмите **Sync Now** вверху справа

---

## ✅ ШАГ 4: Скопировать наши файлы

1. В Finder перейдите: `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/src/main/java/family/aladdin/android/`

2. **Удалите** из Android Studio проекта:
   - `ui/theme/` (старые файлы темы)
   - `MainActivity.kt` (старый, создался автоматически)

3. **Скопируйте** (Drag & Drop или Copy/Paste) в `app/src/main/java/family/aladdin/android/`:
   - Папку `ui/` → все наши файлы UI
   - Папку `viewmodels/` → все ViewModels
   - Папку `navigation/` → NavGraph
   - Папку `network/` → Retrofit + ApiService
   - Папку `repository/` → Repository
   - Папку `config/` → AppConfig
   - Папку `models/` → ApiModels
   - Файл `MainActivity.kt` → главный файл

---

## ✅ ШАГ 5: Настроить AndroidManifest.xml

1. Откройте `app/src/main/AndroidManifest.xml`

2. Добавьте **permissions** перед `<application>`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.VIBRATE" />
```

3. Добавьте `android:usesCleartextTraffic="true"` в тег `<application>` (для localhost):

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

---

## ✅ ШАГ 6: Добавить иконку приложения

1. Правый клик на `res` → **New → Image Asset**
2. Выберите **Launcher Icons**
3. **Path**: `/Users/sergejhlystov/ALADDIN_NEW/design/icon_variant_05.png`
4. Нажмите **Next** → **Finish**

---

## ✅ ШАГ 7: Настроить Python backend URL

1. Откройте файл: `config/AppConfig.kt`

2. Найдите строку:
   ```kotlin
   "http://10.0.2.2:8000/api"  // 10.0.2.2 для Android Emulator
   ```

3. Замените на URL вашего Python сервера:
   ```kotlin
   "http://YOUR_SERVER_IP:PORT/api"
   ```

   **Важно для Android Emulator:**
   - `10.0.2.2` = ваш `localhost` на Mac
   - Для реального устройства используйте IP адрес Mac в сети

---

## ✅ ШАГ 8: Запустить приложение!

1. Выберите **устройство** вверху:
   - **Emulator**: Pixel 7 API 34 (рекомендуется)
   - Или создайте новый: **Tools → Device Manager → Create Device**

2. Нажмите **▶️ Run** (или Shift + F10)

3. Подождите компиляции (~2-3 минуты первый раз)

4. Приложение запустится! 🎉

---

## 🎯 ЧТО УВИДИТЕ:

✅ **Онбординг** (4 слайда приветствия)  
✅ **Главный экран** с VPN и 4 функциями  
✅ **Все 14 экранов** работают  
✅ **Навигация** между экранами  
✅ **Material Design 3** дизайн  
✅ **Градиенты** и эффекты  

⚠️ **API данные** - заглушки (пока не подключён backend)

---

## 🔧 Если есть ошибки компиляции:

### Ошибка: "Unresolved reference: RetrofitClient"

**Решение:**
1. Проверьте что все зависимости добавлены в `build.gradle.kts`
2. Нажмите **File → Sync Project with Gradle Files**

### Ошибка: "Cannot access internet"

**Решение:**
- Убедитесь что добавили `<uses-permission android:name="android.permission.INTERNET" />` в AndroidManifest.xml
- Добавьте `android:usesCleartextTraffic="true"` для localhost

### Ошибка: Import errors

**Решение:**
- Все файлы должны быть в правильных пакетах: `package family.aladdin.android...`
- Проверьте что нет опечаток в imports

---

## 📱 Запуск на реальном Android устройстве:

1. Включите **Режим разработчика** на Android:
   - Настройки → О телефоне → 7 раз нажать на "Номер сборки"
2. Включите **Отладка по USB**:
   - Настройки → Для разработчиков → Отладка по USB
3. Подключите устройство USB кабелем к Mac
4. В Android Studio выберите ваше устройство вместо эмулятора
5. Нажмите **▶️ Run**
6. Приложение установится на ваш телефон! ✅

---

## 🎉 ГОТОВО!

После запуска вы увидите полноценное Android приложение!

**Для подключения к Python backend:**
- Измените URL в `AppConfig.kt`
- Убедитесь что ваш Python сервер запущен
- Проверьте что API endpoints соответствуют

**Приятного использования!** 🌟

---

## 📝 ВАЖНЫЕ ЗАМЕТКИ:

### Localhost на Android Emulator:
- `localhost` на Mac = `10.0.2.2` в Android Emulator
- На реальном устройстве используйте IP адрес Mac (например `192.168.1.100`)

### Проверка IP адреса Mac:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Разрешение CORS на Python backend:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```




