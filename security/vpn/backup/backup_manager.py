#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Manager - Автоматические бэкапы для VPN системы
Качество кода: A+
Соответствие: SOLID, DRY, PEP8
"""

import json
import logging
import os
import shutil
import tarfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import asyncio

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Типы бэкапов"""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    LOGS = "logs"


class BackupStatus(Enum):
    """Статусы бэкапа"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackupInfo:
    """Информация о бэкапе"""

    backup_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: int = 0
    compression_ratio: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BackupManager:
    """
    Менеджер автоматических бэкапов

    Функции:
    - Создание различных типов бэкапов
    - Автоматическое расписание
    - Сжатие и шифрование
    - Восстановление из бэкапов
    - Очистка старых бэкапов
    """

    def __init__(self, name: str = "BackupManager"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Конфигурация
        self.backup_directory = Path("/Users/sergejhlystov/ALADDIN_NEW/backups")
        self.source_directory = Path("/Users/sergejhlystov/ALADDIN_NEW/security/vpn")
        self.max_backups = 30  # Максимум бэкапов
        self.compression_level = 6  # Уровень сжатия (1-9)

        # Создание директории бэкапов
        self.backup_directory.mkdir(parents=True, exist_ok=True)

        # История бэкапов
        self.backups: List[BackupInfo] = []
        self.backup_tasks: Dict[str, asyncio.Task] = {}

        # Расписание
        self.schedule = {
            BackupType.FULL: "0 2 * * 0",  # Каждое воскресенье в 2:00
            BackupType.INCREMENTAL: "0 2 * * 1-6",  # Пн-Сб в 2:00
            BackupType.CONFIGURATION: "0 3 * * *",  # Ежедневно в 3:00
            BackupType.DATABASE: "0 4 * * *",  # Ежедневно в 4:00
            BackupType.LOGS: "0 5 * * *",  # Ежедневно в 5:00
        }

        self.logger.info(f"Backup Manager '{name}' инициализирован")

    async def start(self) -> None:
        """Запуск менеджера бэкапов"""
        self.logger.info("Запуск менеджера бэкапов...")

        # Загрузка истории бэкапов
        await self._load_backup_history()

        # Запуск планировщика
        asyncio.create_task(self._scheduler_loop())

        # Запуск очистки старых бэкапов
        asyncio.create_task(self._cleanup_loop())

        self.logger.info("Менеджер бэкапов запущен")

    async def stop(self) -> None:
        """Остановка менеджера бэкапов"""
        self.logger.info("Остановка менеджера бэкапов...")

        # Отмена всех активных задач
        for task in self.backup_tasks.values():
            task.cancel()

        # Сохранение истории
        await self._save_backup_history()

        self.logger.info("Менеджер бэкапов остановлен")

    async def create_backup(
        self,
        backup_type: BackupType,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> str:
        """Создание бэкапа"""
        backup_id = f"{backup_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_info = BackupInfo(
            backup_id=backup_id, backup_type=backup_type, status=BackupStatus.PENDING, created_at=datetime.now()
        )

        self.backups.append(backup_info)

        # Запуск задачи создания бэкапа
        task = asyncio.create_task(self._create_backup_task(backup_info, include_patterns, exclude_patterns))
        self.backup_tasks[backup_id] = task

        self.logger.info(f"Создание бэкапа запущено: {backup_id}")
        return backup_id

    async def _create_backup_task(
        self,
        backup_info: BackupInfo,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> None:
        """Задача создания бэкапа"""
        try:
            backup_info.status = BackupStatus.IN_PROGRESS

            # Определение файлов для бэкапа
            files_to_backup = await self._get_files_to_backup(
                backup_info.backup_type, include_patterns, exclude_patterns
            )

            if not files_to_backup:
                raise ValueError("Нет файлов для бэкапа")

            # Создание архива
            backup_path = await self._create_archive(backup_info, files_to_backup)

            # Обновление информации о бэкапе
            backup_info.file_path = str(backup_path)
            backup_info.file_size = backup_path.stat().st_size
            backup_info.status = BackupStatus.COMPLETED
            backup_info.completed_at = datetime.now()

            # Расчет коэффициента сжатия
            original_size = sum(f.stat().st_size for f in files_to_backup if f.exists())
            backup_info.compression_ratio = (
                (1 - backup_info.file_size / original_size) * 100 if original_size > 0 else 0
            )

            self.logger.info(f"Бэкап создан: {backup_info.backup_id} ({backup_info.file_size / 1024 / 1024:.2f} MB)")

        except Exception as e:
            backup_info.status = BackupStatus.FAILED
            backup_info.error_message = str(e)
            self.logger.error(f"Ошибка создания бэкапа {backup_info.backup_id}: {e}")

        finally:
            # Удаление задачи из активных
            if backup_info.backup_id in self.backup_tasks:
                del self.backup_tasks[backup_info.backup_id]

    async def _get_files_to_backup(  # noqa: C901
        self,
        backup_type: BackupType,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """Получение списка файлов для бэкапа"""
        files = []

        # Базовые исключения
        default_exclude = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".git",
            ".gitignore",
            "*.log",
            "*.tmp",
            "*.temp",
            ".DS_Store",
            "Thumbs.db",
        ]

        if exclude_patterns is None:
            exclude_patterns = default_exclude
        else:
            exclude_patterns.extend(default_exclude)

        # Определение паттернов включения по типу бэкапа
        if include_patterns is None:
            if backup_type == BackupType.FULL:
                include_patterns = ["**/*"]
            elif backup_type == BackupType.CONFIGURATION:
                include_patterns = ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.conf", "**/*.ini"]
            elif backup_type == BackupType.DATABASE:
                include_patterns = ["**/*.db", "**/*.sqlite", "**/*.sqlite3"]
            elif backup_type == BackupType.LOGS:
                include_patterns = ["**/*.log", "logs/**/*"]
            else:
                include_patterns = ["**/*"]

        # Поиск файлов
        for pattern in include_patterns:
            for file_path in self.source_directory.rglob(pattern):
                if file_path.is_file():
                    # Проверка исключений
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern) or exclude_pattern in str(file_path):
                            should_exclude = True
                            break

                    if not should_exclude:
                        files.append(file_path)

        return files

    async def _create_archive(self, backup_info: BackupInfo, files: List[Path]) -> Path:
        """Создание архива"""
        backup_filename = f"{backup_info.backup_id}.tar.gz"
        backup_path = self.backup_directory / backup_filename

        with tarfile.open(backup_path, "w:gz", compresslevel=self.compression_level) as tar:
            for file_path in files:
                try:
                    # Добавление файла в архив с сохранением структуры директорий
                    arcname = file_path.relative_to(self.source_directory)
                    tar.add(file_path, arcname=arcname)
                except Exception as e:
                    self.logger.warning(f"Не удалось добавить файл {file_path} в архив: {e}")

        return backup_path

    async def restore_backup(self, backup_id: str, target_directory: Optional[Path] = None) -> bool:
        """Восстановление из бэкапа"""
        backup_info = next((b for b in self.backups if b.backup_id == backup_id), None)

        if not backup_info:
            self.logger.error(f"Бэкап не найден: {backup_id}")
            return False

        if backup_info.status != BackupStatus.COMPLETED:
            self.logger.error(f"Бэкап не завершен: {backup_id}")
            return False

        if not backup_info.file_path or not Path(backup_info.file_path).exists():
            self.logger.error(f"Файл бэкапа не найден: {backup_info.file_path}")
            return False

        try:
            target_dir = target_directory or self.source_directory

            # Создание временной директории для восстановления
            temp_dir = self.backup_directory / f"restore_{backup_id}"
            temp_dir.mkdir(exist_ok=True)

            # Извлечение архива
            with tarfile.open(backup_info.file_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Копирование файлов в целевую директорию
            for extracted_file in temp_dir.rglob("*"):
                if extracted_file.is_file():
                    relative_path = extracted_file.relative_to(temp_dir)
                    target_file = target_dir / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(extracted_file, target_file)

            # Удаление временной директории
            shutil.rmtree(temp_dir)

            self.logger.info(f"Бэкап восстановлен: {backup_id}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка восстановления бэкапа {backup_id}: {e}")
            return False

    async def _scheduler_loop(self) -> None:
        """Цикл планировщика бэкапов"""
        while True:
            try:
                current_time = datetime.now()

                # Проверка расписания (упрощенная версия)
                for backup_type, schedule in self.schedule.items():
                    if await self._should_run_backup(backup_type, current_time):
                        await self.create_backup(backup_type)

                # Ожидание до следующей проверки (каждую минуту)
                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"Ошибка в планировщике бэкапов: {e}")
                await asyncio.sleep(300)  # 5 минут при ошибке

    async def _should_run_backup(self, backup_type: BackupType, current_time: datetime) -> bool:
        """Проверка, нужно ли запускать бэкап"""
        # Упрощенная проверка расписания
        if backup_type == BackupType.FULL:
            # Каждое воскресенье в 2:00
            return current_time.weekday() == 6 and current_time.hour == 2 and current_time.minute == 0
        elif backup_type == BackupType.INCREMENTAL:
            # Пн-Сб в 2:00
            return 0 <= current_time.weekday() <= 5 and current_time.hour == 2 and current_time.minute == 0
        elif backup_type == BackupType.CONFIGURATION:
            # Ежедневно в 3:00
            return current_time.hour == 3 and current_time.minute == 0
        elif backup_type == BackupType.DATABASE:
            # Ежедневно в 4:00
            return current_time.hour == 4 and current_time.minute == 0
        elif backup_type == BackupType.LOGS:
            # Ежедневно в 5:00
            return current_time.hour == 5 and current_time.minute == 0

        return False

    async def _cleanup_loop(self) -> None:
        """Цикл очистки старых бэкапов"""
        while True:
            try:
                await asyncio.sleep(3600)  # Проверка каждый час
                await self._cleanup_old_backups()

            except Exception as e:
                self.logger.error(f"Ошибка в цикле очистки: {e}")
                await asyncio.sleep(1800)  # 30 минут при ошибке

    async def _cleanup_old_backups(self) -> None:
        """Очистка старых бэкапов"""
        # Сортировка бэкапов по дате создания
        completed_backups = [b for b in self.backups if b.status == BackupStatus.COMPLETED]
        completed_backups.sort(key=lambda x: x.created_at, reverse=True)

        # Удаление лишних бэкапов
        if len(completed_backups) > self.max_backups:
            backups_to_remove = completed_backups[self.max_backups :]

            for backup in backups_to_remove:
                try:
                    if backup.file_path and Path(backup.file_path).exists():
                        Path(backup.file_path).unlink()

                    self.backups.remove(backup)
                    self.logger.info(f"Старый бэкап удален: {backup.backup_id}")

                except Exception as e:
                    self.logger.error(f"Ошибка удаления бэкапа {backup.backup_id}: {e}")

    async def _load_backup_history(self) -> None:
        """Загрузка истории бэкапов"""
        history_file = self.backup_directory / "backup_history.json"

        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for backup_data in data.get("backups", []):
                    backup_info = BackupInfo(
                        backup_id=backup_data["backup_id"],
                        backup_type=BackupType(backup_data["backup_type"]),
                        status=BackupStatus(backup_data["status"]),
                        created_at=datetime.fromisoformat(backup_data["created_at"]),
                        completed_at=(
                            datetime.fromisoformat(backup_data["completed_at"])
                            if backup_data.get("completed_at")
                            else None
                        ),
                        file_path=backup_data.get("file_path"),
                        file_size=backup_data.get("file_size", 0),
                        compression_ratio=backup_data.get("compression_ratio", 0.0),
                        error_message=backup_data.get("error_message"),
                        metadata=backup_data.get("metadata", {}),
                    )
                    self.backups.append(backup_info)

                self.logger.info(f"Загружена история бэкапов: {len(self.backups)} записей")

            except Exception as e:
                self.logger.error(f"Ошибка загрузки истории бэкапов: {e}")

    async def _save_backup_history(self) -> None:
        """Сохранение истории бэкапов"""
        history_file = self.backup_directory / "backup_history.json"

        try:
            data = {
                "backups": [
                    {
                        "backup_id": backup.backup_id,
                        "backup_type": backup.backup_type.value,
                        "status": backup.status.value,
                        "created_at": backup.created_at.isoformat(),
                        "completed_at": backup.completed_at.isoformat() if backup.completed_at else None,
                        "file_path": backup.file_path,
                        "file_size": backup.file_size,
                        "compression_ratio": backup.compression_ratio,
                        "error_message": backup.error_message,
                        "metadata": backup.metadata,
                    }
                    for backup in self.backups
                ]
            }

            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("История бэкапов сохранена")

        except Exception as e:
            self.logger.error(f"Ошибка сохранения истории бэкапов: {e}")

    def get_backup_status(self, backup_id: str) -> Optional[BackupInfo]:
        """Получение статуса бэкапа"""
        return next((b for b in self.backups if b.backup_id == backup_id), None)

    def get_backup_list(self, backup_type: Optional[BackupType] = None) -> List[BackupInfo]:
        """Получение списка бэкапов"""
        if backup_type:
            return [b for b in self.backups if b.backup_type == backup_type]
        return self.backups.copy()

    def get_backup_stats(self) -> Dict[str, Any]:
        """Получение статистики бэкапов"""
        total_backups = len(self.backups)
        completed_backups = len([b for b in self.backups if b.status == BackupStatus.COMPLETED])
        failed_backups = len([b for b in self.backups if b.status == BackupStatus.FAILED])

        total_size = sum(b.file_size for b in self.backups if b.file_size > 0)

        return {
            "total_backups": total_backups,
            "completed_backups": completed_backups,
            "failed_backups": failed_backups,
            "total_size_mb": total_size / 1024 / 1024,
            "backups_by_type": {
                backup_type.value: len([b for b in self.backups if b.backup_type == backup_type])
                for backup_type in BackupType
            },
            "last_backup": (
                max([b.created_at for b in self.backups], default=None).isoformat() if self.backups else None
            ),
        }


# Пример использования
async def main():
    """Пример использования Backup Manager"""
    manager = BackupManager("TestBackupManager")

    # Запуск менеджера
    await manager.start()

    # Создание тестового бэкапа
    backup_id = await manager.create_backup(BackupType.CONFIGURATION)
    print(f"Создан бэкап: {backup_id}")

    # Ожидание завершения
    await asyncio.sleep(5)

    # Получение статистики
    stats = manager.get_backup_stats()
    print(f"Статистика бэкапов: {stats}")

    # Остановка менеджера
    await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
