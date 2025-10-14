# Иерархия классов incident_response_agent.py

## Структура классов

### Enum классы (Перечисления)
1. **IncidentSeverity(Enum)** - Уровни серьезности инцидентов
   - LOW, MEDIUM, HIGH, CRITICAL, EMERGENCY

2. **IncidentStatus(Enum)** - Статусы инцидентов  
   - NEW, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, ESCALATED, CANCELLED

3. **IncidentType(Enum)** - Типы инцидентов
   - MALWARE, PHISHING, DDOS, DATA_BREACH, UNAUTHORIZED_ACCESS, etc.

4. **ResponseAction(Enum)** - Действия реагирования
   - ISOLATE, QUARANTINE, BLOCK, MONITOR, INVESTIGATE, etc.

### Основные классы
5. **Incident** - Класс для хранения данных об инциденте
   - Базовый класс (не наследует)
   - Содержит: ID, заголовок, описание, тип, серьезность, статус, время

6. **IncidentResponseMetrics** - Метрики агента реагирования
   - Базовый класс (не наследует)
   - Содержит: статистику, время реагирования, эффективность

7. **IncidentResponseAgent(SecurityBase)** - Главный агент
   - Наследует от SecurityBase
   - Основная функциональность реагирования на инциденты

## Наследование
- Все Enum классы наследуют от стандартного Enum
- IncidentResponseAgent наследует от SecurityBase
- Остальные классы являются базовыми

## Полиморфизм
- Enum классы обеспечивают типобезопасность
- IncidentResponseAgent использует полиморфизм через наследование от SecurityBase