# ДОКУМЕНТАЦИЯ ФАЙЛА: data_protection_manager.py

## ОБЩАЯ ИНФОРМАЦИЯ
- **Путь:** security/data_protection_manager.py
- **Дата создания документации:** 2025-09-14 13:00:53
- **Размер файла:** 14707 символов
- **Количество строк:** 407

## СТРУКТУРА КОДА
- **Количество классов:** 6
  - DataClassification
  - DataType
  - ProtectionLevel
  - DataRecord
  - DataPolicy
  - DataProtectionManager
- **Количество функций:** 12
- **Количество импортов:** 17

## ИМПОРТЫ
- logging
- json
- hashlib
- base64
- datetime.datetime
- datetime.timedelta
- typing.Dict
- typing.List
- typing.Any
- typing.Optional

## АСИНХРОННЫЕ ФУНКЦИИ
- **Количество асинхронных функций:** 5
  - __init__
  - _create_default_policies
  - _encrypt_data
  - _decrypt_data
  - _cleanup_expired_data

## ОБРАБОТКА ОШИБОК
- **Количество try-except блоков:** 8
