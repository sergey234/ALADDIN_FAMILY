# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Report Manager
Система генерации отчетов безопасности
Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-10
"""

import logging
import json
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from core.base import SecurityBase
from core.security_base import SecurityEvent, IncidentSeverity


class ReportType(Enum):
    """Типы отчетов"""
    DAILY = "daily"  # Ежедневный отчет
    WEEKLY = "weekly"  # Еженедельный отчет
    MONTHLY = "monthly"  # Ежемесячный отчет
    QUARTERLY = "quarterly"  # Квартальный отчет
    ANNUAL = "annual"  # Годовой отчет
    INCIDENT = "incident"  # Отчет об инциденте
    THREAT = "threat"  # Отчет об угрозах
    COMPLIANCE = "compliance"  # Отчет о соответствии


class ReportFormat(Enum):
    """Форматы отчетов"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"


class ReportPriority(Enum):
    """Приоритеты отчетов"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReportData:
    """Данные отчета"""
    report_id: str
    title: str
    report_type: ReportType
    priority: ReportPriority
    created_at: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""


@dataclass
class ReportTemplate:
    """Шаблон отчета"""
    template_id: str
    name: str
    report_type: ReportType
    sections: List[str]
    chart_types: List[str]
    filters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class ReportManager(SecurityBase):
    """
    Менеджер отчетов безопасности
    Генерация, анализ и экспорт отчетов
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ReportManager", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Данные системы
        self.reports: Dict[str, ReportData] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.report_queue: List[str] = []
        self.export_path = Path("reports")

        # Конфигурация
        self.auto_generate = True
        self.retention_days = 365
        self.max_reports = 1000

        # Инициализация
        self._initialize_default_templates()
        self._setup_export_directory()

    def _initialize_default_templates(self) -> None:
        """Инициализация шаблонов по умолчанию"""
        default_templates = [
            {
                "template_id": "daily_security",
                "name": "Ежедневный отчет безопасности",
                "report_type": ReportType.DAILY,
                "sections": [
                    "summary", "incidents", "threats", "performance"
                ],
                "chart_types": ["line", "bar", "pie"]
            },
            {
                "template_id": "weekly_analysis",
                "name": "Еженедельный анализ",
                "report_type": ReportType.WEEKLY,
                "sections": [
                    "trends", "anomalies", "recommendations"
                ],
                "chart_types": ["line", "heatmap", "scatter"]
            },
            {
                "template_id": "monthly_compliance",
                "name": "Ежемесячный отчет соответствия",
                "report_type": ReportType.MONTHLY,
                "sections": [
                    "compliance_status", "violations", "improvements"
                ],
                "chart_types": ["gauge", "bar", "table"]
            },
            {
                "template_id": "incident_report",
                "name": "Отчет об инциденте",
                "report_type": ReportType.INCIDENT,
                "sections": [
                    "incident_details", "timeline", "impact", "resolution"
                ],
                "chart_types": ["timeline", "impact_matrix"]
            }
        ]

        for template_data in default_templates:
            self._create_template(template_data)

    def _create_template(self, template_data: Dict[str, Any]) -> None:
        """Создание шаблона отчета"""
        template = ReportTemplate(
            template_id=template_data["template_id"],
            name=template_data["name"],
            report_type=template_data["report_type"],
            sections=template_data["sections"],
            chart_types=template_data["chart_types"]
        )
        self.templates[template_data["template_id"]] = template

    def _setup_export_directory(self) -> None:
        """Настройка директории экспорта"""
        self.export_path.mkdir(exist_ok=True)
        (self.export_path / "daily").mkdir(exist_ok=True)
        (self.export_path / "weekly").mkdir(exist_ok=True)
        (self.export_path / "monthly").mkdir(exist_ok=True)
        (self.export_path / "incidents").mkdir(exist_ok=True)

    def generate_report(
        self,
        report_type: ReportType,
        title: str,
        data: Dict[str, Any],
        template_id: Optional[str] = None,
        priority: ReportPriority = ReportPriority.MEDIUM
    ) -> str:
        """Генерация отчета"""
        report_id = f"report_{int(time.time())}_{report_type.value}"

        # Выбираем шаблон
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
        else:
            template = self._get_default_template(report_type)

        # Создаем данные отчета
        report_data = ReportData(
            report_id=report_id,
            title=title,
            report_type=report_type,
            priority=priority,
            created_at=datetime.now(),
            data=data
        )

        # Генерируем содержимое отчета
        self._generate_report_content(report_data, template)

        # Сохраняем отчет
        self.reports[report_id] = report_data

        # Добавляем в очередь на экспорт
        if report_id not in self.report_queue:
            self.report_queue.append(report_id)

        self.logger.info(f"Отчет {report_id} сгенерирован успешно")
        return report_id

    def _get_default_template(self, report_type: ReportType) -> ReportTemplate:
        """Получение шаблона по умолчанию для типа отчета"""
        for template in self.templates.values():
            if template.report_type == report_type:
                return template

        # Возвращаем первый доступный шаблон
        return list(self.templates.values())[0]

    def _generate_report_content(
        self,
        report_data: ReportData,
        template: ReportTemplate
    ) -> None:
        """Генерация содержимого отчета"""
        content = {
            "title": report_data.title,
            "type": report_data.report_type.value,
            "created_at": report_data.created_at.isoformat(),
            "sections": {}
        }

        # Генерируем секции отчета
        for section in template.sections:
            content["sections"][section] = self._generate_section(
                section, report_data.data
            )

        # Генерируем графики
        for chart_type in template.chart_types:
            chart_data = self._generate_chart(
                chart_type, report_data.data
            )
            if chart_data:
                report_data.charts.append(chart_data)

        # Генерируем сводку
        report_data.summary = self._generate_summary(report_data.data)
        content["summary"] = report_data.summary

        report_data.data = content

    def _generate_section(
        self,
        section: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация секции отчета"""
        if section == "summary":
            return self._generate_summary_section(data)
        elif section == "incidents":
            return self._generate_incidents_section(data)
        elif section == "threats":
            return self._generate_threats_section(data)
        elif section == "performance":
            return self._generate_performance_section(data)
        elif section == "trends":
            return self._generate_trends_section(data)
        elif section == "anomalies":
            return self._generate_anomalies_section(data)
        elif section == "recommendations":
            return self._generate_recommendations_section(data)
        elif section == "compliance_status":
            return self._generate_compliance_section(data)
        elif section == "violations":
            return self._generate_violations_section(data)
        elif section == "improvements":
            return self._generate_improvements_section(data)
        elif section == "incident_details":
            return self._generate_incident_details_section(data)
        elif section == "timeline":
            return self._generate_timeline_section(data)
        elif section == "impact":
            return self._generate_impact_section(data)
        elif section == "resolution":
            return self._generate_resolution_section(data)
        else:
            return {"error": f"Неизвестная секция: {section}"}

    def _generate_summary_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции сводки"""
        return {
            "total_incidents": data.get("total_incidents", 0),
            "resolved_incidents": data.get("resolved_incidents", 0),
            "active_threats": data.get("active_threats", 0),
            "security_score": data.get("security_score", 0),
            "uptime_percentage": data.get("uptime_percentage", 0)
        }

    def _generate_incidents_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции инцидентов"""
        incidents = data.get("incidents", [])
        return {
            "total": len(incidents),
            "by_severity": self._count_by_severity(incidents),
            "by_type": self._count_by_type(incidents),
            "recent": incidents[-5:] if incidents else []
        }

    def _generate_threats_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции угроз"""
        threats = data.get("threats", [])
        return {
            "total": len(threats),
            "by_category": self._count_by_category(threats),
            "by_risk_level": self._count_by_risk_level(threats),
            "active": [t for t in threats if t.get("status") == "active"]
        }

    def _generate_performance_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции производительности"""
        return {
            "response_time": data.get("avg_response_time", 0),
            "throughput": data.get("throughput", 0),
            "error_rate": data.get("error_rate", 0),
            "availability": data.get("availability", 0)
        }

    def _generate_trends_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции трендов"""
        trends = data.get("trends", {})
        return {
            "incident_trend": trends.get("incidents", []),
            "threat_trend": trends.get("threats", []),
            "performance_trend": trends.get("performance", []),
            "correlation": trends.get("correlation", {})
        }

    def _generate_anomalies_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции аномалий"""
        anomalies = data.get("anomalies", [])
        return {
            "total": len(anomalies),
            "by_type": self._count_by_type(anomalies),
            "severity_distribution": self._count_by_severity(anomalies),
            "recent": anomalies[-10:] if anomalies else []
        }

    def _generate_recommendations_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции рекомендаций"""
        recommendations = data.get("recommendations", [])
        return {
            "total": len(recommendations),
            "by_priority": self._count_by_priority(recommendations),
            "implemented": len([r for r in recommendations if r.get("implemented")]),
            "pending": len([r for r in recommendations if not r.get("implemented")])
        }

    def _generate_compliance_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции соответствия"""
        compliance = data.get("compliance", {})
        return {
            "overall_score": compliance.get("overall_score", 0),
            "by_standard": compliance.get("by_standard", {}),
            "violations": compliance.get("violations", []),
            "improvements": compliance.get("improvements", [])
        }

    def _generate_violations_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции нарушений"""
        violations = data.get("violations", [])
        return {
            "total": len(violations),
            "by_type": self._count_by_type(violations),
            "by_severity": self._count_by_severity(violations),
            "resolved": len([v for v in violations if v.get("resolved")])
        }

    def _generate_improvements_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции улучшений"""
        improvements = data.get("improvements", [])
        return {
            "total": len(improvements),
            "implemented": len([i for i in improvements if i.get("implemented")]),
            "in_progress": len([i for i in improvements if i.get("in_progress")]),
            "planned": len([i for i in improvements if i.get("planned")])
        }

    def _generate_incident_details_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции деталей инцидента"""
        incident = data.get("incident", {})
        return {
            "id": incident.get("id", ""),
            "title": incident.get("title", ""),
            "description": incident.get("description", ""),
            "severity": incident.get("severity", ""),
            "status": incident.get("status", ""),
            "created_at": incident.get("created_at", ""),
            "resolved_at": incident.get("resolved_at", "")
        }

    def _generate_timeline_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции временной линии"""
        timeline = data.get("timeline", [])
        return {
            "events": timeline,
            "duration": self._calculate_duration(timeline),
            "key_milestones": self._extract_milestones(timeline)
        }

    def _generate_impact_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции воздействия"""
        impact = data.get("impact", {})
        return {
            "business_impact": impact.get("business", 0),
            "technical_impact": impact.get("technical", 0),
            "financial_impact": impact.get("financial", 0),
            "reputation_impact": impact.get("reputation", 0)
        }

    def _generate_resolution_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация секции разрешения"""
        resolution = data.get("resolution", {})
        return {
            "status": resolution.get("status", ""),
            "steps_taken": resolution.get("steps", []),
            "lessons_learned": resolution.get("lessons", []),
            "prevention_measures": resolution.get("prevention", [])
        }

    def _generate_chart(
        self,
        chart_type: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Генерация графика"""
        try:
            if chart_type == "line":
                return self._create_line_chart(data)
            elif chart_type == "bar":
                return self._create_bar_chart(data)
            elif chart_type == "pie":
                return self._create_pie_chart(data)
            elif chart_type == "heatmap":
                return self._create_heatmap(data)
            elif chart_type == "scatter":
                return self._create_scatter_chart(data)
            elif chart_type == "gauge":
                return self._create_gauge_chart(data)
            elif chart_type == "table":
                return self._create_table_chart(data)
            elif chart_type == "timeline":
                return self._create_timeline_chart(data)
            elif chart_type == "impact_matrix":
                return self._create_impact_matrix(data)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Ошибка создания графика {chart_type}: {e}")
            return None

    def _create_line_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание линейного графика"""
        return {
            "type": "line",
            "title": "Тренд инцидентов",
            "data": {
                "x": data.get("timeline", []),
                "y": data.get("incident_counts", [])
            },
            "config": {
                "x_title": "Время",
                "y_title": "Количество инцидентов"
            }
        }

    def _create_bar_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание столбчатого графика"""
        return {
            "type": "bar",
            "title": "Распределение по типам",
            "data": {
                "categories": data.get("categories", []),
                "values": data.get("values", [])
            },
            "config": {
                "x_title": "Типы",
                "y_title": "Количество"
            }
        }

    def _create_pie_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание круговой диаграммы"""
        return {
            "type": "pie",
            "title": "Распределение по серьезности",
            "data": {
                "labels": data.get("severity_labels", []),
                "values": data.get("severity_values", [])
            },
            "config": {
                "show_legend": True
            }
        }

    def _create_heatmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание тепловой карты"""
        return {
            "type": "heatmap",
            "title": "Корреляция угроз",
            "data": {
                "matrix": data.get("correlation_matrix", []),
                "labels": data.get("threat_labels", [])
            },
            "config": {
                "color_scale": "Blues"
            }
        }

    def _create_scatter_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание точечного графика"""
        return {
            "type": "scatter",
            "title": "Связь между параметрами",
            "data": {
                "x": data.get("x_values", []),
                "y": data.get("y_values", []),
                "labels": data.get("point_labels", [])
            },
            "config": {
                "x_title": "Параметр X",
                "y_title": "Параметр Y"
            }
        }

    def _create_gauge_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание датчика"""
        return {
            "type": "gauge",
            "title": "Общий балл безопасности",
            "data": {
                "value": data.get("security_score", 0),
                "max": 100
            },
            "config": {
                "thresholds": [30, 70, 90]
            }
        }

    def _create_table_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание таблицы"""
        return {
            "type": "table",
            "title": "Детальная статистика",
            "data": {
                "headers": data.get("table_headers", []),
                "rows": data.get("table_rows", [])
            },
            "config": {
                "sortable": True,
                "filterable": True
            }
        }

    def _create_timeline_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание временной линии"""
        return {
            "type": "timeline",
            "title": "Временная линия инцидента",
            "data": {
                "events": data.get("timeline_events", [])
            },
            "config": {
                "show_duration": True
            }
        }

    def _create_impact_matrix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание матрицы воздействия"""
        return {
            "type": "impact_matrix",
            "title": "Матрица воздействия",
            "data": {
                "matrix": data.get("impact_matrix", []),
                "dimensions": data.get("impact_dimensions", [])
            },
            "config": {
                "color_scale": "Reds"
            }
        }

    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Генерация сводки отчета"""
        total_incidents = data.get("total_incidents", 0)
        resolved_incidents = data.get("resolved_incidents", 0)
        security_score = data.get("security_score", 0)

        summary = f"Отчет содержит {total_incidents} инцидентов, "
        summary += f"из которых {resolved_incidents} разрешены. "
        summary += f"Общий балл безопасности: {security_score}/100."

        return summary

    def _count_by_severity(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Подсчет по серьезности"""
        counts = {}
        for item in items:
            severity = item.get("severity", "unknown")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _count_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Подсчет по типу"""
        counts = {}
        for item in items:
            item_type = item.get("type", "unknown")
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts

    def _count_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Подсчет по категории"""
        counts = {}
        for item in items:
            category = item.get("category", "unknown")
            counts[category] = counts.get(category, 0) + 1
        return counts

    def _count_by_risk_level(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Подсчет по уровню риска"""
        counts = {}
        for item in items:
            risk_level = item.get("risk_level", "unknown")
            counts[risk_level] = counts.get(risk_level, 0) + 1
        return counts

    def _count_by_priority(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Подсчет по приоритету"""
        counts = {}
        for item in items:
            priority = item.get("priority", "unknown")
            counts[priority] = counts.get(priority, 0) + 1
        return counts

    def _calculate_duration(self, timeline: List[Dict[str, Any]]) -> int:
        """Расчет продолжительности"""
        if not timeline:
            return 0

        start_time = timeline[0].get("timestamp", "")
        end_time = timeline[-1].get("timestamp", "")

        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return int((end - start).total_seconds() / 60)  # В минутах
        except Exception:
            return 0

    def _extract_milestones(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлечение ключевых этапов"""
        milestones = []
        for event in timeline:
            if event.get("milestone", False):
                milestones.append(event)
        return milestones

    def export_report(
        self,
        report_id: str,
        format_type: ReportFormat,
        file_path: Optional[str] = None
    ) -> str:
        """Экспорт отчета"""
        if report_id not in self.reports:
            raise ValueError(f"Отчет {report_id} не найден")

        report = self.reports[report_id]

        if not file_path:
            file_path = self._generate_file_path(report, format_type)

        if format_type == ReportFormat.JSON:
            return self._export_json(report, file_path)
        elif format_type == ReportFormat.CSV:
            return self._export_csv(report, file_path)
        elif format_type == ReportFormat.HTML:
            return self._export_html(report, file_path)
        elif format_type == ReportFormat.EXCEL:
            return self._export_excel(report, file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format_type}")

    def _generate_file_path(
        self,
        report: ReportData,
        format_type: ReportFormat
    ) -> str:
        """Генерация пути к файлу"""
        timestamp = report.created_at.strftime("%Y%m%d_%H%M%S")
        filename = f"{report.report_id}_{timestamp}.{format_type.value}"
        return str(self.export_path / report.report_type.value / filename)

    def _export_json(self, report: ReportData, file_path: str) -> str:
        """Экспорт в JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report.data, f, ensure_ascii=False, indent=2)
        return file_path

    def _export_csv(self, report: ReportData, file_path: str) -> str:
        """Экспорт в CSV"""
        # Создаем плоскую структуру для CSV
        flat_data = self._flatten_data(report.data)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(flat_data.keys())
            writer.writerow(flat_data.values())
        return file_path

    def _export_html(self, report: ReportData, file_path: str) -> str:
        """Экспорт в HTML"""
        html_content = self._generate_html_content(report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return file_path

    def _export_excel(self, report: ReportData, file_path: str) -> str:
        """Экспорт в Excel"""
        # Создаем DataFrame из данных отчета
        df = pd.DataFrame([report.data])
        df.to_excel(file_path, index=False)
        return file_path

    def _flatten_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Сглаживание данных для CSV"""
        flat = {}
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._flatten_data(value, new_key))
            elif isinstance(value, list):
                flat[new_key] = str(value)
            else:
                flat[new_key] = value
        return flat

    def _generate_html_content(self, report: ReportData) -> str:
        """Генерация HTML содержимого"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .section {{ margin: 20px 0; }}
                .chart {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>Тип: {report.report_type.value}</p>
                <p>Создан: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Сводка</h2>
                <p>{report.summary}</p>
            </div>
            
            <div class="section">
                <h2>Данные</h2>
                <pre>{json.dumps(report.data, ensure_ascii=False, indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        return html

    def get_report(self, report_id: str) -> Optional[ReportData]:
        """Получение отчета по ID"""
        return self.reports.get(report_id)

    def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        limit: int = 100
    ) -> List[ReportData]:
        """Список отчетов"""
        reports = list(self.reports.values())
        
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        
        # Сортируем по дате создания (новые первые)
        reports.sort(key=lambda x: x.created_at, reverse=True)
        
        return reports[:limit]

    def delete_report(self, report_id: str) -> bool:
        """Удаление отчета"""
        if report_id in self.reports:
            del self.reports[report_id]
            if report_id in self.report_queue:
                self.report_queue.remove(report_id)
            return True
        return False

    def cleanup_old_reports(self) -> int:
        """Очистка старых отчетов"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        old_reports = [
            report_id for report_id, report in self.reports.items()
            if report.created_at < cutoff_date
        ]
        
        for report_id in old_reports:
            self.delete_report(report_id)
        
        return len(old_reports)

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "status": "active",
            "total_reports": len(self.reports),
            "total_templates": len(self.templates),
            "queue_size": len(self.report_queue),
            "export_path": str(self.export_path),
            "auto_generate": self.auto_generate,
            "retention_days": self.retention_days,
            "last_updated": datetime.now().isoformat()
        }

    def get_analytics(self) -> Dict[str, Any]:
        """Получение аналитики отчетов"""
        reports = list(self.reports.values())
        
        if not reports:
            return {"message": "Нет отчетов для анализа"}
        
        # Статистика по типам
        type_counts = {}
        for report in reports:
            report_type = report.report_type.value
            type_counts[report_type] = type_counts.get(report_type, 0) + 1
        
        # Статистика по приоритетам
        priority_counts = {}
        for report in reports:
            priority = report.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Статистика по времени
        recent_reports = [
            r for r in reports
            if r.created_at > datetime.now() - timedelta(days=7)
        ]
        
        return {
            "total_reports": len(reports),
            "recent_reports": len(recent_reports),
            "by_type": type_counts,
            "by_priority": priority_counts,
            "oldest_report": min(r.created_at for r in reports).isoformat(),
            "newest_report": max(r.created_at for r in reports).isoformat()
        }