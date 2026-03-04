"""
Анонимный режим ALADDIN - работа без персональных данных
Соответствует требованиям 152-ФЗ (не обрабатывает ПД)
"""

import uuid
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class AnonymousSession:
    """Анонимная сессия без персональных данных"""
    
    def __init__(self):
        self.session_id = self._generate_anonymous_id()
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=24)
        self.activities = []
        self.no_personal_data = True
    
    def _generate_anonymous_id(self) -> str:
        """Генерация анонимного ID без привязки к пользователю"""
        random_data = f"{uuid.uuid4()}{time.time()}"
        return hashlib.sha256(random_data.encode()).hexdigest()[:16]
    
    def is_valid(self) -> bool:
        """Проверка валидности сессии"""
        return datetime.now() < self.expires_at
    
    def add_activity(self, activity: str) -> None:
        """Добавление активности (без ПД)"""
        self.activities.append({
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'session_id': self.session_id
        })


class AnonymousThreatAnalyzer:
    """Анализатор угроз в анонимном режиме"""
    
    def __init__(self):
        self.global_threats = []
        self.public_stats = {}
    
    def analyze_global_threats(self) -> Dict[str, Any]:
        """Анализ глобальных угроз (без ПД)"""
        return {
            'threat_level': 'medium',
            'active_threats': len(self.global_threats),
            'recommendations': self._get_general_recommendations(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_general_recommendations(self) -> List[str]:
        """Общие рекомендации по безопасности"""
        return [
            "Используйте сложные пароли",
            "Обновляйте программное обеспечение",
            "Не переходите по подозрительным ссылкам",
            "Используйте двухфакторную аутентификацию",
            "Регулярно делайте резервные копии"
        ]
    
    def get_public_stats(self) -> Dict[str, Any]:
        """Публичная статистика (без ПД)"""
        return {
            'total_attacks_blocked': 12543,
            'countries_affected': 45,
            'threat_categories': {
                'phishing': 35,
                'malware': 28,
                'ddos': 20,
                'data_breach': 17
            },
            'last_updated': datetime.now().isoformat()
        }


class AnonymousEducationSystem:
    """Образовательная система в анонимном режиме"""
    
    def __init__(self):
        self.courses = self._load_public_courses()
        self.quizzes = self._load_public_quizzes()
    
    def _load_public_courses(self) -> List[Dict[str, Any]]:
        """Загрузка публичных курсов"""
        return [
            {
                'id': 'cyber_basics',
                'title': 'Основы кибербезопасности',
                'duration': '2 часа',
                'level': 'Начальный',
                'topics': ['Пароли', 'Фишинг', 'Антивирусы']
            },
            {
                'id': 'mobile_security',
                'title': 'Безопасность мобильных устройств',
                'duration': '1.5 часа',
                'level': 'Средний',
                'topics': ['Приложения', 'WiFi', 'Bluetooth']
            }
        ]
    
    def _load_public_quizzes(self) -> List[Dict[str, Any]]:
        """Загрузка публичных тестов"""
        return [
            {
                'id': 'password_security',
                'title': 'Тест на безопасность паролей',
                'questions': 10,
                'difficulty': 'Начальный'
            },
            {
                'id': 'phishing_detection',
                'title': 'Определение фишинга',
                'questions': 15,
                'difficulty': 'Средний'
            }
        ]
    
    def get_course_content(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Получение контента курса (без ПД)"""
        for course in self.courses:
            if course['id'] == course_id:
                return course
        return None
    
    def submit_quiz_answer(self, quiz_id: str, answers: List[str], 
                          session: AnonymousSession) -> Dict[str, Any]:
        """Отправка ответов на тест (анонимно)"""
        # Анализ ответов без сохранения ПД
        score = self._calculate_score(quiz_id, answers)
        
        # Добавляем активность в сессию
        session.add_activity(f"Completed quiz: {quiz_id}")
        
        return {
            'score': score,
            'total_questions': len(answers),
            'percentage': (score / len(answers)) * 100,
            'recommendations': self._get_quiz_recommendations(score, len(answers))
        }
    
    def _calculate_score(self, quiz_id: str, answers: List[str]) -> int:
        """Расчет баллов (упрощенный)"""
        # В реальной реализации здесь была бы проверка правильности
        return len(answers) - 1  # Демо-логика
    
    def _get_quiz_recommendations(self, score: int, total: int) -> List[str]:
        """Рекомендации по результатам теста"""
        percentage = (score / total) * 100
        
        if percentage >= 80:
            return ["Отличные знания! Продолжайте изучать новые темы."]
        elif percentage >= 60:
            return ["Хорошие знания. Рекомендуем изучить дополнительные материалы."]
        else:
            return ["Рекомендуем пройти курсы по основам кибербезопасности."]


class AnonymousModeManager:
    """Менеджер анонимного режима"""
    
    def __init__(self):
        self.sessions: Dict[str, AnonymousSession] = {}
        self.threat_analyzer = AnonymousThreatAnalyzer()
        self.education_system = AnonymousEducationSystem()
    
    def create_session(self) -> str:
        """Создание новой анонимной сессии"""
        session = AnonymousSession()
        self.sessions[session.session_id] = session
        return session.session_id
    
    def get_session(self, session_id: str) -> Optional[AnonymousSession]:
        """Получение сессии"""
        session = self.sessions.get(session_id)
        if session and session.is_valid():
            return session
        return None
    
    def cleanup_expired_sessions(self) -> None:
        """Очистка истекших сессий"""
        current_time = datetime.now()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.expires_at < current_time
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
    
    def get_dashboard_data(self, session_id: str) -> Dict[str, Any]:
        """Получение данных дашборда (анонимно)"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_info': {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'activities_count': len(session.activities)
            },
            'threat_analysis': self.threat_analyzer.analyze_global_threats(),
            'public_stats': self.threat_analyzer.get_public_stats(),
            'available_courses': self.education_system.courses,
            'available_quizzes': self.education_system.quizzes,
            'no_personal_data': True
        }


# Пример использования
if __name__ == "__main__":
    manager = AnonymousModeManager()
    
    # Создание анонимной сессии
    session_id = manager.create_session()
    print(f"Создана анонимная сессия: {session_id}")
    
    # Получение данных дашборда
    dashboard = manager.get_dashboard_data(session_id)
    print("Дашборд готов (без персональных данных)")
    
    # Очистка истекших сессий
    manager.cleanup_expired_sessions()
    print("Очистка завершена")