# =============================================================================
# AI ASSISTANT (8 endpoints) - для добавления на сервер
# =============================================================================

# AI Assistant Chat
@app.post("/api/ai/assistant/chat")
async def ai_assistant_chat(data: dict):
    """AI помощник - обработка сообщений пользователя"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_chat", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        # Fallback mock response
        user_message = data.get("message", "")
        context = data.get("context", "general")
        responses = {
            "protection_status": "Ваша защита ALADDIN активна! Все 187 функций безопасности работают корректно.",
            "threat_analysis": "Анализ угроз завершен. Обнаружено 3 потенциальные угрозы, все заблокированы.",
            "recommendations": "Рекомендую включить все уровни защиты для максимальной безопасности.",
            "help": "Я - ваш AI помощник по безопасности ALADDIN. Могу помочь с анализом угроз, настройками защиты и ответами на вопросы.",
            "general": "Привет! Я AI помощник ALADDIN. Как я могу помочь вам с безопасностью?"
        }
        response_text = responses.get(context, responses["general"])
        return {
            "response": response_text,
            "confidence": 0.95,
            "suggestions": ["Проверить статус защиты", "Посмотреть статистику", "Настроить параметры"],
            "follow_up_questions": ["Что вас беспокоит?", "Нужна ли дополнительная защита?"],
            "source": "mock"
        }

@app.get("/api/ai/assistant/history")
async def ai_assistant_history():
    """История разговоров с AI помощником"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_history", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "conversations": [
                {"date": "2026-02-04", "messages": 12, "topics": ["protection", "threats"]},
                {"date": "2026-02-03", "messages": 8, "topics": ["settings", "analysis"]}
            ],
            "source": "mock"
        }

@app.post("/api/ai/assistant/feedback")
async def ai_assistant_feedback(data: dict):
    """Обратная связь по работе AI помощника"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_feedback", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        rating = data.get("rating", 5)
        comment = data.get("comment", "")
        return {
            "feedback_recorded": True,
            "average_rating": 4.8,
            "total_feedbacks": 1250,
            "source": "mock"
        }

@app.get("/api/ai/assistant/capabilities")
async def ai_assistant_capabilities():
    """Возможности AI помощника"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_capabilities", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "features": [
                "Анализ угроз в реальном времени",
                "Персональные рекомендации по безопасности",
                "Объяснение работы функций защиты",
                "Мониторинг подозрительной активности",
                "Советы по улучшению безопасности",
                "Ответы на вопросы о кибербезопасности"
            ],
            "languages": ["Русский", "English"],
            "response_time": "<2 сек",
            "accuracy": "95%",
            "source": "mock"
        }

@app.post("/api/ai/assistant/analyze_threat")
async def ai_assistant_analyze_threat(data: dict):
    """AI анализ конкретной угрозы"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_analyze_threat", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        threat_description = data.get("threat", "")
        threat_type = data.get("type", "unknown")
        return {
            "threat_level": "medium",
            "analysis": "Угроза проанализирована. Рекомендуется усилить защиту.",
            "actions_taken": ["Заблокирован IP", "Отправлено уведомление", "Добавлен в черный список"],
            "prevention_tips": ["Включите VPN", "Обновите пароли", "Используйте 2FA"],
            "source": "mock"
        }

@app.get("/api/ai/assistant/recommendations")
async def ai_assistant_recommendations():
    """Персональные рекомендации по безопасности"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_recommendations", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "personal_recommendations": [
                "Включите все уровни защиты для максимальной безопасности",
                "Настройте автоматические обновления",
                "Используйте сложные пароли",
                "Регулярно проверяйте подключенные устройства"
            ],
            "security_score": 95,
            "improvement_areas": ["VPN использование", "Парольная политика"],
            "source": "mock"
        }

@app.post("/api/ai/assistant/report_incident")
async def ai_assistant_report_incident(data: dict):
    """Сообщить о инциденте через AI помощника"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_report_incident", data)
        return result if success else {"error": message, "source": "mock"}
    else:
        incident_type = data.get("type", "")
        description = data.get("description", "")
        return {
            "incident_id": "INC-2026-004-001",
            "status": "investigating",
            "estimated_resolution": "2 hours",
            "assigned_specialist": "AI Security Team",
            "follow_up_actions": ["Анализ логов", "Проверка систем", "Уведомление пользователя"],
            "source": "mock"
        }

@app.get("/api/ai/assistant/security_tips")
async def ai_assistant_security_tips():
    """Полезные советы по безопасности от AI"""
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("ai_assistant_security_tips", {})
        return result if success else {"error": message, "source": "mock"}
    else:
        return {
            "daily_tips": [
                "Всегда проверяйте URL перед вводом личных данных",
                "Используйте менеджер паролей для сложных комбинаций",
                "Регулярно обновляйте приложения и ОС",
                "Будьте осторожны с email от неизвестных отправителей"
            ],
            "weekly_focus": "Защита от фишинга",
            "monthly_goal": "Достичь 100% безопасности",
            "source": "mock"
        }
