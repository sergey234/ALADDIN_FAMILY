#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Export Manager
Система экспорта данных в различные форматы

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import io

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.base import ComponentStatus
from core.security_base import SecurityBase
from elasticsearch_simulator import ElasticsearchSimulator, LogEntry, LogLevel

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab не установлен. PDF экспорт будет недоступен.")


class ExportManager(SecurityBase):
    """Менеджер экспорта данных"""
    
    def __init__(self):
        super().__init__("ExportManager")
        self.service_name = "ExportManager"
        self.status = ComponentStatus.RUNNING
        self.export_dir = "exports"
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """Создание директории для экспорта"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            self.logger.info(f"Создана директория экспорта: {self.export_dir}")
    
    def export_logs_csv(self, logs: List[LogEntry], filename: Optional[str] = None) -> str:
        """Экспорт логов в CSV формат"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"aladdin_logs_{timestamp}.csv"
            
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['log_id', 'timestamp', 'level', 'component', 'message', 'metadata']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    row = {
                        'log_id': log.log_id,
                        'timestamp': log.timestamp.isoformat(),
                        'level': log.level.value,
                        'component': log.component,
                        'message': log.message,
                        'metadata': json.dumps(log.metadata, ensure_ascii=False)
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Экспорт CSV завершен: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта CSV: {e}")
            raise
    
    def export_logs_json(self, logs: List[LogEntry], filename: Optional[str] = None) -> str:
        """Экспорт логов в JSON формат"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"aladdin_logs_{timestamp}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Преобразуем логи в словари
            logs_data = []
            for log in logs:
                log_dict = {
                    'log_id': log.log_id,
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level.value,
                    'component': log.component,
                    'message': log.message,
                    'metadata': log.metadata
                }
                logs_data.append(log_dict)
            
            # Добавляем метаданные экспорта
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_logs': len(logs),
                    'export_format': 'JSON',
                    'version': '1.0'
                },
                'logs': logs_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Экспорт JSON завершен: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта JSON: {e}")
            raise
    
    def export_logs_pdf(self, logs: List[LogEntry], filename: Optional[str] = None) -> str:
        """Экспорт логов в PDF формат"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab не установлен. Установите: pip install reportlab")
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"aladdin_logs_{timestamp}.pdf"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Создаем PDF документ
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Заголовок
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph("ALADDIN Security System - Отчет по логам", title_style))
            story.append(Spacer(1, 12))
            
            # Информация об экспорте
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey
            )
            
            export_info = f"""
            <b>Дата экспорта:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}<br/>
            <b>Всего логов:</b> {len(logs)}<br/>
            <b>Формат:</b> PDF<br/>
            <b>Версия:</b> 1.0
            """
            story.append(Paragraph(export_info, info_style))
            story.append(Spacer(1, 20))
            
            # Статистика по уровням
            level_counts = {}
            component_counts = {}
            
            for log in logs:
                level = log.level.value
                component = log.component
                
                level_counts[level] = level_counts.get(level, 0) + 1
                component_counts[component] = component_counts.get(component, 0) + 1
            
            # Таблица статистики
            stats_data = [['Уровень', 'Количество'], ['Компонент', 'Количество']]
            
            for level, count in sorted(level_counts.items()):
                stats_data[0].append(f"{level}: {count}")
            
            for component, count in sorted(component_counts.items()):
                stats_data[1].append(f"{component}: {count}")
            
            # Максимальная длина для выравнивания
            max_len = max(len(stats_data[0]), len(stats_data[1]))
            for i in range(len(stats_data)):
                while len(stats_data[i]) < max_len:
                    stats_data[i].append("")
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("<b>Статистика по логам:</b>", styles['Heading2']))
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Логи (ограничиваем количество для PDF)
            max_logs_in_pdf = 100
            logs_to_show = logs[:max_logs_in_pdf]
            
            story.append(Paragraph(f"<b>Логи (показано {len(logs_to_show)} из {len(logs)}):</b>", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for i, log in enumerate(logs_to_show, 1):
                # Заголовок лога
                log_title = f"{i}. {log.component} - {log.level.value}"
                story.append(Paragraph(log_title, styles['Heading3']))
                
                # Время
                time_str = log.timestamp.strftime('%d.%m.%Y %H:%M:%S')
                story.append(Paragraph(f"<b>Время:</b> {time_str}", styles['Normal']))
                
                # Сообщение
                message = log.message.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f"<b>Сообщение:</b> {message}", styles['Normal']))
                
                # Метаданные
                if log.metadata:
                    metadata_str = json.dumps(log.metadata, ensure_ascii=False, indent=2)
                    metadata_str = metadata_str.replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"<b>Метаданные:</b><br/><font name='Courier' size='8'>{metadata_str}</font>", styles['Normal']))
                
                story.append(Spacer(1, 12))
            
            # Если логов больше чем помещается в PDF
            if len(logs) > max_logs_in_pdf:
                story.append(Paragraph(f"<i>... и еще {len(logs) - max_logs_in_pdf} логов (см. CSV/JSON экспорт)</i>", styles['Normal']))
            
            # Создаем PDF
            doc.build(story)
            
            self.logger.info(f"Экспорт PDF завершен: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта PDF: {e}")
            raise
    
    def export_system_stats(self, stats: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Экспорт статистики системы в JSON"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"aladdin_stats_{timestamp}.json"
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Добавляем метаданные экспорта
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'export_format': 'System Statistics JSON',
                    'version': '1.0'
                },
                'system_stats': stats
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Экспорт статистики завершен: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта статистики: {e}")
            raise
    
    def get_export_list(self) -> List[Dict[str, Any]]:
        """Получение списка экспортированных файлов"""
        try:
            files = []
            if os.path.exists(self.export_dir):
                for filename in os.listdir(self.export_dir):
                    filepath = os.path.join(self.export_dir, filename)
                    if os.path.isfile(filepath):
                        stat = os.stat(filepath)
                        files.append({
                            'filename': filename,
                            'filepath': filepath,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            # Сортируем по дате создания (новые сверху)
            files.sort(key=lambda x: x['created'], reverse=True)
            return files
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка файлов: {e}")
            return []
    
    def delete_export(self, filename: str) -> bool:
        """Удаление экспортированного файла"""
        try:
            filepath = os.path.join(self.export_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Файл удален: {filepath}")
                return True
            else:
                self.logger.warning(f"Файл не найден: {filepath}")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла: {e}")
            return False


if __name__ == "__main__":
    # Тестирование экспорта
    print("🚀 Тестирование Export Manager")
    print("=" * 40)
    
    # Создаем менеджер экспорта
    export_manager = ExportManager()
    
    # Создаем тестовые логи
    test_logs = [
        LogEntry(
            timestamp=datetime.now() - timedelta(minutes=5),
            level=LogLevel.INFO,
            component="TestComponent",
            message="Тестовое сообщение для экспорта",
            metadata={"test": True, "value": 123},
            log_id="test_001"
        ),
        LogEntry(
            timestamp=datetime.now() - timedelta(minutes=3),
            level=LogLevel.WARNING,
            component="AnotherComponent",
            message="Предупреждение о тестировании",
            metadata={"warning_type": "test", "severity": "medium"},
            log_id="test_002"
        )
    ]
    
    # Тестируем экспорт
    try:
        print("1. Экспорт в CSV...")
        csv_file = export_manager.export_logs_csv(test_logs)
        print(f"   ✅ CSV файл создан: {csv_file}")
        
        print("2. Экспорт в JSON...")
        json_file = export_manager.export_logs_json(test_logs)
        print(f"   ✅ JSON файл создан: {json_file}")
        
        if REPORTLAB_AVAILABLE:
            print("3. Экспорт в PDF...")
            pdf_file = export_manager.export_logs_pdf(test_logs)
            print(f"   ✅ PDF файл создан: {pdf_file}")
        else:
            print("3. PDF экспорт пропущен (ReportLab не установлен)")
        
        print("4. Список экспортированных файлов:")
        files = export_manager.get_export_list()
        for file_info in files:
            size_kb = file_info['size'] / 1024
            print(f"   📄 {file_info['filename']} ({size_kb:.1f} KB)")
        
        print("\n✅ Тестирование экспорта завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")