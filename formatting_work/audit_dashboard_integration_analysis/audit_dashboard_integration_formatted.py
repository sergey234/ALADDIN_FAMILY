#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Dashboard Integration для ALADDIN Security System
Интеграция системы аудитов с дашбордом

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from audit_scheduler import AuditSchedule, AuditScheduler
from automated_audit_system import AuditResult, AuditType, AutomatedAuditSystem
from compliance_monitor import (
    ComplianceLevel,
    ComplianceMonitor,
    ComplianceStandard,
)

# Создание роутера для API аудитов
audit_router = APIRouter(prefix="/api/audits", tags=["audits"])

# Глобальные экземпляры систем
audit_system = None
audit_scheduler = None
compliance_monitor = None


def initialize_audit_systems():
    """Инициализация систем аудитов"""
    global audit_system, audit_scheduler, compliance_monitor

    if audit_system is None:
        audit_system = AutomatedAuditSystem("audit_results.db")

    if audit_scheduler is None:
        audit_scheduler = AuditScheduler("audit_schedule.db")

    if compliance_monitor is None:
        compliance_monitor = ComplianceMonitor("compliance_monitor.db")
        compliance_monitor.initialize_default_requirements()


# API Endpoints для аудитов


@audit_router.get("/status")
async def get_audit_status():
    """Получение статуса системы аудитов"""
    initialize_audit_systems()

    # Получение последних результатов аудитов
    recent_audits = audit_system.get_audit_results(limit=10)

    # Статистика по типам аудитов
    audit_stats = {}
    for audit_type in AuditType:
        type_audits = [a for a in recent_audits if a.audit_type == audit_type]
        if type_audits:
            latest_audit = type_audits[0]
            audit_stats[audit_type.value] = {
                "last_run": latest_audit.timestamp.isoformat(),
                "status": latest_audit.status,
                "score": latest_audit.score,
                "severity": latest_audit.severity.value,
            }

    # Статус планировщика
    schedule_status = audit_scheduler.get_schedule_status()

    # Дашборд соответствия
    compliance_dashboard = compliance_monitor.get_compliance_dashboard()

    return {
        "audit_system": {
            "status": "active",
            "total_audits": len(recent_audits),
            "recent_audits": audit_stats,
        },
        "scheduler": schedule_status,
        "compliance": compliance_dashboard["summary"],
        "last_updated": datetime.now().isoformat(),
    }


@audit_router.get("/results")
async def get_audit_results(
    audit_type: Optional[str] = None,
    limit: int = 100,
    status: Optional[str] = None,
):
    """Получение результатов аудитов"""
    initialize_audit_systems()

    # Фильтрация по типу аудита
    if audit_type:
        try:
            audit_type_enum = AuditType(audit_type)
            results = audit_system.get_audit_results(audit_type_enum, limit)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid audit type: {audit_type}"
            )
    else:
        results = audit_system.get_audit_results(limit=limit)

    # Фильтрация по статусу
    if status:
        results = [r for r in results if r.status == status]

    # Конвертация в словари
    audit_results = []
    for result in results:
        audit_results.append(
            {
                "audit_id": result.audit_id,
                "audit_type": result.audit_type.value,
                "severity": result.severity.value,
                "title": result.title,
                "description": result.description,
                "status": result.status,
                "score": result.score,
                "findings": result.findings,
                "recommendations": result.recommendations,
                "timestamp": result.timestamp.isoformat(),
                "duration": result.duration,
                "compliance_standards": [
                    s.value for s in result.compliance_standards
                ],
                "metadata": result.metadata,
            }
        )

    return {
        "results": audit_results,
        "total": len(audit_results),
        "filters": {
            "audit_type": audit_type,
            "status": status,
            "limit": limit,
        },
    }


@audit_router.post("/run")
async def run_audit(
    background_tasks: BackgroundTasks,
    audit_type: str,
    compliance_standard: Optional[str] = None,
):
    """Запуск аудита"""
    initialize_audit_systems()

    try:
        audit_type_enum = AuditType(audit_type)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid audit type: {audit_type}"
        )

    # Запуск аудита в фоновом режиме
    background_tasks.add_task(run_audit_task, audit_type_enum)

    return {
        "message": f"Audit {audit_type} started",
        "audit_type": audit_type,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


async def run_audit_task(audit_type: AuditType):
    """Фоновая задача запуска аудита"""
    try:
        if audit_type == AuditType.SECURITY:
            result = await audit_system.run_security_audit()
        elif audit_type == AuditType.COMPLIANCE:
            result = await audit_system.run_compliance_audit()
        elif audit_type == AuditType.PERFORMANCE:
            result = await audit_system.run_performance_audit()
        elif audit_type == AuditType.CODE_QUALITY:
            result = await audit_system.run_code_quality_audit()
        elif audit_type == AuditType.DEPENDENCIES:
            result = await audit_system.run_dependencies_audit()
        elif audit_type == AuditType.INFRASTRUCTURE:
            result = await audit_system.run_infrastructure_audit()
        else:
            print(f"Unknown audit type: {audit_type}")
            return

        print(
            f"✅ Audit {audit_type.value} completed: {result.status} ({result.score}%)"
        )

    except Exception as e:
        print(f"❌ Error running audit {audit_type.value}: {e}")


@audit_router.post("/run-all")
async def run_all_audits(background_tasks: BackgroundTasks):
    """Запуск всех аудитов"""
    initialize_audit_systems()

    background_tasks.add_task(run_all_audits_task)

    return {
        "message": "All audits started",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


async def run_all_audits_task():
    """Фоновая задача запуска всех аудитов"""
    try:
        results = await audit_system.run_all_audits()
        print(f"✅ All {len(results)} audits completed")

        # Генерация отчета
        report = audit_system.generate_audit_report(results)

        # Сохранение отчета
        with open("audit_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        print("📊 Audit report saved to audit_report.json")

    except Exception as e:
        print(f"❌ Error running all audits: {e}")


@audit_router.get("/report")
async def get_audit_report():
    """Получение отчета по аудитам"""
    initialize_audit_systems()

    # Получение всех результатов
    all_results = audit_system.get_audit_results(limit=1000)

    # Генерация отчета
    report = audit_system.generate_audit_report(all_results)

    return report


@audit_router.get("/schedule")
async def get_audit_schedule():
    """Получение расписания аудитов"""
    initialize_audit_systems()

    status = audit_scheduler.get_schedule_status()
    return status


@audit_router.post("/schedule")
async def add_audit_schedule(audit_type: str, frequency: str, time: str):
    """Добавление расписания аудита"""
    initialize_audit_systems()

    try:
        audit_type_enum = AuditType(audit_type)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid audit type: {audit_type}"
        )

    if frequency not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid frequency. Must be: daily, weekly, monthly",
        )

    # Проверка формата времени
    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time format")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid time format. Use HH:MM"
        )

    audit_scheduler.add_schedule(audit_type_enum, frequency, time)

    return {
        "message": f"Schedule added for {audit_type} - {frequency} at {time}",
        "audit_type": audit_type,
        "frequency": frequency,
        "time": time,
    }


@audit_router.get("/compliance")
async def get_compliance_status():
    """Получение статуса соответствия"""
    initialize_audit_systems()

    dashboard = compliance_monitor.get_compliance_dashboard()
    return dashboard


@audit_router.get("/compliance/requirements")
async def get_compliance_requirements(standard: Optional[str] = None):
    """Получение требований соответствия"""
    initialize_audit_systems()

    if standard:
        try:
            standard_enum = ComplianceStandard(standard)
            requirements = compliance_monitor.get_requirements_status(
                standard_enum
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid compliance standard: {standard}",
            )
    else:
        requirements = compliance_monitor.get_requirements_status()

    return {
        "requirements": requirements,
        "total": len(requirements),
        "standard": standard,
    }


@audit_router.post("/compliance/assess")
async def assess_compliance(background_tasks: BackgroundTasks, standard: str):
    """Оценка соответствия стандарту"""
    initialize_audit_systems()

    try:
        standard_enum = ComplianceStandard(standard)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid compliance standard: {standard}"
        )

    background_tasks.add_task(assess_compliance_task, standard_enum)

    return {
        "message": f"Compliance assessment for {standard} started",
        "standard": standard,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


async def assess_compliance_task(standard: ComplianceStandard):
    """Фоновая задача оценки соответствия"""
    try:
        assessment = await compliance_monitor.assess_compliance(standard)
        print(
            f"✅ Compliance assessment for {standard.value} completed: {assessment.overall_level.value} ({assessment.score}%)"
        )

    except Exception as e:
        print(f"❌ Error assessing compliance for {standard.value}: {e}")


@audit_router.post("/compliance/assess-all")
async def assess_all_compliance(background_tasks: BackgroundTasks):
    """Оценка соответствия всем стандартам"""
    initialize_audit_systems()

    background_tasks.add_task(assess_all_compliance_task)

    return {
        "message": "All compliance assessments started",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


async def assess_all_compliance_task():
    """Фоновая задача оценки соответствия всем стандартам"""
    try:
        assessments = await compliance_monitor.assess_all_standards()
        print(f"✅ All {len(assessments)} compliance assessments completed")

        # Сохранение дашборда
        dashboard = compliance_monitor.get_compliance_dashboard()
        with open("compliance_dashboard.json", "w") as f:
            json.dump(dashboard, f, indent=2, default=str)

        print("📊 Compliance dashboard saved to compliance_dashboard.json")

    except Exception as e:
        print(f"❌ Error assessing all compliance: {e}")


@audit_router.put("/compliance/requirements/{requirement_id}")
async def update_requirement_status(
    requirement_id: str,
    status: str,
    evidence: Optional[List[str]] = None,
    notes: Optional[str] = None,
):
    """Обновление статуса требования соответствия"""
    initialize_audit_systems()

    if status not in ["implemented", "partial", "not_implemented"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: implemented, partial, not_implemented",
        )

    compliance_monitor.update_requirement_status(
        requirement_id, status, evidence, notes
    )

    return {
        "message": f"Requirement {requirement_id} updated to {status}",
        "requirement_id": requirement_id,
        "status": status,
        "evidence": evidence,
        "notes": notes,
    }


@audit_router.get("/compliance/report/{standard}")
async def get_compliance_report(standard: str):
    """Получение отчета по соответствию стандарту"""
    initialize_audit_systems()

    try:
        standard_enum = ComplianceStandard(standard)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid compliance standard: {standard}"
        )

    report = compliance_monitor.generate_compliance_report(standard_enum)
    return report


@audit_router.get("/metrics")
async def get_audit_metrics():
    """Получение метрик аудитов"""
    initialize_audit_systems()

    # Получение результатов за последние 30 дней
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_results = audit_system.get_audit_results(limit=1000)
    recent_results = [
        r for r in recent_results if r.timestamp >= thirty_days_ago
    ]

    # Группировка по дням
    daily_metrics = {}
    for result in recent_results:
        date_key = result.timestamp.date().isoformat()
        if date_key not in daily_metrics:
            daily_metrics[date_key] = {
                "total_audits": 0,
                "passed": 0,
                "failed": 0,
                "warning": 0,
                "avg_score": 0,
                "audit_types": {},
            }

        daily_metrics[date_key]["total_audits"] += 1
        daily_metrics[date_key][result.status] += 1

        if (
            result.audit_type.value
            not in daily_metrics[date_key]["audit_types"]
        ):
            daily_metrics[date_key]["audit_types"][result.audit_type.value] = 0
        daily_metrics[date_key]["audit_types"][result.audit_type.value] += 1

    # Расчет средних оценок
    for date_key in daily_metrics:
        date_results = [
            r
            for r in recent_results
            if r.timestamp.date().isoformat() == date_key
        ]
        if date_results:
            daily_metrics[date_key]["avg_score"] = sum(
                r.score for r in date_results
            ) / len(date_results)

    # Общая статистика
    total_audits = len(recent_results)
    passed_audits = len([r for r in recent_results if r.status == "passed"])
    failed_audits = len([r for r in recent_results if r.status == "failed"])
    warning_audits = len([r for r in recent_results if r.status == "warning"])
    avg_score = (
        sum(r.score for r in recent_results) / len(recent_results)
        if recent_results
        else 0
    )

    # Статистика по типам аудитов
    audit_type_stats = {}
    for audit_type in AuditType:
        type_results = [
            r for r in recent_results if r.audit_type == audit_type
        ]
        if type_results:
            audit_type_stats[audit_type.value] = {
                "count": len(type_results),
                "avg_score": sum(r.score for r in type_results)
                / len(type_results),
                "passed": len(
                    [r for r in type_results if r.status == "passed"]
                ),
                "failed": len(
                    [r for r in type_results if r.status == "failed"]
                ),
                "warning": len(
                    [r for r in type_results if r.status == "warning"]
                ),
            }

    return {
        "period": "30_days",
        "summary": {
            "total_audits": total_audits,
            "passed": passed_audits,
            "failed": failed_audits,
            "warning": warning_audits,
            "avg_score": round(avg_score, 2),
            "success_rate": round(
                (
                    (passed_audits / total_audits * 100)
                    if total_audits > 0
                    else 0
                ),
                2,
            ),
        },
        "daily_metrics": daily_metrics,
        "audit_type_stats": audit_type_stats,
        "generated_at": datetime.now().isoformat(),
    }


@audit_router.get("/health")
async def audit_health_check():
    """Проверка здоровья системы аудитов"""
    initialize_audit_systems()

    try:
        # Проверка системы аудитов
        audit_results = audit_system.get_audit_results(limit=1)
        audit_system_status = "healthy" if audit_results else "no_data"

        # Проверка планировщика
        schedule_status = audit_scheduler.get_schedule_status()
        scheduler_status = (
            "healthy"
            if schedule_status["total_schedules"] > 0
            else "no_schedules"
        )

        # Проверка монитора соответствия
        compliance_dashboard = compliance_monitor.get_compliance_dashboard()
        compliance_status = (
            "healthy"
            if compliance_dashboard["summary"]["total_assessments"] > 0
            else "no_data"
        )

        overall_status = (
            "healthy"
            if all(
                status == "healthy"
                for status in [
                    audit_system_status,
                    scheduler_status,
                    compliance_status,
                ]
            )
            else "degraded"
        )

        return {
            "status": overall_status,
            "components": {
                "audit_system": audit_system_status,
                "scheduler": scheduler_status,
                "compliance_monitor": compliance_status,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# Функция для инициализации при запуске приложения
def initialize_audit_dashboard():
    """Инициализация интеграции аудитов с дашбордом"""
    initialize_audit_systems()
    print("✅ Audit dashboard integration initialized")


# Функция для получения роутера
def get_audit_router():
    """Получение роутера аудитов"""
    return audit_router
