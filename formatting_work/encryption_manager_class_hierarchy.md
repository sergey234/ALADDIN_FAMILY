# ИЕРАРХИЯ КЛАССОВ - encryption_manager.py

## 📊 ДИАГРАММА ИЕРАРХИИ КЛАССОВ

```
                    object
                        │
                        ▼
                EncryptionManager
                (Основной класс)
                        │
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   EncryptionKey    EncryptedData    (Методы)
   (Dataclass)      (Dataclass)      (encrypt_data,
                                     decrypt_data,
                                     etc.)


    Enum
    ├── EncryptionAlgorithm
    │   ├── AES_256_GCM
    │   ├── AES_256_CBC
    │   ├── FERNET
    │   ├── RSA_OAEP
    │   └── CHACHA20_POLY1305
    │
    └── KeyDerivation
        ├── PBKDF2
        ├── SCRYPT
        └── ARGON2
```

## 🔗 СВЯЗИ МЕЖДУ КЛАССАМИ

### ОСНОВНЫЕ СВЯЗИ:
1. **EncryptionManager** использует:
   - `EncryptionAlgorithm` (для выбора алгоритма)
   - `KeyDerivation` (для выбора метода выведения ключей)
   - `EncryptionKey` (для хранения ключей)
   - `EncryptedData` (для хранения зашифрованных данных)

2. **EncryptionKey** содержит:
   - `EncryptionAlgorithm` (тип алгоритма)
   - `datetime` (время создания и истечения)

3. **EncryptedData** содержит:
   - `EncryptionAlgorithm` (использованный алгоритм)
   - `str` (ID ключа)

## 📋 ДЕТАЛЬНАЯ ИЕРАРХИЯ

### 1. EncryptionManager
```
EncryptionManager
├── __init__(logger, master_password, key_derivation, default_algorithm, key_rotation_days)
├── _initialize_encryption()
├── _create_master_key()
├── _generate_master_password()
├── _derive_key(password, salt, algorithm)
├── _get_or_create_cipher(algorithm, key)
├── _cleanup_expired_keys()
├── encrypt_data(data, algorithm=None)
├── decrypt_data(encrypted_data)
├── encrypt_file(file_path, output_path, algorithm=None)
├── decrypt_file(encrypted_file_path, output_path)
├── hash_password(password, salt=None)
├── verify_password(password, stored_hash, salt)
├── get_encryption_stats()
├── cleanup_expired_keys()
├── export_key(key_id, password)
└── import_key(exported_key, password)
```

### 2. EncryptionKey (Dataclass)
```
EncryptionKey
├── key_id: str
├── algorithm: EncryptionAlgorithm
├── key_data: bytes
├── created_at: datetime
├── expires_at: Optional[datetime]
├── is_active: bool
├── metadata: Optional[Dict[str, Any]]
└── is_expired() -> bool
```

### 3. EncryptedData (Dataclass)
```
EncryptedData
├── data: bytes
├── key_id: str
├── algorithm: EncryptionAlgorithm
├── iv: Optional[bytes]
├── tag: Optional[bytes]
├── metadata: Optional[Dict[str, Any]]
├── timestamp: datetime
└── __post_init__()
```

### 4. EncryptionAlgorithm (Enum)
```
EncryptionAlgorithm
├── AES_256_GCM = "aes_256_gcm"
├── AES_256_CBC = "aes_256_cbc"
├── FERNET = "fernet"
├── RSA_OAEP = "rsa_oaep"
└── CHACHA20_POLY1305 = "chacha20_poly1305"
```

### 5. KeyDerivation (Enum)
```
KeyDerivation
├── PBKDF2 = "pbkdf2"
├── SCRYPT = "scrypt"
└── ARGON2 = "argon2"
```

## 🎯 ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ

### ИСПОЛЬЗУЕМЫЕ ПАТТЕРНЫ:
1. **Factory Pattern** - создание ключей и шифров
2. **Strategy Pattern** - выбор алгоритмов шифрования
3. **Data Transfer Object** - EncryptionKey и EncryptedData
4. **Singleton Pattern** - один экземпляр EncryptionManager
5. **Builder Pattern** - построение зашифрованных данных

### ПРИНЦИПЫ SOLID:
- ✅ **Single Responsibility** - каждый класс имеет одну ответственность
- ✅ **Open/Closed** - легко добавлять новые алгоритмы
- ✅ **Liskov Substitution** - Enum классы взаимозаменяемы
- ✅ **Interface Segregation** - четкие интерфейсы для каждого класса
- ✅ **Dependency Inversion** - зависимость от абстракций (Enum)

## 📈 МЕТРИКИ КЛАССОВ

### СЛОЖНОСТЬ:
- **EncryptionManager**: Высокая (основная логика)
- **EncryptionKey**: Низкая (простое хранение данных)
- **EncryptedData**: Низкая (простое хранение данных)
- **EncryptionAlgorithm**: Очень низкая (перечисление)
- **KeyDerivation**: Очень низкая (перечисление)

### СВЯЗНОСТЬ:
- **Высокая** - классы тесно связаны по функциональности
- **Логическая** - связь через общую задачу шифрования

### СЦЕПЛЕНИЕ:
- **Низкое** - классы слабо зависят друг от друга
- **Интерфейсное** - зависимость через четкие интерфейсы