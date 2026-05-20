# -*- coding: utf-8 -*-
"""Shared Family Chat WebSocket manager (main.py + family.py send push)."""
from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class FamilyChatWSManager:
    def __init__(self):
        self._rooms = defaultdict(set)

    async def connect(self, family_id: str, websocket: WebSocket):
        await websocket.accept()
        self._rooms[family_id].add(websocket)
        await self.broadcast(
            family_id,
            {
                "type": "presence",
                "status": "online",
                "family_id": family_id,
            },
        )

    def disconnect(self, family_id: str, websocket: WebSocket):
        room = self._rooms.get(family_id)
        if not room:
            return
        room.discard(websocket)
        if not room:
            self._rooms.pop(family_id, None)

    async def broadcast(self, family_id: str, payload: dict):
        stale = []
        for socket in list(self._rooms.get(family_id, set())):
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(socket)
        for socket in stale:
            self.disconnect(family_id, socket)


family_ws_manager = FamilyChatWSManager()
