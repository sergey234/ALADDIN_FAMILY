#!/usr/bin/env python3
"""
ALADDIN Security System - Secrets API
Стандартизированный API для работы с секретами

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-26
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from core.security_base import ComponentStatus, SecurityBase
from security.secrets_manager import (
    SecretsManager,
    SecretType,
    get_secrets_manager,
)


class SecretsAPI(SecurityBase):
    """Стандартизированный API для работы с секретами"""

    def __init__(self, secrets_manager: Optional[SecretsManager] = None):
        """Инициализация API"""
        super().__init__("SecretsAPI")
        self.secrets_manager = secrets_manager or get_secrets_manager()
        self.log_activity("SecretsAPI инициализирован")

    def initialize(self) -> bool:
        """Инициализация API"""
        try:
            if not self.secrets_manager.initialize():
                self.log_activity(
                    "Ошибка инициализации SecretsManager", "error"
                )
                return False

            self.status = ComponentStatus.RUNNING
            self.log_activity("SecretsAPI инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(f"Ошибка инициализации SecretsAPI: {e}", "error")
            self.status = ComponentStatus.ERROR
            return False

    # ==================== ОСНОВНЫЕ ОПЕРАЦИИ ====================

    def create_secret(
        self,
        name: str,
        value: str,
        secret_type: str = "custom",
        expires_in_days: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Создание нового секрета

        Args:
            name: Название секрета
            value: Значение секрета
            secret_type: Тип секрета (password, api_key, jwt_token, etc.)
            expires_in_days: Срок действия в днях
            tags: Теги для категоризации
            description: Описание секрета
            owner: Владелец секрета

        Returns:
            Dict с информацией о созданном секрете
        """
        try:
            # Валидация параметров
            if not name or not isinstance(name, str):
                return {
                    "error": "Название секрета должно быть непустой строкой"
                }

            if not value or not isinstance(value, str):
                return {
                    "error": "Значение секрета должно быть непустой строкой"
                }

            # Преобразование типа секрета
            try:
                secret_type_enum = SecretType(secret_type.lower())
            except ValueError:
                return {"error": f"Неизвестный тип секрета: {secret_type}"}

            # Расчет даты истечения
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)

            # Создание секрета
            secret_id = self.secrets_manager.store_secret(
                name=name,
                value=value,
                secret_type=secret_type_enum,
                expires_at=expires_at,
                tags=tags,
                description=description,
                owner=owner,
            )

            # Получение метаданных
            metadata = self.secrets_manager.get_secret_metadata(secret_id)

            return {
                "success": True,
                "secret_id": secret_id,
                "name": name,
                "type": secret_type,
                "created_at": metadata["created_at"],
                "expires_at": metadata["expires_at"],
                "status": metadata["status"],
            }

        except Exception as e:
            self.log_activity(f"Ошибка создания секрета {name}: {e}", "error")
            return {"error": str(e)}

    def get_secret(
        self, identifier: str, by_name: bool = False
    ) -> Dict[str, Any]:
        """Получение секрета

        Args:
            identifier: ID секрета или имя (если by_name=True)
            by_name: Поиск по имени вместо ID

        Returns:
            Dict с секретом и метаданными
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Получение секрета
            if by_name:
                secret_value = self.secrets_manager.get_secret_by_name(
                    identifier
                )
                if secret_value is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }

                # Поиск метаданных по имени
                metadata = None
                for secret_id, meta in self.secrets_manager.metadata.items():
                    if meta.name == identifier:
                        metadata = meta.to_dict()
                        break
            else:
                secret_value = self.secrets_manager.get_secret(identifier)
                if secret_value is None:
                    return {"error": f"Секрет с ID '{identifier}' не найден"}

                metadata = self.secrets_manager.get_secret_metadata(identifier)

            if metadata is None:
                return {"error": "Метаданные секрета не найдены"}

            return {
                "success": True,
                "secret_id": metadata["secret_id"],
                "name": metadata["name"],
                "value": secret_value,
                "type": metadata["secret_type"],
                "status": metadata["status"],
                "created_at": metadata["created_at"],
                "expires_at": metadata["expires_at"],
                "access_count": metadata["access_count"],
                "version": metadata["version"],
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения секрета {identifier}: {e}", "error"
            )
            return {"error": str(e)}

    def update_secret(
        self,
        identifier: str,
        new_value: Optional[str] = None,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        new_tags: Optional[Dict[str, str]] = None,
        by_name: bool = False,
    ) -> Dict[str, Any]:
        """Обновление секрета

        Args:
            identifier: ID секрета или имя
            new_value: Новое значение секрета
            new_name: Новое имя секрета
            new_description: Новое описание
            new_tags: Новые теги
            by_name: Поиск по имени

        Returns:
            Dict с результатом обновления
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Поиск секрета
            if by_name:
                secret_id = None
                for sid, metadata in self.secrets_manager.metadata.items():
                    if metadata.name == identifier:
                        secret_id = sid
                        break
                if secret_id is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }
            else:
                secret_id = identifier
                if secret_id not in self.secrets_manager.secrets:
                    return {"error": f"Секрет с ID '{identifier}' не найден"}

            # Обновление значения (ротация)
            if new_value:
                success = self.secrets_manager.rotate_secret(
                    secret_id, new_value
                )
                if not success:
                    return {"error": "Ошибка обновления значения секрета"}

            # Обновление метаданных
            metadata = self.secrets_manager.metadata.get(secret_id)
            if metadata:
                if new_name:
                    metadata.name = new_name
                if new_description:
                    metadata.description = new_description
                if new_tags:
                    metadata.tags.update(new_tags)

            # Сохранение изменений
            self.secrets_manager._save_secrets()

            return {
                "success": True,
                "secret_id": secret_id,
                "message": "Секрет успешно обновлен",
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления секрета {identifier}: {e}", "error"
            )
            return {"error": str(e)}

    def delete_secret(
        self, identifier: str, by_name: bool = False
    ) -> Dict[str, Any]:
        """Удаление секрета

        Args:
            identifier: ID секрета или имя
            by_name: Поиск по имени

        Returns:
            Dict с результатом удаления
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Поиск секрета
            if by_name:
                secret_id = None
                for sid, metadata in self.secrets_manager.metadata.items():
                    if metadata.name == identifier:
                        secret_id = sid
                        break
                if secret_id is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }
            else:
                secret_id = identifier

            # Удаление секрета
            success = self.secrets_manager.delete_secret(secret_id)
            if not success:
                return {"error": "Ошибка удаления секрета"}

            return {
                "success": True,
                "message": f"Секрет {identifier} успешно удален",
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка удаления секрета {identifier}: {e}", "error"
            )
            return {"error": str(e)}

    def rotate_secret(
        self,
        identifier: str,
        new_value: Optional[str] = None,
        by_name: bool = False,
    ) -> Dict[str, Any]:
        """Ротация секрета

        Args:
            identifier: ID секрета или имя
            new_value: Новое значение (если не указано, генерируется
                автоматически)
            by_name: Поиск по имени

        Returns:
            Dict с результатом ротации
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Поиск секрета
            if by_name:
                secret_id = None
                for sid, metadata in self.secrets_manager.metadata.items():
                    if metadata.name == identifier:
                        secret_id = sid
                        break
                if secret_id is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }
            else:
                secret_id = identifier

            # Ротация секрета
            success = self.secrets_manager.rotate_secret(secret_id, new_value)
            if not success:
                return {"error": "Ошибка ротации секрета"}

            # Получение обновленных метаданных
            metadata = self.secrets_manager.get_secret_metadata(secret_id)

            return {
                "success": True,
                "secret_id": secret_id,
                "name": metadata["name"],
                "version": metadata["version"],
                "message": "Секрет успешно ротирован",
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка ротации секрета {identifier}: {e}", "error"
            )
            return {"error": str(e)}

    # ==================== СПИСКИ И ПОИСК ====================

    def list_secrets(
        self,
        secret_type: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Список секретов с фильтрацией

        Args:
            secret_type: Фильтр по типу секрета
            status: Фильтр по статусу
            owner: Фильтр по владельцу
            tags: Фильтр по тегам
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Dict со списком секретов
        """
        try:
            # Получение всех секретов
            all_secrets = self.secrets_manager.list_secrets()

            # Применение фильтров
            filtered_secrets = []

            for secret in all_secrets:
                # Фильтр по типу
                if secret_type and secret["type"] != secret_type:
                    continue

                # Фильтр по статусу
                if status and secret["status"] != status:
                    continue

                # Фильтр по владельцу
                if owner:
                    metadata = self.secrets_manager.get_secret_metadata(
                        secret["secret_id"]
                    )
                    if not metadata or metadata.get("owner") != owner:
                        continue

                # Фильтр по тегам
                if tags:
                    metadata = self.secrets_manager.get_secret_metadata(
                        secret["secret_id"]
                    )
                    if not metadata:
                        continue
                    secret_tags = metadata.get("tags", {})
                    if not all(
                        secret_tags.get(k) == v for k, v in tags.items()
                    ):
                        continue

                filtered_secrets.append(secret)

            # Пагинация
            total_count = len(filtered_secrets)
            if offset > 0:
                filtered_secrets = filtered_secrets[offset:]
            if limit:
                filtered_secrets = filtered_secrets[:limit]

            return {
                "success": True,
                "secrets": filtered_secrets,
                "total_count": total_count,
                "returned_count": len(filtered_secrets),
                "offset": offset,
                "limit": limit,
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения списка секретов: {e}", "error"
            )
            return {"error": str(e)}

    def search_secrets(
        self, query: str, search_in: List[str] = None
    ) -> Dict[str, Any]:
        """Поиск секретов по тексту

        Args:
            query: Поисковый запрос
            search_in: Поля для поиска (name, description, tags)

        Returns:
            Dict с результатами поиска
        """
        try:
            if not query:
                return {"error": "Поисковый запрос не может быть пустым"}

            if search_in is None:
                search_in = ["name", "description", "tags"]

            query_lower = query.lower()
            results = []

            for secret_id, metadata in self.secrets_manager.metadata.items():
                match = False

                # Поиск в имени
                if (
                    "name" in search_in
                    and query_lower in metadata.name.lower()
                ):
                    match = True

                # Поиск в описании
                if "description" in search_in and metadata.description:
                    if query_lower in metadata.description.lower():
                        match = True

                # Поиск в тегах
                if "tags" in search_in and metadata.tags:
                    for tag_key, tag_value in metadata.tags.items():
                        if (
                            query_lower in tag_key.lower()
                            or query_lower in tag_value.lower()
                        ):
                            match = True
                            break

                if match:
                    results.append(
                        {
                            "secret_id": secret_id,
                            "name": metadata.name,
                            "type": metadata.secret_type.value,
                            "status": metadata.status.value,
                            "created_at": metadata.created_at.isoformat(),
                            "description": metadata.description,
                        }
                    )

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
            }

        except Exception as e:
            self.log_activity(f"Ошибка поиска секретов: {e}", "error")
            return {"error": str(e)}

    # ==================== МЕТАДАННЫЕ ====================

    def get_secret_metadata(
        self, identifier: str, by_name: bool = False
    ) -> Dict[str, Any]:
        """Получение метаданных секрета

        Args:
            identifier: ID секрета или имя
            by_name: Поиск по имени

        Returns:
            Dict с метаданными секрета
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Поиск секрета
            if by_name:
                metadata = None
                for sid, meta in self.secrets_manager.metadata.items():
                    if meta.name == identifier:
                        metadata = meta.to_dict()
                        break
                if metadata is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }
            else:
                metadata = self.secrets_manager.get_secret_metadata(identifier)
                if metadata is None:
                    return {"error": f"Секрет с ID '{identifier}' не найден"}

            return {"success": True, "metadata": metadata}

        except Exception as e:
            self.log_activity(
                f"Ошибка получения метаданных секрета {identifier}: {e}",
                "error",
            )
            return {"error": str(e)}

    def update_secret_metadata(
        self,
        identifier: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        owner: Optional[str] = None,
        by_name: bool = False,
    ) -> Dict[str, Any]:
        """Обновление метаданных секрета

        Args:
            identifier: ID секрета или имя
            description: Новое описание
            tags: Новые теги
            owner: Новый владелец
            by_name: Поиск по имени

        Returns:
            Dict с результатом обновления
        """
        try:
            if not identifier:
                return {"error": "Идентификатор секрета не может быть пустым"}

            # Поиск секрета
            if by_name:
                secret_id = None
                for sid, metadata in self.secrets_manager.metadata.items():
                    if metadata.name == identifier:
                        secret_id = sid
                        break
                if secret_id is None:
                    return {
                        "error": f"Секрет с именем '{identifier}' не найден"
                    }
            else:
                secret_id = identifier

            # Обновление метаданных
            metadata = self.secrets_manager.metadata.get(secret_id)
            if not metadata:
                return {"error": f"Секрет с ID '{secret_id}' не найден"}

            if description is not None:
                metadata.description = description
            if tags is not None:
                metadata.tags.update(tags)
            if owner is not None:
                metadata.owner = owner

            # Сохранение изменений
            self.secrets_manager._save_secrets()

            return {
                "success": True,
                "secret_id": secret_id,
                "message": "Метаданные секрета обновлены",
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка обновления метаданных секрета {identifier}: {e}",
                "error",
            )
            return {"error": str(e)}

    # ==================== СТАТИСТИКА И МЕТРИКИ ====================

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по секретам

        Returns:
            Dict со статистикой
        """
        try:
            all_secrets = self.secrets_manager.list_secrets()

            # Подсчет по типам
            type_counts = {}
            status_counts = {}
            total_access_count = 0
            expired_count = 0

            for secret in all_secrets:
                # По типам
                secret_type = secret["type"]
                type_counts[secret_type] = type_counts.get(secret_type, 0) + 1

                # По статусам
                status = secret["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

                # Общее количество обращений
                total_access_count += secret["access_count"]

                # Истекшие секреты
                if status == "expired":
                    expired_count += 1

            # Метрики менеджера
            manager_metrics = self.secrets_manager.get_metrics()

            return {
                "success": True,
                "statistics": {
                    "total_secrets": len(all_secrets),
                    "type_distribution": type_counts,
                    "status_distribution": status_counts,
                    "total_access_count": total_access_count,
                    "expired_secrets": expired_count,
                    "manager_metrics": manager_metrics,
                },
            }

        except Exception as e:
            self.log_activity(f"Ошибка получения статистики: {e}", "error")
            return {"error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья системы секретов

        Returns:
            Dict со статусом здоровья
        """
        try:
            manager_health = self.secrets_manager.health_check()

            return {
                "success": True,
                "health": {
                    "api_status": self.status.value,
                    "manager_status": manager_health["status"],
                    "secrets_count": manager_health["secrets_count"],
                    "external_providers": manager_health["external_providers"],
                    "storage_writable": manager_health["storage_writable"],
                    "rotation_active": manager_health["rotation_thread"],
                },
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка получения статуса здоровья: {e}", "error"
            )
            return {"error": str(e)}

    # ==================== МАССОВЫЕ ОПЕРАЦИИ ====================

    def bulk_create_secrets(
        self, secrets_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Массовое создание секретов

        Args:
            secrets_data: Список данных для создания секретов

        Returns:
            Dict с результатами массового создания
        """
        try:
            if not secrets_data:
                return {"error": "Список секретов не может быть пустым"}

            results = []
            success_count = 0
            error_count = 0

            for secret_data in secrets_data:
                result = self.create_secret(**secret_data)
                results.append(result)

                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1

            return {
                "success": True,
                "total": len(secrets_data),
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка массового создания секретов: {e}", "error"
            )
            return {"error": str(e)}

    def bulk_delete_secrets(
        self, identifiers: List[str], by_name: bool = False
    ) -> Dict[str, Any]:
        """Массовое удаление секретов

        Args:
            identifiers: Список ID секретов или имен
            by_name: Поиск по имени

        Returns:
            Dict с результатами массового удаления
        """
        try:
            if not identifiers:
                return {"error": "Список идентификаторов не может быть пустым"}

            results = []
            success_count = 0
            error_count = 0

            for identifier in identifiers:
                result = self.delete_secret(identifier, by_name=by_name)
                results.append(result)

                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1

            return {
                "success": True,
                "total": len(identifiers),
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка массового удаления секретов: {e}", "error"
            )
            return {"error": str(e)}

    def bulk_rotate_secrets(
        self, identifiers: List[str], by_name: bool = False
    ) -> Dict[str, Any]:
        """Массовая ротация секретов

        Args:
            identifiers: Список ID секретов или имен
            by_name: Поиск по имени

        Returns:
            Dict с результатами массовой ротации
        """
        try:
            if not identifiers:
                return {"error": "Список идентификаторов не может быть пустым"}

            results = []
            success_count = 0
            error_count = 0

            for identifier in identifiers:
                result = self.rotate_secret(identifier, by_name=by_name)
                results.append(result)

                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1

            return {
                "success": True,
                "total": len(identifiers),
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
            }

        except Exception as e:
            self.log_activity(
                f"Ошибка массовой ротации секретов: {e}", "error"
            )
            return {"error": str(e)}


# Глобальный экземпляр API
_secrets_api_instance = None


def get_secrets_api() -> SecretsAPI:
    """Получение глобального экземпляра API секретов"""
    global _secrets_api_instance
    if _secrets_api_instance is None:
        _secrets_api_instance = SecretsAPI()
        _secrets_api_instance.initialize()
    return _secrets_api_instance


def initialize_secrets_api(
    secrets_manager: Optional[SecretsManager] = None,
) -> SecretsAPI:
    """Инициализация глобального API секретов"""
    global _secrets_api_instance
    _secrets_api_instance = SecretsAPI(secrets_manager)
    _secrets_api_instance.initialize()
    return _secrets_api_instance


# Удобные функции для быстрого доступа
def create_secret(name: str, value: str, **kwargs) -> Dict[str, Any]:
    """Быстрое создание секрета"""
    api = get_secrets_api()
    return api.create_secret(name, value, **kwargs)


def get_secret(identifier: str, by_name: bool = False) -> Dict[str, Any]:
    """Быстрое получение секрета"""
    api = get_secrets_api()
    return api.get_secret(identifier, by_name=by_name)


def delete_secret(identifier: str, by_name: bool = False) -> Dict[str, Any]:
    """Быстрое удаление секрета"""
    api = get_secrets_api()
    return api.delete_secret(identifier, by_name=by_name)


def list_secrets(**kwargs) -> Dict[str, Any]:
    """Быстрое получение списка секретов"""
    api = get_secrets_api()
    return api.list_secrets(**kwargs)


if __name__ == "__main__":
    # Пример использования API
    api = initialize_secrets_api()

    # Создание секрета
    result = api.create_secret(
        name="test_api_key",
        value="test_value_123",
        secret_type="api_key",
        description="Тестовый API ключ",
        tags={"environment": "test", "service": "api"},
    )
    print(f"Создание секрета: {result}")

    if result.get("success"):
        secret_id = result["secret_id"]

        # Получение секрета
        secret = api.get_secret(secret_id)
        print(f"Получение секрета: {secret}")

        # Список секретов
        secrets_list = api.list_secrets(limit=10)
        print(f"Список секретов: {secrets_list}")

        # Статистика
        stats = api.get_statistics()
        print(f"Статистика: {stats}")

        # Удаление секрета
        delete_result = api.delete_secret(secret_id)
        print(f"Удаление секрета: {delete_result}")
