#!/usr/bin/env python3
"""
🤖 АВТОМАТИЧЕСКОЕ ДОБАВЛЕНИЕ ЭКРАНОВ В XCODE ПРОЕКТ
Добавляет все экраны из папки Screens/ в project.pbxproj
"""

import re
import uuid
import os

def add_screens_to_xcode():
    """Добавляет все экраны в Xcode проект"""
    
    # Читаем project.pbxproj
    with open('ALADDIN.xcodeproj/project.pbxproj', 'r') as f:
        content = f.read()
    
    # Находим все Swift файлы в папке Screens
    screens_dir = 'Screens'
    swift_files = []
    
    if os.path.exists(screens_dir):
        for file in os.listdir(screens_dir):
            if file.endswith('.swift'):
                swift_files.append(os.path.join(screens_dir, file))
    
    print(f"📱 Найдено {len(swift_files)} экранов для добавления")
    
    # Создаем PBXFileReference для каждого файла
    file_references = []
    for file_path in sorted(swift_files):
        file_id = str(uuid.uuid4()).replace('-', '').upper()[:24]
        file_name = os.path.basename(file_path)
        
        # Создаем PBXFileReference
        file_ref = f'\\t\t{file_id} /* {file_name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "{file_name}"; sourceTree = "<group>"; }};'
        file_references.append(file_ref)
        
        # Добавляем в PBXBuildFile
        build_file_id = str(uuid.uuid4()).replace('-', '').upper()[:24]
        build_file = f'\\t\t{build_file_id} /* {file_name} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_id} /* {file_name} */; }};'
        
        # Добавляем PBXFileReference
        content = content.replace('/* Begin PBXFileReference section */', 
                                '/* Begin PBXFileReference section */\\n' + file_ref)
        
        # Добавляем PBXBuildFile
        content = content.replace('/* Begin PBXBuildFile section */', 
                                '/* Begin PBXBuildFile section */\\n' + build_file)
        
        # Добавляем в Sources build phase
        sources_phase = f'\\t\\t\\t{build_file_id} /* {file_name} in Sources */,'
        content = content.replace('/* Sources */ = (', 
                                '/* Sources */ = (\\n' + sources_phase)
    
    # Создаем группу Screens если её нет
    screens_group_id = str(uuid.uuid4()).replace('-', '').upper()[:24]
    
    # Добавляем группу Screens
    screens_group = f'\\t\t{screens_group_id} /* Screens */ = {{\\n\\t\\t\\tisa = PBXGroup;\\n\\t\\t\\tchildren = (\\n'
    
    # Добавляем все файлы в группу
    for file_path in sorted(swift_files):
        file_id = str(uuid.uuid4()).replace('-', '').upper()[:24]
        file_name = os.path.basename(file_path)
        screens_group += f'\\t\\t\\t{file_id} /* {file_name} */,\\n'
    
    screens_group += '\\t\\t\\t);\\n\\t\\t\\tpath = "Screens";\\n\\t\\t\\tsourceTree = "<group>";\\n\\t\\t}};'
    
    # Добавляем группу Screens
    content = content.replace('/* Begin PBXGroup section */', 
                            '/* Begin PBXGroup section */\\n' + screens_group)
    
    # Добавляем Screens в корневую группу
    root_group_match = re.search(r'(A3000[0-9A-F]+) /\* ALADDIN \*/ = \{[^}]+children = \(([^)]+)\);[^}]+sourceTree = "<group>";', content, re.DOTALL)
    
    if root_group_match:
        root_group_id = root_group_match.group(1)
        existing_children = root_group_match.group(2)
        
        # Добавляем Screens в children
        new_children = existing_children + f'\\n\\t\\t\\t{screens_group_id} /* Screens */,'
        content = content.replace(root_group_match.group(0), 
                                f'{root_group_id} /* ALADDIN */ = {{\\n\\t\\t\\tisa = PBXGroup;\\n\\t\\t\\tchildren = ({new_children}\\n\\t\\t);\\n\\t\\t\\tsourceTree = "<group>";\\n\\t\\t}};')
    
    # Записываем обратно
    with open('ALADDIN.xcodeproj/project.pbxproj', 'w') as f:
        f.write(content)
    
    print(f"✅ Добавлено {len(swift_files)} экранов в Xcode проект")
    print("📱 Группа Screens создана")
    print("🔧 Файлы добавлены в Target Membership")
    
    return len(swift_files)

if __name__ == "__main__":
    try:
        count = add_screens_to_xcode()
        print(f"\\n🎉 УСПЕШНО! Добавлено {count} экранов")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        print("💡 Рекомендуется ручное добавление через Xcode UI")
