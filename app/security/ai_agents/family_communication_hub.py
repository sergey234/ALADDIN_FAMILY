"""Family Communication Hub
============================

High-level orchestrator that unifies different family communication
channels (mobile app, SMS, email, voice) and keeps delivery metrics.
The module aggregates the specialised expansion modules that live in the
same package and provides a clean, testable façade for the Safe Function
Manager.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Deque, Dict, Iterable, List, Optional

try:  # Optional dependency: specialised expansion (children protection)
    from .family_communication_hub_children_protection_expansion import (
        ChildrenProtectionExpansion,
    )
except Exception:  # pragma: no cover - graceful degradation
    ChildrenProtectionExpansion = None  # type: ignore

try:  # Optional dependency: messenger integrations
    from .family_communication_hub_max_messenger_expansion import (
        MessengerExpansion,
    )
except Exception:  # pragma: no cover - graceful degradation
    MessengerExpansion = None  # type: ignore


class CommunicationError(RuntimeError):
    """Raised when a channel cannot deliver a message."""


class CommunicationChannel(Enum):
    """Supported communication channels."""

    MOBILE_APP = "mobile_app"
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"
    MESSENGER = "messenger"


@dataclass
class FamilyMessage:
    """Message that should be delivered to every active channel."""

    message_id: str
    author: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 3  # 1 – highest priority, 5 – informational


@dataclass
class ChannelStats:
    """Runtime metrics for a channel."""

    name: str
    channel_type: CommunicationChannel
    deliveries: int = 0
    failures: int = 0
    muted_until: Optional[datetime] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def is_active(self, now: Optional[datetime] = None) -> bool:
        moment = now or datetime.utcnow()
        return self.muted_until is None or self.muted_until <= moment


class FamilyCommunicationHub:
    """Central hub that distributes messages across registered channels."""

    def __init__(
        self,
        retention_limit: int = 200,
        escalation_threshold: int = 3,
        children_expansion: Optional[ChildrenProtectionExpansion] = None,
        messenger_expansion: Optional[MessengerExpansion] = None,
    ) -> None:
        self._channels: Dict[str, ChannelStats] = {}
        self._messages: Deque[FamilyMessage] = deque(maxlen=retention_limit)
        self._deliveries: Dict[str, List[datetime]] = defaultdict(list)
        self._escalation_threshold = escalation_threshold
        self._children_expansion = children_expansion
        self._messenger_expansion = messenger_expansion
        self._lock = asyncio.Lock()

    def register_channel(
        self,
        name: str,
        channel_type: CommunicationChannel,
        *,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """Register a new communication channel."""

        if name in self._channels:
            raise ValueError(f"Channel '{name}' is already registered")

        self._channels[name] = ChannelStats(
            name=name,
            channel_type=channel_type,
            metadata=metadata or {},
        )

    def mute_channel(self, name: str, duration: timedelta) -> None:
        """Temporarily disable a noisy channel."""

        channel = self._get_channel(name)
        channel.muted_until = datetime.utcnow() + duration

    def resume_channel(self, name: str) -> None:
        """Re-enable a channel immediately."""

        channel = self._get_channel(name)
        channel.muted_until = None

    async def broadcast(self, message: FamilyMessage) -> Dict[str, bool]:
        """Deliver a message to all active channels."""

        async with self._lock:
            self._messages.appendleft(message)
            results: Dict[str, bool] = {}
            now = datetime.utcnow()

            for name, channel in self._channels.items():
                if not channel.is_active(now):
                    results[name] = False
                    continue

                try:
                    await self._deliver_to_channel(channel, message)
                except CommunicationError:
                    channel.failures += 1
                    results[name] = False
                else:
                    channel.deliveries += 1
                    self._deliveries[name].append(now)
                    results[name] = True

            await self._maybe_escalate(message)
            return results

    async def _deliver_to_channel(
        self, channel: ChannelStats, message: FamilyMessage
    ) -> None:
        """Delegate message delivery to the appropriate expansion."""

        if channel.channel_type == CommunicationChannel.MOBILE_APP:
            return
        if (
            channel.channel_type == CommunicationChannel.MESSENGER
            and self._messenger_expansion
        ):
            success = await self._messenger_expansion.send_to_messengers(
                message.content, channel.metadata
            )
            if not success:
                raise CommunicationError("Messenger delivery failed")
            return
        if (
            channel.channel_type == CommunicationChannel.VOICE
            and self._children_expansion
        ):
            success = await self._children_expansion.place_guardian_call(
                message.content, channel.metadata
            )
            if not success:
                raise CommunicationError("Guardian call failed")
            return

        if channel.channel_type in {
            CommunicationChannel.SMS,
            CommunicationChannel.EMAIL,
            CommunicationChannel.VOICE,
        }:
            return

        raise CommunicationError(
            f"Unsupported communication channel: {channel.channel_type.value}"
        )

    async def _maybe_escalate(self, message: FamilyMessage) -> None:
        """Trigger escalation logic when repeated failures occur."""

        if not self._children_expansion:
            return

        failed_channels = [
            stats
            for stats in self._channels.values()
            if stats.failures >= self._escalation_threshold
        ]
        if failed_channels:
            await self._children_expansion.escalate_to_emergency_team(
                message_id=message.message_id,
                failed_channels=[stats.name for stats in failed_channels],
                priority=message.priority,
            )
            for stats in failed_channels:
                stats.failures = 0

    def recent_messages(self, limit: int = 10) -> Iterable[FamilyMessage]:
        """Return the most recent messages."""

        return list(list(self._messages)[:limit])

    def channel_statistics(self) -> Dict[str, ChannelStats]:
        """Expose a snapshot of channel metrics."""

        return {name: stats for name, stats in self._channels.items()}

    def delivery_velocity(self, name: str, window: timedelta) -> int:
        """Calculate how many messages a channel delivered within a window."""

        deliveries = self._deliveries.get(name, [])
        threshold = datetime.utcnow() - window
        return sum(1 for timestamp in deliveries if timestamp >= threshold)

    def _get_channel(self, name: str) -> ChannelStats:
        if name not in self._channels:
            raise KeyError(f"Unknown channel '{name}'")
        return self._channels[name]


__all__ = [
    "FamilyCommunicationHub",
    "FamilyMessage",
    "CommunicationChannel",
    "CommunicationError",
]

