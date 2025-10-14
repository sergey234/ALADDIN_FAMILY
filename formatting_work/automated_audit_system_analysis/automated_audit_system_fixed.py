#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Audit System для ALADDIN Security System
Автоматические аудиты безопасности, соответствия и мониторинга

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
# import hashlib  # Не используется
import json
import os
# import re  # Не используется
import sqlite3
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuditType(Enum):
    """Типы аудитов"""

    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    DEPENDENCIES = "dependencies"
    INFRASTRUCTURE = "infrastructure"


class AuditSeverity(Enum):
    """Уровни серьезности аудитов"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


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


@dataclass
class AuditResult:
    """Результат аудита"""

    audit_id: str
    audit_type: AuditType
    severity: AuditSeverity
    title: str
    description: str
    status: str  # passed, failed, warning, error
    score: float  # 0-100
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime
    duration: float
    compliance_standards: List[ComplianceStandard]
    metadata: Dict[str, Any]


class AutomatedAuditSystem:
    """Система автоматических аудитов"""

    def __init__(self, db_path: str = "audit_results.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT UNIQUE,
                audit_type TEXT,
                severity TEXT,
                title TEXT,
                description TEXT,
                status TEXT,
                score REAL,
                findings TEXT,
                recommendations TEXT,
                timestamp DATETIME,
                duration REAL,
                compliance_standards TEXT,
                metadata TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def save_audit_result(self, result: AuditResult):
        """Сохранение результата аудита"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO audit_results
            (audit_id, audit_type, severity, title, description, status, score,
             findings, recommendations, timestamp, duration, compliance_standards, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.audit_id,
                result.audit_type.value,
                result.severity.value,
                result.title,
                result.description,
                result.status,
                result.score,
                json.dumps(result.findings),
                json.dumps(result.recommendations),
                result.timestamp.isoformat(),
                result.duration,
                json.dumps([s.value for s in result.compliance_standards]),
                json.dumps(result.metadata),
            ),
        )

        conn.commit()
        conn.close()

    def get_audit_results(
        self, audit_type: Optional[AuditType] = None, limit: int = 100
    ) -> List[AuditResult]:
        """Получение результатов аудитов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if audit_type:
            cursor.execute(
                """
                SELECT audit_id, audit_type, severity, title, description, status, score,
                       findings, recommendations, timestamp, duration, compliance_standards, metadata
                FROM audit_results
                WHERE audit_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (audit_type.value, limit),
            )
        else:
            cursor.execute(
                """
                SELECT audit_id, audit_type, severity, title, description, status, score,
                       findings, recommendations, timestamp, duration, compliance_standards, metadata
                FROM audit_results
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

        results = []
        for row in cursor.fetchall():
            results.append(
                AuditResult(
                    audit_id=row[0],
                    audit_type=AuditType(row[1]),
                    severity=AuditSeverity(row[2]),
                    title=row[3],
                    description=row[4],
                    status=row[5],
                    score=row[6],
                    findings=json.loads(row[7]),
                    recommendations=json.loads(row[8]),
                    timestamp=datetime.fromisoformat(row[9]),
                    duration=row[10],
                    compliance_standards=[
                        ComplianceStandard(s) for s in json.loads(row[11])
                    ],
                    metadata=json.loads(row[12]),
                )
            )

        conn.close()
        return results

    async def run_security_audit(self) -> AuditResult:
        """Запуск аудита безопасности"""
        start_time = time.time()
        audit_id = f"security_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка уязвимостей в зависимостях
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                safety_data = json.loads(result.stdout)
                for vuln in safety_data:
                    findings.append(
                        {
                            "type": "dependency_vulnerability",
                            "package": vuln.get("package", "unknown"),
                            "version": vuln.get(
                                "installed_version", "unknown"
                            ),
                            "vulnerability": vuln.get(
                                "vulnerability", "unknown"
                            ),
                            "severity": vuln.get("severity", "medium"),
                        }
                    )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Safety check failed: {str(e)}",
                }
            )

        # Проверка кода на уязвимости
        try:
            result = subprocess.run(
                ["bandit", "-r", ".", "-f", "json"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                bandit_data = json.loads(result.stdout)
                for issue in bandit_data.get("results", []):
                    findings.append(
                        {
                            "type": "code_vulnerability",
                            "file": issue.get("filename", "unknown"),
                            "line": issue.get("line_number", 0),
                            "severity": issue.get("issue_severity", "medium"),
                            "confidence": issue.get(
                                "issue_confidence", "medium"
                            ),
                            "description": issue.get("issue_text", "unknown"),
                        }
                    )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Bandit check failed: {str(e)}",
                }
            )

        # Проверка секретов в коде
        try:
            result = subprocess.run(
                ["detect-secrets", "scan", "--all-files"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                findings.append(
                    {
                        "type": "secrets_detected",
                        "description": "Potential secrets found in code",
                        "details": result.stdout,
                    }
                )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Secrets detection failed: {str(e)}",
                }
            )

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Обновить уязвимые зависимости",
                    "Исправить найденные уязвимости в коде",
                    "Удалить секреты из кода",
                    "Настроить автоматическое сканирование безопасности",
                ]
            )
        else:
            recommendations.append(
                "Продолжить регулярные проверки безопасности"
            )

        # Расчет оценки
        critical_findings = len(
            [f for f in findings if f.get("severity") == "critical"]
        )
        high_findings = len(
            [f for f in findings if f.get("severity") == "high"]
        )
        medium_findings = len(
            [f for f in findings if f.get("severity") == "medium"]
        )

        score = max(
            0,
            100
            - (
                critical_findings * 20
                + high_findings * 10
                + medium_findings * 5
            ),
        )

        if critical_findings > 0:
            status = "failed"
            severity = AuditSeverity.CRITICAL
        elif high_findings > 0:
            status = "warning"
            severity = AuditSeverity.HIGH
        elif medium_findings > 0:
            status = "warning"
            severity = AuditSeverity.MEDIUM
        else:
            status = "passed"
            severity = AuditSeverity.INFO

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.SECURITY,
            severity=severity,
            title="Security Audit",
            description="Comprehensive security audit of the system",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[
                ComplianceStandard.ISO_27001,
                ComplianceStandard.PCI_DSS,
            ],
            metadata={
                "total_findings": len(findings),
                "critical": critical_findings,
                "high": high_findings,
            },
        )

        self.save_audit_result(result)
        return result

    async def run_compliance_audit(self) -> AuditResult:
        """Запуск аудита соответствия"""
        start_time = time.time()
        audit_id = f"compliance_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка соответствия GDPR
        gdpr_findings = await self._check_gdpr_compliance()
        findings.extend(gdpr_findings)

        # Проверка соответствия 152-ФЗ
        federal_152_findings = await self._check_federal_152_compliance()
        findings.extend(federal_152_findings)

        # Проверка соответствия PCI DSS
        pci_findings = await self._check_pci_dss_compliance()
        findings.extend(pci_findings)

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Реализовать политику конфиденциальности",
                    "Настроить согласие на обработку данных",
                    "Шифровать персональные данные",
                    "Настроить логирование доступа к данным",
                ]
            )
        else:
            recommendations.append("Поддерживать текущий уровень соответствия")

        # Расчет оценки
        score = max(0, 100 - len(findings) * 10)
        status = (
            "passed" if score >= 80 else "warning" if score >= 60 else "failed"
        )
        severity = (
            AuditSeverity.HIGH
            if score < 60
            else AuditSeverity.MEDIUM if score < 80 else AuditSeverity.INFO
        )

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.COMPLIANCE,
            severity=severity,
            title="Compliance Audit",
            description="Compliance audit for various standards",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[
                ComplianceStandard.GDPR,
                ComplianceStandard.FEDERAL_152,
                ComplianceStandard.PCI_DSS,
            ],
            metadata={"total_findings": len(findings)},
        )

        self.save_audit_result(result)
        return result

    async def _check_gdpr_compliance(self) -> List[Dict[str, Any]]:
        """Проверка соответствия GDPR"""
        findings = []

        # Проверка наличия политики конфиденциальности
        if not os.path.exists("privacy_policy.md"):
            findings.append(
                {
                    "type": "gdpr_violation",
                    "description": "Privacy policy not found",
                    "severity": "high",
                }
            )

        # Проверка согласия на обработку данных
        # Это упрощенная проверка - в реальности нужно проверять код
        findings.append(
            {
                "type": "gdpr_recommendation",
                "description": "Implement user consent mechanism",
                "severity": "medium",
            }
        )

        return findings

    async def _check_federal_152_compliance(self) -> List[Dict[str, Any]]:
        """Проверка соответствия 152-ФЗ"""
        findings = []

        # Проверка локализации данных
        findings.append(
            {
                "type": "federal_152_recommendation",
                "description": "Ensure data localization compliance",
                "severity": "medium",
            }
        )

        # Проверка уведомления о нарушении
        findings.append(
            {
                "type": "federal_152_recommendation",
                "description": "Implement data breach notification system",
                "severity": "high",
            }
        )

        return findings

    async def _check_pci_dss_compliance(self) -> List[Dict[str, Any]]:
        """Проверка соответствия PCI DSS"""
        findings = []

        # Проверка шифрования данных
        findings.append(
            {
                "type": "pci_dss_recommendation",
                "description": "Implement end-to-end encryption for payment data",
                "severity": "high",
            }
        )

        # Проверка доступа к данным
        findings.append(
            {
                "type": "pci_dss_recommendation",
                "description": "Implement access control for payment data",
                "severity": "medium",
            }
        )

        return findings

    async def run_performance_audit(self) -> AuditResult:
        """Запуск аудита производительности"""
        start_time = time.time()
        audit_id = f"performance_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка времени отклика
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent

            if cpu_usage > 80:
                findings.append(
                    {
                        "type": "performance_issue",
                        "description": f"High CPU usage: {cpu_usage}%",
                        "severity": "high",
                    }
                )

            if memory_usage > 85:
                findings.append(
                    {
                        "type": "performance_issue",
                        "description": f"High memory usage: {memory_usage}%",
                        "severity": "high",
                    }
                )

        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Performance check failed: {str(e)}",
                }
            )

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Оптимизировать использование CPU",
                    "Оптимизировать использование памяти",
                    "Настроить мониторинг производительности",
                ]
            )
        else:
            recommendations.append("Производительность в норме")

        # Расчет оценки
        score = 100 - len(findings) * 20
        status = (
            "passed" if score >= 80 else "warning" if score >= 60 else "failed"
        )
        severity = (
            AuditSeverity.HIGH
            if score < 60
            else AuditSeverity.MEDIUM if score < 80 else AuditSeverity.INFO
        )

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.PERFORMANCE,
            severity=severity,
            title="Performance Audit",
            description="System performance audit",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[],
            metadata={"total_findings": len(findings)},
        )

        self.save_audit_result(result)
        return result

    async def run_code_quality_audit(self) -> AuditResult:
        """Запуск аудита качества кода"""
        start_time = time.time()
        audit_id = f"code_quality_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка flake8
        try:
            result = subprocess.run(
                ["flake8", ".", "--count"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                error_count = int(result.stdout.strip().split("\n")[-1])
                findings.append(
                    {
                        "type": "code_quality_issue",
                        "description": f"Flake8 found {error_count} issues",
                        "severity": "medium",
                    }
                )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Flake8 check failed: {str(e)}",
                }
            )

        # Проверка покрытия тестами
        try:
            result = subprocess.run(
                ["coverage", "report", "--show-missing"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                # Парсим покрытие из вывода
                lines = result.stdout.split("\n")
                for line in lines:
                    if "TOTAL" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            coverage = float(parts[3].replace("%", ""))
                            if coverage < 80:
                                findings.append(
                                    {
                                        "type": "test_coverage_issue",
                                        "description": f"Low test coverage: {coverage}%",
                                        "severity": "medium",
                                    }
                                )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Coverage check failed: {str(e)}",
                }
            )

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Исправить ошибки flake8",
                    "Увеличить покрытие тестами",
                    "Настроить pre-commit hooks",
                ]
            )
        else:
            recommendations.append("Качество кода в норме")

        # Расчет оценки
        score = max(0, 100 - len(findings) * 15)
        status = (
            "passed" if score >= 80 else "warning" if score >= 60 else "failed"
        )
        severity = (
            AuditSeverity.HIGH
            if score < 60
            else AuditSeverity.MEDIUM if score < 80 else AuditSeverity.INFO
        )

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.CODE_QUALITY,
            severity=severity,
            title="Code Quality Audit",
            description="Code quality and test coverage audit",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[],
            metadata={"total_findings": len(findings)},
        )

        self.save_audit_result(result)
        return result

    async def run_dependencies_audit(self) -> AuditResult:
        """Запуск аудита зависимостей"""
        start_time = time.time()
        audit_id = f"dependencies_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка устаревших зависимостей
        try:
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    findings.append(
                        {
                            "type": "dependency_vulnerability",
                            "package": vuln.get("package", "unknown"),
                            "version": vuln.get(
                                "installed_version", "unknown"
                            ),
                            "vulnerability": vuln.get(
                                "vulnerability", "unknown"
                            ),
                            "severity": vuln.get("severity", "medium"),
                        }
                    )
        except Exception as e:
            findings.append(
                {
                    "type": "audit_error",
                    "error": f"Dependencies audit failed: {str(e)}",
                }
            )

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Обновить уязвимые зависимости",
                    "Настроить автоматическое обновление зависимостей",
                    "Использовать requirements.txt с зафиксированными версиями",
                ]
            )
        else:
            recommendations.append("Зависимости в безопасности")

        # Расчет оценки
        score = max(0, 100 - len(findings) * 25)
        status = (
            "passed" if score >= 80 else "warning" if score >= 60 else "failed"
        )
        severity = (
            AuditSeverity.HIGH
            if score < 60
            else AuditSeverity.MEDIUM if score < 80 else AuditSeverity.INFO
        )

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.DEPENDENCIES,
            severity=severity,
            title="Dependencies Audit",
            description="Dependencies security audit",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[],
            metadata={"total_findings": len(findings)},
        )

        self.save_audit_result(result)
        return result

    async def run_infrastructure_audit(self) -> AuditResult:
        """Запуск аудита инфраструктуры"""
        start_time = time.time()
        audit_id = f"infrastructure_audit_{int(time.time())}"

        findings = []
        recommendations = []

        # Проверка Dockerfile
        if os.path.exists("Dockerfile"):
            with open("Dockerfile", "r") as f:
                dockerfile_content = f.read()

            # Проверка на использование root пользователя
            if (
                "USER root" in dockerfile_content
                and "USER" not in dockerfile_content.replace("USER root", "")
            ):
                findings.append(
                    {
                        "type": "infrastructure_issue",
                        "description": "Dockerfile runs as root user",
                        "severity": "medium",
                    }
                )

        # Проверка GitHub Actions
        if os.path.exists(".github/workflows"):
            for file in os.listdir(".github/workflows"):
                if file.endswith(".yml"):
                    with open(f".github/workflows/{file}", "r") as f:
                        workflow_content = f.read()

                    # Проверка на хардкодные секреты
                    if (
                        "password" in workflow_content.lower()
                        and "secrets." not in workflow_content
                    ):
                        findings.append(
                            {
                                "type": "infrastructure_issue",
                                "description": f"Potential hardcoded secrets in {file}",
                                "severity": "high",
                            }
                        )

        # Генерация рекомендаций
        if findings:
            recommendations.extend(
                [
                    "Использовать non-root пользователя в Docker",
                    "Использовать GitHub Secrets для чувствительных данных",
                    "Настроить сканирование контейнеров",
                ]
            )
        else:
            recommendations.append("Инфраструктура настроена корректно")

        # Расчет оценки
        score = max(0, 100 - len(findings) * 20)
        status = (
            "passed" if score >= 80 else "warning" if score >= 60 else "failed"
        )
        severity = (
            AuditSeverity.HIGH
            if score < 60
            else AuditSeverity.MEDIUM if score < 80 else AuditSeverity.INFO
        )

        duration = time.time() - start_time

        result = AuditResult(
            audit_id=audit_id,
            audit_type=AuditType.INFRASTRUCTURE,
            severity=severity,
            title="Infrastructure Audit",
            description="Infrastructure security audit",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations,
            timestamp=datetime.now(),
            duration=duration,
            compliance_standards=[],
            metadata={"total_findings": len(findings)},
        )

        self.save_audit_result(result)
        return result

    async def run_all_audits(self) -> List[AuditResult]:
        """Запуск всех аудитов"""
        print("🔍 Запуск автоматических аудитов...")

        audits = [
            self.run_security_audit(),
            self.run_compliance_audit(),
            self.run_performance_audit(),
            self.run_code_quality_audit(),
            self.run_dependencies_audit(),
            self.run_infrastructure_audit(),
        ]

        results = await asyncio.gather(*audits, return_exceptions=True)

        # Фильтруем исключения
        valid_results = [r for r in results if isinstance(r, AuditResult)]

        print(f"✅ Завершено {len(valid_results)} аудитов")
        return valid_results

    def generate_audit_report(
        self, results: List[AuditResult]
    ) -> Dict[str, Any]:
        """Генерация отчета по аудитам"""
        total_audits = len(results)
        passed_audits = len([r for r in results if r.status == "passed"])
        failed_audits = len([r for r in results if r.status == "failed"])
        warning_audits = len([r for r in results if r.status == "warning"])

        avg_score = (
            sum(r.score for r in results) / total_audits
            if total_audits > 0
            else 0
        )

        critical_findings = len(
            [
                f
                for r in results
                for f in r.findings
                if f.get("severity") == "critical"
            ]
        )
        high_findings = len(
            [
                f
                for r in results
                for f in r.findings
                if f.get("severity") == "high"
            ]
        )
        medium_findings = len(
            [
                f
                for r in results
                for f in r.findings
                if f.get("severity") == "medium"
            ]
        )

        report = {
            "summary": {
                "total_audits": total_audits,
                "passed": passed_audits,
                "failed": failed_audits,
                "warning": warning_audits,
                "average_score": round(avg_score, 2),
                "total_findings": critical_findings
                + high_findings
                + medium_findings,
                "critical_findings": critical_findings,
                "high_findings": high_findings,
                "medium_findings": medium_findings,
            },
            "audits": [asdict(r) for r in results],
            "timestamp": datetime.now().isoformat(),
        }

        return report


# Пример использования
async def main():
    """Основная функция"""
    audit_system = AutomatedAuditSystem()

    # Запуск всех аудитов
    results = await audit_system.run_all_audits()

    # Генерация отчета
    report = audit_system.generate_audit_report(results)

    # Сохранение отчета
    with open("audit_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("📊 Отчет по аудитам сохранен в audit_report.json")

    # Вывод краткой статистики
    summary = report["summary"]
    print("\n📈 Статистика аудитов:")
    print(f"  Всего аудитов: {summary['total_audits']}")
    print(f"  Пройдено: {summary['passed']}")
    print(f"  Предупреждения: {summary['warning']}")
    print(f"  Ошибки: {summary['failed']}")
    print(f"  Средняя оценка: {summary['average_score']}")
    print(f"  Критических находок: {summary['critical_findings']}")
    print(f"  Высокий приоритет: {summary['high_findings']}")


if __name__ == "__main__":
    asyncio.run(main())
