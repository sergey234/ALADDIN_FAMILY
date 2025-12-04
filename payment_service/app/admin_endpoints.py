"""
Admin Dashboard Endpoints
Endpoints для админ-панели
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional

from app.models import Payment, ActivationCode
from app.utils import generate_activation_code, now_utc
from app.database import get_session
from app.config import settings

router = APIRouter()


async def verify_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Проверка админского ключа"""
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return x_admin_key


@router.get("/users/list")
async def get_users_list(
    admin_key: str = Depends(verify_admin_key),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
):
    """
    Получить список всех пользователей с детальной информацией
    
    Args:
        limit: Количество записей на странице
        offset: Смещение для пагинации
        search: Поиск по alias
    
    Returns:
        Список пользователей с информацией о подписках и кодах
    """
    try:
        # Базовый запрос
        query = select(
            Payment.alias,
            func.count(Payment.id).label('total_payments'),
            func.count(func.distinct(Payment.id)).filter(Payment.status == 'paid').label('paid_payments'),
            func.max(Payment.created_at).label('last_payment_date'),
            func.max(ActivationCode.expires_at).label('latest_expires_at')
        ).outerjoin(
            ActivationCode, Payment.id == ActivationCode.payment_id
        ).group_by(Payment.alias)
        
        # Поиск по alias
        if search:
            query = query.where(Payment.alias.ilike(f'%{search}%'))
        
        # Сортировка по последнему платежу
        query = query.order_by(desc(func.max(Payment.created_at)))
        
        # Применяем limit и offset
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        users_data = result.all()
        
        # Формируем ответ
        users = []
        for row in users_data:
            alias = row.alias
            total_payments = row.total_payments
            paid_payments = row.paid_payments or 0
            
            # Обработка дат с учетом timezone
            last_payment_date = None
            if row.last_payment_date:
                if row.last_payment_date.tzinfo is None:
                    # Если дата без timezone, добавляем UTC
                    last_payment_date = row.last_payment_date.replace(tzinfo=timezone.utc).isoformat()
                else:
                    last_payment_date = row.last_payment_date.isoformat()
            
            latest_expires_at = None
            is_active = False
            if row.latest_expires_at:
                if row.latest_expires_at.tzinfo is None:
                    # Если дата без timezone, добавляем UTC
                    latest_expires_at = row.latest_expires_at.replace(tzinfo=timezone.utc).isoformat()
                    expires_at = row.latest_expires_at.replace(tzinfo=timezone.utc)
                else:
                    latest_expires_at = row.latest_expires_at.isoformat()
                    expires_at = row.latest_expires_at
                
                # Проверяем активность подписки
                is_active = expires_at > now_utc()
            
            users.append({
                "alias": alias,
                "total_payments": total_payments,
                "paid_payments": paid_payments,
                "last_payment_date": last_payment_date,
                "latest_expires_at": latest_expires_at,
                "is_active": is_active
            })
        
        # Получаем общее количество
        count_query = select(func.count(func.distinct(Payment.alias)))
        if search:
            count_query = count_query.where(Payment.alias.ilike(f'%{search}%'))
        
        total_count = await session.execute(count_query)
        total = total_count.scalar() or 0
        
        return {
            "users": users,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        print(f"❌ Error getting users list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threats/list")
async def get_threats_list(
    admin_key: str = Depends(verify_admin_key),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
):
    """
    Получить список угроз (пока заглушка, в будущем подключить к системе логирования)
    
    Args:
        limit: Количество записей на странице
        offset: Смещение для пагинации
        category: Фильтр по категории
    
    Returns:
        Список угроз
    """
    # TODO: В будущем подключить к реальной системе логирования угроз
    # Пока возвращаем примерные данные на основе статистики
    
    try:
        # Получаем количество активных пользователей
        active_users = await session.execute(
            select(func.count(func.distinct(Payment.alias)))
            .where(Payment.status == "paid")
        )
        users_count = active_users.scalar() or 0
        
        # Генерируем примерные данные угроз
        # В будущем это будет реальная база данных угроз
        threats = []
        
        # Примерные категории угроз
        threat_categories = {
            "malware": "Вредоносное ПО",
            "phishing": "Фишинг",
            "spam": "Спам",
            "suspicious": "Подозрительная активность",
            "blocked_url": "Заблокированный URL",
            "other": "Другое"
        }
        
        # Генерируем примерные угрозы на основе количества пользователей
        for i, (cat_key, cat_name) in enumerate(threat_categories.items()):
            if category and category != cat_key:
                continue
            
            threat_count = users_count * (i + 1) * 2  # Примерная формула
            
            threats.append({
                "id": f"threat_{cat_key}_{i}",
                "name": f"Угроза типа {cat_name}",
                "category": cat_key,
                "category_name": cat_name,
                "count": threat_count,
                "last_seen": (now_utc() - timedelta(hours=i)).isoformat(),
                "severity": "medium" if i % 2 == 0 else "high"
            })
        
        # Применяем limit и offset
        total = len(threats)
        threats = threats[offset:offset + limit]
        
        return {
            "threats": threats,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        print(f"❌ Error getting threats list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_logs(
    admin_key: str = Depends(verify_admin_key),
    service: str = Query("payment_service", regex="^(payment_service|nginx|system|security|mysql|postgresql|auth)$"),
    limit: int = Query(100, ge=1, le=500),
    level: Optional[str] = Query(None, regex="^(info|warning|error|debug)$"),
):
    """
    Получить логи сервисов
    
    Args:
        service: Название сервиса (payment_service, nginx, system)
        limit: Количество строк логов
        level: Фильтр по уровню (info, warning, error, debug)
    
    Returns:
        Логи сервиса
    """
    # TODO: В будущем подключить к централизованному логированию
    # Пока возвращаем информацию о том, как получить логи
    
    import subprocess
    import os
    
    try:
        # Определяем команды для получения логов
        if service == "payment_service":
            # Для payment_service пробуем сначала journalctl, потом tail файла
            commands = [
                f"/usr/bin/journalctl -u payment_service -n {limit} --no-pager 2>&1",
                f"/usr/bin/tail -n {limit} /tmp/payment_service.log 2>&1"
            ]
        elif service == "nginx":
            commands = [
                f"/usr/bin/tail -n {limit} /var/log/nginx/aladdin-ai.ru-error.log 2>&1",
                f"/usr/bin/tail -n {limit} /var/log/nginx/error.log 2>&1"
            ]
        elif service == "system":
            commands = [
                f"/usr/bin/journalctl -n {limit} --no-pager 2>&1",
                f"/usr/bin/tail -n {limit} /var/log/syslog 2>&1"
            ]
        elif service == "security":
            # Логи системы безопасности (VPN, Family, Security Monitoring)
            commands = [
                f"/usr/bin/tail -n {limit} /opt/aladdin-backend/security/vpn/logs/error.log 2>&1",
                f"/usr/bin/tail -n {limit} /opt/aladdin-backend/security/vpn/logs/security.log 2>&1",
                f"/usr/bin/tail -n {limit} /opt/aladdin-backend/security/vpn/logs/audit.log 2>&1",
                f"/usr/bin/tail -n {limit} /opt/aladdin-backend/security/family/logs/SecurityMonitoring.log 2>&1",
                f"/usr/bin/tail -n {limit} /opt/aladdin-backend/security/vpn/vpn_monitor.log 2>&1"
            ]
        elif service == "mysql":
            commands = [
                f"/usr/bin/journalctl -u mysql.service -n {limit} --no-pager 2>&1",
                f"/usr/bin/journalctl -u mariadb.service -n {limit} --no-pager 2>&1",
                f"/usr/bin/tail -n {limit} /var/log/mysql/error.log 2>&1"
            ]
        elif service == "postgresql":
            commands = [
                f"/usr/bin/journalctl -u postgresql.service -n {limit} --no-pager 2>&1",
                f"/usr/bin/journalctl -u postgresql@16-main.service -n {limit} --no-pager 2>&1",
                f"/usr/bin/tail -n {limit} /var/log/postgresql/postgresql-16-main.log 2>&1"
            ]
        elif service == "auth":
            commands = [
                f"/usr/bin/journalctl _COMM=sshd -n {limit} --no-pager 2>&1",
                f"/usr/bin/journalctl -u ssh.service -n {limit} --no-pager 2>&1",
                f"/usr/bin/tail -n {limit} /var/log/auth.log 2>&1"
            ]
        else:
            commands = [f"/usr/bin/tail -n {limit} /var/log/syslog 2>&1"]
        
        # Пытаемся выполнить команды
        logs = []
        error_msg = None
        
        for command in commands:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    executable="/bin/bash"
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    output = result.stdout.strip()
                    # Пропускаем "No entries" от journalctl
                    if "-- No entries --" not in output:
                        logs = output.split('\n')
                        # Фильтруем по уровню если указан
                        if level:
                            logs = [log for log in logs if level.upper() in log.upper()]
                        
                        if logs:
                            break  # Успешно получили логи
                else:
                    error_msg = result.stderr if result.stderr else "Команда не вернула данные"
            except subprocess.TimeoutExpired:
                error_msg = "Таймаут выполнения команды"
            except Exception as e:
                error_msg = str(e)
        
        if logs:
            return {
                "service": service,
                "logs": logs[-limit:] if len(logs) > limit else logs,
                "total": len(logs),
                "note": "Логи получены с сервера. Для централизованного логирования нужна настройка."
            }
        else:
            # Специальные сообщения для пустых логов
            empty_messages = {
                "mysql": "Логи MySQL пусты (нет ошибок) или логирование не настроено. Используйте: journalctl -u mysql.service -n 100",
                "postgresql": "Логи PostgreSQL пусты (нет ошибок) или логирование не настроено. Используйте: journalctl -u postgresql.service -n 100",
                "auth": "Логи авторизации не найдены. Используйте: journalctl _COMM=sshd -n 100"
            }
            
            return {
                "service": service,
                "logs": [],
                "total": 0,
                "error": error_msg or "Не удалось получить логи",
                "note": empty_messages.get(service, "Используйте SSH для просмотра логов на сервере. Команды: journalctl -u payment_service -n 100 или tail -f /tmp/payment_service.log")
            }
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/create-free")
async def create_free_subscription(
    alias: str = Body(...),
    tariff_id: str = Body("yearly"),  # или "lifetime" для навсегда
    duration_years: Optional[int] = Body(None),  # Количество лет (если не указано - год)
    admin_key: str = Depends(verify_admin_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Создать бесплатную подписку для пользователя
    
    Args:
        alias: ID пользователя (alias)
        tariff_id: ID тарифа (yearly, monthly, lifetime)
        duration_years: Количество лет подписки (если не указано - 1 год, для lifetime игнорируется)
    
    Returns:
        Информация о созданной подписке и код активации
    """
    try:
        # Определяем срок действия
        if tariff_id == "lifetime":
            # Навсегда - ставим дату далеко в будущем (2100 год)
            expires_at = datetime(2100, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        elif duration_years:
            expires_at = now_utc() + timedelta(days=duration_years * 365)
        else:
            # По умолчанию - 1 год
            expires_at = now_utc() + timedelta(days=365)
        
        # Создаем платеж со статусом "paid"
        payment = Payment(
            alias=alias,
            pin_hash="",  # Для бесплатной подписки PIN не нужен
            tariff_id=tariff_id,
            amount=0,  # Бесплатно
            status="paid",
            payment_method="admin_free",
            psp_payment_id=None
        )
        
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        
        # Генерируем код активации
        code = generate_activation_code()
        
        activation_code = ActivationCode(
            code=code,
            payment_id=payment.id,
            alias=alias,
            tariff_id=tariff_id,
            status="active",
            expires_at=expires_at,
            redeemed_at=None
        )
        
        session.add(activation_code)
        await session.commit()
        
        return {
            "success": True,
            "payment_id": payment.id,
            "activation_code": code,
            "alias": alias,
            "tariff_id": tariff_id,
            "expires_at": expires_at.isoformat(),
            "is_lifetime": tariff_id == "lifetime",
            "message": f"Бесплатная подписка создана для {alias}"
        }
    except Exception as e:
        print(f"❌ Error creating free subscription: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/user/{alias}")
async def get_user_subscriptions(
    alias: str,
    admin_key: str = Depends(verify_admin_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить все подписки пользователя
    
    Args:
        alias: ID пользователя (alias)
    
    Returns:
        Список всех подписок пользователя
    """
    try:
        # Получаем все платежи пользователя
        payments_result = await session.execute(
            select(Payment)
            .where(Payment.alias == alias)
            .order_by(desc(Payment.created_at))
        )
        payments = payments_result.scalars().all()
        
        subscriptions = []
        for payment in payments:
            # Получаем код активации если есть
            activation_result = await session.execute(
                select(ActivationCode).where(ActivationCode.payment_id == payment.id)
            )
            activation = activation_result.scalar_one_or_none()
            
            is_active = False
            if activation and activation.expires_at:
                is_active = activation.expires_at > now_utc()
            
            subscriptions.append({
                "payment_id": payment.id,
                "tariff_id": payment.tariff_id,
                "amount": payment.amount / 100 if payment.amount else 0,
                "status": payment.status,
                "payment_method": payment.payment_method,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "activation_code": activation.code if activation else None,
                "expires_at": activation.expires_at.isoformat() if activation and activation.expires_at else None,
                "is_active": is_active,
                "redeemed_at": activation.redeemed_at.isoformat() if activation and activation.redeemed_at else None
            })
        
        return {
            "alias": alias,
            "subscriptions": subscriptions,
            "total": len(subscriptions),
            "active_count": sum(1 for s in subscriptions if s["is_active"])
        }
    except Exception as e:
        print(f"❌ Error getting user subscriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

