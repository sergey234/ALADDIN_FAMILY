#!/bin/bash

echo "🔄 ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ ANDROID STUDIO"
echo "=============================================="

# Переходим в папку проекта
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android

echo "📁 Текущая папка: $(pwd)"

# Удаляем все кэши
echo "🗑️ Удаляем кэши..."
rm -rf .gradle
rm -rf .idea
rm -rf app/build
rm -rf build

# Устанавливаем переменные окружения
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="/Users/sergejhlystov/Library/Android/sdk"

echo "🔧 Переменные окружения установлены:"
echo "   JAVA_HOME: $JAVA_HOME"
echo "   ANDROID_HOME: $ANDROID_HOME"

# Создаем новую папку .gradle
echo "📁 Создаем новую папку .gradle..."
mkdir -p .gradle

# Создаем новую папку .idea
echo "📁 Создаем новую папку .idea..."
mkdir -p .idea/runConfigurations

# Создаем modules.xml
echo "📝 Создаем modules.xml..."
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

# Создаем workspace.xml
echo "📝 Создаем workspace.xml..."
cat > .idea/workspace.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="AutoImportSettings">
    <option name="autoReloadType" value="NONE" />
  </component>
  <component name="ChangeListManager">
    <list default="true" id="ALADDIN" name="Changes" comment="" />
    <option name="SHOW_DIALOG" value="false" />
    <option name="HIGHLIGHT_CONFLICTS" value="true" />
    <option name="HIGHLIGHT_NON_ACTIVE_CHANGELIST" value="false" />
    <option name="LAST_RESOLUTION" value="IGNORE" />
  </component>
  <component name="ProjectId" id="ALADDIN" />
  <component name="ProjectViewState">
    <option name="hideEmptyMiddlePackages" value="true" />
    <option name="showLibraryContents" value="true" />
  </component>
  <component name="PropertiesComponent"><![CDATA[{
  "keyToString": {
    "RunOnceActivity.OpenProjectViewOnStart": "true",
    "RunOnceActivity.ShowReadmeOnStart": "true",
    "RunOnceActivity.cidr.known.project.marker": "true",
    "cf.first.check.clang-format": "false",
    "cidr.known.project.marker": "true"
  }
}]]></component>
  <component name="RunManager">
    <configuration name="ALADDIN Debug" type="AndroidRunConfigurationType" factoryName="Android App">
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
</project>
EOF

# Создаем конфигурацию запуска
echo "📝 Создаем конфигурацию запуска..."
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

# Принудительная синхронизация Gradle
echo "🔄 Принудительная синхронизация Gradle..."
./gradlew clean
./gradlew build --refresh-dependencies

echo "✅ ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!"
echo "🚀 Теперь откройте Android Studio:"
echo "   open -a \"Android Studio\" /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android"
echo ""
echo "📱 В Android Studio:"
echo "   1. Дождитесь завершения 'Gradle sync'"
echo "   2. 'Project Structure' должен стать активным"
echo "   3. Перейдите в Run → Edit Configurations"
echo "   4. В поле Module должно появиться: ALADDIN.app"
echo "   5. В поле Deploy выберите: Default APK"
echo "   6. Запустите приложение!"

