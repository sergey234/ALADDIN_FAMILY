# Инструкция по добавлению файлов в Xcode

## Файлы для добавления:
1. Core/Network/NetworkError.swift
2. Shared/Components/StatItem.swift
3. Shared/Components/Cards/FamilyMemberCard.swift
4. Shared/Components/Modals/ProfileEditView.swift
5. Shared/Components/QRScannerModal.swift
6. Shared/Components/RecoveryOptionsModal.swift

## Шаги:

### Вариант 1: Через Finder (Рекомендуется)
1. Откройте Xcode
2. Найдите папку нужного файла в Project Navigator (левая панель)
3. Правой кнопкой на папку → "Add Files to ALADDIN..."
4. Выберите файл
5. ✅ НЕ ставим галочку "Copy items if needed"
6. ✅ Group: создаем группу или выбираем существующую
7. ✅ Target Membership: выбираем "ALADDIN"
8. Нажимаем "Add"

### Вариант 2: Drag & Drop
1. Откройте Finder
2. Найдите файл
3. Перетащите его в нужную папку в Xcode Project Navigator
4. В диалоге:
   - ✅ НЕ ставим "Copy items if needed"
   - ✅ Group: нужная папка
   - ✅ Target Membership: ALADDIN
5. "Finish"

## Проверка:
После добавления каждого файла проверьте:
- Файл появился в Project Navigator
- Target Membership включает "ALADDIN" ✅
- Файл виден в Source Phase Build
