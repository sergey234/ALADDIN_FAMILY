# Анализ DeviceDetailScreen.swift - все строки для локализации

## Список всех прямых строк (~30-35 ключей):

1. "Инфо" (таб)
2. "Статистика" (таб)
3. "Угрозы" (таб)
4. "Настройки" (таб)
5. "Навигационная панель деталей устройства" (accessibilityLabel)
6. "устройство" (accessibilityLabel в "\(device.type.rawValue) устройство")
7. "Статус: \(statusText(device.status))" (accessibilityLabel)
8. "Последняя активность: \(device.lastActive)" (Text и accessibilityLabel)
9. "Выбор вкладки: \(selectedTab.rawValue)" (accessibilityLabel)
10. "Детали устройства \(device.name)" (accessibilityLabel)
11. "Защищено" (statusText)
12. "Требует внимания" (statusText)
13. "Опасность" (statusText)
14. "Неактивно" (statusText)
15. "Заблокировать устройство" (кнопка и accessibilityLabel)
16. "Нажмите для блокировки устройства" (accessibilityHint)
17. "Удалить устройство" (кнопка и accessibilityLabel)
18. "Нажмите для удаления устройства из системы" (accessibilityHint)
19. "\(title) вкладка" (accessibilityLabel в TabButton)
20. "Выбранная вкладка \(title)" / "Нажмите для переключения на вкладку \(title)" (accessibilityHint в TabButton)
21. "Владелец" (InfoRow)
22. "Тип" (InfoRow)
23. "Модель" (InfoRow)
24. "Система" (InfoRow)
25. "IP адрес" (InfoRow)
26. "MAC адрес" (InfoRow)
27. "Угрозы заблокированы" (StatCard)
28. "Трафик загружено" (StatCard)
29. "Трафик отправлено" (StatCard)
30. "Время использования" (StatCard)
31. "Вредоносный сайт" (ThreatItemRow - mock данные)
32. "Трекер заблокирован" (ThreatItemRow - mock данные)
33. "Фишинг попытка" (ThreatItemRow - mock данные)
34. "5 мин назад" / "15 мин назад" / "1 час назад" (ThreatItemRow - mock данные)
35. "Уровень угрозы: \(severityText)" (accessibilityLabel)
36. "время: \(time)" (accessibilityLabel)
37. "Угроза: \(name), уровень \(severityText), время \(time)" (accessibilityLabel)
38. "низкий" (severityText)
39. "средний" (severityText)
40. "высокий" (severityText)
41. "Защита устройства" (ALADDINToggle)
42. "Автоматическое сканирование" (ALADDINToggle)

## Ключи для создания (префикс device_detail_):

device_detail_tab_info
device_detail_tab_stats
device_detail_tab_threats
device_detail_tab_settings
device_detail_nav_accessibility
device_detail_device_type
device_detail_status
device_detail_status_protected
device_detail_status_warning
device_detail_status_danger
device_detail_status_inactive
device_detail_last_activity
device_detail_tab_selector
device_detail_accessibility
device_detail_block_device
device_detail_block_device_hint
device_detail_remove_device
device_detail_remove_device_hint
device_detail_tab_accessibility
device_detail_tab_selected_hint
device_detail_tab_switch_hint
device_detail_info_owner
device_detail_info_type
device_detail_info_model
device_detail_info_system
device_detail_info_ip
device_detail_info_mac
device_detail_stats_threats_blocked
device_detail_stats_traffic_downloaded
device_detail_stats_traffic_uploaded
device_detail_stats_usage_time
device_detail_threat_severity
device_detail_threat_severity_low
device_detail_threat_severity_medium
device_detail_threat_severity_high
device_detail_threat_accessibility
device_detail_threat_time
device_detail_protection_enabled
device_detail_scanning_enabled

