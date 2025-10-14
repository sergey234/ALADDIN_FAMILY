# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Smart Data Manager
Умное управление данными безопасности с автоматической очисткой

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import gzip
import json
import os
import shutil
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from core.base import SecurityBase
from security.protected_data_manager import PROTECTED_DATA_MANAGER


class DataPriority(Enum):
    """Приоритеты данных"""

    CRITICAL = "critical"  # Критические данные - храним вечно
    HIGH = "high"  # Высокий приоритет - храним 1 год
    MEDIUM = "medium"  # Средний приоритет - храним 6 месяцев
    LOW = "low"  # Низкий приоритет - храним 1 месяц
    TEMP = "temp"  # Временные данные - храним 1 неделю


class DataRetentionPolicy:
    """Политика хранения данных"""

    def __init__(self):
        self.retention_periods = {
            # 100 лет (практически вечно)
            DataPriority.CRITICAL: timedelta(days=36500),
            DataPriority.HIGH: timedelta(days=365),  # 1 год
            DataPriority.MEDIUM: timedelta(days=180),  # 6 месяцев
            DataPriority.LOW: timedelta(days=30),  # 1 месяц
            DataPriority.TEMP: timedelta(days=7),  # 1 неделя
        }

        self.max_disk_usage = 0.8  # Максимум 80% диска
        self.compression_threshold = 0.5  # Сжимаем данные старше 50% периода хранения
        self.archive_threshold = 0.8  # Архивируем данные старше 80% периода хранения


class SmartDataManager(SecurityBase):
    """Умный менеджер данных безопасности"""

    def __init__(self, name: str = "SmartDataManager", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Конфигурация хранения
        self.data_directory = config.get("data_directory", "data/security") if config else "data/security"
        self.max_total_size_gb = config.get("max_total_size_gb", 10) if config else 10  # Максимум 10 ГБ
        self.enable_compression = config.get("enable_compression", True) if config else True
        self.enable_archiving = config.get("enable_archiving", True) if config else True

        # Политика хранения
        self.retention_policy = DataRetentionPolicy()

        # Статистика хранения
        self.total_data_size = 0
        self.data_by_priority = {priority: 0 for priority in DataPriority}
        self.oldest_data_date = datetime.now()
        self.newest_data_date = datetime.now()

        # Создание директорий
        self._create_directories()

    def _create_directories(self):
        """Создание структуры директорий для данных"""
        directories = [
            self.data_directory,
            f"{self.data_directory}/critical",
            f"{self.data_directory}/high",
            f"{self.data_directory}/medium",
            f"{self.data_directory}/low",
            f"{self.data_directory}/temp",
            f"{self.data_directory}/archived",
            f"{self.data_directory}/compressed",
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def store_security_data(
        self,
        data: Dict[str, Any],
        priority: DataPriority,
        data_type: str,
        identifier: str,
    ) -> bool:
        """
        Сохранение данных безопасности с умным управлением

        Args:
            data: Данные для сохранения
            priority: Приоритет данных
            data_type: Тип данных (alerts, logs, events, etc.)
            identifier: Уникальный идентификатор

        Returns:
            bool: Успешность сохранения
        """
        try:
            # Проверка места на диске
            if not self._check_disk_space():
                self._cleanup_old_data()

            # Определение пути сохранения
            file_path = self._get_file_path(priority, data_type, identifier)

            # Добавление метаданных
            data_with_metadata = {
                "data": data,
                "metadata": {
                    "priority": priority.value,
                    "data_type": data_type,
                    "identifier": identifier,
                    "created_at": datetime.now().isoformat(),
                    "size_bytes": len(json.dumps(data, ensure_ascii=False).encode("utf-8")),
                },
            }

            # Сохранение данных
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)

            # Обновление статистики
            self._update_storage_stats(file_path, priority)

            # Автоматическая очистка при необходимости
            self._auto_cleanup()

            self.log_activity(f"Данные безопасности сохранены: {data_type}/{identifier} (приоритет: {priority.value})")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка сохранения данных безопасности: {e}", "error")
            return False

    def _get_file_path(self, priority: DataPriority, data_type: str, identifier: str) -> str:
        """Получение пути для сохранения файла"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{identifier}_{timestamp}.json"
        return os.path.join(self.data_directory, priority.value, filename)

    def _check_disk_space(self) -> bool:
        """Проверка свободного места на диске"""
        try:
            total, used, free = shutil.disk_usage(self.data_directory)
            usage_percent = used / total

            if usage_percent > self.retention_policy.max_disk_usage:
                self.log_activity(f"ВНИМАНИЕ: Диск заполнен на {usage_percent:.1%}", "warning")
                return False

            return True

        except Exception as e:
            self.log_activity(f"Ошибка проверки места на диске: {e}", "error")
            return False

    def _update_storage_stats(self, file_path: str, priority: DataPriority):
        """Обновление статистики хранения"""
        try:
            file_size = os.path.getsize(file_path)
            self.total_data_size += file_size
            self.data_by_priority[priority] += file_size

            # Обновление дат
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_time < self.oldest_data_date:
                self.oldest_data_date = file_time
            if file_time > self.newest_data_date:
                self.newest_data_date = file_time

        except Exception as e:
            self.log_activity(f"Ошибка обновления статистики: {e}", "error")

    def _auto_cleanup(self):
        """Автоматическая очистка старых данных"""
        try:
            # Проверка необходимости очистки
            if self.total_data_size > self.max_total_size_gb * 1024 * 1024 * 1024:  # Превышен лимит
                self.log_activity("Автоматическая очистка: превышен лимит размера данных")
                self._cleanup_old_data()

            # Ежедневная очистка по времени
            if datetime.now().hour == 2:  # В 2 часа ночи
                self._cleanup_by_time()

        except Exception as e:
            self.log_activity(f"Ошибка автоматической очистки: {e}", "error")

    def _cleanup_old_data(self):
        """Очистка старых данных по приоритету"""
        try:
            cleaned_size = 0

            # Очистка от низкого приоритета к высокому
            for priority in [DataPriority.TEMP, DataPriority.LOW, DataPriority.MEDIUM]:
                cleaned_size += self._cleanup_priority_data(priority)

            if cleaned_size > 0:
                self.log_activity(f"Очищено {cleaned_size / (1024*1024):.1f} МБ старых данных")

        except Exception as e:
            self.log_activity(f"Ошибка очистки старых данных: {e}", "error")

    def _cleanup_priority_data(self, priority: DataPriority) -> int:
        """Очистка данных определенного приоритета"""
        try:
            priority_dir = os.path.join(self.data_directory, priority.value)
            if not os.path.exists(priority_dir):
                return 0

            cleaned_size = 0
            current_time = datetime.now()

            for filename in os.listdir(priority_dir):
                file_path = os.path.join(priority_dir, filename)

                # КРИТИЧЕСКАЯ ПРОВЕРКА: Защищен ли файл от удаления?
                if not PROTECTED_DATA_MANAGER.can_delete(file_path):
                    self.log_activity(f"ФАЙЛ ЗАЩИЩЕН ОТ УДАЛЕНИЯ: {file_path}", "warning")
                    continue

                # Проверка возраста файла
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                retention_period = self.retention_policy.retention_periods[priority]

                if current_time - file_time > retention_period:
                    # Файл превысил период хранения
                    file_size = os.path.getsize(file_path)

                    # Для критических данных - архивируем, для остальных -
                    # удаляем
                    if priority == DataPriority.CRITICAL:
                        if PROTECTED_DATA_MANAGER.can_archive(file_path):
                            self._archive_file(file_path, priority)
                        else:
                            self.log_activity(f"ФАЙЛ ЗАЩИЩЕН ОТ АРХИВИРОВАНИЯ: {file_path}", "warning")
                    else:
                        os.remove(file_path)
                        cleaned_size += file_size

                        # Обновление статистики
                        self.total_data_size -= file_size
                        self.data_by_priority[priority] -= file_size

            return cleaned_size

        except Exception as e:
            self.log_activity(f"Ошибка очистки данных приоритета {priority.value}: {e}", "error")
            return 0

    def _cleanup_by_time(self):
        """Очистка по времени (ежедневная)"""
        try:
            current_time = datetime.now()

            for priority in DataPriority:
                if priority == DataPriority.CRITICAL:
                    continue  # Критические данные не очищаем

                priority_dir = os.path.join(self.data_directory, priority.value)
                if not os.path.exists(priority_dir):
                    continue

                retention_period = self.retention_policy.retention_periods[priority]
                cutoff_date = current_time - retention_period

                for filename in os.listdir(priority_dir):
                    file_path = os.path.join(priority_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))

                    if file_time < cutoff_date:
                        # Файл устарел
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)

                        # Обновление статистики
                        self.total_data_size -= file_size
                        self.data_by_priority[priority] -= file_size

        except Exception as e:
            self.log_activity(f"Ошибка очистки по времени: {e}", "error")

    def _archive_file(self, file_path: str, priority: DataPriority):
        """Архивирование файла"""
        try:
            if not self.enable_archiving:
                return

            # Создание архива
            archive_dir = os.path.join(self.data_directory, "archived", priority.value)
            os.makedirs(archive_dir, exist_ok=True)

            archive_name = os.path.basename(file_path).replace(".json", ".gz")
            archive_path = os.path.join(archive_dir, archive_name)

            # Сжатие файла
            with open(file_path, "rb") as f_in:
                with gzip.open(archive_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Удаление оригинального файла
            os.remove(file_path)

            self.log_activity(f"Файл заархивирован: {file_path} → {archive_path}")

        except Exception as e:
            self.log_activity(f"Ошибка архивирования файла {file_path}: {e}", "error")

    def get_storage_statistics(self) -> Dict[str, Any]:
        """Получение статистики хранения"""
        return {
            "total_size_gb": self.total_data_size / (1024 * 1024 * 1024),
            "max_size_gb": self.max_total_size_gb,
            "usage_percent": (self.total_data_size / (self.max_total_size_gb * 1024 * 1024 * 1024)) * 100,
            "data_by_priority": {
                priority.value: {
                    "size_mb": size / (1024 * 1024),
                    "files_count": self._count_files_in_priority(priority),
                }
                for priority, size in self.data_by_priority.items()
            },
            "oldest_data": self.oldest_data_date.isoformat(),
            "newest_data": self.newest_data_date.isoformat(),
            "retention_policies": {
                priority.value: str(policy) for priority, policy in self.retention_policy.retention_periods.items()
            },
        }

    def _count_files_in_priority(self, priority: DataPriority) -> int:
        """Подсчет файлов в директории приоритета"""
        try:
            priority_dir = os.path.join(self.data_directory, priority.value)
            if os.path.exists(priority_dir):
                return len([f for f in os.listdir(priority_dir) if f.endswith(".json")])
            return 0
        except Exception:
            return 0

    def cleanup_manual(
        self,
        priority: Optional[DataPriority] = None,
        older_than_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Ручная очистка данных

        Args:
            priority: Приоритет для очистки (если None - все приоритеты)
            older_than_days: Очищать данные старше N дней (если None - по политике)

        Returns:
            Dict[str, Any]: Результат очистки
        """
        try:
            start_size = self.total_data_size
            start_time = datetime.now()

            if priority:
                cleaned_size = self._cleanup_priority_data(priority)
            else:
                # Очистка всех приоритетов
                cleaned_size = 0
                for p in DataPriority:
                    cleaned_size += self._cleanup_priority_data(p)

            end_time = datetime.now()
            end_size = self.total_data_size

            result = {
                "cleaned_size_mb": cleaned_size / (1024 * 1024),
                "start_size_gb": start_size / (1024 * 1024 * 1024),
                "end_size_gb": end_size / (1024 * 1024 * 1024),
                "freed_space_gb": (start_size - end_size) / (1024 * 1024 * 1024),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "priority": priority.value if priority else "all",
            }

            self.log_activity(f"Ручная очистка завершена: {result}")
            return result

        except Exception as e:
            self.log_activity(f"Ошибка ручной очистки: {e}", "error")
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера данных"""
        return {
            "name": self.name,
            "status": self.status.value,
            "data_directory": self.data_directory,
            "max_total_size_gb": self.max_total_size_gb,
            "enable_compression": self.enable_compression,
            "enable_archiving": self.enable_archiving,
            "storage_statistics": self.get_storage_statistics(),
        }


# Глобальный экземпляр умного менеджера данных
SMART_DATA_MANAGER = SmartDataManager()
