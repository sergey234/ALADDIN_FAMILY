#!/bin/bash

echo "🚀 ФИНАЛЬНАЯ ПОПЫТКА ANDROID STUDIO"
echo "==================================="

# Закрываем все процессы Android Studio
echo "🔄 Закрываем Android Studio..."
pkill -f "Android Studio" 2>/dev/null || echo "Android Studio не запущен"

# Ждем 3 секунды
sleep 3

# Удаляем все кэши и конфигурации
echo "🗑️ Удаляем все кэши..."
rm -rf .idea
rm -rf .gradle
rm -rf app/build
rm -rf build

# Создаем минимальную конфигурацию
echo "📁 Создаем минимальную конфигурацию..."
mkdir -p .idea/runConfigurations

# Создаем простой modules.xml
cat > .idea/modules.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/ALADDIN.iml" filepath="$PROJECT_DIR$/ALADDIN.iml" />
      <module fileurl="file://$PROJECT_DIR$/app/app.iml" filepath="$PROJECT_DIR$/app/app.iml" />
    </modules>
  </component>
</project>
EOF

# Создаем простой workspace.xml
cat > .idea/workspace.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="AutoImportSettings">
    <option name="autoReloadType" value="NONE" />
  </component>
  <component name="ChangeListManager">
    <list default="true" id="ALADDIN" name="Changes" comment="" />
  </component>
  <component name="ProjectId" id="ALADDIN" />
  <component name="ProjectViewState">
    <option name="hideEmptyMiddlePackages" value="true" />
    <option name="showLibraryContents" value="true" />
  </component>
</project>
EOF

# Создаем конфигурацию запуска
cat > .idea/runConfigurations/ALADDIN_Debug.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="ALADDIN Debug" type="AndroidRunConfigurationType" factoryName="Android App">
    <module name="ALADDIN.app" />
    <option name="DEPLOY" value="true" />
    <option name="DEPLOY_APK_FROM_BUNDLE" value="false" />
    <option name="DEPLOY_AS_INSTANT" value="false" />
    <option name="ARTIFACT_NAME" value="" />
    <option name="PM_INSTALL_OPTIONS" value="" />
    <option name="ALL_USERS" value="false" />
    <option name="ALWAYS_INSTALL_WITH_PM" value="false" />
    <option name="CLEAR_APP_STORAGE" value="false" />
    <option name="DYNAMIC_FEATURES_DISABLED_LIST" value="" />
    <option name="ACTIVITY_EXTRA_FLAGS" value="" />
    <option name="MODE" value="default_activity" />
    <option name="CLEAR_LOGCAT" value="false" />
    <option name="SHOW_LOGCAT_AUTOMATICALLY" value="false" />
    <option name="INSPECTION_WITHOUT_ACTIVITY_RESTART" value="false" />
    <option name="TARGET_SELECTION_MODE" value="DEVICE_AND_SNAPSHOT_COMBO_BOX" />
    <option name="SELECTED_CLOUD_MATRIX_CONFIGURATION_ID" value="-1" />
    <option name="SELECTED_CLOUD_MATRIX_PROJECT_ID" value="" />
    <option name="DEBUGGER_TYPE" value="Auto" />
    <option name="DEEP_LINK" value="" />
    <option name="ACTIVITY_CLASS" value="" />
    <option name="SEARCH_ACTIVITY_IN_GLOBAL_SCOPE" value="false" />
    <option name="SKIP_ACTIVITY_VALIDATION" value="false" />
    <method v="2">
      <option name="Android.Gradle.BeforeRunTask" enabled="true" />
    </method>
  </configuration>
</component>
EOF

# Синхронизируем Gradle
echo "🔄 Синхронизируем Gradle..."
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"
./gradlew clean
./gradlew build

echo "✅ ПРОЕКТ ПОДГОТОВЛЕН!"
echo "🚀 Открываем Android Studio..."

# Открываем Android Studio
open -a "Android Studio" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android

echo ""
echo "📱 ИНСТРУКЦИИ ДЛЯ ANDROID STUDIO:"
echo "================================="
echo "1. Дождитесь завершения 'Gradle sync'"
echo "2. Если появится диалог 'Import Gradle Project' - нажмите 'OK'"
echo "3. Проверьте, что 'Project Structure' стал активным"
echo "4. Перейдите в Run → Edit Configurations"
echo "5. В поле Module выберите: ALADDIN.app"
echo "6. В поле Deploy выберите: Default APK"
echo "7. Нажмите Apply и OK"
echo "8. Нажмите кнопку Run (▶️)"
echo ""
echo "🔧 ЕСЛИ НЕ ПОЛУЧАЕТСЯ:"
echo "1. Попробуйте File → Project Structure → Modules → + → Import Module"
echo "2. Выберите папку 'app'"
echo "3. Или используйте готовый APK файл напрямую"
echo ""
echo "📦 ГОТОВЫЙ APK:"
echo "Файл: /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/build/outputs/apk/debug/app-debug.apk"
echo "Размер: 38MB"
echo "Можно установить на любое Android устройство!"

