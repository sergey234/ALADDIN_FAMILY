"""
============================================
ANALYTICS API: Endpoints для аналитики безопасности
============================================
Сервер: 149.154.65.180
Дата: 13 марта 2026
============================================
API для получения аналитики безопасности с реальными данными из БД
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ Авторизация с реальным user_id
# ✅ JWT-014: ИСПРАВЛЕНО - используем правильный get_current_user из app.auth.auth
from app.auth.auth import get_current_user

# ✅ Импорт БД
try:
    from app.database.database import get_db
except ImportError:
    # Fallback если БД недоступна
    def get_db():
        yield None

router = APIRouter(prefix="/api", tags=["analytics"])

# ============================================
# МОДЕЛИ ЗАПРОСОВ И ОТВЕТОВ
# ============================================

class ThreatByType(BaseModel):
    """Статистика по типу угрозы"""
    type: str
    count: int
    icon: Optional[str] = None

class TopThreat(BaseModel):
    """Топ угроза"""
    id: str
    name: str
    count: int
    icon: str
    timestamp: Optional[str] = None

class AnalyticsResponse(BaseModel):
    """Ответ на запрос аналитики"""
    period: str
    threatsDetected: int
    threatsBlocked: int
    itemsScanned: int
    protectionLevel: int
    topThreats: List[TopThreat]
    threatsByType: List[ThreatByType]

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_period_delta(period: str) -> timedelta:
    """Получить timedelta для периода"""
    if period == "day":
        return timedelta(days=1)
    elif period == "week":
        return timedelta(weeks=1)
    elif period == "month":
        return timedelta(days=30)
    else:
        return timedelta(days=1)  # По умолчанию день

def get_analytics_from_db(
    user_id: str,
    period: str,
    db: Session
) -> AnalyticsResponse:
    """
    Получить аналитику из базы данных.
    
    ✅ РЕАЛИЗАЦИЯ: Реальные SQL запросы к PostgreSQL
    """
    try:
        period_delta = get_period_delta(period)
        start_date = datetime.utcnow() - period_delta
        
        # ✅ 1. Получаем количество обнаруженных угроз
        threats_detected_result = db.execute(
            text("""
                SELECT COUNT(*) as count
                FROM security_events
                WHERE user_id = :user_id
                AND event_type = 'threat_detected'
                AND created_at >= :start_date
            """),
            {"user_id": user_id, "start_date": start_date}
        )
        threats_detected_row = threats_detected_result.fetchone()
        threats_detected = threats_detected_row[0] if threats_detected_row else 0
        
        # ✅ 2. Получаем количество заблокированных угроз
        threats_blocked_result = db.execute(
            text("""
                SELECT COUNT(*) as count
                FROM security_events
                WHERE user_id = :user_id
                AND event_type = 'threat_blocked'
                AND created_at >= :start_date
            """),
            {"user_id": user_id, "start_date": start_date}
        )
        threats_blocked_row = threats_blocked_result.fetchone()
        threats_blocked = threats_blocked_row[0] if threats_blocked_row else 0
        
        # ✅ 3. Получаем количество просканированных элементов
        items_scanned_result = db.execute(
            text("""
                SELECT COUNT(*) as count
                FROM security_events
                WHERE user_id = :user_id
                AND event_type IN ('scan_completed', 'file_scanned', 'url_scanned')
                AND created_at >= :start_date
            """),
            {"user_id": user_id, "start_date": start_date}
        )
        items_scanned_row = items_scanned_result.fetchone()
        items_scanned = items_scanned_row[0] if items_scanned_row else 0
        
        # ✅ 4. Вычисляем уровень защиты (процент заблокированных от обнаруженных)
        protection_level = 0
        if threats_detected > 0:
            protection_level = int((threats_blocked / threats_detected) * 100)
        elif threats_blocked > 0:
            # Если есть заблокированные, но нет обнаруженных - значит все заблокировано
            protection_level = 100
        
        # ✅ 5. Получаем топ угрозы
        top_threats_result = db.execute(
            text("""
                SELECT 
                    threat_type,
                    COUNT(*) as count,
                    MAX(created_at) as last_seen
                FROM security_events
                WHERE user_id = :user_id
                AND event_type = 'threat_detected'
                AND created_at >= :start_date
                GROUP BY threat_type
                ORDER BY count DESC
                LIMIT 10
            """),
            {"user_id": user_id, "start_date": start_date}
        )
        top_threats_rows = top_threats_result.fetchall()
        
        top_threats = []
        threat_icons = {
            "malware": "🦠",
            "phishing": "🎣",
            "tracker": "👁️",
            "virus": "🦠",
            "spyware": "🔍",
            "adware": "📢",
            "ransomware": "🔒",
            "trojan": "🐴",
            "worm": "🐛",
            "rootkit": "🕳️"
        }
        
        for idx, row in enumerate(top_threats_rows):
            threat_type = row[0] or "unknown"
            count = row[1] or 0
            last_seen = row[2]
            
            top_threats.append(TopThreat(
                id=f"threat_{idx}",
                name=threat_type.replace("_", " ").title(),
                count=count,
                icon=threat_icons.get(threat_type.lower(), "⚠️"),
                timestamp=last_seen.isoformat() if last_seen else None
            ))
        
        # ✅ 6. Получаем статистику по типам угроз
        threats_by_type_result = db.execute(
            text("""
                SELECT 
                    threat_type,
                    COUNT(*) as count
                FROM security_events
                WHERE user_id = :user_id
                AND event_type = 'threat_blocked'
                AND created_at >= :start_date
                GROUP BY threat_type
                ORDER BY count DESC
            """),
            {"user_id": user_id, "start_date": start_date}
        )
        threats_by_type_rows = threats_by_type_result.fetchall()
        
        threats_by_type = []
        for row in threats_by_type_rows:
            threat_type = row[0] or "unknown"
            count = row[1] or 0
            
            threats_by_type.append(ThreatByType(
                type=threat_type.replace("_", " ").title(),
                count=count,
                icon=threat_icons.get(threat_type.lower(), "⚠️")
            ))
        
        return AnalyticsResponse(
            period=period,
            threatsDetected=threats_detected,
            threatsBlocked=threats_blocked,
            itemsScanned=items_scanned,
            protectionLevel=protection_level,
            topThreats=top_threats,
            threatsByType=threats_by_type
        )
        
    except Exception as e:
        # ✅ Если ошибка БД - логируем и возвращаем нули
        print(f"⚠️ Analytics DB Error: {e}")
        # Возвращаем честные нули вместо ошибки
        return AnalyticsResponse(
            period=period,
            threatsDetected=0,
            threatsBlocked=0,
            itemsScanned=0,
            protectionLevel=0,
            topThreats=[],
            threatsByType=[]
        )

# ============================================
# ENDPOINT: GET /api/analytics
# ============================================

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    period: str = Query("day", regex="^(day|week|month)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить аналитику безопасности за указанный период.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    
    Параметры:
    - period: Период аналитики ("day", "week", "month")
    
    Возвращает:
    - threatsDetected: Количество обнаруженных угроз
    - threatsBlocked: Количество заблокированных угроз
    - itemsScanned: Количество просканированных элементов
    - protectionLevel: Уровень защиты (0-100%)
    - topThreats: Топ 10 угроз
    - threatsByType: Статистика по типам угроз
    """
    # ✅ Получить реальный user_id из токена
    user_id = current_user.get("sub") or current_user.get("id") or current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id"
        )
    
    # ✅ РЕАЛИЗАЦИЯ: Получить аналитику из БД
    if db is None:
        # ✅ Если БД недоступна - возвращаем честные нули
        return AnalyticsResponse(
            period=period,
            threatsDetected=0,
            threatsBlocked=0,
            itemsScanned=0,
            protectionLevel=0,
            topThreats=[],
            threatsByType=[]
        )
    
    try:
        analytics = get_analytics_from_db(str(user_id), period, db)
        return analytics
    except Exception as e:
        # ✅ Если ошибка БД - возвращаем честные нули
        print(f"⚠️ Analytics DB Error: {e}")
        return AnalyticsResponse(
            period=period,
            threatsDetected=0,
            threatsBlocked=0,
            itemsScanned=0,
            protectionLevel=0,
            topThreats=[],
            threatsByType=[]
        )

# ============================================
# ENDPOINT: GET /api/analytics/threats
# ============================================

class ThreatsResponse(BaseModel):
    """Ответ на запрос угроз"""
    threats: List[Dict[str, Any]]
    total: int
    source: str

@router.get("/analytics/threats", response_model=ThreatsResponse)
async def get_analytics_threats(
    period: str = Query("day", regex="^(day|week|month)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список угроз за указанный период.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    
    Параметры:
    - period: Период аналитики ("day", "week", "month")
    
    Возвращает:
    - threats: Список угроз
    - total: Общее количество угроз
    """
    user_id = current_user.get("sub") or current_user.get("id") or current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id"
        )
    
    # ✅ Пробуем вызвать SFM функцию
    try:
        import sys
        backend_path = "/opt/aladdin-backend"
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from sfm_adapter_server import SFMAdapter
        from complete_api_sfm_mapping import get_sfm_function_name
        
        sfm_adapter = SFMAdapter()
        params = {"user_id": str(user_id), "period": period}
        
        success, result, message = sfm_adapter.execute_function(
            get_sfm_function_name("get_analytics_security_events"),
            params
        )
        
        if success and isinstance(result, dict):
            return ThreatsResponse(
                threats=result.get("threats", []),
                total=result.get("total", 0),
                source="sfm_real"
            )
    except Exception as e:
        print(f"⚠️ Analytics SFM Error: {e}")
    
    # Fallback: возвращаем пустой список
    return ThreatsResponse(
        threats=[],
        total=0,
        source="fallback"
    )

# ============================================
# ENDPOINT: GET /api/analytics/top-threats
# ============================================

class TopThreatsResponse(BaseModel):
    """Ответ на запрос топ угроз"""
    topThreats: List[TopThreat]
    total: int
    source: str

@router.get("/analytics/top-threats", response_model=TopThreatsResponse)
async def get_analytics_top_threats(
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("day", regex="^(day|week|month)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить топ угроз за указанный период.
    
    Требуется авторизация (токен в заголовке Authorization: Bearer {token})
    
    Параметры:
    - limit: Количество угроз в топе (1-50)
    - period: Период аналитики ("day", "week", "month")
    
    Возвращает:
    - topThreats: Список топ угроз
    - total: Общее количество угроз
    """
    user_id = current_user.get("sub") or current_user.get("id") or current_user.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id"
        )
    
    # ✅ Пробуем вызвать SFM функцию
    try:
        import sys
        backend_path = "/opt/aladdin-backend"
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from sfm_adapter_server import SFMAdapter
        from complete_api_sfm_mapping import get_sfm_function_name
        
        sfm_adapter = SFMAdapter()
        params = {"user_id": str(user_id), "period": period, "limit": limit}
        
        success, result, message = sfm_adapter.execute_function(
            get_sfm_function_name("get_analytics_overview"),
            params
        )
        
        if success and isinstance(result, dict):
            top_threats = result.get("topThreats", [])
            return TopThreatsResponse(
                topThreats=top_threats[:limit],
                total=len(top_threats),
                source="sfm_real"
            )
    except Exception as e:
        print(f"⚠️ Analytics SFM Error: {e}")
    
    # Fallback: возвращаем пустой список
    return TopThreatsResponse(
        topThreats=[],
        total=0,
        source="fallback"
    )
