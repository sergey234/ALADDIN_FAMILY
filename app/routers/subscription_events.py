"""
Subscription Events API
-----------------------
Принимает батч событий подписки от клиента.
Безопасность: user_id извлекается из Bearer токена (не доверяем клиентскому userId).
Дедупликация: по event_id.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import get_current_user
from app.database.database import get_session


router = APIRouter(prefix="/api/subscription/events", tags=["subscription-events"])


class SubscriptionEventItem(BaseModel):
    eventId: str = Field(..., min_length=8, max_length=128)
    eventType: str = Field(..., min_length=3, max_length=64)
    timestamp: float
    deviceId: str = Field(..., min_length=3, max_length=128)
    subscriptionLevel: Optional[str] = Field(default=None, max_length=32)
    metadata: Optional[Dict[str, str]] = None


class SubscriptionEventsBatchRequest(BaseModel):
    events: List[SubscriptionEventItem] = Field(..., min_length=1, max_length=100)


class SubscriptionEventsBatchResponse(BaseModel):
    acceptedCount: int
    duplicateCount: int
    failedCount: int
    failedEventIds: List[str]


async def ensure_table_exists(db: AsyncSession) -> None:
    # Совместимо с SQLite; в прод-контуре таблица создается лениво при первом запросе.
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS subscription_event_ingest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_ts REAL NOT NULL,
                device_id TEXT NOT NULL,
                subscription_level TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    await db.commit()


@router.post("/batch", response_model=SubscriptionEventsBatchResponse)
async def ingest_subscription_events_batch(
    request_body: SubscriptionEventsBatchRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> SubscriptionEventsBatchResponse:
    try:
        await ensure_table_exists(db)
        user_id = str(current_user["id"])

        accepted = 0
        duplicate = 0
        failed = 0
        failed_ids: List[str] = []

        for event in request_body.events:
            # Дедупликация по event_id на уровне запроса (до insert)
            existing = await db.execute(
                text("SELECT id FROM subscription_event_ingest WHERE event_id = :event_id"),
                {"event_id": event.eventId},
            )
            if existing.fetchone() is not None:
                duplicate += 1
                continue

            try:
                await db.execute(
                    text(
                        """
                        INSERT INTO subscription_event_ingest
                        (event_id, user_id, event_type, event_ts, device_id, subscription_level, metadata_json)
                        VALUES (:event_id, :user_id, :event_type, :event_ts, :device_id, :subscription_level, :metadata_json)
                        """
                    ),
                    {
                        "event_id": event.eventId,
                        "user_id": user_id,
                        "event_type": event.eventType,
                        "event_ts": event.timestamp,
                        "device_id": event.deviceId,
                        "subscription_level": event.subscriptionLevel,
                        "metadata_json": None if event.metadata is None else json.dumps(event.metadata, ensure_ascii=False),
                    },
                )
                accepted += 1
            except Exception:
                failed += 1
                failed_ids.append(event.eventId)

        await db.commit()
        return SubscriptionEventsBatchResponse(
            acceptedCount=accepted,
            duplicateCount=duplicate,
            failedCount=failed,
            failedEventIds=failed_ids,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to ingest events: {exc}")

class SummaryTimeseriesPoint(BaseModel):
    date: str
    count: int

class SubscriptionEventsSummary(BaseModel):
    totalEvents: int
    uniqueUsers: int
    uniqueDevices: int
    byEventType: Dict[str, int]
    timeseriesDaily: List[SummaryTimeseriesPoint]

@router.get("/stats/summary", response_model=SubscriptionEventsSummary)
async def get_subscription_events_summary(
    days: int = 7,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> SubscriptionEventsSummary:
    # Общая сводка за N дней (по user_id токена доступ разрешён; админ-гранулярность можно расширить позже)
    _ = current_user  # зарезервировано под RBAC
    if days < 1 or days > 90:
        days = 7

    # totalEvents
    total_q = await db.execute(
        text("SELECT COUNT(*) FROM subscription_event_ingest WHERE event_ts >= strftime('%s','now') - :sec"),
        {"sec": days * 86400},
    )
    total_events = int(total_q.scalar() or 0)

    # unique users
    users_q = await db.execute(
        text("SELECT COUNT(DISTINCT user_id) FROM subscription_event_ingest WHERE event_ts >= strftime('%s','now') - :sec"),
        {"sec": days * 86400},
    )
    unique_users = int(users_q.scalar() or 0)

    # unique devices
    dev_q = await db.execute(
        text("SELECT COUNT(DISTINCT device_id) FROM subscription_event_ingest WHERE event_ts >= strftime('%s','now') - :sec"),
        {"sec": days * 86400},
    )
    unique_devices = int(dev_q.scalar() or 0)

    # byEventType
    bytype_q = await db.execute(
        text(
            """
            SELECT event_type, COUNT(*) as cnt
            FROM subscription_event_ingest
            WHERE event_ts >= strftime('%s','now') - :sec
            GROUP BY event_type
            ORDER BY cnt DESC
            """
        ),
        {"sec": days * 86400},
    )
    by_event_type: Dict[str, int] = {row[0]: int(row[1]) for row in bytype_q.fetchall()}

    # timeseries daily
    ts_q = await db.execute(
        text(
            """
            SELECT strftime('%Y-%m-%d', datetime(event_ts, 'unixepoch')) as d, COUNT(*) as cnt
            FROM subscription_event_ingest
            WHERE event_ts >= strftime('%s','now') - :sec
            GROUP BY d
            ORDER BY d ASC
            """
        ),
        {"sec": days * 86400},
    )
    timeseries = [SummaryTimeseriesPoint(date=row[0], count=int(row[1])) for row in ts_q.fetchall()]

    return SubscriptionEventsSummary(
        totalEvents=total_events,
        uniqueUsers=unique_users,
        uniqueDevices=unique_devices,
        byEventType=by_event_type,
        timeseriesDaily=timeseries,
    )

class RecentEvent(BaseModel):
    eventId: str
    userId: str
    eventType: str
    timestamp: float
    deviceId: str
    subscriptionLevel: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    createdAt: str

@router.get("/recent", response_model=List[RecentEvent])
async def get_recent_subscription_events(
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> List[RecentEvent]:
    if limit < 1 or limit > 500:
        limit = 100
    rows = await db.execute(
        text(
            f"""
            SELECT event_id, user_id, event_type, event_ts, device_id, subscription_level, metadata_json, created_at
            FROM subscription_event_ingest
            ORDER BY id DESC
            LIMIT {limit}
            """
        )
    )
    result: List[RecentEvent] = []
    for r in rows.fetchall():
        metadata_obj = None
        if r[6]:
            try:
                metadata_obj = json.loads(r[6])
            except Exception:
                metadata_obj = {"raw": r[6]}
        result.append(
            RecentEvent(
                eventId=r[0],
                userId=r[1],
                eventType=r[2],
                timestamp=float(r[3]),
                deviceId=r[4],
                subscriptionLevel=r[5],
                metadata=metadata_obj,
                createdAt=str(r[7]),
            )
        )
    return result

class AlertCheckResponse(BaseModel):
    status: str  # ok | warn
    eventsLastHour: int
    thresholdMinPerHour: int

@router.get("/alert/check", response_model=AlertCheckResponse)
async def alert_check_subscription_events(
    minPerHour: int = 1,
    db: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> AlertCheckResponse:
    # Простой сигнал: минимальный объём телеметрии за последний час
    if minPerHour < 0:
        minPerHour = 0
    cnt_q = await db.execute(
        text("SELECT COUNT(*) FROM subscription_event_ingest WHERE event_ts >= strftime('%s','now') - 3600")
    )
    events_last_hour = int(cnt_q.scalar() or 0)
    status = "ok" if events_last_hour >= minPerHour else "warn"
    return AlertCheckResponse(status=status, eventsLastHour=events_last_hour, thresholdMinPerHour=minPerHour)

