#!/bin/bash

echo "🚀 Исправление Android Studio проекта ALADDIN"
echo "=============================================="

# Переходим в директорию проекта
cd "/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"

echo "📁 Текущая директория: $(pwd)"

# 1. Очищаем кэш Gradle
echo "🧹 Очистка кэша Gradle..."
./gradlew clean

# 2. Очищаем кэш Android Studio
echo "🧹 Очистка кэша Android Studio..."
rm -rf .idea/caches/
rm -rf .idea/compiler.xml
rm -rf .idea/encodings.xml
rm -rf .idea/libraries/
rm -rf .idea/misc.xml
rm -rf .idea/modules.xml
rm -rf .idea/runConfigurations/
rm -rf .idea/vcs.xml
rm -rf .idea/workspace.xml

# 3. Пересоздаем конфигурацию Android Studio
echo "🔧 Пересоздание конфигурации Android Studio..."

# Создаем директорию .idea если её нет
mkdir -p .idea/runConfigurations

# Создаем правильный misc.xml
cat > .idea/misc.xml << 'EOF'
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

# Создаем правильный gradle.xml
cat > .idea/gradle.xml << 'EOF'
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

# Создаем правильный modules.xml
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

# Создаем правильную конфигурацию запуска
cat > .idea/runConfigurations/ALADDIN_Debug.xml << 'EOF'
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

# 4. Синхронизируем Gradle
echo "🔄 Синхронизация Gradle..."
./gradlew --refresh-dependencies

# 5. Собираем проект
echo "🔨 Сборка проекта..."
./gradlew assembleDebug

echo "✅ Исправление завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте Android Studio"
echo "2. Выберите 'Open an existing project'"
echo "3. Выберите папку: /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android_New"
echo "4. Дождитесь синхронизации Gradle"
echo "5. Выберите конфигурацию 'ALADDIN Debug' для запуска"
echo ""
echo "🔧 Если эмулятор не работает, попробуйте:"
echo "   - Создать новый эмулятор через AVD Manager"
echo "   - Или подключить реальное устройство через USB"

