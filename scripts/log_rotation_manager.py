#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Rotation Manager - Менеджер ротации логов
Автоматическая очистка и ротация лог-файлов для оптимизации производительности
"""

import os
import gzip
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class LogRotationManager:
    """Менеджер ротации логов"""
    
    def __init__(self, logs_dir: str = "logs", max_size_mb: int = 10, keep_days: int = 7):
        """
        Инициализация менеджера ротации логов
        
        Args:
            logs_dir: Директория с логами
            max_size_mb: Максимальный размер лог-файла в MB
            keep_days: Количество дней хранения логов
        """
        self.logs_dir = Path(logs_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.keep_days = keep_days
        self.rotation_stats = {
            "files_rotated": 0,
            "files_compressed": 0,
            "files_deleted": 0,
            "space_freed_mb": 0
        }
    
    def rotate_logs(self) -> Dict[str, Any]:
        """Ротация всех лог-файлов"""
        print("🔄 Начинаем ротацию логов...")
        
        if not self.logs_dir.exists():
            print(f"❌ Директория {self.logs_dir} не существует")
            return self.rotation_stats
        
        # Находим все лог-файлы
        log_files = list(self.logs_dir.glob("*.log"))
        
        for log_file in log_files:
            try:
                self._rotate_single_log(log_file)
            except Exception as e:
                print(f"❌ Ошибка ротации {log_file}: {e}")
        
        # Удаляем старые архивы
        self._cleanup_old_archives()
        
        print(f"✅ Ротация завершена. Статистика: {self.rotation_stats}")
        return self.rotation_stats
    
    def _rotate_single_log(self, log_file: Path):
        """Ротация одного лог-файла"""
        file_size = log_file.stat().st_size
        
        if file_size < self.max_size_bytes:
            return  # Файл не превышает лимит
        
        print(f"🔄 Ротируем {log_file.name} ({file_size / 1024 / 1024:.1f} MB)")
        
        # Создаем архивное имя с timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{log_file.stem}_{timestamp}.log.gz"
        archive_path = log_file.parent / archive_name
        
        # Сжимаем файл
        with open(log_file, 'rb') as f_in:
            with gzip.open(archive_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Очищаем оригинальный файл
        with open(log_file, 'w') as f:
            f.write("")
        
        self.rotation_stats["files_rotated"] += 1
        self.rotation_stats["files_compressed"] += 1
        self.rotation_stats["space_freed_mb"] += file_size / 1024 / 1024
        
        print(f"✅ {log_file.name} сжат в {archive_name}")
    
    def _cleanup_old_archives(self):
        """Удаление старых архивов"""
        cutoff_date = datetime.now() - timedelta(days=self.keep_days)
        
        for archive in self.logs_dir.glob("*.log.gz"):
            try:
                # Извлекаем дату из имени файла
                name_parts = archive.stem.split('_')
                if len(name_parts) >= 2:
                    date_str = f"{name_parts[-2]}_{name_parts[-1]}"
                    archive_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    
                    if archive_date < cutoff_date:
                        file_size = archive.stat().st_size
                        archive.unlink()
                        self.rotation_stats["files_deleted"] += 1
                        self.rotation_stats["space_freed_mb"] += file_size / 1024 / 1024
                        print(f"🗑️ Удален старый архив: {archive.name}")
                        
            except Exception as e:
                print(f"❌ Ошибка удаления {archive}: {e}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Получение статистики логов"""
        if not self.logs_dir.exists():
            return {"error": "Директория логов не существует"}
        
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "largest_file": None,
            "largest_size_mb": 0,
            "files_over_limit": 0
        }
        
        for log_file in self.logs_dir.glob("*.log"):
            file_size = log_file.stat().st_size
            size_mb = file_size / 1024 / 1024
            
            stats["total_files"] += 1
            stats["total_size_mb"] += size_mb
            
            if size_mb > stats["largest_size_mb"]:
                stats["largest_file"] = log_file.name
                stats["largest_size_mb"] = size_mb
            
            if file_size > self.max_size_bytes:
                stats["files_over_limit"] += 1
        
        return stats


def main():
    """Основная функция"""
    print("🚀 Запуск менеджера ротации логов ALADDIN")
    print("=" * 50)
    
    # Создаем менеджер ротации
    rotation_manager = LogRotationManager(
        logs_dir="logs",
        max_size_mb=10,  # 10 MB лимит
        keep_days=7      # Храним 7 дней
    )
    
    # Показываем текущую статистику
    print("📊 Текущая статистика логов:")
    stats = rotation_manager.get_log_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Выполняем ротацию
    rotation_result = rotation_manager.rotate_logs()
    
    print("\n📈 Результаты ротации:")
    for key, value in rotation_result.items():
        print(f"   {key}: {value}")
    
    print(f"\n💾 Освобождено места: {rotation_result['space_freed_mb']:.1f} MB")
    print("✅ Ротация логов завершена успешно!")


if __name__ == "__main__":
    main()