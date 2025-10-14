#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async IO Manager - Менеджер асинхронного I/O
Оптимизация I/O операций с использованием asyncio
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
import aiohttp


@dataclass
class IOOperation:
    """Операция I/O"""

    operation_id: str
    operation_type: (
        str  # 'file_read', 'file_write', 'http_request', 'database_query'
    )
    data: Any
    path: Optional[str] = None
    url: Optional[str] = None
    params: Optional[Dict] = None
    priority: int = 1


class AsyncIOManager:
    """Менеджер асинхронного I/O для оптимизации производительности"""

    def __init__(self, max_concurrent_operations: int = 50):
        """
        Инициализация менеджера асинхронного I/O

        Args:
            max_concurrent_operations: Максимальное количество
                одновременных операций
        """
        self.max_concurrent_operations = max_concurrent_operations
        self.semaphore = asyncio.Semaphore(max_concurrent_operations)
        self.logger = logging.getLogger(__name__)

        # Статистика
        self.stats = {
            "operations_completed": 0,
            "operations_failed": 0,
            "total_bytes_read": 0,
            "total_bytes_written": 0,
            "average_operation_time": 0.0,
            "concurrent_operations": 0,
        }

        # Очередь операций
        self.operation_queue = asyncio.Queue()

        # Флаг работы
        self._running = False

    async def start(self):
        """Запуск менеджера I/O"""
        self._running = True
        self.logger.info("Менеджер асинхронного I/O запущен")

    async def stop(self):
        """Остановка менеджера I/O"""
        self._running = False
        self.logger.info("Менеджер асинхронного I/O остановлен")

    async def read_file_async(self, file_path: Union[str, Path]) -> str:
        """
        Асинхронное чтение файла

        Args:
            file_path: Путь к файлу

        Returns:
            Содержимое файла
        """
        async with self.semaphore:
            start_time = time.time()
            try:
                async with aiofiles.open(
                    file_path, "r", encoding="utf-8"
                ) as f:
                    content = await f.read()

                self.stats["operations_completed"] += 1
                self.stats["total_bytes_read"] += len(content.encode("utf-8"))

                operation_time = time.time() - start_time
                self._update_average_time(operation_time)

                self.logger.debug(
                    f"Файл {file_path} прочитан за {operation_time:.3f}s"
                )
                return content

            except Exception as e:
                self.stats["operations_failed"] += 1
                self.logger.error(f"Ошибка чтения файла {file_path}: {e}")
                raise

    async def write_file_async(
        self, file_path: Union[str, Path], content: str
    ) -> bool:
        """
        Асинхронная запись файла

        Args:
            file_path: Путь к файлу
            content: Содержимое для записи

        Returns:
            True если успешно
        """
        async with self.semaphore:
            start_time = time.time()
            try:
                # Создаем директорию если не существует
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(
                    file_path, "w", encoding="utf-8"
                ) as f:
                    await f.write(content)

                self.stats["operations_completed"] += 1
                self.stats["total_bytes_written"] += len(
                    content.encode("utf-8")
                )

                operation_time = time.time() - start_time
                self._update_average_time(operation_time)

                self.logger.debug(
                    f"Файл {file_path} записан за {operation_time:.3f}s"
                )
                return True

            except Exception as e:
                self.stats["operations_failed"] += 1
                self.logger.error(f"Ошибка записи файла {file_path}: {e}")
                return False

    async def read_json_async(
        self, file_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Асинхронное чтение JSON файла

        Args:
            file_path: Путь к JSON файлу

        Returns:
            Словарь с данными
        """
        content = await self.read_file_async(file_path)
        return json.loads(content)

    async def write_json_async(
        self, file_path: Union[str, Path], data: Dict[str, Any]
    ) -> bool:
        """
        Асинхронная запись JSON файла

        Args:
            file_path: Путь к JSON файлу
            data: Данные для записи

        Returns:
            True если успешно
        """
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return await self.write_file_async(file_path, content)

    async def http_request_async(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Асинхронный HTTP запрос

        Args:
            url: URL для запроса
            method: HTTP метод
            params: Параметры запроса
            headers: Заголовки запроса

        Returns:
            Ответ сервера
        """
        async with self.semaphore:
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, url, params=params, headers=headers
                    ) as response:
                        data = await response.json()

                        self.stats["operations_completed"] += 1
                        operation_time = time.time() - start_time
                        self._update_average_time(operation_time)

                        self.logger.debug(
                            f"HTTP {method} {url} выполнен за "
                            f"{operation_time:.3f}s"
                        )
                        return {
                            "status": response.status,
                            "data": data,
                            "headers": dict(response.headers),
                        }

            except Exception as e:
                self.stats["operations_failed"] += 1
                self.logger.error(f"Ошибка HTTP запроса {url}: {e}")
                raise

    async def batch_file_operations(
        self, operations: List[IOOperation]
    ) -> List[Any]:
        """
        Пакетное выполнение I/O операций

        Args:
            operations: Список операций

        Returns:
            Результаты операций
        """
        tasks = []

        for op in operations:
            if op.operation_type == "file_read":
                task = self.read_file_async(op.path)
            elif op.operation_type == "file_write":
                task = self.write_file_async(op.path, op.data)
            elif op.operation_type == "json_read":
                task = self.read_json_async(op.path)
            elif op.operation_type == "json_write":
                task = self.write_json_async(op.path, op.data)
            elif op.operation_type == "http_request":
                task = self.http_request_async(op.url, params=op.params)
            else:
                self.logger.warning(
                    f"Неизвестный тип операции: {op.operation_type}"
                )
                continue

            tasks.append(task)

        # Выполняем все операции параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Ошибка в операции {i}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)

        return processed_results

    def _update_average_time(self, operation_time: float):
        """Обновление среднего времени выполнения операций"""
        total_ops = (
            self.stats["operations_completed"]
            + self.stats["operations_failed"]
        )
        if total_ops > 0:
            current_avg = self.stats["average_operation_time"]
            self.stats["average_operation_time"] = (
                current_avg * (total_ops - 1) + operation_time
            ) / total_ops

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики I/O операций"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["operations_completed"]
                / max(
                    1,
                    self.stats["operations_completed"]
                    + self.stats["operations_failed"],
                )
            )
            * 100,
            "max_concurrent": self.max_concurrent_operations,
        }

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Глобальный менеджер I/O
_global_io_manager = None


async def get_io_manager() -> AsyncIOManager:
    """Получение глобального менеджера I/O"""
    global _global_io_manager
    if _global_io_manager is None:
        _global_io_manager = AsyncIOManager()
        await _global_io_manager.start()
    return _global_io_manager


def get_io_manager_sync() -> AsyncIOManager:
    """Синхронное получение глобального менеджера I/O"""
    global _global_io_manager
    if _global_io_manager is None:
        _global_io_manager = AsyncIOManager()
        # Запускаем event loop только если он не запущен
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если loop уже запущен, создаем новый в отдельном потоке
                import threading
                import concurrent.futures
                
                def run_async_init():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(_global_io_manager.start())
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async_init)
                    future.result(timeout=5)
            else:
                loop.run_until_complete(_global_io_manager.start())
        except RuntimeError:
            # Если нет event loop, создаем новый
            asyncio.run(_global_io_manager.start())
    return _global_io_manager


# Удобные функции для быстрого использования
async def read_file_async(file_path: Union[str, Path]) -> str:
    """Быстрое асинхронное чтение файла"""
    manager = await get_io_manager()
    return await manager.read_file_async(file_path)


async def write_file_async(file_path: Union[str, Path], content: str) -> bool:
    """Быстрая асинхронная запись файла"""
    manager = await get_io_manager()
    return await manager.write_file_async(file_path, content)


async def read_json_async(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Быстрое асинхронное чтение JSON"""
    manager = await get_io_manager()
    return await manager.read_json_async(file_path)


async def write_json_async(
    file_path: Union[str, Path], data: Dict[str, Any]
) -> bool:
    """Быстрая асинхронная запись JSON"""
    manager = await get_io_manager()
    return await manager.write_json_async(file_path, data)


# Пример использования
async def main():
    """Пример использования асинхронного I/O менеджера"""
    print("🚀 Тестирование асинхронного I/O менеджера")

    async with AsyncIOManager(max_concurrent_operations=10) as io_manager:
        # Создаем тестовые файлы
        test_data = {
            "test1": {"message": "Hello World 1", "timestamp": time.time()},
            "test2": {"message": "Hello World 2", "timestamp": time.time()},
            "test3": {"message": "Hello World 3", "timestamp": time.time()},
        }

        # Параллельная запись файлов
        write_tasks = []
        for key, data in test_data.items():
            file_path = f"temp_{key}.json"
            task = io_manager.write_json_async(file_path, data)
            write_tasks.append(task)

        await asyncio.gather(*write_tasks)
        print("✅ Файлы записаны параллельно")

        # Параллельное чтение файлов
        read_tasks = []
        for key in test_data.keys():
            file_path = f"temp_{key}.json"
            task = io_manager.read_json_async(file_path)
            read_tasks.append(task)

        results = await asyncio.gather(*read_tasks)
        print(f"✅ Файлы прочитаны параллельно: {len(results)} файлов")

        # Показываем статистику
        stats = io_manager.get_statistics()
        print(f"📊 Статистика I/O: {stats}")

        # Очищаем тестовые файлы
        for key in test_data.keys():
            Path(f"temp_{key}.json").unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main())
