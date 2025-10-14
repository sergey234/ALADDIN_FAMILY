#!/bin/bash

# ALADDIN Mobile CI/CD Setup Script
# Настройка автоматической сборки и развертывания

set -e

echo "🚀 ALADDIN Mobile CI/CD Setup"
echo "=============================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    # Проверка Git
    if ! command -v git &> /dev/null; then
        error "Git не установлен"
        exit 1
    fi
    success "Git найден"
    
    # Проверка Docker (для контейнеризации)
    if command -v docker &> /dev/null; then
        success "Docker найден"
    else
        warning "Docker не найден - некоторые функции могут быть недоступны"
    fi
    
    # Проверка Node.js (для веб-интерфейсов)
    if command -v node &> /dev/null; then
        success "Node.js найден"
    else
        warning "Node.js не найден - веб-интерфейсы могут не работать"
    fi
}

# Настройка GitHub Actions
setup_github_actions() {
    log "Настройка GitHub Actions..."
    
    # Создание директории для workflows
    mkdir -p .github/workflows
    
    # Проверка существования workflow файлов
    if [ -f ".github/workflows/ios-build.yml" ]; then
        success "iOS build workflow найден"
    else
        error "iOS build workflow не найден"
        exit 1
    fi
    
    if [ -f ".github/workflows/android-build.yml" ]; then
        success "Android build workflow найден"
    else
        error "Android build workflow не найден"
        exit 1
    fi
    
    if [ -f ".github/workflows/mobile-deploy.yml" ]; then
        success "Mobile deploy workflow найден"
    else
        error "Mobile deploy workflow не найден"
        exit 1
    fi
    
    success "GitHub Actions настроены"
}

# Настройка iOS проекта
setup_ios_project() {
    log "Настройка iOS проекта..."
    
    cd mobile/ios
    
    # Проверка Xcode проекта
    if [ -f "ALADDINMobile.xcodeproj/project.pbxproj" ]; then
        success "Xcode проект найден"
    else
        error "Xcode проект не найден"
        exit 1
    fi
    
    # Создание Podfile если не существует
    if [ ! -f "Podfile" ]; then
        cat > Podfile << EOF
platform :ios, '14.0'
use_frameworks!

target 'ALADDINMobile' do
  # Основные зависимости
  pod 'Alamofire', '~> 5.8'
  pod 'SwiftyJSON', '~> 5.0'
  pod 'KeychainAccess', '~> 4.2'
  pod 'BiometricAuthentication', '~> 3.1'
  
  # UI компоненты
  pod 'SnapKit', '~> 5.6'
  pod 'Charts', '~> 4.1'
  pod 'Lottie', '~> 4.3'
  
  # Сеть и API
  pod 'Moya', '~> 15.0'
  pod 'RxSwift', '~> 6.6'
  pod 'RxCocoa', '~> 6.6'
  
  # Безопасность
  pod 'CryptoSwift', '~> 1.8'
  pod 'RNCryptor', '~> 5.0'
  
  # Аналитика
  pod 'Firebase/Analytics', '~> 10.0'
  pod 'Firebase/Crashlytics', '~> 10.0'
  
  target 'ALADDINMobileTests' do
    inherit! :search_paths
    pod 'Quick', '~> 7.0'
    pod 'Nimble', '~> 12.0'
  end
end
EOF
        success "Podfile создан"
    else
        success "Podfile уже существует"
    fi
    
    # Установка зависимостей
    if command -v pod &> /dev/null; then
        log "Установка CocoaPods зависимостей..."
        pod install
        success "CocoaPods зависимости установлены"
    else
        warning "CocoaPods не найден - зависимости не установлены"
    fi
    
    cd ../..
    success "iOS проект настроен"
}

# Настройка Android проекта
setup_android_project() {
    log "Настройка Android проекта..."
    
    cd mobile/android
    
    # Проверка Gradle проекта
    if [ -f "build.gradle" ]; then
        success "Gradle проект найден"
    else
        error "Gradle проект не найден"
        exit 1
    fi
    
    # Создание gradlew если не существует
    if [ ! -f "gradlew" ]; then
        log "Создание Gradle wrapper..."
        gradle wrapper --gradle-version 8.4
        success "Gradle wrapper создан"
    else
        success "Gradle wrapper уже существует"
    fi
    
    # Создание keystore для подписи
    if [ ! -f "keystore.jks" ]; then
        log "Создание keystore для подписи..."
        keytool -genkey -v -keystore keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias aladdin-key -storepass aladdin123 -keypass aladdin123 -dname "CN=ALADDIN Security, OU=Development, O=ALADDIN, L=Moscow, S=Moscow, C=RU"
        success "Keystore создан"
    else
        success "Keystore уже существует"
    fi
    
    # Создание local.properties
    if [ ! -f "local.properties" ]; then
        cat > local.properties << EOF
# Android SDK location
sdk.dir=\$ANDROID_HOME
# Keystore settings
keystore.path=keystore.jks
keystore.password=aladdin123
key.alias=aladdin-key
key.password=aladdin123
EOF
        success "local.properties создан"
    else
        success "local.properties уже существует"
    fi
    
    cd ../..
    success "Android проект настроен"
}

# Настройка секретов
setup_secrets() {
    log "Настройка секретов..."
    
    # Создание файла с примерами секретов
    cat > .env.example << EOF
# ALADDIN Mobile Environment Variables
# Скопируйте этот файл в .env и заполните реальными значениями

# App Store Connect
APPSTORE_ISSUER_ID=your_issuer_id
APPSTORE_API_KEY_ID=your_api_key_id
APPSTORE_API_PRIVATE_KEY=your_private_key

# Google Play Console
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON=your_service_account_json

# ALADDIN API
ALADDIN_API_ENDPOINT=https://api.aladdin.security
ALADDIN_AI_ENDPOINT=https://ai.aladdin.security
ALADDIN_VPN_ENDPOINT=https://vpn.aladdin.security

# Security
ALADDIN_ENCRYPTION_KEY=your_encryption_key
ALADDIN_JWT_SECRET=your_jwt_secret

# Analytics
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email

# Monitoring
SENTRY_DSN=your_sentry_dsn
CRASHLYTICS_API_KEY=your_crashlytics_api_key
EOF
    
    success "Файл .env.example создан"
    warning "Не забудьте создать .env файл с реальными значениями!"
}

# Настройка мониторинга
setup_monitoring() {
    log "Настройка мониторинга..."
    
    # Создание конфигурации для Sentry
    cat > mobile/monitoring/sentry.properties << EOF
defaults.url=https://sentry.io/
defaults.org=aladdin-security
defaults.project=mobile-app
auth.token=your_sentry_auth_token
EOF
    
    # Создание конфигурации для Firebase
    cat > mobile/monitoring/firebase-config.json << EOF
{
  "project_info": {
    "project_number": "your_project_number",
    "project_id": "your_project_id"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "your_app_id",
        "android_client_info": {
          "package_name": "com.aladdin.mobile"
        }
      }
    }
  ]
}
EOF
    
    success "Мониторинг настроен"
}

# Создание скриптов для локальной разработки
create_dev_scripts() {
    log "Создание скриптов для разработки..."
    
    # Скрипт для запуска iOS
    cat > mobile/scripts/run-ios.sh << 'EOF'
#!/bin/bash
echo "🚀 Запуск iOS приложения..."
cd mobile/ios
if [ -f "ALADDINMobile.xcworkspace" ]; then
    open ALADDINMobile.xcworkspace
else
    open ALADDINMobile.xcodeproj
fi
EOF
    
    # Скрипт для запуска Android
    cat > mobile/scripts/run-android.sh << 'EOF'
#!/bin/bash
echo "🚀 Запуск Android приложения..."
cd mobile/android
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.aladdin.mobile/.MainActivity
EOF
    
    # Скрипт для тестирования
    cat > mobile/scripts/test-all.sh << 'EOF'
#!/bin/bash
echo "🧪 Запуск всех тестов..."
echo "Тестирование iOS..."
cd mobile/ios && xcodebuild test -workspace ALADDINMobile.xcworkspace -scheme ALADDINMobile
echo "Тестирование Android..."
cd ../android && ./gradlew test
echo "✅ Все тесты завершены"
EOF
    
    # Делаем скрипты исполняемыми
    chmod +x mobile/scripts/*.sh
    
    success "Скрипты для разработки созданы"
}

# Основная функция
main() {
    echo "🌩️ ALADDIN Mobile CI/CD Setup"
    echo "=============================="
    
    check_dependencies
    setup_github_actions
    setup_ios_project
    setup_android_project
    setup_secrets
    setup_monitoring
    create_dev_scripts
    
    echo ""
    success "🎉 CI/CD настройка завершена!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Создайте .env файл с реальными секретами"
    echo "2. Настройте App Store Connect и Google Play Console"
    echo "3. Добавьте секреты в GitHub Secrets"
    echo "4. Запустите тесты: ./mobile/scripts/test-all.sh"
    echo "5. Запустите приложения: ./mobile/scripts/run-ios.sh или ./mobile/scripts/run-android.sh"
    echo ""
    echo "🔗 Полезные ссылки:"
    echo "- GitHub Actions: https://github.com/your-repo/actions"
    echo "- App Store Connect: https://appstoreconnect.apple.com"
    echo "- Google Play Console: https://play.google.com/console"
    echo ""
}

# Запуск
main "$@"

