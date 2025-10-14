#!/bin/bash

echo "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ANDROID STUDIO"
echo "======================================="

PROJECT_PATH="/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"
cd "$PROJECT_PATH" || exit

echo "📁 Текущая директория: $(pwd)"

# Закрываем Android Studio если открыт
echo "🔄 Закрытие Android Studio..."
osascript -e 'tell application "Android Studio" to quit' 2>/dev/null || echo "Android Studio не был открыт"

sleep 3

# Полная очистка .idea
echo "🧹 Полная очистка конфигурации Android Studio..."
rm -rf ./.idea/

# Создаем новую структуру .idea
echo "🔧 Создание новой конфигурации..."
mkdir -p ./.idea/runConfigurations
mkdir -p ./.idea/caches

# Создаем modules.xml
cat > ./.idea/modules.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/ALADDIN_Android_New.iml" filepath="$PROJECT_DIR$/ALADDIN_Android_New.iml" />
      <module fileurl="file://$PROJECT_DIR$/app/app.iml" filepath="$PROJECT_DIR$/app/app.iml" />
    </modules>
  </component>
</project>
EOF

# Создаем misc.xml
cat > ./.idea/misc.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ExternalStorageConfigurationManager" enabled="true" />
  <component name="ProjectRootManager" version="2" languageLevel="JDK_1_8" default="true" project-jdk-name="jbr-17" project-jdk-type="JavaSDK">
    <output url="file://$PROJECT_DIR$/build/classes" />
  </component>
  <component name="ProjectType">
    <option name="id" value="Android" />
  </component>
</project>
EOF

# Создаем gradle.xml
cat > ./.idea/gradle.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="GradleSettings">
    <option name="linkedExternalProjectsSettings">
      <GradleProjectSettings>
        <option name="externalProjectPath" value="$PROJECT_DIR$" />
        <option name="gradleJvm" value="jbr-17" />
        <option name="modules">
          <set>
            <option value="$PROJECT_DIR$" />
            <option value="$PROJECT_DIR$/app" />
          </set>
        </option>
        <option name="resolveExternalAnnotations" value="false" />
      </GradleProjectSettings>
    </option>
  </component>
</project>
EOF

# Создаем runConfiguration
cat > ./.idea/runConfigurations/ALADDIN_Debug.xml << 'EOF'
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="ALADDIN Debug" type="AndroidRunConfigurationType" factoryName="Android App">
    <module name="ALADDIN_Android_New.app" />
    <option name="MODULE_NAME" value="ALADDIN_Android_New.app" />
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
    <Auto>
      <option name="USE_JAVA_AWARE_DEBUGGER" value="false" />
      <option name="SHOW_STATIC_VARS" value="true" />
      <option name="WORKING_DIR" value="" />
      <option name="TARGET_LOGGING_CHANNELS" value="lldb process:gdb-remote packets" />
      <option name="SHOW_OPTIMIZED_WARNING" value="true" />
      <option name="ATTACH_ON_WAIT_FOR_DEBUGGER" value="false" />
      <option name="DEBUG_SANDBOX_SDK" value="false" />
    </Auto>
    <Hybrid>
      <option name="USE_JAVA_AWARE_DEBUGGER" value="false" />
      <option name="SHOW_STATIC_VARS" value="true" />
      <option name="WORKING_DIR" value="" />
      <option name="TARGET_LOGGING_CHANNELS" value="lldb process:gdb-remote packets" />
      <option name="SHOW_OPTIMIZED_WARNING" value="true" />
      <option name="ATTACH_ON_WAIT_FOR_DEBUGGER" value="false" />
      <option name="DEBUG_SANDBOX_SDK" value="false" />
    </Hybrid>
    <Java>
      <option name="ATTACH_ON_WAIT_FOR_DEBUGGER" value="false" />
      <option name="DEBUG_SANDBOX_SDK" value="false" />
    </Java>
    <Native>
      <option name="USE_JAVA_AWARE_DEBUGGER" value="false" />
      <option name="SHOW_STATIC_VARS" value="true" />
      <option name="WORKING_DIR" value="" />
      <option name="TARGET_LOGGING_CHANNELS" value="lldb process:gdb-remote packets" />
      <option name="SHOW_OPTIMIZED_WARNING" value="true" />
      <option name="ATTACH_ON_WAIT_FOR_DEBUGGER" value="false" />
      <option name="DEBUG_SANDBOX_SDK" value="false" />
    </Native>
    <Profilers>
      <option name="ADVANCED_PROFILING_ENABLED" value="false" />
      <option name="STARTUP_PROFILING_ENABLED" value="false" />
      <option name="STARTUP_CPU_PROFILING_ENABLED" value="false" />
      <option name="STARTUP_CPU_PROFILING_CONFIGURATION_NAME" value="Java/Kotlin Method Sample (legacy)" />
      <option name="STARTUP_NATIVE_MEMORY_PROFILING_ENABLED" value="false" />
      <option name="NATIVE_MEMORY_SAMPLE_RATE_BYTES" value="2048" />
    </Profilers>
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

# Создаем .gitignore
cat > ./.idea/.gitignore << 'EOF'
# Default ignored files
/shelf/
/workspace.xml
# Datasource local storage ignored files
/dataSources/
/dataSources.ids
/dataSources.local.xml
# Editor-based HTTP Client requests
/httpRequests/
# Firebase Service Account
/firebaseServiceAccount.json
EOF

# Очищаем и пересобираем проект
echo "🔄 Очистка и пересборка проекта..."
./gradlew clean

echo ""
echo "✅ Финальное исправление завершено!"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Откройте Android Studio"
echo "2. File → Open"
echo "3. Выберите папку: $PROJECT_PATH"
echo "4. Дождитесь синхронизации Gradle (2-3 минуты)"
echo "5. Выберите конфигурацию 'ALADDIN Debug'"
echo ""
echo "🎯 Теперь модуль должен работать корректно!"
echo ""
echo "🚀 После открытия проекта в Android Studio:"
echo "   Run → Edit Configurations → ALADDIN Debug"
echo "   Убедитесь что Module: ALADDIN_Android_New.app"
