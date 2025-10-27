#!/usr/bin/env python3
"""
🎯 Автоматическая настройка Widget Extension Target в Xcode
Скрипт для добавления Widget Extension в project.pbxproj
"""

import re
import os
import uuid

def generate_uuid():
    """Генерирует UUID для Xcode"""
    return str(uuid.uuid4()).upper().replace('-', '')

def add_widget_target_to_project():
    """Добавляет Widget Extension target в project.pbxproj"""
    
    project_file = "ALADDIN.xcodeproj/project.pbxproj"
    
    if not os.path.exists(project_file):
        print("❌ Файл project.pbxproj не найден!")
        return False
    
    # Читаем файл
    with open(project_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Генерируем UUID для нового target
    widget_target_uuid = generate_uuid()
    widget_config_uuid = generate_uuid()
    widget_sources_uuid = generate_uuid()
    widget_frameworks_uuid = generate_uuid()
    widget_resources_uuid = generate_uuid()
    widget_product_uuid = generate_uuid()
    
    # 1. Добавляем target в PBXNativeTarget section
    target_section = f'''\t\t{widget_target_uuid} /* ALADDINWidgets */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {widget_config_uuid} /* Build configuration list for PBXNativeTarget "ALADDINWidgets" */;
\t\t\tbuildPhases = (
\t\t\t\t{widget_sources_uuid} /* Sources */,
\t\t\t\t{widget_frameworks_uuid} /* Frameworks */,
\t\t\t\t{widget_resources_uuid} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = ALADDINWidgets;
\t\t\tproductName = ALADDINWidgets;
\t\t\tproductReference = {widget_product_uuid} /* ALADDINWidgets.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};'''
    
    # Находим место для вставки target
    target_pattern = r'(/\* Begin PBXNativeTarget section \*/\n)(.*?)(/\* End PBXNativeTarget section \*/)'
    match = re.search(target_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Не удалось найти PBXNativeTarget section")
        return False
    
    # Вставляем новый target
    before = match.group(1)
    existing_targets = match.group(2)
    after = match.group(3)
    
    new_targets = existing_targets + target_section
    new_content = content.replace(match.group(0), before + new_targets + after)
    
    # 2. Добавляем target в PBXProject targets
    project_pattern = r'(targets = \(\s*)(.*?)(\s*\);.*?/\* End PBXProject section \*/)'
    project_match = re.search(project_pattern, new_content, re.DOTALL)
    
    if project_match:
        existing_targets = project_match.group(2)
        new_targets = existing_targets + f'\n\t\t\t{widget_target_uuid} /* ALADDINWidgets */,'
        new_content = new_content.replace(project_match.group(0), 
                                        project_match.group(1) + new_targets + project_match.group(3))
    
    # 3. Добавляем build phases
    build_phases = f'''
\t\t{widget_sources_uuid} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{widget_frameworks_uuid} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{widget_resources_uuid} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''
    
    # Находим место для build phases
    build_phases_pattern = r'(/\* Begin PBXSourcesBuildPhase section \*/\n)(.*?)(/\* End PBXSourcesBuildPhase section \*/)'
    build_match = re.search(build_phases_pattern, new_content, re.DOTALL)
    
    if build_match:
        existing_phases = build_match.group(2)
        new_phases = existing_phases + build_phases
        new_content = new_content.replace(build_match.group(0), 
                                        build_match.group(1) + new_phases + build_match.group(3))
    
    # 4. Добавляем product reference
    product_reference = f'''
\t\t{widget_product_uuid} /* ALADDINWidgets.appex */ = {{
\t\t\tisa = PBXFileReference;
\t\t\texplicitFileType = "wrapper.app-extension";
\t\t\tincludeInIndex = 0;
\t\t\tpath = ALADDINWidgets.appex;
\t\t\tsourceTree = BUILT_PRODUCTS_DIR;
\t\t}};'''
    
    # Находим место для product references
    product_pattern = r'(/\* Begin PBXFileReference section \*/\n)(.*?)(/\* End PBXFileReference section \*/)'
    product_match = re.search(product_pattern, new_content, re.DOTALL)
    
    if product_match:
        existing_products = product_match.group(2)
        new_products = existing_products + product_reference
        new_content = new_content.replace(product_match.group(0), 
                                        product_match.group(1) + new_products + product_match.group(3))
    
    # 5. Добавляем build configuration
    build_config = f'''
\t\t{widget_config_uuid} /* Build configuration list for PBXNativeTarget "ALADDINWidgets" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{widget_config_uuid} /* Debug */,
\t\t\t\t{widget_config_uuid} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{widget_config_uuid} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_FILE = ALADDINWidgets/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = ALADDINWidgets;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_WKCompanionAppBundleIdentifier = "family.aladdin.ios";
\t\t\t\tINFOPLIST_KEY_WKWidgetDisplayName = ALADDINWidgets;
\t\t\t\tINFOPLIST_KEY_WKWidgetDescription = "ALADDIN Family Protection Widgets";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = family.aladdin.ios.widgets;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{widget_config_uuid} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_TEAM = "";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_FILE = ALADDINWidgets/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = ALADDINWidgets;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_WKCompanionAppBundleIdentifier = "family.aladdin.ios";
\t\t\t\tINFOPLIST_KEY_WKWidgetDisplayName = ALADDINWidgets;
\t\t\t\tINFOPLIST_KEY_WKWidgetDescription = "ALADDIN Family Protection Widgets";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = family.aladdin.ios.widgets;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Release;
\t\t}};'''
    
    # Находим место для build configurations
    config_pattern = r'(/\* Begin XCBuildConfiguration section \*/\n)(.*?)(/\* End XCBuildConfiguration section \*/)'
    config_match = re.search(config_pattern, new_content, re.DOTALL)
    
    if config_match:
        existing_configs = config_match.group(2)
        new_configs = existing_configs + build_config
        new_content = new_content.replace(config_match.group(0), 
                                        config_match.group(1) + new_configs + build_match.group(3))
    
    # Сохраняем обновленный файл
    with open(project_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Widget Extension target добавлен в project.pbxproj")
    return True

def main():
    print("🎯 Настройка Widget Extension Target...")
    
    if add_widget_target_to_project():
        print("✅ Widget Extension target успешно добавлен!")
        print("\n📋 Следующие шаги:")
        print("1. Откройте ALADDIN.xcodeproj в Xcode")
        print("2. Настройте App Groups для основного приложения и виджетов")
        print("3. Добавьте файлы из папки ALADDINWidgets/ в target")
        print("4. Настройте Build Settings")
    else:
        print("❌ Ошибка при добавлении Widget Extension target")

if __name__ == "__main__":
    main()
