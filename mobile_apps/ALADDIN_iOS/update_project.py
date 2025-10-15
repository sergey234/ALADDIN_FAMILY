#!/usr/bin/env python3
"""
Скрипт для обновления Xcode проекта - добавление всех Swift файлов
"""

import os
import re
import uuid

def generate_hex_id():
    """Генерирует hex ID для Xcode проекта"""
    return format(uuid.uuid4().int & (2**32-1), 'X').zfill(8)

def find_swift_files():
    """Находит все Swift файлы в проекте"""
    swift_files = []
    for root, dirs, files in os.walk('ALADDIN'):
        for file in files:
            if file.endswith('.swift'):
                rel_path = os.path.join(root, file)
                swift_files.append(rel_path)
    return sorted(swift_files)

def read_pbxproj():
    """Читает project.pbxproj"""
    with open('ALADDIN.xcodeproj/project.pbxproj', 'r', encoding='utf-8') as f:
        return f.read()

def write_pbxproj(content):
    """Записывает обновленный project.pbxproj"""
    with open('ALADDIN.xcodeproj/project.pbxproj', 'w', encoding='utf-8') as f:
        f.write(content)

def update_project():
    """Основная функция обновления проекта"""
    print("🔍 Находим все Swift файлы...")
    swift_files = find_swift_files()
    print(f"📊 Найдено {len(swift_files)} Swift файлов")
    
    # Читаем текущий проект
    pbxproj_content = read_pbxproj()
    
    # Генерируем ID для новых файлов
    file_refs = {}
    build_files = {}
    
    for swift_file in swift_files:
        file_id = f"A{generate_hex_id()}"
        build_id = f"A{generate_hex_id()}"
        
        file_refs[swift_file] = file_id
        build_files[swift_file] = build_id
    
    # Найдем существующие секции
    pbx_build_file_start = pbxproj_content.find('/* Begin PBXBuildFile section */')
    pbx_build_file_end = pbxproj_content.find('/* End PBXBuildFile section */')
    
    pbx_file_ref_start = pbxproj_content.find('/* Begin PBXFileReference section */')
    pbx_file_ref_end = pbxproj_content.find('/* End PBXFileReference section */')
    
    if pbx_build_file_start == -1 or pbx_build_file_end == -1:
        print("❌ Не могу найти секции PBXBuildFile")
        return False
    
    # Добавляем новые BuildFile записи
    new_build_files = []
    new_file_refs = []
    
    for swift_file in swift_files:
        # Проверяем, не добавлен ли уже файл
        if f"{os.path.basename(swift_file)}" in pbxproj_content:
            continue
            
        file_id = file_refs[swift_file]
        build_id = build_files[swift_file]
        file_name = os.path.basename(swift_file)
        rel_path = swift_file.replace('ALADDIN/', '')
        
        new_build_files.append(f'\t\t{build_id} /* {file_name} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_id} /* {file_name} */; }};')
        new_file_refs.append(f'\t\t{file_id} /* {file_name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "{rel_path}"; sourceTree = "<group>"; }};')
    
    if not new_build_files:
        print("✅ Все файлы уже добавлены в проект")
        return True
    
    print(f"➕ Добавляем {len(new_build_files)} новых файлов...")
    
    # Обновляем PBXBuildFile секцию
    build_section_start = pbxproj_content.find('/* Begin PBXBuildFile section */') + len('/* Begin PBXBuildFile section */')
    build_section_end = pbxproj_content.find('/* End PBXBuildFile section */')
    
    existing_build_files = pbxproj_content[build_section_start:build_section_end]
    new_build_section = existing_build_files.rstrip() + '\n' + '\n'.join(new_build_files) + '\n'
    
    pbxproj_content = (pbxproj_content[:build_section_start] + 
                       new_build_section + 
                       pbxproj_content[build_section_end:])
    
    # Обновляем PBXFileReference секцию
    ref_section_start = pbxproj_content.find('/* Begin PBXFileReference section */') + len('/* Begin PBXFileReference section */')
    ref_section_end = pbxproj_content.find('/* End PBXFileReference section */')
    
    existing_file_refs = pbxproj_content[ref_section_start:ref_section_end]
    new_ref_section = existing_file_refs.rstrip() + '\n' + '\n'.join(new_file_refs) + '\n'
    
    pbxproj_content = (pbxproj_content[:ref_section_start] + 
                       new_ref_section + 
                       pbxproj_content[ref_section_end:])
    
    # Обновляем PBXSourcesBuildPhase - добавляем файлы в сборку
    sources_start = pbxproj_content.find('/* Begin PBXSourcesBuildPhase section */')
    sources_end = pbxproj_content.find('/* End PBXSourcesBuildPhase section */')
    
    if sources_start != -1 and sources_end != -1:
        sources_section = pbxproj_content[sources_start:sources_end]
        
        # Находим files секцию внутри PBXSourcesBuildPhase
        files_match = re.search(r'files = \((.*?)\);', sources_section, re.DOTALL)
        if files_match:
            existing_files = files_match.group(1).strip()
            new_files = []
            
            for swift_file in swift_files:
                file_name = os.path.basename(swift_file)
                if f"{file_name}" not in existing_files:
                    build_id = build_files[swift_file]
                    new_files.append(f'\t\t\t\t{build_id} /* {file_name} in Sources */,')
            
            if new_files:
                updated_files = existing_files.rstrip() + '\n' + '\n'.join(new_files) + '\n\t\t\t'
                sources_section = sources_section.replace(files_match.group(1), updated_files)
                pbxproj_content = pbxproj_content[:sources_start] + sources_section + pbxproj_content[sources_end:]
    
    # Записываем обновленный файл
    write_pbxproj(pbxproj_content)
    print(f"✅ Обновлен project.pbxproj - добавлено {len(new_build_files)} файлов")
    return True

if __name__ == "__main__":
    if update_project():
        print("🎉 Проект успешно обновлен!")
    else:
        print("❌ Ошибка обновления проекта")
