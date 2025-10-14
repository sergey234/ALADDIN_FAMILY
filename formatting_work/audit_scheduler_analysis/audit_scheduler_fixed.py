#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Scheduler для ALADDIN Security System
Планировщик автоматических аудитов с расписанием и уведомлениями

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
# import json  # Не используется
# import os  # Не используется
import smtplib
import sqlite3
# import threading  # Не используется
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from typing import Any, Dict, List, Optional

import schedule

from automated_audit_system import AuditResult, AuditType, AutomatedAuditSystem


@dataclass
class AuditSchedule:
    """Расписание аудита"""

    audit_type: AuditType
    frequency: str  # daily, weekly, monthly
    time: str  # HH:MM format
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class NotificationConfig:
    """Конфигурация уведомлений"""

    email_enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_recipients: List[str] = None
    slack_enabled: bool = False
    slack_webhook: str = ""
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


class AuditScheduler:
    """Планировщик аудитов"""

    def __init__(self, db_path: str = "audit_schedule.db"):
        self.db_path = db_path
        self.audit_system = AutomatedAuditSystem()
        self.notification_config = NotificationConfig()
        self.init_database()
        self.load_schedules()

    def init_database(self):
        """Инициализация базы данных расписаний"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_type TEXT,
                frequency TEXT,
                time TEXT,
                enabled BOOLEAN,
                last_run DATETIME,
                next_run DATETIME
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_config (
                id INTEGER PRIMARY KEY,
                email_enabled BOOLEAN,
                smtp_server TEXT,
                smtp_port INTEGER,
                smtp_username TEXT,
                smtp_password TEXT,
                email_recipients TEXT,
                slack_enabled BOOLEAN,
                slack_webhook TEXT,
                telegram_enabled BOOLEAN,
                telegram_bot_token TEXT,
                telegram_chat_id TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def load_schedules(self):
        """Загрузка расписаний из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM audit_schedules")
        rows = cursor.fetchall()

        self.schedules = []
        for row in rows:
            schedule = AuditSchedule(
                audit_type=AuditType(row[1]),
                frequency=row[2],
                time=row[3],
                enabled=bool(row[4]),
                last_run=datetime.fromisoformat(row[5]) if row[5] else None,
                next_run=datetime.fromisoformat(row[6]) if row[6] else None,
            )
            self.schedules.append(schedule)

        conn.close()

    def save_schedule(self, schedule: AuditSchedule):
        """Сохранение расписания"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO audit_schedules
            (audit_type, frequency, time, enabled, last_run, next_run)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                schedule.audit_type.value,
                schedule.frequency,
                schedule.time,
                schedule.enabled,
                schedule.last_run.isoformat() if schedule.last_run else None,
                schedule.next_run.isoformat() if schedule.next_run else None,
            ),
        )

        conn.commit()
        conn.close()

    def add_schedule(self, audit_type: AuditType, frequency: str, time: str):
        """Добавление нового расписания"""
        schedule = AuditSchedule(
            audit_type=audit_type, frequency=frequency, time=time, enabled=True
        )

        # Вычисляем следующее время запуска
        schedule.next_run = self._calculate_next_run(frequency, time)

        self.schedules.append(schedule)
        self.save_schedule(schedule)

        print(
            f"✅ Добавлено расписание: {audit_type.value} - {frequency} в {time}"
        )

    def _calculate_next_run(self, frequency: str, time: str) -> datetime:
        """Вычисление следующего времени запуска"""
        now = datetime.now()
        hour, minute = map(int, time.split(":"))

        if frequency == "daily":
            next_run = now.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
        elif frequency == "weekly":
            # Запуск в понедельник
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
        elif frequency == "monthly":
            # Запуск в первый день месяца
            if now.month == 12:
                next_run = now.replace(
                    year=now.year + 1,
                    month=1,
                    day=1,
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )
            else:
                next_run = now.replace(
                    month=now.month + 1,
                    day=1,
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )
        else:
            next_run = now + timedelta(hours=1)

        return next_run

    async def run_scheduled_audit(self, schedule: AuditSchedule):
        """Запуск запланированного аудита"""
        print(
            f"🔍 Запуск запланированного аудита: {schedule.audit_type.value}"
        )

        try:
            # Запуск соответствующего аудита
            if schedule.audit_type == AuditType.SECURITY:
                result = await self.audit_system.run_security_audit()
            elif schedule.audit_type == AuditType.COMPLIANCE:
                result = await self.audit_system.run_compliance_audit()
            elif schedule.audit_type == AuditType.PERFORMANCE:
                result = await self.audit_system.run_performance_audit()
            elif schedule.audit_type == AuditType.CODE_QUALITY:
                result = await self.audit_system.run_code_quality_audit()
            elif schedule.audit_type == AuditType.DEPENDENCIES:
                result = await self.audit_system.run_dependencies_audit()
            elif schedule.audit_type == AuditType.INFRASTRUCTURE:
                result = await self.audit_system.run_infrastructure_audit()
            else:
                print(f"❌ Неизвестный тип аудита: {schedule.audit_type}")
                return

            # Обновление расписания
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(
                schedule.frequency, schedule.time
            )
            self.save_schedule(schedule)

            # Отправка уведомлений
            await self.send_notifications(result)

            print(
                f"✅ Аудит {schedule.audit_type.value} завершен с оценкой {result.score}"
            )

        except Exception as e:
            print(
                f"❌ Ошибка при выполнении аудита {schedule.audit_type.value}: {e}"
            )

    async def send_notifications(self, result: AuditResult):
        """Отправка уведомлений о результатах аудита"""
        if result.status == "failed" or result.severity.value in [
            "critical",
            "high",
        ]:
            message = self._format_notification_message(result)

            if self.notification_config.email_enabled:
                await self._send_email_notification(message, result)

            if self.notification_config.slack_enabled:
                await self._send_slack_notification(message, result)

            if self.notification_config.telegram_enabled:
                await self._send_telegram_notification(message, result)

    def _format_notification_message(self, result: AuditResult) -> str:
        """Форматирование сообщения уведомления"""
        status_emoji = (
            "❌"
            if result.status == "failed"
            else "⚠️" if result.status == "warning" else "✅"
        )

        message = f"""
{status_emoji} **Аудит {result.audit_type.value.upper()}**

**Статус:** {result.status.upper()}
**Оценка:** {result.score}/100
**Серьезность:** {result.severity.value.upper()}
**Время выполнения:** {result.duration:.2f}s

**Находки:** {len(result.findings)}
**Рекомендации:** {len(result.recommendations)}

**Время:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        return message

    async def _send_email_notification(
        self, message: str, result: AuditResult
    ):
        """Отправка email уведомления"""
        try:
            msg = MimeMultipart()
            msg["From"] = self.notification_config.smtp_username
            msg["To"] = ", ".join(self.notification_config.email_recipients)
            msg["Subject"] = f"ALADDIN Audit Alert: {result.audit_type.value}"

            msg.attach(MimeText(message, "plain"))

            server = smtplib.SMTP(
                self.notification_config.smtp_server,
                self.notification_config.smtp_port,
            )
            server.starttls()
            server.login(
                self.notification_config.smtp_username,
                self.notification_config.smtp_password,
            )
            server.send_message(msg)
            server.quit()

            print("✅ Email уведомление отправлено")

        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")

    async def _send_slack_notification(
        self, message: str, result: AuditResult
    ):
        """Отправка Slack уведомления"""
        try:
            import httpx

            payload = {
                "text": message,
                "username": "ALADDIN Audit Bot",
                "icon_emoji": ":shield:",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.notification_config.slack_webhook,
                    json=payload,
                    timeout=10,
                )
                response.raise_for_status()

            print("✅ Slack уведомление отправлено")

        except Exception as e:
            print(f"❌ Ошибка отправки Slack: {e}")

    async def _send_telegram_notification(
        self, message: str, result: AuditResult
    ):
        """Отправка Telegram уведомления"""
        try:
            import httpx

            url = f"https://api.telegram.org/bot{self.notification_config.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.notification_config.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()

            print("✅ Telegram уведомление отправлено")

        except Exception as e:
            print(f"❌ Ошибка отправки Telegram: {e}")

    def check_scheduled_audits(self):
        """Проверка запланированных аудитов"""
        now = datetime.now()

        for audit_schedule in self.schedules:
            if not audit_schedule.enabled:
                continue

            if audit_schedule.next_run and now >= audit_schedule.next_run:
                asyncio.create_task(self.run_scheduled_audit(audit_schedule))

    def start_scheduler(self):
        """Запуск планировщика"""
        print("🚀 Запуск планировщика аудитов...")

        # Настройка расписаний по умолчанию
        if not self.schedules:
            self.add_schedule(AuditType.SECURITY, "daily", "02:00")
            self.add_schedule(AuditType.COMPLIANCE, "weekly", "03:00")
            self.add_schedule(AuditType.PERFORMANCE, "daily", "04:00")
            self.add_schedule(AuditType.CODE_QUALITY, "daily", "05:00")
            self.add_schedule(AuditType.DEPENDENCIES, "weekly", "06:00")
            self.add_schedule(AuditType.INFRASTRUCTURE, "monthly", "07:00")

        # Запуск проверки каждую минуту
        schedule.every().minute.do(self.check_scheduled_audits)

        print("✅ Планировщик запущен")
        print("📅 Расписание аудитов:")
        for s in self.schedules:
            if s.enabled:
                print(f"  - {s.audit_type.value}: {s.frequency} в {s.time}")

        # Основной цикл
        while True:
            schedule.run_pending()
            time.sleep(1)

    def stop_scheduler(self):
        """Остановка планировщика"""
        print("🛑 Остановка планировщика аудитов...")
        schedule.clear()
        print("✅ Планировщик остановлен")

    def get_schedule_status(self) -> Dict[str, Any]:
        """Получение статуса расписаний"""
        now = datetime.now()

        status = {
            "total_schedules": len(self.schedules),
            "enabled_schedules": len([s for s in self.schedules if s.enabled]),
            "disabled_schedules": len(
                [s for s in self.schedules if not s.enabled]
            ),
            "schedules": [],
        }

        for audit_schedule in self.schedules:
            schedule_info = {
                "audit_type": audit_schedule.audit_type.value,
                "frequency": audit_schedule.frequency,
                "time": audit_schedule.time,
                "enabled": audit_schedule.enabled,
                "last_run": (
                    audit_schedule.last_run.isoformat()
                    if audit_schedule.last_run
                    else None
                ),
                "next_run": (
                    audit_schedule.next_run.isoformat()
                    if audit_schedule.next_run
                    else None
                ),
                "overdue": (
                    audit_schedule.next_run < now if audit_schedule.next_run else False
                ),
            }
            status["schedules"].append(schedule_info)

        return status


# Пример использования
async def main():
    """Основная функция"""
    scheduler = AuditScheduler()

    # Настройка уведомлений (пример)
    scheduler.notification_config.email_enabled = (
        False  # Настроить по необходимости
    )
    scheduler.notification_config.slack_enabled = (
        False  # Настроить по необходимости
    )
    scheduler.notification_config.telegram_enabled = (
        False  # Настроить по необходимости
    )

    # Запуск планировщика
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        scheduler.stop_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
