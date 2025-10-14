#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compliance Monitor для ALADDIN Security System
Мониторинг соответствия стандартам безопасности и законодательства

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import json
# import os  # Не используется
# import re  # Не используется
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class ComplianceStandard(Enum):
    """Стандарты соответствия"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    FEDERAL_152 = "federal_152"  # 152-ФЗ
    FSTEC = "fstec"  # ФСТЭК
    NIST = "nist"
    CIS = "cis"


class ComplianceLevel(Enum):
    """Уровни соответствия"""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"


@dataclass
class ComplianceRequirement:
    """Требование соответствия"""

    id: str
    standard: ComplianceStandard
    title: str
    description: str
    category: str
    priority: str  # critical, high, medium, low
    implementation_status: str  # implemented, partial, not_implemented
    evidence: List[str]
    last_assessment: datetime
    next_assessment: datetime
    responsible_person: str
    notes: str


@dataclass
class ComplianceAssessment:
    """Оценка соответствия"""

    assessment_id: str
    standard: ComplianceStandard
    overall_level: ComplianceLevel
    score: float  # 0-100
    requirements_total: int
    requirements_compliant: int
    requirements_partial: int
    requirements_non_compliant: int
    critical_issues: List[str]
    recommendations: List[str]
    assessment_date: datetime
    assessor: str
    next_assessment: datetime


class ComplianceMonitor:
    """Монитор соответствия стандартам"""

    def __init__(self, db_path: str = "compliance_monitor.db"):
        self.db_path = db_path
        self.init_database()
        self.load_requirements()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_requirements (
                id TEXT PRIMARY KEY,
                standard TEXT,
                title TEXT,
                description TEXT,
                category TEXT,
                priority TEXT,
                implementation_status TEXT,
                evidence TEXT,
                last_assessment DATETIME,
                next_assessment DATETIME,
                responsible_person TEXT,
                notes TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_assessments (
                assessment_id TEXT PRIMARY KEY,
                standard TEXT,
                overall_level TEXT,
                score REAL,
                requirements_total INTEGER,
                requirements_compliant INTEGER,
                requirements_partial INTEGER,
                requirements_non_compliant INTEGER,
                critical_issues TEXT,
                recommendations TEXT,
                assessment_date DATETIME,
                assessor TEXT,
                next_assessment DATETIME
            )
        """
        )

        conn.commit()
        conn.close()

    def load_requirements(self):
        """Загрузка требований соответствия"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM compliance_requirements")
        rows = cursor.fetchall()

        self.requirements = []
        for row in rows:
            requirement = ComplianceRequirement(
                id=row[0],
                standard=ComplianceStandard(row[1]),
                title=row[2],
                description=row[3],
                category=row[4],
                priority=row[5],
                implementation_status=row[6],
                evidence=json.loads(row[7]) if row[7] else [],
                last_assessment=(
                    datetime.fromisoformat(row[8])
                    if row[8]
                    else datetime.now()
                ),
                next_assessment=(
                    datetime.fromisoformat(row[9])
                    if row[9]
                    else datetime.now() + timedelta(days=30)
                ),
                responsible_person=row[10],
                notes=row[11],
            )
            self.requirements.append(requirement)

        conn.close()

    def save_requirement(self, requirement: ComplianceRequirement):
        """Сохранение требования"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO compliance_requirements
            (id, standard, title, description, category, priority, implementation_status,
             evidence, last_assessment, next_assessment, responsible_person, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                requirement.id,
                requirement.standard.value,
                requirement.title,
                requirement.description,
                requirement.category,
                requirement.priority,
                requirement.implementation_status,
                json.dumps(requirement.evidence),
                requirement.last_assessment.isoformat(),
                requirement.next_assessment.isoformat(),
                requirement.responsible_person,
                requirement.notes,
            ),
        )

        conn.commit()
        conn.close()

    def save_assessment(self, assessment: ComplianceAssessment):
        """Сохранение оценки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO compliance_assessments
            (assessment_id, standard, overall_level, score, requirements_total,
             requirements_compliant, requirements_partial, requirements_non_compliant,
             critical_issues, recommendations, assessment_date, assessor, next_assessment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                assessment.assessment_id,
                assessment.standard.value,
                assessment.overall_level.value,
                assessment.score,
                assessment.requirements_total,
                assessment.requirements_compliant,
                assessment.requirements_partial,
                assessment.requirements_non_compliant,
                json.dumps(assessment.critical_issues),
                json.dumps(assessment.recommendations),
                assessment.assessment_date.isoformat(),
                assessment.assessor,
                assessment.next_assessment.isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def initialize_default_requirements(self):
        """Инициализация требований по умолчанию"""
        default_requirements = [
            # GDPR Requirements
            ComplianceRequirement(
                id="gdpr_001",
                standard=ComplianceStandard.GDPR,
                title="Право на информацию",
                description="Пользователи должны быть проинформированы о сборе и обработке их персональных данных",
                category="Privacy Rights",
                priority="critical",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Data Protection Officer",
                notes="Требуется создание политики конфиденциальности",
            ),
            ComplianceRequirement(
                id="gdpr_002",
                standard=ComplianceStandard.GDPR,
                title="Согласие на обработку данных",
                description="Необходимо явное согласие пользователя на обработку персональных данных",
                category="Consent Management",
                priority="critical",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Legal Team",
                notes="Требуется реализация механизма согласия",
            ),
            ComplianceRequirement(
                id="gdpr_003",
                standard=ComplianceStandard.GDPR,
                title="Право на удаление",
                description="Пользователи имеют право на удаление своих персональных данных",
                category="Data Rights",
                priority="high",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Development Team",
                notes="Требуется реализация функции удаления данных",
            ),
            # 152-ФЗ Requirements
            ComplianceRequirement(
                id="federal_152_001",
                standard=ComplianceStandard.FEDERAL_152,
                title="Локализация персональных данных",
                description="Персональные данные российских граждан должны храниться на территории РФ",
                category="Data Localization",
                priority="critical",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Infrastructure Team",
                notes="Требуется настройка серверов в России",
            ),
            ComplianceRequirement(
                id="federal_152_002",
                standard=ComplianceStandard.FEDERAL_152,
                title="Уведомление о нарушении",
                description="Обязательное уведомление Роскомнадзора о нарушениях в течение 24 часов",
                category="Incident Response",
                priority="critical",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Security Team",
                notes="Требуется процедура уведомления регулятора",
            ),
            # PCI DSS Requirements
            ComplianceRequirement(
                id="pci_dss_001",
                standard=ComplianceStandard.PCI_DSS,
                title="Шифрование данных карт",
                description="Данные карт должны быть зашифрованы при передаче и хранении",
                category="Data Protection",
                priority="critical",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Security Team",
                notes="Требуется реализация шифрования платежных данных",
            ),
            ComplianceRequirement(
                id="pci_dss_002",
                standard=ComplianceStandard.PCI_DSS,
                title="Контроль доступа",
                description="Ограничение доступа к данным карт только для авторизованного персонала",
                category="Access Control",
                priority="high",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Security Team",
                notes="Требуется настройка контроля доступа",
            ),
            # ISO 27001 Requirements
            ComplianceRequirement(
                id="iso_27001_001",
                standard=ComplianceStandard.ISO_27001,
                title="Политика информационной безопасности",
                description="Документированная политика информационной безопасности",
                category="Security Policy",
                priority="high",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="CISO",
                notes="Требуется создание политики ИБ",
            ),
            ComplianceRequirement(
                id="iso_27001_002",
                standard=ComplianceStandard.ISO_27001,
                title="Управление инцидентами",
                description="Процедуры выявления, анализа и реагирования на инциденты ИБ",
                category="Incident Management",
                priority="high",
                implementation_status="not_implemented",
                evidence=[],
                last_assessment=datetime.now(),
                next_assessment=datetime.now() + timedelta(days=30),
                responsible_person="Security Team",
                notes="Требуется процедура управления инцидентами",
            ),
        ]

        for requirement in default_requirements:
            self.save_requirement(requirement)

        print(
            f"✅ Инициализировано {len(default_requirements)} требований соответствия"
        )

    async def assess_compliance(
        self, standard: ComplianceStandard
    ) -> ComplianceAssessment:
        """Оценка соответствия стандарту"""
        assessment_id = f"assessment_{standard.value}_{int(time.time())}"

        # Получение требований для стандарта
        standard_requirements = [
            r for r in self.requirements if r.standard == standard
        ]

        if not standard_requirements:
            print(f"❌ Нет требований для стандарта {standard.value}")
            return None

        # Подсчет статусов
        total = len(standard_requirements)
        compliant = len(
            [
                r
                for r in standard_requirements
                if r.implementation_status == "implemented"
            ]
        )
        partial = len(
            [
                r
                for r in standard_requirements
                if r.implementation_status == "partial"
            ]
        )
        non_compliant = len(
            [
                r
                for r in standard_requirements
                if r.implementation_status == "not_implemented"
            ]
        )

        # Расчет оценки
        score = (compliant * 100 + partial * 50) / total if total > 0 else 0

        # Определение общего уровня
        if score >= 90:
            overall_level = ComplianceLevel.COMPLIANT
        elif score >= 70:
            overall_level = ComplianceLevel.PARTIALLY_COMPLIANT
        elif score >= 50:
            overall_level = ComplianceLevel.NON_COMPLIANT
        else:
            overall_level = ComplianceLevel.NON_COMPLIANT

        # Критические проблемы
        critical_issues = []
        for req in standard_requirements:
            if (
                req.priority == "critical"
                and req.implementation_status != "implemented"
            ):
                critical_issues.append(f"{req.title}: {req.description}")

        # Рекомендации
        recommendations = []
        for req in standard_requirements:
            if req.implementation_status != "implemented":
                recommendations.append(f"Реализовать: {req.title}")

        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            standard=standard,
            overall_level=overall_level,
            score=score,
            requirements_total=total,
            requirements_compliant=compliant,
            requirements_partial=partial,
            requirements_non_compliant=non_compliant,
            critical_issues=critical_issues,
            recommendations=recommendations,
            assessment_date=datetime.now(),
            assessor="Automated System",
            next_assessment=datetime.now() + timedelta(days=90),
        )

        self.save_assessment(assessment)
        return assessment

    async def assess_all_standards(self) -> List[ComplianceAssessment]:
        """Оценка соответствия всем стандартам"""
        print("🔍 Запуск оценки соответствия всем стандартам...")

        assessments = []
        for standard in ComplianceStandard:
            assessment = await self.assess_compliance(standard)
            if assessment:
                assessments.append(assessment)
                print(
                    f"✅ {standard.value}: {assessment.overall_level.value} ({assessment.score:.1f}%)"
                )

        return assessments

    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Получение дашборда соответствия"""
        # Получение последних оценок
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM compliance_assessments
            ORDER BY assessment_date DESC
        """
        )
        rows = cursor.fetchall()

        assessments = []
        for row in rows:
            assessment = ComplianceAssessment(
                assessment_id=row[0],
                standard=ComplianceStandard(row[1]),
                overall_level=ComplianceLevel(row[2]),
                score=row[3],
                requirements_total=row[4],
                requirements_compliant=row[5],
                requirements_partial=row[6],
                requirements_non_compliant=row[7],
                critical_issues=json.loads(row[8]),
                recommendations=json.loads(row[9]),
                assessment_date=datetime.fromisoformat(row[10]),
                assessor=row[11],
                next_assessment=datetime.fromisoformat(row[12]),
            )
            assessments.append(assessment)

        conn.close()

        # Группировка по стандартам
        standards_data = {}
        for assessment in assessments:
            if assessment.standard not in standards_data:
                standards_data[assessment.standard] = assessment

        # Общая статистика
        total_assessments = len(assessments)
        compliant_count = len(
            [
                a
                for a in assessments
                if a.overall_level == ComplianceLevel.COMPLIANT
            ]
        )
        partially_compliant_count = len(
            [
                a
                for a in assessments
                if a.overall_level == ComplianceLevel.PARTIALLY_COMPLIANT
            ]
        )
        non_compliant_count = len(
            [
                a
                for a in assessments
                if a.overall_level == ComplianceLevel.NON_COMPLIANT
            ]
        )

        avg_score = (
            sum(a.score for a in assessments) / len(assessments)
            if assessments
            else 0
        )

        # Критические проблемы
        all_critical_issues = []
        for assessment in assessments:
            all_critical_issues.extend(assessment.critical_issues)

        dashboard = {
            "summary": {
                "total_assessments": total_assessments,
                "compliant": compliant_count,
                "partially_compliant": partially_compliant_count,
                "non_compliant": non_compliant_count,
                "average_score": round(avg_score, 2),
                "critical_issues_count": len(all_critical_issues),
            },
            "standards": {
                standard.value: asdict(assessment)
                for standard, assessment in standards_data.items()
            },
            "critical_issues": all_critical_issues,
            "last_updated": datetime.now().isoformat(),
        }

        return dashboard

    def get_requirements_status(
        self, standard: Optional[ComplianceStandard] = None
    ) -> List[Dict[str, Any]]:
        """Получение статуса требований"""
        requirements = self.requirements
        if standard:
            requirements = [r for r in requirements if r.standard == standard]

        return [asdict(r) for r in requirements]

    def update_requirement_status(
        self,
        requirement_id: str,
        status: str,
        evidence: List[str] = None,
        notes: str = "",
    ):
        """Обновление статуса требования"""
        for req in self.requirements:
            if req.id == requirement_id:
                req.implementation_status = status
                if evidence:
                    req.evidence.extend(evidence)
                if notes:
                    req.notes = notes
                req.last_assessment = datetime.now()
                self.save_requirement(req)
                print(
                    f"✅ Обновлен статус требования {requirement_id}: {status}"
                )
                return

        print(f"❌ Требование {requirement_id} не найдено")

    def generate_compliance_report(
        self, standard: ComplianceStandard
    ) -> Dict[str, Any]:
        """Генерация отчета по соответствию"""
        # Получение последней оценки
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM compliance_assessments
            WHERE standard = ?
            ORDER BY assessment_date DESC
            LIMIT 1
        """,
            (standard.value,),
        )

        row = cursor.fetchone()
        if not row:
            return {"error": f"Нет оценок для стандарта {standard.value}"}

        assessment = ComplianceAssessment(
            assessment_id=row[0],
            standard=ComplianceStandard(row[1]),
            overall_level=ComplianceLevel(row[2]),
            score=row[3],
            requirements_total=row[4],
            requirements_compliant=row[5],
            requirements_partial=row[6],
            requirements_non_compliant=row[7],
            critical_issues=json.loads(row[8]),
            recommendations=json.loads(row[9]),
            assessment_date=datetime.fromisoformat(row[10]),
            assessor=row[11],
            next_assessment=datetime.fromisoformat(row[12]),
        )

        # Получение требований
        requirements = [r for r in self.requirements if r.standard == standard]

        report = {
            "standard": standard.value,
            "assessment": asdict(assessment),
            "requirements": [asdict(r) for r in requirements],
            "generated_at": datetime.now().isoformat(),
        }

        conn.close()
        return report


# Пример использования
async def main():
    """Основная функция"""
    monitor = ComplianceMonitor()

    # Инициализация требований по умолчанию
    monitor.initialize_default_requirements()

    # Оценка соответствия всем стандартам
    # assessments = await monitor.assess_all_standards()  # Не используется

    # Получение дашборда
    dashboard = monitor.get_compliance_dashboard()

    # Сохранение отчета
    with open("compliance_dashboard.json", "w") as f:
        json.dump(dashboard, f, indent=2, default=str)

    print("📊 Дашборд соответствия сохранен в compliance_dashboard.json")

    # Вывод статистики
    summary = dashboard["summary"]
    print("\n📈 Статистика соответствия:")
    print(f"  Всего оценок: {summary['total_assessments']}")
    print(f"  Соответствует: {summary['compliant']}")
    print(f"  Частично соответствует: {summary['partially_compliant']}")
    print(f"  Не соответствует: {summary['non_compliant']}")
    print(f"  Средняя оценка: {summary['average_score']}%")
    print(f"  Критических проблем: {summary['critical_issues_count']}")


if __name__ == "__main__":
    asyncio.run(main())
